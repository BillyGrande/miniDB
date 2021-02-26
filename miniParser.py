import sys
from pyparsing import *
from database import Database
from smallRelationsInsertFile import db



selectStmt = Forward()
updateStmt = Forward()
insertStmt = Forward()
deleteStmt = Forward()
createStmt = Forward()
dropStmt = Forward()

keywords = {
    k: CaselessKeyword(k)
    for k in """\
    SELECT FROM WHERE UPDATE SET INSERT INTO DELETE
    DROP TABLE CREATE INDEX DATABASE ON INNER JOIN
    ORDER BY ASC DESC
    """.split()
    }
vars().update(keywords)


#SELECT, FROM, WHERE = map(CaselessKeyword, "select from where".split())

ident = Word(alphas, alphanums + "_$").setName("identifier")
columnName = delimitedList(ident, ".", combine=True).setName("column name")
columnNameList = Group(delimitedList(columnName))
tableName = delimitedList(ident, ".", combine=True).setName("table name")
tableNameList = Group(delimitedList(tableName))

digits = Word(nums).setName("numeric digits")
real_num = Combine(digits + '.' + digits)
dataTypes = oneOf("str int float complex")
binop = oneOf("< <= == >= >")
realNum = pyparsing_common.real()
intNum = pyparsing_common.signed_integer()
newTable = ident + dataTypes

#stringVal = Word(alphanums)

#for select
columnRval = (
    realNum | intNum | columnName | QuotedString('"')
    )

columnRval = (
    digits| real_num | columnName | QuotedString('"')
    )

#for update
setColumnVal = (
    intNum | realNum | QuotedString('"')
    )

setColumnVal = (
    digits | real_num | QuotedString('"')
    )

#for select
whereCondition = Group(columnName + binop + columnRval)

#for update
whereConditionSet = Group(ident + binop + setColumnVal)

joinCondition = columnName + binop + columnName

#whereExpression = infixNotation(whereCondition, [("==",1,opAssoc.RIGHT)],)

setCondition = Group(ident + "=" + setColumnVal)

insertRow = Suppress("(") + Group(delimitedList(setColumnVal)) + Suppress(")")

createRow =  Suppress("(") + Group(delimitedList(newTable)) + Suppress(")")

indexRow = ident + Suppress("(") + Group(delimitedList(ident)) +Suppress(")")

selectStmt <<= (
    SELECT 
    + ("*" | columnNameList)("columns")
    + FROM
    + tableNameList("tables")
    + Optional(Group(INNER + JOIN + tableName + ON + joinCondition))("inner join")
    + Optional(Group(WHERE + whereCondition))("where")
    + Optional(Group(ORDER + BY + columnName))("order")
    + Optional(ASC|DESC)
    )

#UPDATE Customers SET name = 'Alfred' WHERE ID == 1;
updateStmt <<= (UPDATE 
                + tableName("table")
                + SET 
                + setCondition("column") 
                + (WHERE + whereConditionSet)("where")
                )

#INSERT INTO student (00128, Zhang', 'Comp. Sci.', '102');
insertStmt <<= (
    INSERT 
    + INTO
    + tableName("table")
    + insertRow("row")
    )

#DELETE FROM Customers WHERE CustomerName='Alfreds Futterkiste';
deleteStmt <<= (
    DELETE 
    + FROM
    + tableName("table")
    + (WHERE + whereConditionSet)("where")
    )

#Create
createStmt <<=(
    CREATE 
    + 
    ((DATABASE + ident)
    | (TABLE + ident + createRow)
    | (INDEX + ident + ON + ident)
    ))


#DROP TABLE student
dropStmt <<= (
    DROP
    + 
    ((DATABASE + ident)
    | (TABLE + tableName("table"))
    | (INDEX + ident)
    ))

miniParsers = {
    "SELECT" : selectStmt,
    "UPDATE": updateStmt,
    "INSERT": insertStmt,
    "DELETE": deleteStmt,
    "CREATE": createStmt,
    "DROP": dropStmt}

simpleSQL = selectStmt
miniSQL = selectStmt

updateSQL = updateStmt
selectSQL = selectStmt
insertSQL = insertStmt
deleteSQL = deleteStmt
dropSQL = dropStmt
createSQL = createStmt

if __name__ == "__main__":
    
    updateTest = "UPDATE A"
    selectTest = "SELECT * from XYZYY, ABC"
    try:
        miniSQL = miniParsers[updateTest.split()[0]]
        print(miniSQL.parseString(updateTest))
    
        miniSQL = miniParsers[selectTest.split()[0]]
        print(miniSQL.parseString(selectTest))
    except:
        print("Fail")
        
    try:
        miniSQL = miniParsers["choco"]
        print(miniSQL.parseString(selectTest))
    except KeyError:
        print("Invalids Start Of Statement")
    
    dropSQL.runTests(
        """\
        #Should work
        DROP TABLE student
        
        #FAIL
        DROP TABLE student where help==3
        
        """)
        
    
    
    insertSQL.runTests(
        """\
        
        #Insert normal statement
        INSERT INTO student (00128, "Zhang", "Comp. Sci.", "102")
        
        #FAIL not parenthesis
        INSERT INTO student (00128, "Zhang", "Comp. Sci.", "102"
        
        """
        )
    
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
       
       
    deleteSQL.runTests(
        """\
        
        #Delete normal statement
        DELETE FROM student WHERE name=="Zhang@"
        
        #Delete normal statement
        DELETE FROM student WHERE ID==1
        
        #Fail
        DELETE FROM student WHERE name==Zhang@
        
        #Fail
        DELETE FROM student WHERE name="Zhang@"
        
        """)
    
    createSQL.runTests(
        """\
        #Create database
        Create database NewSchema
        
        #Create table
        CREATE TABLE Student ( ID int, Name str)
        
        #Create table
        CREATE TABLE Student ( ID int, Name lol)
        
        #Create index
        CREATE INDEX id_3 ON Stundet(ID)
        
        """)
    
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
        
        # Inner Join
        Select BurgerCode.Mac, Names.Burgers, Price.Burgers from Mac INNER JOIN Burgers ON Names.Burgers == BurgerCode.Mac 
        
        #Select Complete
        Select BurgerCode.Mac, Names.Burgers, Price.Burgers from Mac INNER JOIN Burgers ON Names.Burgers == BurgerCode.Mac WHERE Price.Burgers > 3
        
        #Select Order
        Select BurgerCode.Mac, Names.Burgers, Price.Burgers from Mac INNER JOIN Burgers ON Names.Burgers == BurgerCode.Mac WHERE Price.Burgers > 3 ORDER BY BurgerCode
        
        #Select Order
        Select BurgerCode.Mac, Names.Burgers, Price.Burgers from Mac INNER JOIN Burgers ON Names.Burgers == BurgerCode.Mac WHERE Price.Burgers > 3 ORDER BY BurgerCode ASC
        """
        
        )