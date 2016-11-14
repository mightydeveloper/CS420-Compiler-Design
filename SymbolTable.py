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

    def add_decllist(self, p):
        for decl in p.declarations:
            symtype = decl.type
            for iden in decl.identlist.identifiers:
                if iden.idtype == 'array':
                    self.add_entry(symtype.printast(), iden.id, iden.intnum, "variable")
                else:
                    self.add_entry(symtype.printast(), iden.id, None, "variable")




# p should be given as program node
def generate_symbol_table(p):
    tables = []
    gTable = SymbolTable("GLOBAL")          # This is the Global symbol table
    gTable.add_decllist(p.DecList)
    tables.append(gTable)

    # Make output string
    outputstr = ""
    for tb in tables:
        outputstr += str(tb) + "\n"
    return outputstr




