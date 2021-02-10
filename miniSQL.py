from pyparsing import (
    Word,
    delimitedList,
    Optional,
    Group,
    alphas,
    alphanums,
    Forward,
    oneOf,
    quotedString,
    infixNotation,
    opAssoc,
    restOfLine,
    CaselessKeyword,
    ParserElement,
    pyparsing_common as ppc,
)

from database import Database

selectStmt = Forward()

SELECT, FROM, WHERE = map(CaselessKeyword, "select from where".split())

ident = Word(alphas,alphanums + "_$").setName("identifier")
columnName = delimitedList(ident, ".", combine=True).setName("column name")
columnName.addParseAction(ppc.upcaseTokens)
columnNameList = Group(delimitedList(columnName))
tableName = delimitedList(ident, ".", combine=True).setName("table name")
tableName.addParseAction(ppc.upcaseTokens)
tableNameList = Group(delimitedList(tableName))

binop = oneOf("< <= == >= >")
realNum = ppc.real()
intNum = ppc.signed_integer()

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
        
        # multiple tables
        SELECT A from ABC WHERE A.ABC == 3
        
        """
        )
    