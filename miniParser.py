import sys
from pyparsing import *
from database import Database
from smallRelationsInsertFile import db

selectStmt = Forward()

keywords = {
    k: CaselessKeyword(k)
    for k in """\
    SELECT FROM WHERE
    """.split()
    }
vars().update(keywords)


#SELECT, FROM, WHERE = map(CaselessKeyword, "select from where".split())

ident = Word(alphas,alphanums + "_$").setName("identifier")
columnName = delimitedList(ident, ".", combine=True).setName("column name")
columnNameList = Group(delimitedList(columnName))
tableName = delimitedList(ident, ".", combine=True).setName("table name")
tableNameList = Group(delimitedList(tableName))

binop = oneOf("< <= == >= >")
realNum = pyparsing_common .real()
intNum = pyparsing_common .signed_integer()

columnRval = (
    realNum | intNum | columnName
    )
whereCondition = Group(columnName + binop + columnRval)

whereExpression = infixNotation(whereCondition, [
    ("==",1,opAssoc.RIGHT)],)

selectStmt <<= (
    SELECT 
    + ("*" | columnNameList)("columns")
    + FROM
    + tableNameList("tables")
    + Optional(Group(WHERE + whereExpression), "")("where")
    )

simpleSQL = selectStmt

if __name__ == "__main__":
       simpleSQL.runTests(
        """\

        # multiple tables
        SELECT * from XYZZY, ABC

        # dotted table name
        select * from SYS.XYZZY

        Select A from Sys.dual

        Select A,B,C from Sys.dual

        Select A, B, C from Sys.dual, Table2

        # FAIL - invalid SELECT keyword
        Xelect A, B, C from Sys.dual

        # FAIL - invalid FROM keyword
        Select A, B, C frox Sys.dual

        # FAIL - incomplete statement
        Select

        # FAIL - incomplete statement
        Select * from

        # FAIL - invalid column
        Select &&& frox Sys.dual
        
        """
        )
       