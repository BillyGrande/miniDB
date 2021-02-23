import sys,os
from pyparsing import *
from database import Database
import contextlib

#Suppress print statements of Small Relations database when loading
with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
    from miniParser import miniParsers
    from smallRelationsInsertFile import db
  
#A general parser for all accepted characters
sqltext = Word(alphanums + "_$, -*.()<=>\"\'").setName("text")
parser = delimitedList(sqltext, ";",)

#The heart of compiler, function exits, only when we the last char is ";"
def sqlInput(query):
    try:
        text = input()
        try:
            if text[-1] == ";":
                query = query + text
                sql = parser.parseString(query)
                return sql
            else:
                text = query + text + " "
                return sqlInput(text)
        except ParseException:
            sqlInput("")
    except IndexError:
        print("\n")
        sqlInput("")
        
        
print("Welcome to Mini Compiler. A sql-like compiler for miniDB framework made from Python!")

class Compiler:
    
    
    def __init__(self, database=None):
        self.db = database
        self.parsedText = []
        self.sql = []
        self.parsingGrammar = []
        print("Compiler is activated!")
        self.screen()
    
    def screen(self):
        self.parsedText.extend(sqlInput(""))
        self.sqlText()
    
    def sqlText(self):
        self.sql.extend(self.parsedText)
        print(self.sql)
        self.typeOfQuery()
    
    def validator(self, query):
        pass
    
    def typeOfQuery(self):
        for query in self.sql:
            initialStmt = query.split()[0]
            try:
                type = initialStmt.upper()
                parser = miniParsers[type]
                self.parsing(query,parser)
            except KeyError as err:
                print("'" + initialStmt + "' is not a valid initial token {0}".format(err))
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
                
                
    def parsing(self, query, parser):
        result = parser.parseString(query)
        functionName = result[0].lower() + "Stm"
        
        #One liner code to call the appropriate database function
        getattr(self, functionName)(result)
        
    def selectStm(self,parsedText):
        columns = parsedText[1]
        table = parsedText[3][0]
        condition = None
        print(parsedText)
        
        try:
            lastToken = parsedText[4][0].lower() 
            if lastToken == "where":
                condition = "".join(parsedText[4][1])
                print(condition)
            elif lastToken == "inner":
                pass
                return None
        except IndexError:
            pass
        
        self.db.select(table,columns,condition)
        
    def updateStm(self,parsedText):
        table = parsedText[1]
        set_value = parsedText[3][2]
        set_column = parsedText[3][0]
        condition = "".join(parsedText[5])
        self.db.update(table, set_value, set_column, condition)
        
    #def insert(self, table_name, row, lock_load_save=True):
    def insertStm(self,parsedText):
        table = parsedText[2]
        row = parsedText[3]
        self.db.insert(table,row)
    
    #['DELETE', 'FROM', 'student', 'WHERE', ['name', '==', 'Zhang@']]
    def deleteStm(self,parsedText):
        table = parsedText[2]
        condition = "".join(parsedText[4])
        self.db.delete(table,condition)
    
    def createStm(self,parsedText):
        pass
    
    def dropStm(self,parsedText):
        pass
    
    

if __name__ == "__main__":
    
    comp = Compiler(db)
    comp2 = Compiler(db)
    