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
    
    data_types = {
        "int": int,
        "float": float,
        "str": str,
        "complex": complex
        }
    
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
        functionName = result[0].lower() + "Stmt"
        
        #One liner code to call the appropriate database function
        getattr(self, functionName)(result)
        
    def selectStmt(self,parsedText):
        columns = parsedText[1]
        table = parsedText[3][0]
        condition = None
        order_by = None
        asc = False;
        flag_join = False
        flag_where = False
        
        print(parsedText)
        
        if len(parsedText) > 4:
            print("EIMAI MESA")
            second_part = parsedText[4:]
            print(second_part)
            for text in second_part:
                token = text[0].lower()
                
                if token == "inner":
                    print("inner")
                    flag_join = True
                    table2 = text[2]
                    condition_join = "".join(text[4:])
                    print(condition_join)
                elif token == "where":
                    print("where")
                    flag_where = True
                    condition = "".join(text[1])
                    print(condition)
                elif token == "order":
                    print("order")
                    flag_where = True
                    order_by =  text[2]
                    print(order_by)
                else:
                    print("desc")
                    flag_where = True
                    if token == "a":
                        asc = True
                    print(asc)
       
        if flag_join:
            if flag_where:
                db.inner_join(table,table2,condition_join,return_object=True)._select_where(columns,condition,order_by,asc)
            else:
                db.inner_join(table,table2,condition_join)
        else:
            self.db.select(table,columns,condition,order_by,asc)

#         try:
#             lastToken = parsedText[4][0].lower() 
#             if lastToken == "where":
#                 condition = "".join(parsedText[4][1])
#                 print(condition)
#             elif lastToken == "inner":
#                 pass
#                 return None
#         except IndexError:
#             pass
        
#        self.db.select(table,columns,condition)


        
    def updateStmt(self,parsedText):
        table = parsedText[1]
        set_value = parsedText[3][2]
        set_column = parsedText[3][0]
        condition = "".join(parsedText[5])
        self.db.update(table, set_value, set_column, condition)
        
    #def insert(self, table_name, row, lock_load_save=True):
    def insertStmt(self,parsedText):
        table = parsedText[2]
        row = parsedText[3]
        self.db.insert(table,row)
    
    #['DELETE', 'FROM', 'student', 'WHERE', ['name', '==', 'Zhang@']]
    #Delete From student WHERE name=="Zhang";
    def deleteStmt(self,parsedText):
        table = parsedText[2]
        condition = "".join(parsedText[4])
        self.db.delete(table,condition)
    
    def createStmt(self,parsedText):
        functionName = "create_" + parsedText[1].lower()
        getattr(self, functionName)(parsedText)
        
    def create_database(self,parsedText):
        name = parsedText[2]
        self.db = Database(name)
    
    def create_index(self,parsedText):
        index_name = parsedText[2]
        table = parsedText[4]
        self.db.create_index(table,index_name)
    
    def create_table(self, parsedText):
        if len(parsedText[3]) % 2 == 0:
            unpacked_list = self._unpack_list(parsedText[3])
            table_name = parsedText[2]
            column_names = unpacked_list[0]
            column_types = unpacked_list[1]
            self.db.create_table(table_name,column_names,column_types)
        
        
    
    def _unpack_list(self,columns):
        unpacked_list = []
        column_names = []
        column_types = []
        column_number = len(columns)
        
        for i in range(0,column_number):
            if i % 2:
                column_types.append(Compiler.data_types[columns[i]])
            else:
                column_names.append(columns[i])
        
        unpacked_list.append(column_names)
        unpacked_list.append(column_types)
        print(unpacked_list)
        return unpacked_list
                    
    
    def dropStmt(self,parsedText):
        functionName = "drop_" + parsedText[1].lower()
        getattr(self, functionName)(parsedText)
    
    def drop_database(self,parsedText):
        database = parsedText[2]
        tmp = db
        del tmp
    
    def drop_table(self,parsedText):
        table = parsedText[2]
        db.drop_table(table)
    
    def drop_index(self,parsedText):
        pass

if __name__ == "__main__":
    
    #db.drop_table("KingKong")
    comp1 = Compiler(db)
    comp = Compiler(db)
    comp2 = Compiler(db)
    