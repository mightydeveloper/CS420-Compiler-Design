# Symbol table generator implementation
# 20121022 Young Seok Kim

import AST
import ply.yacc as yacc
from lexer import tokens
import logging


class SymbolTable(object):
    def __init__(self, name):
        self.name = name
        self.table = []

    def add_entry(self, symtype, name, array, role):
        self.table.append((symtype, name, array, role))

    def __str__(self):
        outputstr = ""
        count = 1
        outputstr += "Function name : "+self.name+"\n"
        outputstr += "{:>5} {:>8}  {:>10}  {:>7}  {:>13}\n".format("count", "Type", "name", "array", "role")
        for (symtype, name, array, role) in self.table:
            if array is None:
                array = ""
            else:
                array = str(array)
            outputstr += "{:>5} {:>8}  {:>10}  {:>7}  {:>13}\n".format(count, symtype, name, array, role)
            count += 1
        return outputstr

    def test(self):
        self.add_entry("int", "in", None, "parameter")
        self.add_entry("int", "var4", None, "variable")
        self.add_entry("float", "var5", 10, "variable")

    # The node p should be given as DecList node
    def add_decllist(self, p):
        for decl in p.declarations:
            symtype = decl.type
            for iden in decl.identlist.identifiers:
                if iden.idtype == 'array':
                    self.add_entry(symtype.printast(), iden.id, iden.intnum, "variable")
                else:
                    self.add_entry(symtype.printast(), iden.id, None, "variable")

    # The node p should be given as ParamList node
    def add_paramList(self, p):
        if p is None:
            return
        for (paramType, paramIden) in p.paramlist:
            if paramIden.idtype == 'array':
                self.add_entry(paramType.printast(), paramIden.id, paramIden.intnum, "parameter")
            else:
                self.add_entry(paramType.printast(), paramIden.id, None, "parameter")




# p should be given as program node
def generate_symbol_table(p):
    tables = []
    gTable = SymbolTable("GLOBAL")          # This is the Global symbol table
    gTable.add_decllist(p.DecList)
    tables.append(gTable)

    for function in p.FuncList.functions:
        fTable = SymbolTable(str(function.id))
        fTable.add_paramList(function.params)
        tables.append(fTable)
        tables += make_tables_for_compoundStmt(function.comoundstmt, str(function.id), fTable)

    # Make output string
    outputstr = ""
    for tb in tables:
        outputstr += str(tb) + "\n"
    return outputstr


# if it is from function, give scope as function name,
# if it is from normal compound stmt, add compound stmt to function name (also add number)
def make_tables_for_compoundStmt(p, scope, count=None, topTable=None):
    tables = []

    # Add its decllist to the top scope (function case)
    if topTable is not None:
        topTable.add_decllist(p.declist)
    else: # normal case
        scope += " - " + "compound(" + str(count) + ")"
        cTable = SymbolTable(scope)
        cTable.add_decllist(p.declist)
        tables.append(cTable)

    tables += make_tables_for_stmtlist(p.stmtlist, scope)

    return tables


# p should be given as StmtList Node
def make_tables_for_stmtlist(p, scope):
    tables = []
    # initialize counts
    counts = {}
    counts["while"] = 0
    counts["for"] = 0
    counts["if"] = 0
    counts["switch"] = 0
    counts["compound"] = 0

    for stmt in p.stmts:
        if p.stmttype == "assignstmt":
            tables += make_tables_for_assignstmt(p, scope)
        elif p.stmttype == "callstmt":
            continue
        elif p.stmttype == "retstmt":
            continue
        elif p.stmttype == "whilestmt":

        elif p.stmttype == "forstmt":

        elif p.stmttype == "ifstmt":

        elif p.stmttype == "switchstmt":

        elif p.stmttype == "compoundstmt":
            counts["compound"] += 1
            tables += make_tables_for_compoundStmt(p, scope, count=counts["compound"])
        else: # Semicolon case
            continue

    return tables


# p should be given as Stmt Node
def make_tables_for_stmt(p, scope):
    if p.stmttype == "assignstmt":
        make_tables_for_assignstmt(p, scope)
    elif p.stmttype == "callstmt":
        return []
    elif p.stmttype == "retstmt":
        return []
    elif p.stmttype == "whilestmt":

    elif p.stmttype == "forstmt":

    elif p.stmttype == "ifstmt":

    elif p.stmttype == "switchstmt":

    elif p.stmttype == "compoundstmt":

    else:
        return []



def make_tables_for_whilestmt(p, scope, count):
    pass


def make_tables_for_ifstmt(p, scope, count):
    p.thenstmt

    p.elsestmt
    


def make_tables_for_forstmt(p, scope, count):
    pass








