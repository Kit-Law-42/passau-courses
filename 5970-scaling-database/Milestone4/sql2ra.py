import radb.ast
from radb.ast import RANumber, RelExpr
import radb.parse
import radb
from radb.parse import RAParser as sym
import sqlparse


def translate(stmt):
    tokens = stmt.tokens
    # return a Project object from radb.
    idx = 0
    idxDistinct = -1
    idxFrom = -1
    idxWhere = -1
    for token in tokens:
        if (token.value.lower() == "distinct"):
            # do nothing
            idxDistinct = idx
        elif (token.value.lower() == "from"):
            # do nothing
            idxFrom = idx
        elif (token.value.lower().startswith("where")):
            idxWhere = idx
        else:
            print("")
        idx = idx+1

    isStar = True
    projectAtt = []
    # print(idxDistinct, " ", idxFrom, " ", idxWhere)
    # 1. check * or 1+ attributes
    if tokens[idxDistinct+2].value == "*":
        isStar = True
    else:
        # process words between distinct and from
        isStar = False
        att = []
        selectFullString = tokens[idxDistinct+2].value
        projectAtt = [radb.ast.AttrRef(None, x.strip())
                      for x in selectFullString.split(',')]

    # 2. check 1 or more table. (not handle rename yet)
    tableFullString = tokens[idxFrom+2].value
    tableList = [x.strip() for x in tableFullString.split(',')]
    # return variable
    tablesName = ""
    # only 1 table
    if len(tableList) == 1:
        # no rename case
        if len(tableList[0].split(' ')) == 1:
            tablesName = radb.ast.RelRef(tableList[0])
        # rename case
        else:
            tableListList = tableList[0].split(' ')
            table = radb.ast.RelRef(tableListList[0])
            tablesName = radb.ast.Rename(tableListList[1], None, table)
    # more than 1 table.
    else:
        temptable = ""
        for table in tableList:
            # no rename case
            if len(table.split(' ')) == 1:

                if temptable == "":
                    temptable = radb.ast.RelRef(table)
                else:
                    temptable = radb.ast.Cross(
                        temptable, radb.ast.RelRef(table))
            # rename case
            else:
                tableListList = table.split(' ')
                table = radb.ast.RelRef(tableListList[0])
                renameTable = radb.ast.Rename(tableListList[1], None, table)
                if temptable == "":
                    temptable = renameTable
                else:
                    temptable = radb.ast.Cross(temptable, renameTable)
        tablesName = temptable
    # 3. check where clause
    if (idxWhere != -1):
        whereTokens = tokens[idxWhere].tokens
        startToken = -1
        # return variable
        whereClauses = ""
        for index, token in enumerate(whereTokens):
            if (token.value == "where"):
                startToken = index+2
                break
        whereList = whereTokens[startToken:]
        # only 1 where clause
        if len(whereList) == 1:
            # select need 1 valExpr + 1 RelExpr
            # delete blank tokens
            whereSingleClause = [x for x in whereList.pop(
                0).tokens if x.value != ' ']
            # convert BinaryOperator = index
            biIndex = sym.literalNames.index(
                "'" + whereSingleClause[1].value + "'")
            # split both clause in whereSingleClause[0].value and whereSingleClause[2].value by the dot.
            tableName0, colName0, tableName2, colName2 = ["" for _ in range(4)]
            if whereSingleClause[0].value.find('.') != -1:
                tableName0 = whereSingleClause[0].value.split('.')[0]
                colName0 = whereSingleClause[0].value.split('.')[1]
            else:
                tableName0 = None
                colName0 = whereSingleClause[0].value
            if whereSingleClause[2].value.find('.') != -1:
                tableName2 = whereSingleClause[2].value.split('.')[0]
                colName2 = whereSingleClause[2].value.split('.')[1]
            else:
                tableName2 = None
                colName2 = whereSingleClause[2].value
            # use ValExprBinaryOp
            obj1, obj2 = ["" for _ in range(2)]
            if ((isinstance(whereSingleClause[0], sqlparse.sql.Identifier) and whereSingleClause[2].ttype is not None)) or ((isinstance(whereSingleClause[2], sqlparse.sql.Identifier) and whereSingleClause[0].ttype is not None)):
                obj1 = radb.ast.AttrRef(tableName0, colName0)
                if (whereSingleClause[2].ttype is not None):
                    if (whereSingleClause[2].value.startswith("'")):
                        obj2 = radb.ast.RAString(colName2)
                    else:
                        obj2 = radb.ast.RANumber(colName2)
                elif(whereSingleClause[0].ttype is not None):
                    if (whereSingleClause[0].value.startswith("'")):
                        obj2 = radb.ast.RAString(colName2)
                    else:
                        obj2 = radb.ast.RANumber(colName2)
            elif ((isinstance(whereSingleClause[0], sqlparse.sql.Identifier) and isinstance(whereSingleClause[2], sqlparse.sql.Identifier)) or (isinstance(whereSingleClause[2], sqlparse.sql.Identifier) and isinstance(whereSingleClause[0], sqlparse.sql.Identifier))):
                obj1 = radb.ast.AttrRef(tableName0, colName0)
                obj2 = radb.ast.AttrRef(tableName2, colName2)
            BinaryOp = radb.ast.ValExprBinaryOp(
                obj1, biIndex, obj2)
            whereClauses = radb.ast.Select(BinaryOp, tablesName)
        else:
            # delete blank tokens in wherelist
            whereListWithoutBlanks = [x for x in whereList if x.value != ' ']

            # 1. get the first where token (same as above)
            whereSingleClause = [
                x for x in whereListWithoutBlanks.pop(0).tokens if x.value != ' ']

            # convert BinaryOperator = index
            biIndex = sym.literalNames.index(
                "'" + whereSingleClause[1].value + "'")
            # split both clause in whereSingleClause[0].value and whereSingleClause[2].value by the dot.
            tableName0, colName0, tableName2, colName2 = ["" for _ in range(4)]
            if whereSingleClause[0].value.find('.') != -1:
                tableName0 = whereSingleClause[0].value.split('.')[0]
                colName0 = whereSingleClause[0].value.split('.')[1]
            else:
                tableName0 = None
                colName0 = whereSingleClause[0].value
            if whereSingleClause[2].value.find('.') != -1:
                tableName2 = whereSingleClause[2].value.split('.')[0]
                colName2 = whereSingleClause[2].value.split('.')[1]
            else:
                tableName2 = None
                colName2 = whereSingleClause[2].value
            # use ValExprBinaryOp
            obj1, obj2 = ["" for _ in range(2)]
            if ((isinstance(whereSingleClause[0], sqlparse.sql.Identifier) and whereSingleClause[2].ttype is not None)) or ((isinstance(whereSingleClause[2], sqlparse.sql.Identifier) and whereSingleClause[0].ttype is not None)):
                obj1 = radb.ast.AttrRef(tableName0, colName0)
                if (whereSingleClause[2].ttype is not None):
                    if (whereSingleClause[2].value.startswith("'")):
                        obj2 = radb.ast.RAString(colName2)
                    else:
                        obj2 = radb.ast.RANumber(colName2)
                elif(whereSingleClause[0].ttype is not None):
                    if (whereSingleClause[0].value.startswith("'")):
                        obj2 = radb.ast.RAString(colName2)
                    else:
                        obj2 = radb.ast.RANumber(colName2)
            elif ((isinstance(whereSingleClause[0], sqlparse.sql.Identifier) and isinstance(whereSingleClause[2], sqlparse.sql.Identifier)) or (isinstance(whereSingleClause[2], sqlparse.sql.Identifier) and isinstance(whereSingleClause[0], sqlparse.sql.Identifier))):
                obj1 = radb.ast.AttrRef(tableName0, colName0)
                obj2 = radb.ast.AttrRef(tableName2, colName2)
            BinaryOp = radb.ast.ValExprBinaryOp(
                obj1, biIndex, obj2)

            # 2. get a pair of token  (2nd & 3rd, 4th & 5th etc.)
            # 2nd token will be binary operator.
            while (len(whereListWithoutBlanks) > 0):
                operator, secondClause = [
                    whereListWithoutBlanks.pop(0) for idx in range(2)]
                # if operator.lower() == 'and':  # we neglect or in this case.
                #    AndIndex = sym.AND
                whereSingleClause = [
                    x for x in secondClause.tokens if x.value != ' ']
                biIndex = sym.literalNames.index(
                    "'" + whereSingleClause[1].value + "'")

                # split both clause in whereSingleClause[0].value and whereSingleClause[2].value by the dot.
                tableName0, colName0, tableName2, colName2 = [
                    "" for _ in range(4)]
                if whereSingleClause[0].value.find('.') != -1:
                    tableName0 = whereSingleClause[0].value.split('.')[0]
                    colName0 = whereSingleClause[0].value.split('.')[1]
                else:
                    tableName0 = None
                    colName0 = whereSingleClause[0].value
                if whereSingleClause[2].value.find('.') != -1:
                    tableName2 = whereSingleClause[2].value.split('.')[0]
                    colName2 = whereSingleClause[2].value.split('.')[1]
                else:
                    tableName2 = None
                    colName2 = whereSingleClause[2].value
                # use ValExprBinaryOp
                obj1, obj2 = ["" for _ in range(2)]
                if ((isinstance(whereSingleClause[0], sqlparse.sql.Identifier) and whereSingleClause[2].ttype is not None)) or ((isinstance(whereSingleClause[2], sqlparse.sql.Identifier) and whereSingleClause[0].ttype is not None)):
                    obj1 = radb.ast.AttrRef(tableName0, colName0)
                    if (whereSingleClause[2].ttype is not None):
                        if (whereSingleClause[2].value.startswith("'")):
                            obj2 = radb.ast.RAString(colName2)
                        else:
                            obj2 = radb.ast.RANumber(colName2)
                    elif(whereSingleClause[0].ttype is not None):
                        if (whereSingleClause[0].value.startswith("'")):
                            obj2 = radb.ast.RAString(colName2)
                        else:
                            obj2 = radb.ast.RANumber(colName2)
                elif ((isinstance(whereSingleClause[0], sqlparse.sql.Identifier) and isinstance(whereSingleClause[2], sqlparse.sql.Identifier)) or (isinstance(whereSingleClause[2], sqlparse.sql.Identifier) and isinstance(whereSingleClause[0], sqlparse.sql.Identifier))):
                    obj1 = radb.ast.AttrRef(tableName0, colName0)
                    obj2 = radb.ast.AttrRef(tableName2, colName2)
                nextBinaryOp = radb.ast.ValExprBinaryOp(
                    obj1, biIndex, obj2)

                # conjunct 2 where clause.
                BinaryOp = radb.ast.ValExprBinaryOp(
                    BinaryOp, sym.AND, nextBinaryOp)

            whereClauses = radb.ast.Select(BinaryOp, tablesName)

        if (whereClauses != ""):
            tablesName = whereClauses
    # 9. return value
    if (isStar):
        input = tablesName
    else:
        input = radb.ast.Project(projectAtt, tablesName)

    result = input
    return result


def main(file_path):
    print("This is main program.")


if __name__ == "__main__":
    main()
