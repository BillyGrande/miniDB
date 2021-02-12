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
from smallRelationsInsertFile import db

selectStmt = Forward()

SELECT, FROM, WHERE = map(CaselessKeyword, "select from where".split())

ident = Word(alphas,alphanums + "_$").setName("identifier")
columnName = delimitedList(ident, ".", combine=True).setName("column name")
columnNameList = Group(delimitedList(columnName))
tableName = delimitedList(ident, ".", combine=True).setName("table name")
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
    db.show_table("student")
    select = simpleSQL.parseString("Select name, ID from student where name==Zhang")
    print(select)
    where = select[4][1][0] + select[4][1][1] + select[4][1][2]
    db.select(select[3][0],select[1],where)
    
       