import sys
from pyparsing import *
from database import Database
from smallRelationsInsertFile import db


selectStmt = Forward()
updateStmt = Forward()
insertStmt = Forward()
deleteStmt = Forward()
createStmt = Forward()

keywords = {
    k: CaselessKeyword(k)
    for k in """\
    SELECT FROM WHERE UPDATE SET
    """.split()
    }
vars().update(keywords)


#SELECT, FROM, WHERE = map(CaselessKeyword, "select from where".split())

ident = Word(alphas, alphanums + "_$").setName("identifier")
columnName = delimitedList(ident, ".", combine=True).setName("column name")
columnNameList = Group(delimitedList(columnName))
tableName = delimitedList(ident, ".", combine=True).setName("table name")
tableNameList = Group(delimitedList(tableName))

binop = oneOf("< <= == >= >")
realNum = pyparsing_common.real()
intNum = pyparsing_common.signed_integer()

#stringVal = Word(alphanums)

#for select
columnRval = (
    realNum | intNum | columnName | QuotedString('"')
    )

#for update
setColumnVal = (
    realNum | intNum | QuotedString('"')
    )

#for select
whereCondition = Group(columnName + binop + columnRval)

#for update
whereConditionSet = Group(ident + binop + setColumnVal)

#whereExpression = infixNotation(whereCondition, [("==",1,opAssoc.RIGHT)],)

setCondition = Group(ident + "=" + setColumnVal)

selectStmt <<= (
    SELECT 
    + ("*" | columnNameList)("columns")
    + FROM
    + tableNameList("tables")
    + Optional(Group(WHERE + whereCondition), "")("where")
    )

#UPDATE Customers SET name = 'Alfred' WHERE ID == 1;
updateStmt <<= (UPDATE 
                + ident("table")
                + SET 
                + setCondition("column") 
                + (WHERE + whereConditionSet)("where")
                )

queries = {
    "SELECT" : selectStmt,
    "UPDATE": updateStmt,
    "INSERT": insertStmt,
    "DELETE": deleteStmt,
    "CREATE": createStmt}

simpleSQL = selectStmt
miniSQL = selectStmt

updateSQL = updateStmt
selectSQL = selectStmt

if __name__ == "__main__":
    
    updateTest = "UPDATE A"
    selectTest = "SELECT * from XYZYY, ABC"
    try:
        miniSQL = queries[updateTest.split()[0]]
        print(miniSQL.parseString(updateTest))
    
        miniSQL = queries[selectTest.split()[0]]
        print(miniSQL.parseString(selectTest))
    except:
        print("Fail")
        
    try:
        miniSQL = queries["choco"]
        print(miniSQL.parseString(selectTest))
    except KeyError:
        print("Invalids Start Of Statement")
        
    updateSQL.runTests(
        """\
        
        #update normal statement
        UPDATE student SET name="Zhang@" where ID == 1
        
        #fail not in string quotes
        UPDATE student SET name=Zhang where ID == 1
        
        #fail not in string quotes
        UPDATE student SET name="Zhang" where ID == coffee
        
        #fail not in string quotes
        UPDATE student SET name="Zhang" where ID == "1"
        
        """
        )
        
    selectSQL.runTests(
        """\
        
        #update
        UPDATE student SET name="Zhang@" where ID == 1

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
       