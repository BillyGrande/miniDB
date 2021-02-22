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
        print(result)
        print(result[0])
        self.selectStm(result)
        
    def selectStm(self,parsedText):
        columns = parsedText[1]
        table = parsedText[3][0]
        
        self.db.select(table,columns)

if __name__ == "__main__":
    
    comp = Compiler(db)
    