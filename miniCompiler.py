import sys, os
from pyparsing import *
from database import Database
import contextlib

#Suppress print statements of Small Relations database
with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
    from miniParser import queries
    from smallRelationsInsertFile import db
  

def sqlInput():
    text = input("Compiler is running \n")
    sql = text.split(";")
    print(sql)


print("Welcome to Mini Compiler. A sql-like compiler for miniDB framework made from Python!")

sqlInput()
    
