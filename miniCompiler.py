import sys, os
from pyparsing import *
from database import Database
import contextlib

#Suppress print statements of Small Relations database
with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
    from miniParser import queries
    from smallRelationsInsertFile import db
  

sqltext = Word(alphanums + "_$, -*.()<=>\"\'")
parser = delimitedList(sqltext, ";",)

def sqlInput(query):
    try:
        text = input()
        try:
            if text[-1] == ";":
                query = query + text
                sql = parser.parseString(query)
                print(parser.parseString(query))
                return sql
            else:
                text = query + " " + text
                sqlInput(text)
        except ParseException:
            sqlInput("")
    except IndexError:
        print("\n")
        sqlInput("")
        
        
print("Welcome to Mini Compiler. A sql-like compiler for miniDB framework made from Python!")

class Compiler:
    
    
    def __init__(self, query):
        self.query = query
        self.parsedText = []
        self.sql = []
        print("Compiler is activated!")
        self.screen()
    
    def screen(self):
        self.parsedText.append(sqlInput(""))
    
    def sqlText(self):
        self.sql.append(self.parsedText[0][0])
        print(self.sql)
    
    def validator(self, query):
        pass
    
    def typeOfQuery(self):
        pass
    
    