from typing import List
import radb.ast
from radb.ast import AttrRef, RelExpr
import radb.parse
import radb
from radb.parse import RAParser as sym


def rule_break_up_selections(ra):
    if isinstance(ra, radb.ast.Select) and isinstance(ra.cond.inputs[0], radb.ast.ValExprBinaryOp):
        # base case
        selectObjList = ra.cond.inputs
        tableObj = ra.inputs[0]
        result = None
        selectList = []
        # TO-DO reversed order need edit.
        # for selectObj in reversed(selectObjList):
        while (isinstance(selectObjList[0].inputs[0], radb.ast.ValExprBinaryOp)):
            selectList.append(selectObjList[1])
            selectObjList = selectObjList[0].inputs

        # if length of selectList >0
        if selectList:
            while selectList:
                if result is None:
                    result = radb.ast.Select(selectList.pop(), tableObj)
                else:
                    result = radb.ast.Select(selectList.pop(), result)

            result = radb.ast.Select(selectObjList[1], result)
        else:
            result = radb.ast.Select(selectObjList[1], tableObj)

        result = radb.ast.Select(selectObjList[0], result)

        return result
    elif isinstance(ra, radb.ast.Select):
        return ra
    elif isinstance(ra, radb.ast.Project):
        attrList = ra.attrs
        selectObj = rule_break_up_selections(ra.inputs[0])
        result = radb.ast.Project(attrList, selectObj)
        return result
    elif isinstance(ra, radb.ast.Cross):
        firstCrossObj = ra.inputs[0]
        secondCrossObj = ra.inputs[1]
        result = radb.ast.Cross(rule_break_up_selections(
            firstCrossObj), rule_break_up_selections(secondCrossObj))
        return result
    elif isinstance(ra, radb.ast.RelRef):
        return ra
    elif isinstance(ra, radb.ast.Rename):
        return ra


def find_all_table_Object(ra):
    result = []
    if isinstance(ra, radb.ast.Select):
        result = find_all_table_Object(ra.inputs[0])
    elif isinstance(ra, radb.ast.Project):
        result = find_all_table_Object(ra.inputs[0])
    elif isinstance(ra, radb.ast.Cross):
        result = find_all_table_Object(
            ra.inputs[0]) + find_all_table_Object(ra.inputs[1])
    elif isinstance(ra, radb.ast.RelRef):
        result.append(ra.rel)
    elif isinstance(ra, radb.ast.Rename):
        result = [ra.relname]
    return result


def rule_push_down_selections(ra1, dd, selectClauses=None):
    # if isinstance(ra1, radb.ast.Select) and isinstance(ra1.inputs[0], radb.ast.RelRef):
    #    return rule_push_down_selections()
    if isinstance(ra1, radb.ast.Select):
        subSelect = ra1.inputs[0]
        result = None
        BinaryOp = ra1.cond
        # check if cond are equal kind
        if selectClauses is None:
            selectClauses = [ra1.cond]
        else:
            selectClauses.append(ra1.cond)
        # past variables down
        result = rule_push_down_selections(
            ra1.inputs[0], dd, selectClauses)

        return result

    elif isinstance(ra1, radb.ast.Project):
        attrList = ra1.attrs
        selectObj = rule_push_down_selections(ra1.inputs[0], dd, selectClauses)
        result = radb.ast.Project(attrList, selectObj)
        return result

    elif isinstance(ra1, radb.ast.Cross):
        firstCrossObj = ra1.inputs[0]
        secondCrossObj = ra1.inputs[1]
        # check if both sides are RelExpr

        result = radb.ast.Cross(rule_push_down_selections(
            firstCrossObj, dd, selectClauses), rule_push_down_selections(secondCrossObj, dd, selectClauses))
        # find inherited table list
        firstCrossTableList = find_all_table_Object(firstCrossObj)
        secondCrossTableList = find_all_table_Object(secondCrossObj)
        if selectClauses is not None:
            for selectClause in reversed(selectClauses):
                # if select clause rel is Empty (no table specified)
                if (isinstance(selectClause.inputs[0], radb.ast.AttrRef) and isinstance(selectClause.inputs[1], radb.ast.AttrRef)):
                    # if both table name in select clause appear in sub-list
                    if ((selectClause.inputs[0].rel in firstCrossTableList and selectClause.inputs[1].rel in secondCrossTableList)):
                        result = radb.ast.Select(selectClause, result)
                    elif (selectClause.inputs[1].rel in firstCrossTableList and selectClause.inputs[0].rel in secondCrossTableList):
                        result = radb.ast.Select(selectClause, result)
        return result
    elif isinstance(ra1, radb.ast.RelRef):
        # insert select clause to table.
        result = ra1
        tableName = ra1.rel
        if tableName not in dd.keys():
            return result

        schemaTableContent = dd[tableName]
        for key in schemaTableContent:
            # loop over each clause of listofClauses
            if selectClauses is not None:
                for selectClause in reversed(selectClauses):
                    if isinstance(selectClause.inputs[1], radb.ast.Literal):
                        if (selectClause.inputs[0].rel is None and selectClause.inputs[0].name == key) or (selectClause.inputs[0].rel == tableName and selectClause.inputs[0].name == key):
                            result = radb.ast.Select(selectClause, result)
                    elif isinstance(selectClause.inputs[0], radb.ast.Literal):
                        if (selectClause.inputs[1].rel is None and selectClause.inputs[1].name == key) or (selectClause.inputs[1].rel == tableName and selectClause.inputs[1].name == key):
                            result = radb.ast.Select(selectClause, result)
        return result
    # stop at rename level, as it always comes before table.
    elif isinstance(ra1, radb.ast.Rename):
        result = ra1
        originTableName = ra1.inputs[0].rel
        renameTableName = ra1.relname
        if originTableName not in dd.keys():
            return result
        schemaTableContent = dd[originTableName]
        for key in schemaTableContent:
            # loop over each clause of listofClauses
            if selectClauses is not None:
                for selectClause in reversed(selectClauses):
                    if isinstance(selectClause.inputs[1], radb.ast.Literal):
                        if (selectClause.inputs[0].rel is None and selectClause.inputs[0].name == key) or (selectClause.inputs[0].rel == renameTableName and selectClause.inputs[0].name == key):
                            result = radb.ast.Select(selectClause, result)
                    elif isinstance(selectClause.inputs[0], radb.ast.Literal):
                        if (selectClause.inputs[1].rel is None and selectClause.inputs[1].name == key) or (selectClause.inputs[1].rel == renameTableName and selectClause.inputs[1].name == key):
                            result = radb.ast.Select(selectClause, result)
        return result


def rule_merge_selections(ra2):
    if isinstance(ra2, radb.ast.Select) and isinstance(ra2.inputs[0], radb.ast.Select):
        subSelect = ra2.inputs[0]
        result = None
        BinaryOp = ra2.cond
        # Always true for 1st loop.
        while (isinstance(subSelect, radb.ast.Select)):
            BinaryOp = radb.ast.ValExprBinaryOp(
                BinaryOp, sym.AND, subSelect.cond)
            # result = radb.ast.Select(BinaryOp, ra2.inputs[0].inputs[0])
            subSelect = subSelect.inputs[0]
        result = subSelect
        result = radb.ast.Select(BinaryOp, result)
        return result
    elif isinstance(ra2, radb.ast.Select):
        return ra2
    elif isinstance(ra2, radb.ast.Project):
        attrList = ra2.attrs
        selectObj = rule_merge_selections(ra2.inputs[0])
        result = radb.ast.Project(attrList, selectObj)
        return result
    elif isinstance(ra2, radb.ast.Cross):
        firstCrossObj = ra2.inputs[0]
        secondCrossObj = ra2.inputs[1]
        result = radb.ast.Cross(rule_merge_selections(
            firstCrossObj), rule_merge_selections(secondCrossObj))
        return result
    elif isinstance(ra2, radb.ast.RelRef):
        return ra2
    elif isinstance(ra2, radb.ast.Rename):
        return ra2


def rule_introduce_joins(ra3):
    if isinstance(ra3, radb.ast.Select) and isinstance(ra3.inputs[0], radb.ast.Cross):
        BinaryOp = ra3.cond
        result = None
        if isinstance(ra3.inputs[0].inputs[0], radb.ast.Select):
            leftTable = rule_introduce_joins(ra3.inputs[0].inputs[0])
            rightTable = ra3.inputs[0].inputs[1]
            result = radb.ast.Join(leftTable, BinaryOp, rightTable)
        else:
            leftTable = ra3.inputs[0].inputs[0]
            rightTable = ra3.inputs[0].inputs[1]
            # dont check whether select cause are join clause, assume they have been pushed down by step 2.
            result = radb.ast.Join(leftTable, BinaryOp, rightTable)
        return result
    elif isinstance(ra3, radb.ast.Select):
        return ra3
    elif isinstance(ra3, radb.ast.Project):
        attrList = ra3.attrs
        selectObj = rule_introduce_joins(ra3.inputs[0])
        result = radb.ast.Project(attrList, selectObj)
        return result
    elif isinstance(ra3, radb.ast.Cross):
        firstCrossObj = ra3.inputs[0]
        secondCrossObj = ra3.inputs[1]
        result = radb.ast.Cross(rule_introduce_joins(
            firstCrossObj), rule_introduce_joins(secondCrossObj))
        return result
    elif isinstance(ra3, radb.ast.RelRef):
        return ra3
    elif isinstance(ra3, radb.ast.Rename):
        return ra3
