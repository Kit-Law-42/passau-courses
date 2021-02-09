from enum import Enum
import json
import luigi
import luigi.contrib.hadoop
import luigi.contrib.hdfs
from luigi.mock import MockTarget
import radb
import radb.ast
import radb.parse

'''
Control where the input data comes from, and where output data should go.
'''


class ExecEnv(Enum):
    LOCAL = 1  # read/write local files
    HDFS = 2  # read/write HDFS
    MOCK = 3  # read/write mock data to an in-memory file system.


'''
Switches between different execution environments and file systems.
'''


class OutputMixin(luigi.Task):
    exec_environment = luigi.EnumParameter(enum=ExecEnv, default=ExecEnv.HDFS)
    # deterine which environment we are in

    def get_output(self, fn):
        if self.exec_environment == ExecEnv.HDFS:
            return luigi.contrib.hdfs.HdfsTarget(fn)
        elif self.exec_environment == ExecEnv.MOCK:
            return MockTarget(fn)
        else:
            return luigi.LocalTarget(fn)


class InputData(OutputMixin):
    filename = luigi.Parameter()

    def output(self):
        return self.get_output(self.filename)


'''
Counts the number of steps / luigi tasks that we need for evaluating this query.
'''


def count_steps(raquery):
    assert (isinstance(raquery, radb.ast.Node))

    if (isinstance(raquery, radb.ast.Project) and isinstance(raquery.inputs[0], radb.ast.Select) and isinstance(raquery.inputs[0].inputs[0], radb.ast.Select)):
        return 1 + count_steps(raquery.inputs[0].inputs[0].inputs[0])

    elif (isinstance(raquery, radb.ast.Project) and isinstance(raquery.inputs[0], radb.ast.Select)):
        return 1 + count_steps(raquery.inputs[0].inputs[0])
    elif (isinstance(raquery, radb.ast.Join) and isinstance(raquery.inputs[1], radb.ast.Select)) or (isinstance(raquery, radb.ast.Join) and isinstance(raquery.inputs[0], radb.ast.Select)):
        return 1 + count_steps(raquery.inputs[0]) + count_steps(raquery.inputs[1])
    elif (isinstance(raquery, radb.ast.Select) or isinstance(raquery, radb.ast.Project) or
            isinstance(raquery, radb.ast.Rename)):
        return 1 + count_steps(raquery.inputs[0])

    elif isinstance(raquery, radb.ast.Join):
        return 1 + count_steps(raquery.inputs[0]) + count_steps(raquery.inputs[1])

    elif isinstance(raquery, radb.ast.RelRef):
        return 1

    else:
        raise Exception("count_steps: Cannot handle operator " +
                        str(type(raquery)) + ".")


class RelAlgQueryTask(luigi.contrib.hadoop.JobTask, OutputMixin):
    '''
    Each physical operator knows its (partial) query string.
    As a string, the value of this parameter can be searialized
    and shipped to the data node in the Hadoop cluster.
    '''
    querystring = luigi.Parameter()

    '''
    Each physical operator within a query has its own step-id.
    This is used to rename the temporary files for exhanging
    data between chained MapReduce jobs.
    '''
    step = luigi.IntParameter(default=1)

    '''
    Add optimize parameter for miniHive.py
    '''

    optimize = luigi.BoolParameter()
    '''
    In HDFS, we call the folders for temporary data tmp1, tmp2, ...
    In the local or mock file system, we call the files tmp1.tmp...
    '''

    def output(self):
        if self.exec_environment == ExecEnv.HDFS:
            filename = "tmp" + str(self.step)
        else:
            filename = "tmp" + str(self.step) + ".tmp"
        return self.get_output(filename)


'''
Given the radb-string representation of a relational algebra query,
this produces a tree of luigi tasks with the physical query operators.
'''

'''
Rules of chain folding
1. If multiple map phases are adjacent, merge them into one phase.
2. If the job ends with a map phase (combined or otherwise), push that phase into the reducer right before it.
3. In some cases, this is not possible
because you may need some enrichment data in order to do the filtering
4. Push the processes that decrease the amount of data
into the previous reducer, while keeping the processes that increase the amount of
data where they are.
'''


def task_factory(raquery, optimize=False, step=1, env=ExecEnv.HDFS):
    assert (isinstance(raquery, radb.ast.Node))

    if (isinstance(raquery, radb.ast.Project) and optimize and isinstance(raquery.inputs[0], radb.ast.Select) and isinstance(raquery.inputs[0].inputs[0], radb.ast.Rename)):
        # do something
        return ProjectSelectRenameTask(querystring=str(raquery) + ";", step=step, exec_environment=env, optimize=optimize)
    elif (isinstance(raquery, radb.ast.Project) and isinstance(raquery.inputs[0], radb.ast.Select) and optimize):
        return ProjectSelectTask(querystring=str(raquery) + ";", step=step, exec_environment=env, optimize=optimize)
    elif (isinstance(raquery, radb.ast.Join) and isinstance(raquery.inputs[1], radb.ast.Select) and isinstance(raquery.inputs[0], radb.ast.Select) and optimize):
        return JoinBothSelectTask(querystring=str(raquery) + ";", step=step, exec_environment=env, optimize=optimize)
    elif (isinstance(raquery, radb.ast.Join) and isinstance(raquery.inputs[1], radb.ast.Select) and optimize):
        return JoinRightSelectTask(querystring=str(raquery) + ";", step=step, exec_environment=env, optimize=optimize)
    elif (isinstance(raquery, radb.ast.Join) and isinstance(raquery.inputs[0], radb.ast.Select) and optimize):
        return JoinLeftSelectTask(querystring=str(raquery) + ";", step=step, exec_environment=env, optimize=optimize)
    #-----------Above are chain folding tasks----------#
    #-----------Below are default tasks----------#
    elif isinstance(raquery, radb.ast.Select):  # Only mapper exists
        return SelectTask(querystring=str(raquery) + ";", step=step, exec_environment=env, optimize=optimize)

    elif isinstance(raquery, radb.ast.RelRef):
        filename = raquery.rel + ".json"
        return InputData(filename=filename, exec_environment=env)

    elif isinstance(raquery, radb.ast.Join):
        return JoinTask(querystring=str(raquery) + ";", step=step, exec_environment=env, optimize=optimize)

    elif isinstance(raquery, radb.ast.Project):
        return ProjectTask(querystring=str(raquery) + ";", step=step, exec_environment=env, optimize=optimize)

    elif isinstance(raquery, radb.ast.Rename):  # Only mapper exists
        return RenameTask(querystring=str(raquery) + ";", step=step, exec_environment=env, optimize=optimize)

    else:
        # We will not evaluate the Cross product on Hadoop, too expensive.
        raise Exception("Operator " + str(type(raquery)) +
                        " not implemented (yet).")


class JoinTask(RelAlgQueryTask):

    def requires(self):
        raquery = radb.parse.one_statement_from_string(self.querystring)
        assert (isinstance(raquery, radb.ast.Join))

        task1 = task_factory(
            raquery.inputs[0], step=self.step + 1, env=self.exec_environment, optimize=self.optimize)
        task2 = task_factory(raquery.inputs[1], step=self.step + count_steps(raquery.inputs[0]) + 1,
                             env=self.exec_environment, optimize=self.optimize)

        return [task1, task2]

    def mapper(self, line):
        relation, tuple = line.split('\t')
        json_tuple = json.loads(tuple)

        raquery = radb.parse.one_statement_from_string(self.querystring)
        condition = raquery.cond

        ''' ...................... fill in your code below ........................'''

        listCondition = []
        # add itself to list if only 1 equal condition
        if (isinstance(condition, radb.ast.ValExprBinaryOp) and isinstance(condition.inputs[0], radb.ast.AttrRef)):
            listCondition.append(condition)
        else:
            # add whole list of >1 equal condition.
            for cond in condition.inputs:
                listCondition.append(cond)

        attr = ""
        listKey = []
        for cond in listCondition:
            # join keys only exist in one of the table, determine this row is in tableA or tableB
            if cond.inputs[0].rel == relation or cond.inputs[0].rel in relation:
                relation = cond.inputs[0].rel
                attr = cond.inputs[0].name
            elif cond.inputs[1].rel == relation or cond.inputs[1].rel in relation:
                relation = cond.inputs[1].rel
                attr = cond.inputs[1].name
            listKey.append(str(json_tuple[relation + "." + attr]))

        key = ','.join(listKey)
        yield (key, tuple)

        ''' ...................... fill in your code above ........................'''

    def reducer(self, key, values):
        raquery = radb.parse.one_statement_from_string(self.querystring)

        ''' ...................... fill in your code below ........................'''
        # the key already store 2 common key, so no need to find key here.
        condition = raquery.cond

        # take one of the key to be the identifier, it does not affect the corrcetness of the algo.
        if not (isinstance(condition, radb.ast.ValExprBinaryOp) and isinstance(condition.inputs[0], radb.ast.AttrRef)):
            condition = condition.inputs[1]

        list_of_values = list(values)
        if (len(list_of_values)) > 1:
            JoinClause1 = condition.inputs[0].rel + \
                "." + condition.inputs[0].name
            JoinClause2 = condition.inputs[1].rel + \
                "." + condition.inputs[1].name
            rowsFromTable1 = []
            rowsFromTable2 = []
            # divide lines into 2 list, by their origin table.
            for jsonVal in list_of_values:
                if (JoinClause1 in jsonVal):
                    rowsFromTable1.append(jsonVal)
                elif (JoinClause2 in jsonVal):
                    rowsFromTable2.append(jsonVal)
            # if matched rows = 0, do not process.
            if len(rowsFromTable1) > 0 and len(rowsFromTable2) > 0:
                for row2 in rowsFromTable2:
                    rowsMergedTable = {}
                    jsonRow = json.loads(row2)
                    # add all entries from json 2 to merged json
                    for rowkey in jsonRow:
                        rowsMergedTable[rowkey] = jsonRow[rowkey]
                    for row1 in rowsFromTable1:
                        jsonRow = json.loads(row1)
                        # add all entries from json 1 to merged json
                        for rowkey in jsonRow:
                            rowsMergedTable[rowkey] = jsonRow[rowkey]
                        jsonString_merged = json.dumps(rowsMergedTable)
                        yield (condition.inputs[0].rel + "_" + condition.inputs[1].rel, jsonString_merged)

        ''' ...................... fill in your code above ........................'''


class SelectTask(RelAlgQueryTask):

    def requires(self):
        raquery = radb.parse.one_statement_from_string(self.querystring)
        assert (isinstance(raquery, radb.ast.Select))

        return [task_factory(raquery.inputs[0], step=self.step + 1, env=self.exec_environment, optimize=self.optimize)]

    def mapper(self, line):
        relation, tuple = line.split('\t')
        json_tuple = json.loads(tuple)

        condition = radb.parse.one_statement_from_string(self.querystring).cond

        ''' ...................... fill in your code below ........................'''
        attr = ""
        value = ""

        # multiple select clause
        if isinstance(condition.inputs[0], radb.ast.ValExprBinaryOp):

            selectObj = condition.inputs
            selectList = []
            while (isinstance(selectObj[0], radb.ast.ValExprBinaryOp)):
                selectList.append(selectObj[1])
                selectObj = selectObj[0].inputs

            selectList.append(radb.ast.ValExprBinaryOp(
                selectObj[0], radb.parse.RAParser.EQ, selectObj[1]))
            allValid = True
            if selectList:
                while selectList:
                    condition = selectList.pop()
                    if isinstance(condition.inputs[0], radb.ast.AttrRef):
                        attr = condition.inputs[0].name
                        value = condition.inputs[1]
                    else:
                        attr = condition.inputs[1].name
                        value = condition.inputs[0]
                    if isinstance(value, radb.ast.RAString):
                        value = str(value).strip('\'')
                    else:
                        value = int(value.val)
                    if json_tuple[relation + "." + attr] != value:
                        allValid = False
                        break
                if allValid == True:
                    yield (relation, tuple)
        # only 1 select clause.
        else:
            if isinstance(condition.inputs[0], radb.ast.AttrRef):
                attr = condition.inputs[0].name
                value = condition.inputs[1]
            else:
                attr = condition.inputs[1].name
                value = condition.inputs[0]
            if isinstance(value, radb.ast.RAString):
                value = str(value).strip('\'')
            else:
                value = int(value.val)
            if json_tuple[relation + "." + attr] == value:
                yield (relation, tuple)

        ''' ...................... fill in your code above ........................'''


class RenameTask(RelAlgQueryTask):

    def requires(self):
        raquery = radb.parse.one_statement_from_string(self.querystring)
        assert (isinstance(raquery, radb.ast.Rename))

        return [task_factory(raquery.inputs[0], step=self.step + 1, env=self.exec_environment, optimize=self.optimize)]

    def mapper(self, line):
        relation, tuple = line.split('\t')
        json_tuple = json.loads(tuple)

        raquery = radb.parse.one_statement_from_string(self.querystring)

        ''' ...................... fill in your code below ........................'''
        newTableName = raquery.relname
        oldTableName = raquery.inputs[0].rel
        tuple = tuple.replace(oldTableName, newTableName)
        relation = relation.replace(oldTableName, newTableName)
        yield (relation, tuple)

        ''' ...................... fill in your code above ........................'''


class ProjectTask(RelAlgQueryTask):

    def requires(self):
        raquery = radb.parse.one_statement_from_string(self.querystring)
        assert (isinstance(raquery, radb.ast.Project))

        return [task_factory(raquery.inputs[0], step=self.step + 1, env=self.exec_environment, optimize=self.optimize)]

    def mapper(self, line):
        relation, tuple = line.split('\t')
        json_tuple = json.loads(tuple)

        attrs = radb.parse.one_statement_from_string(self.querystring).attrs

        ''' ...................... fill in your code below ........................'''
        output_json_tuple = {}
        for attr in attrs:
            attrname = attr.name
            if attr.rel != None:
                relation = attr.rel
            output_json_tuple[relation + "." +
                              attrname] = json_tuple[relation + "." + attrname]

        output_json_data = json.dumps(output_json_tuple)
        yield (relation, output_json_data)

        ''' ...................... fill in your code above ........................'''

    def reducer(self, key, values):
        ''' ...................... fill in your code below ........................'''
        set_of_values = set(values)
        sorted_list = sorted(set_of_values)
        for element in sorted_list:
            yield (key, element)

        ''' ...................... fill in your code above ........................'''


class ProjectSelectTask(RelAlgQueryTask):
    def requires(self):
        raquery = radb.parse.one_statement_from_string(self.querystring)
        assert (isinstance(raquery, radb.ast.Project))
        assert (isinstance(raquery.inputs[0], radb.ast.Select))

        return [task_factory(raquery.inputs[0].inputs[0], step=self.step + 2, env=self.exec_environment, optimize=self.optimize)]

    def mapper(self, line):
        '''-----------------------------Select Task Start-----------------------------'''
        relation, tuple = line.split('\t')
        json_tuple = json.loads(tuple)

        condition = radb.parse.one_statement_from_string(
            self.querystring).inputs[0].cond
        resultList = []
        ''' ...................... fill in your code below ........................'''
        attr = ""
        value = ""

        # multiple select clause
        if isinstance(condition.inputs[0], radb.ast.ValExprBinaryOp):

            selectObj = condition.inputs
            selectList = []
            while (isinstance(selectObj[0], radb.ast.ValExprBinaryOp)):
                selectList.append(selectObj[1])
                selectObj = selectObj[0].inputs

            selectList.append(radb.ast.ValExprBinaryOp(
                selectObj[0], radb.parse.RAParser.EQ, selectObj[1]))
            allValid = True
            if selectList:
                while selectList:
                    condition = selectList.pop()
                    if isinstance(condition.inputs[0], radb.ast.AttrRef):
                        attr = condition.inputs[0].name
                        value = condition.inputs[1]
                    else:
                        attr = condition.inputs[1].name
                        value = condition.inputs[0]
                    if isinstance(value, radb.ast.RAString):
                        value = str(value).strip('\'')
                    else:
                        value = int(value.val)
                    if json_tuple[relation + "." + attr] != value:
                        allValid = False
                        break
                if allValid == True:
                    # yield (relation, tuple)
                    resultList.append((relation, tuple))
        # only 1 select clause.
        else:
            if isinstance(condition.inputs[0], radb.ast.AttrRef):
                attr = condition.inputs[0].name
                value = condition.inputs[1]
            else:
                attr = condition.inputs[1].name
                value = condition.inputs[0]
            if isinstance(value, radb.ast.RAString):
                value = str(value).strip('\'')
            else:
                value = int(value.val)
            if json_tuple[relation + "." + attr] == value:
                # yield (relation, tuple)
                resultList.append((relation, tuple))

        ''' ...................... fill in your code above ........................'''
        '''-----------------------------Select Task End-----------------------------'''
        '''-----------------------------Project Task Start-------------------------------'''
        for result in resultList:
            #relation, tuple = line.split('\t')
            relation, tuple = result
            json_tuple = json.loads(tuple)

            attrs = radb.parse.one_statement_from_string(
                self.querystring).attrs

            ''' ...................... fill in your code below ........................'''
            output_json_tuple = {}
            for attr in attrs:
                attrname = attr.name
                if attr.rel != None:
                    relation = attr.rel
                output_json_tuple[relation + "." +
                                  attrname] = json_tuple[relation + "." + attrname]

            output_json_data = json.dumps(output_json_tuple)
            yield (relation, output_json_data)

        ''' ...................... fill in your code above ........................'''
        '''-----------------------------Project Task End-------------------------------'''

    def reducer(self, key, values):
        ''' ...................... fill in your code below ........................'''
        set_of_values = set(values)
        sorted_list = sorted(set_of_values)
        for element in sorted_list:
            yield (key, element)

        ''' ...................... fill in your code above ........................'''


class ProjectSelectRenameTask(RelAlgQueryTask):
    def requires(self):
        raquery = radb.parse.one_statement_from_string(self.querystring)
        assert (isinstance(raquery, radb.ast.Project))
        assert (isinstance(raquery.inputs[0], radb.ast.Select))
        assert (isinstance(raquery.inputs[0].inputs[0], radb.ast.Rename))
        return [task_factory(raquery.inputs[0].inputs[0].inputs[0], step=self.step + 3, env=self.exec_environment, optimize=self.optimize)]

    def mapper(self, line):
        '''-----------------------------Rename Task Start-----------------------------'''
        relation, tuple = line.split('\t')
        json_tuple = json.loads(tuple)

        raquery = radb.parse.one_statement_from_string(
            self.querystring).inputs[0].inputs[0]

        ''' ...................... fill in your code below ........................'''
        newTableName = raquery.relname
        oldTableName = raquery.inputs[0].rel
        tuple = tuple.replace(oldTableName, newTableName)
        relation = relation.replace(oldTableName, newTableName)
        # yield (relation, tuple)
        resulttuple = (relation, tuple)
        '''-----------------------------Rename Task End-------------------------------'''
        '''-----------------------------Select Task Start-----------------------------'''
        relation, tuple = resulttuple
        json_tuple = json.loads(tuple)

        condition = radb.parse.one_statement_from_string(
            self.querystring).inputs[0].cond
        resultList = []
        ''' ...................... fill in your code below ........................'''
        attr = ""
        value = ""

        # multiple select clause
        if isinstance(condition.inputs[0], radb.ast.ValExprBinaryOp):

            selectObj = condition.inputs
            selectList = []
            while (isinstance(selectObj[0], radb.ast.ValExprBinaryOp)):
                selectList.append(selectObj[1])
                selectObj = selectObj[0].inputs

            selectList.append(radb.ast.ValExprBinaryOp(
                selectObj[0], radb.parse.RAParser.EQ, selectObj[1]))
            allValid = True
            if selectList:
                while selectList:
                    condition = selectList.pop()
                    if isinstance(condition.inputs[0], radb.ast.AttrRef):
                        attr = condition.inputs[0].name
                        value = condition.inputs[1]
                    else:
                        attr = condition.inputs[1].name
                        value = condition.inputs[0]
                    if isinstance(value, radb.ast.RAString):
                        value = str(value).strip('\'')
                    else:
                        value = int(value.val)
                    if json_tuple[relation + "." + attr] != value:
                        allValid = False
                        break
                if allValid == True:
                    # yield (relation, tuple)
                    resultList.append((relation, tuple))
        # only 1 select clause.
        else:
            if isinstance(condition.inputs[0], radb.ast.AttrRef):
                attr = condition.inputs[0].name
                value = condition.inputs[1]
            else:
                attr = condition.inputs[1].name
                value = condition.inputs[0]
            if isinstance(value, radb.ast.RAString):
                value = str(value).strip('\'')
            else:
                value = int(value.val)
            if json_tuple[relation + "." + attr] == value:
                # yield (relation, tuple)
                resultList.append((relation, tuple))

        ''' ...................... fill in your code above ........................'''
        '''-----------------------------Select Task End-----------------------------'''
        '''-----------------------------Project Task Start-------------------------------'''
        for result in resultList:
            #relation, tuple = line.split('\t')
            relation, tuple = result
            json_tuple = json.loads(tuple)

            attrs = radb.parse.one_statement_from_string(
                self.querystring).attrs

            ''' ...................... fill in your code below ........................'''
            output_json_tuple = {}
            for attr in attrs:
                attrname = attr.name
                if attr.rel != None:
                    relation = attr.rel
                output_json_tuple[relation + "." +
                                  attrname] = json_tuple[relation + "." + attrname]

            output_json_data = json.dumps(output_json_tuple)
            yield (relation, output_json_data)

        ''' ...................... fill in your code above ........................'''
        '''-----------------------------Project Task End-------------------------------'''

    def reducer(self, key, values):
        ''' ...................... fill in your code below ........................'''
        set_of_values = set(values)
        sorted_list = sorted(set_of_values)
        for element in sorted_list:
            yield (key, element)

        ''' ...................... fill in your code above ........................'''


class JoinRightSelectTask(RelAlgQueryTask):
    def requires(self):
        raquery = radb.parse.one_statement_from_string(self.querystring)
        assert (isinstance(raquery, radb.ast.Join))
        assert (isinstance(raquery.inputs[1], radb.ast.Select))
        task1 = task_factory(
            raquery.inputs[0], step=self.step + 1, env=self.exec_environment, optimize=self.optimize)
        task2 = task_factory(raquery.inputs[1].inputs[0], step=self.step + count_steps(raquery.inputs[0]) + 1,
                             env=self.exec_environment, optimize=self.optimize)

        return [task1, task2]

    def mapper(self, line):
        '''-----------------------------Select Task Start-------------------------------'''
        relation, tuple = line.split('\t')
        json_tuple = json.loads(tuple)

        condition = radb.parse.one_statement_from_string(
            self.querystring).inputs[1].cond
        resultList = []
        # left table name: radb.parse.one_statement_from_string(self.querystring).cond.inputs[0].rel
        rightTblName = radb.parse.one_statement_from_string(
            self.querystring).cond.inputs[1].rel
        ''' ...................... fill in your code below ........................'''
        attr = ""
        value = ""
        # multiple select clause
        if (relation == rightTblName):
            if isinstance(condition.inputs[0], radb.ast.ValExprBinaryOp):

                selectObj = condition.inputs
                selectList = []
                while (isinstance(selectObj[0], radb.ast.ValExprBinaryOp)):
                    selectList.append(selectObj[1])
                    selectObj = selectObj[0].inputs

                selectList.append(radb.ast.ValExprBinaryOp(
                    selectObj[0], radb.parse.RAParser.EQ, selectObj[1]))
                allValid = True
                if selectList:
                    while selectList:
                        condition = selectList.pop()
                        if isinstance(condition.inputs[0], radb.ast.AttrRef):
                            attr = condition.inputs[0].name
                            value = condition.inputs[1]
                        else:
                            attr = condition.inputs[1].name
                            value = condition.inputs[0]
                        if isinstance(value, radb.ast.RAString):
                            value = str(value).strip('\'')
                        else:
                            value = int(value.val)
                        if json_tuple[relation + "." + attr] != value:
                            allValid = False
                            break
                    if allValid == True:
                        # yield (relation, tuple)
                        resultList.append((relation, tuple))
        # only 1 select clause.
            else:
                if isinstance(condition.inputs[0], radb.ast.AttrRef):
                    attr = condition.inputs[0].name
                    value = condition.inputs[1]
                else:
                    attr = condition.inputs[1].name
                    value = condition.inputs[0]
                if isinstance(value, radb.ast.RAString):
                    value = str(value).strip('\'')
                else:
                    value = int(value.val)
                if json_tuple[relation + "." + attr] == value:
                    # yield (relation, tuple)
                    resultList.append((relation, tuple))
        else:
            resultList.append((relation, tuple))

        ''' ...................... fill in your code above ........................'''

        '''-----------------------------Select Task End-------------------------------'''
        '''-----------------------------Join Task Start-------------------------------'''
        for result in resultList:
            relation, tuple = result
            json_tuple = json.loads(tuple)

            raquery = radb.parse.one_statement_from_string(self.querystring)
            condition = raquery.cond

            ''' ...................... fill in your code below ........................'''

            listCondition = []
            # add itself to list if only 1 equal condition
            if (isinstance(condition, radb.ast.ValExprBinaryOp) and isinstance(condition.inputs[0], radb.ast.AttrRef)):
                listCondition.append(condition)
            else:
                # add whole list of >1 equal condition.
                for cond in condition.inputs:
                    listCondition.append(cond)

            attr = ""
            listKey = []
            for cond in listCondition:
                # join keys only exist in one of the table, determine this row is in tableA or tableB
                if cond.inputs[0].rel == relation or cond.inputs[0].rel in relation:
                    relation = cond.inputs[0].rel
                    attr = cond.inputs[0].name
                elif cond.inputs[1].rel == relation or cond.inputs[1].rel in relation:
                    relation = cond.inputs[1].rel
                    attr = cond.inputs[1].name
                listKey.append(str(json_tuple[relation + "." + attr]))

            key = ','.join(listKey)
            yield (key, tuple)

        ''' ...................... fill in your code above ........................'''
        '''-----------------------------Join Task End-------------------------------'''

    def reducer(self, key, values):
        raquery = radb.parse.one_statement_from_string(self.querystring)

        ''' ...................... fill in your code below ........................'''
        # the key already store 2 common key, so no need to find key here.
        condition = raquery.cond

        # take one of the key to be the identifier, it does not affect the corrcetness of the algo.
        if not (isinstance(condition, radb.ast.ValExprBinaryOp) and isinstance(condition.inputs[0], radb.ast.AttrRef)):
            condition = condition.inputs[1]

        list_of_values = list(values)
        if (len(list_of_values)) > 1:
            JoinClause1 = condition.inputs[0].rel + \
                "." + condition.inputs[0].name
            JoinClause2 = condition.inputs[1].rel + \
                "." + condition.inputs[1].name
            rowsFromTable1 = []
            rowsFromTable2 = []
            # divide lines into 2 list, by their origin table.
            for jsonVal in list_of_values:
                if (JoinClause1 in jsonVal):
                    rowsFromTable1.append(jsonVal)
                elif (JoinClause2 in jsonVal):
                    rowsFromTable2.append(jsonVal)
            # if matched rows = 0, do not process.
            if len(rowsFromTable1) > 0 and len(rowsFromTable2) > 0:
                for row2 in rowsFromTable2:
                    rowsMergedTable = {}
                    jsonRow = json.loads(row2)
                    # add all entries from json 2 to merged json
                    for rowkey in jsonRow:
                        rowsMergedTable[rowkey] = jsonRow[rowkey]
                    for row1 in rowsFromTable1:
                        jsonRow = json.loads(row1)
                        # add all entries from json 1 to merged json
                        for rowkey in jsonRow:
                            rowsMergedTable[rowkey] = jsonRow[rowkey]
                        jsonString_merged = json.dumps(rowsMergedTable)
                        yield (condition.inputs[0].rel + "_" + condition.inputs[1].rel, jsonString_merged)

        ''' ...................... fill in your code above ........................'''


class JoinLeftSelectTask(RelAlgQueryTask):
    def requires(self):
        raquery = radb.parse.one_statement_from_string(self.querystring)
        assert (isinstance(raquery, radb.ast.Join))
        assert (isinstance(raquery.inputs[0], radb.ast.Select))
        task1 = task_factory(
            raquery.inputs[0].inputs[0], step=self.step + 1, env=self.exec_environment, optimize=self.optimize)
        task2 = task_factory(raquery.inputs[1], step=self.step + count_steps(raquery.inputs[0]) + 1,
                             env=self.exec_environment, optimize=self.optimize)

        return [task1, task2]

    def mapper(self, line):
        '''-----------------------------Select Task Start-------------------------------'''
        relation, tuple = line.split('\t')
        json_tuple = json.loads(tuple)

        condition = radb.parse.one_statement_from_string(
            self.querystring).inputs[0].cond
        resultList = []

        # do not make an assumption than "order \join{ order.key = customer.key} customer".
        # It might be the opposite! order \join{  customer.key = order.key} customer
        leftTblName = radb.parse.one_statement_from_string(
            self.querystring).cond.inputs[0].rel
        # rightTblName = radb.parse.one_statement_from_string(
        #    self.querystring).cond.inputs[1].rel
        ''' ...................... fill in your code below ........................'''
        attr = ""
        value = ""
        # multiple select clause
        if (relation == leftTblName):
            if isinstance(condition.inputs[0], radb.ast.ValExprBinaryOp):

                selectObj = condition.inputs
                selectList = []
                while (isinstance(selectObj[0], radb.ast.ValExprBinaryOp)):
                    selectList.append(selectObj[1])
                    selectObj = selectObj[0].inputs

                selectList.append(radb.ast.ValExprBinaryOp(
                    selectObj[0], radb.parse.RAParser.EQ, selectObj[1]))
                allValid = True
                if selectList:
                    while selectList:
                        condition = selectList.pop()
                        if isinstance(condition.inputs[0], radb.ast.AttrRef):
                            attr = condition.inputs[0].name
                            value = condition.inputs[1]
                        else:
                            attr = condition.inputs[1].name
                            value = condition.inputs[0]
                        if isinstance(value, radb.ast.RAString):
                            value = str(value).strip('\'')
                        else:
                            value = int(value.val)
                        if json_tuple[relation + "." + attr] != value:
                            allValid = False
                            break
                    if allValid == True:
                        # yield (relation, tuple)
                        resultList.append((relation, tuple))
        # only 1 select clause.
            else:
                if isinstance(condition.inputs[0], radb.ast.AttrRef):
                    attr = condition.inputs[0].name
                    value = condition.inputs[1]
                else:
                    attr = condition.inputs[1].name
                    value = condition.inputs[0]
                if isinstance(value, radb.ast.RAString):
                    value = str(value).strip('\'')
                else:
                    value = int(value.val)
                if json_tuple[relation + "." + attr] == value:
                    # yield (relation, tuple)
                    resultList.append((relation, tuple))
        else:
            resultList.append((relation, tuple))

        ''' ...................... fill in your code above ........................'''

        '''-----------------------------Select Task End-------------------------------'''
        '''-----------------------------Join Task Start-------------------------------'''
        for result in resultList:
            relation, tuple = result
            json_tuple = json.loads(tuple)

            raquery = radb.parse.one_statement_from_string(self.querystring)
            condition = raquery.cond

            ''' ...................... fill in your code below ........................'''

            listCondition = []
            # add itself to list if only 1 equal condition
            if (isinstance(condition, radb.ast.ValExprBinaryOp) and isinstance(condition.inputs[0], radb.ast.AttrRef)):
                listCondition.append(condition)
            else:
                # add whole list of >1 equal condition.
                for cond in condition.inputs:
                    listCondition.append(cond)

            attr = ""
            listKey = []
            for cond in listCondition:
                # join keys only exist in one of the table, determine this row is in tableA or tableB
                if cond.inputs[0].rel == relation or cond.inputs[0].rel in relation:
                    relation = cond.inputs[0].rel
                    attr = cond.inputs[0].name
                elif cond.inputs[1].rel == relation or cond.inputs[1].rel in relation:
                    relation = cond.inputs[1].rel
                    attr = cond.inputs[1].name
                listKey.append(str(json_tuple[relation + "." + attr]))

            key = ','.join(listKey)
            yield (key, tuple)

        ''' ...................... fill in your code above ........................'''
        '''-----------------------------Join Task End-------------------------------'''

    def reducer(self, key, values):
        raquery = radb.parse.one_statement_from_string(self.querystring)

        ''' ...................... fill in your code below ........................'''
        # the key already store 2 common key, so no need to find key here.
        condition = raquery.cond

        # take one of the key to be the identifier, it does not affect the corrcetness of the algo.
        if not (isinstance(condition, radb.ast.ValExprBinaryOp) and isinstance(condition.inputs[0], radb.ast.AttrRef)):
            condition = condition.inputs[1]

        list_of_values = list(values)
        if (len(list_of_values)) > 1:
            JoinClause1 = condition.inputs[0].rel + \
                "." + condition.inputs[0].name
            JoinClause2 = condition.inputs[1].rel + \
                "." + condition.inputs[1].name
            rowsFromTable1 = []
            rowsFromTable2 = []
            # divide lines into 2 list, by their origin table.
            for jsonVal in list_of_values:
                if (JoinClause1 in jsonVal):
                    rowsFromTable1.append(jsonVal)
                elif (JoinClause2 in jsonVal):
                    rowsFromTable2.append(jsonVal)
            # if matched rows = 0, do not process.
            if len(rowsFromTable1) > 0 and len(rowsFromTable2) > 0:
                for row2 in rowsFromTable2:
                    rowsMergedTable = {}
                    jsonRow = json.loads(row2)
                    # add all entries from json 2 to merged json
                    for rowkey in jsonRow:
                        rowsMergedTable[rowkey] = jsonRow[rowkey]
                    for row1 in rowsFromTable1:
                        jsonRow = json.loads(row1)
                        # add all entries from json 1 to merged json
                        for rowkey in jsonRow:
                            rowsMergedTable[rowkey] = jsonRow[rowkey]
                        jsonString_merged = json.dumps(rowsMergedTable)
                        yield (condition.inputs[0].rel + "_" + condition.inputs[1].rel, jsonString_merged)

        ''' ...................... fill in your code above ........................'''


class JoinBothSelectTask(RelAlgQueryTask):
    def requires(self):
        raquery = radb.parse.one_statement_from_string(self.querystring)
        assert (isinstance(raquery, radb.ast.Join))
        assert (isinstance(raquery.inputs[1], radb.ast.Select))
        assert (isinstance(raquery.inputs[0], radb.ast.Select))
        task1 = task_factory(
            raquery.inputs[0].inputs[0], step=self.step + 1, env=self.exec_environment, optimize=self.optimize)
        task2 = task_factory(raquery.inputs[1].inputs[0], step=self.step + count_steps(raquery.inputs[0]) + 1,
                             env=self.exec_environment, optimize=self.optimize)

        return [task1, task2]

    def mapper(self, line):
        '''-----------------------------Select Task Start-------------------------------'''
        relation, tuple = line.split('\t')
        json_tuple = json.loads(tuple)

        condition = radb.parse.one_statement_from_string(
            self.querystring).inputs[1].cond
        resultList = []
        leftTblName = radb.parse.one_statement_from_string(
            self.querystring).cond.inputs[0].rel
        rightTblName = radb.parse.one_statement_from_string(
            self.querystring).cond.inputs[1].rel
        ''' ...................... fill in your code below ........................'''
        attr = ""
        value = ""
        # multiple select clause
        if (relation == rightTblName):
            if isinstance(condition.inputs[0], radb.ast.ValExprBinaryOp):

                selectObj = condition.inputs
                selectList = []
                while (isinstance(selectObj[0], radb.ast.ValExprBinaryOp)):
                    selectList.append(selectObj[1])
                    selectObj = selectObj[0].inputs

                selectList.append(radb.ast.ValExprBinaryOp(
                    selectObj[0], radb.parse.RAParser.EQ, selectObj[1]))
                allValid = True
                if selectList:
                    while selectList:
                        condition = selectList.pop()
                        if isinstance(condition.inputs[0], radb.ast.AttrRef):
                            attr = condition.inputs[0].name
                            value = condition.inputs[1]
                        else:
                            attr = condition.inputs[1].name
                            value = condition.inputs[0]
                        if isinstance(value, radb.ast.RAString):
                            value = str(value).strip('\'')
                        else:
                            value = int(value.val)
                        if json_tuple[relation + "." + attr] != value:
                            allValid = False
                            break
                    if allValid == True:
                        # yield (relation, tuple)
                        resultList.append((relation, tuple))
        # only 1 select clause.
            else:
                if isinstance(condition.inputs[0], radb.ast.AttrRef):
                    attr = condition.inputs[0].name
                    value = condition.inputs[1]
                else:
                    attr = condition.inputs[1].name
                    value = condition.inputs[0]
                if isinstance(value, radb.ast.RAString):
                    value = str(value).strip('\'')
                else:
                    value = int(value.val)
                if json_tuple[relation + "." + attr] == value:
                    # yield (relation, tuple)
                    resultList.append((relation, tuple))
        elif (relation == leftTblName):
            if isinstance(condition.inputs[0], radb.ast.ValExprBinaryOp):
                selectObj = condition.inputs
                selectList = []
                while (isinstance(selectObj[0], radb.ast.ValExprBinaryOp)):
                    selectList.append(selectObj[1])
                    selectObj = selectObj[0].inputs

                selectList.append(radb.ast.ValExprBinaryOp(
                    selectObj[0], radb.parse.RAParser.EQ, selectObj[1]))
                allValid = True
                if selectList:
                    while selectList:
                        condition = selectList.pop()
                        if isinstance(condition.inputs[0], radb.ast.AttrRef):
                            attr = condition.inputs[0].name
                            value = condition.inputs[1]
                        else:
                            attr = condition.inputs[1].name
                            value = condition.inputs[0]
                        if isinstance(value, radb.ast.RAString):
                            value = str(value).strip('\'')
                        else:
                            value = int(value.val)
                        if json_tuple[relation + "." + attr] != value:
                            allValid = False
                            break
                    if allValid == True:
                        # yield (relation, tuple)
                        resultList.append((relation, tuple))
        # only 1 select clause.
            else:
                if isinstance(condition.inputs[0], radb.ast.AttrRef):
                    attr = condition.inputs[0].name
                    value = condition.inputs[1]
                else:
                    attr = condition.inputs[1].name
                    value = condition.inputs[0]
                if isinstance(value, radb.ast.RAString):
                    value = str(value).strip('\'')
                else:
                    value = int(value.val)
                if json_tuple[relation + "." + attr] == value:
                    # yield (relation, tuple)
                    resultList.append((relation, tuple))

        ''' ...................... fill in your code above ........................'''

        '''-----------------------------Select Task End-------------------------------'''
        '''-----------------------------Join Task Start-------------------------------'''
        for result in resultList:
            relation, tuple = result
            json_tuple = json.loads(tuple)

            raquery = radb.parse.one_statement_from_string(self.querystring)
            condition = raquery.cond

            ''' ...................... fill in your code below ........................'''

            listCondition = []
            # add itself to list if only 1 equal condition
            if (isinstance(condition, radb.ast.ValExprBinaryOp) and isinstance(condition.inputs[0], radb.ast.AttrRef)):
                listCondition.append(condition)
            else:
                # add whole list of >1 equal condition.
                for cond in condition.inputs:
                    listCondition.append(cond)

            attr = ""
            listKey = []
            for cond in listCondition:
                # join keys only exist in one of the table, determine this row is in tableA or tableB
                if cond.inputs[0].rel == relation or cond.inputs[0].rel in relation:
                    relation = cond.inputs[0].rel
                    attr = cond.inputs[0].name
                elif cond.inputs[1].rel == relation or cond.inputs[1].rel in relation:
                    relation = cond.inputs[1].rel
                    attr = cond.inputs[1].name
                listKey.append(str(json_tuple[relation + "." + attr]))

            key = ','.join(listKey)
            yield (key, tuple)

        ''' ...................... fill in your code above ........................'''
        '''-----------------------------Join Task End-------------------------------'''

    def reducer(self, key, values):
        raquery = radb.parse.one_statement_from_string(self.querystring)

        ''' ...................... fill in your code below ........................'''
        # the key already store 2 common key, so no need to find key here.
        condition = raquery.cond

        # take one of the key to be the identifier, it does not affect the corrcetness of the algo.
        if not (isinstance(condition, radb.ast.ValExprBinaryOp) and isinstance(condition.inputs[0], radb.ast.AttrRef)):
            condition = condition.inputs[1]

        list_of_values = list(values)
        if (len(list_of_values)) > 1:
            JoinClause1 = condition.inputs[0].rel + \
                "." + condition.inputs[0].name
            JoinClause2 = condition.inputs[1].rel + \
                "." + condition.inputs[1].name
            rowsFromTable1 = []
            rowsFromTable2 = []
            # divide lines into 2 list, by their origin table.
            for jsonVal in list_of_values:
                if (JoinClause1 in jsonVal):
                    rowsFromTable1.append(jsonVal)
                elif (JoinClause2 in jsonVal):
                    rowsFromTable2.append(jsonVal)
            # if matched rows = 0, do not process.
            if len(rowsFromTable1) > 0 and len(rowsFromTable2) > 0:
                for row2 in rowsFromTable2:
                    rowsMergedTable = {}
                    jsonRow = json.loads(row2)
                    # add all entries from json 2 to merged json
                    for rowkey in jsonRow:
                        rowsMergedTable[rowkey] = jsonRow[rowkey]
                    for row1 in rowsFromTable1:
                        jsonRow = json.loads(row1)
                        # add all entries from json 1 to merged json
                        for rowkey in jsonRow:
                            rowsMergedTable[rowkey] = jsonRow[rowkey]
                        jsonString_merged = json.dumps(rowsMergedTable)
                        yield (condition.inputs[0].rel + "_" + condition.inputs[1].rel, jsonString_merged)

        ''' ...................... fill in your code above ........................'''


if __name__ == '__main__':
    luigi.run()
