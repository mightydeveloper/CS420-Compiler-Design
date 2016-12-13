# Symbol table generator implementation
# 20121022 Young Seok Kim

import AST
import ply.yacc as yacc
from lexer import tokens
import logging
import ErrorCollector

class SymbolInfo(object):
    def __init__(self, symtype, name, array, role, linepos):
        self.symtype = symtype
        self.name = name
        self.array = array
        self.role = role
        self.linepos = linepos
        self.stack_index = -9999

    def __getitem__(self, key):
        if key == 0:
            return self.symtype
        elif key == 1:
            return self.name
        elif key == 2:
            return self.array
        elif key == 3:
            return self.role
        elif key == 4:
            return self.linepos

    def __iter__(self):
        return self.Iterator(self)

    class Iterator(object):
        def __init__(self, info):
            self.index = 0
            self.info = info

        def __next__(self):
            if self.index < 5:
                idx = self.index
                self.index += 1
                return self.info[idx]
            else:
                raise StopIteration()

class SymbolTable(object):
    def __init__(self, name):
        self.name = name
        self.table = []

    def add_entry(self, symtype, name, array, role, linepos):
        for entry in self.table:
            if entry[1] == name:
                ErrorCollector.error("declaration conflict(%s)" % name, linepos)
                break
        self.table.append(SymbolInfo(symtype, name, array, role, linepos))

    def add_entry_with_shadowing(self, entry):
        symtype, name, array, role, linepos = entry
        for registered in self.table:
            if registered.name == name:
                self.table.remove(registered)
                break

        self.add_entry(symtype, name, array, role, linepos)

    def __str__(self):
        if len(self.table) == 0:
            return ""
        outputstr = ""
        count = 1
        outputstr += "Function name : "+self.name+"\n"
        outputstr += "{:>5} {:>8}  {:>25}  {:>7}  {:>13}  {:>4} {:>4}\n".format(
            "count", "Type", "name", "array", "role", "line", "position")
        for (symtype, name, array, role, linepos) in self.table:
            line, pos = linepos
            if array is None:
                array = ""
            else:
                array = str(array)

            # print("-----------")
            # print(symtype)
            # print(name)
            # print(array)
            # print(role)
            # print(line)
            # print(pos)
            outputstr += "{:>5} {:>8}  {:>25}  {:>7}  {:>13}  {:>4} {:>4}\n".format(
                         count, symtype, name, array, role, line, pos)
            count += 1
        return outputstr

    # The node p should be given as DecList node
    def add_decllist(self, p):
        if p is None:
            return
        for decl in p.declarations:
            symtype = decl.type
            for iden in decl.identlist.identifiers:
                if iden.idtype == 'array':
                    self.add_entry(symtype.printast(), iden.id, iden.intnum, "variable", iden.line_position)
                else:
                    self.add_entry(symtype.printast(), iden.id, None, "variable", iden.line_position)

    # The node p should be given as ParamList node
    def add_paramList(self, p):
        if p is None:
            return
        for (paramType, paramIden) in p.paramlist:
            if paramIden.idtype == 'array':
                self.add_entry(paramType.printast(), paramIden.id, paramIden.intnum, "parameter", paramIden.line_position)
            else:
                self.add_entry(paramType.printast(), paramIden.id, None, "parameter", paramIden.line_position)


# Helper function for 'find_all_variables(scope, all_symbol_tables)'
def find_symbol_table(scope_name, tables):
    for table in tables:
        if table.name == scope_name:
            return table


# scope: string, all_symbol_tables: [SymbolTables]
# returns a single Symbol table having all the variables in that scope
def find_all_variables(scope, all_symbol_tables):
    scopes = scope.split(" - ")
    scope_sym_table = SymbolTable("(cumulative)"+scope)
    # copy GLOBAL Symbol table
    gTable = find_symbol_table("GLOBAL", all_symbol_tables)
    for entry in gTable.table:
        scope_sym_table.add_entry_with_shadowing(entry)
    # copy rest of the scopes
    for i in range(len(scopes)):
        name = " - ".join(scopes[:i+1])     # from 0 th ith, inclusive
        found_table = find_symbol_table(name, all_symbol_tables)
        if found_table is None:
            continue # TODO found table must not be None
        for entry in found_table.table:
            scope_sym_table.add_entry_with_shadowing(entry)
    return scope_sym_table


def find_function(name, all_symbol_tables) -> AST.Function:
    gTable = find_symbol_table('GLOBAL', all_symbol_tables)
    if name in gTable.funcTables:
        return gTable.funcTables[name]
    else:
        return None


def find_symbol(name, symbol_table):
    for entry in symbol_table.table:
        if entry[1] == name:
            return entry
    return None

# p should be given as program node
def generate_symbol_table(p):
    tables = []
    gTable = SymbolTable("GLOBAL")          # This is the Global symbol table
    gTable.add_decllist(p.DecList)
    tables.append(gTable)
    gTable.funcTables = {}     # function name to SymbolTable object mapping (dictionary)

    for function in p.FuncList.functions:
        gTable.add_entry(function.type.type, str(function.id), None, "function", function.line_position)
        fTable = SymbolTable(str(function.id))
        fTable.add_paramList(function.params)
        tables.append(fTable)
        tables += make_tables_for_compoundStmt(function.comoundstmt, str(function.id), topTable=fTable)
        gTable.funcTables[str(function.id)] = function

    return tables


# if it is from function/if/while/for, give scope as function name,
# if it is from normal compound stmt, add compound stmt to function name (also add number)
def make_tables_for_compoundStmt(p, scope, count=None, topTable=None):
    tables = []

    # Add its decllist to the top scope (function case)
    if topTable is not None:
        topTable.add_decllist(p.declist)
    else: # normal case
        scope += " - compound(" + str(count) + ")"
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
        if stmt.stmttype == "assignstmt":
            continue
        elif stmt.stmttype == "callstmt":
            continue
        elif stmt.stmttype == "retstmt":
            continue
        elif stmt.stmttype == "whilestmt":
            counts["while"] += 1
            tables += make_tables_for_whilestmt(stmt.stmt, scope, count=counts["while"])
        elif stmt.stmttype == "forstmt":
            counts["for"] += 1
            tables += make_tables_for_forstmt(stmt.stmt, scope, count=counts["for"])
        elif stmt.stmttype == "ifstmt":
            counts["if"] += 1
            tables += make_tables_for_ifstmt(stmt.stmt, scope, count=counts["if"])
        elif stmt.stmttype == "switchstmt":
            counts["switch"] += 1
            tables += make_tables_for_switchstmt(stmt.stmt, scope, count=counts["switch"])
        elif stmt.stmttype == "compoundstmt":
            counts["compound"] += 1
            tables += make_tables_for_compoundStmt(stmt.stmt, scope, count=counts["compound"])
        else: # Semicolon case
            continue

    return tables


# p should be given as Stmt Node
def make_tables_for_stmt(p, scope):
    if p.stmttype == "assignstmt":
        return []
    elif p.stmttype == "callstmt":
        return []
    elif p.stmttype == "retstmt":
        return []
    elif p.stmttype == "whilestmt":
        return make_tables_for_whilestmt(p.stmt, scope, count=1)
    elif p.stmttype == "forstmt":
        return make_tables_for_forstmt(p.stmt, scope, count=1)
    elif p.stmttype == "ifstmt":
        return make_tables_for_ifstmt(p.stmt, scope, count=1)
    elif p.stmttype == "switchstmt":
        return make_tables_for_switchstmt(p.stmt, scope, count=1)
    elif p.stmttype == "compoundstmt":
        return make_tables_for_compoundStmt(p.stmt, scope, count=1)
    else: # Semicolon case
        return []


def make_tables_for_ifstmt(p, scope, count):
    tables = []
    scope += " - if("+str(count)+")"
    # If
    if_scope = scope+"(if)"
    if p.thenstmt.stmttype == "compoundstmt":
        ifTable = SymbolTable(if_scope)
        tables.append(ifTable)
        tables += make_tables_for_compoundStmt(p.thenstmt.stmt, if_scope, topTable=ifTable)
    else:
        tables += make_tables_for_stmt(p.thenstmt, if_scope)

    # Else
    else_scope = scope+"(else)"
    if p.elsestmt is not None:
        if p.elsestmt.stmttype == "compoundstmt":
            elseTable = SymbolTable(else_scope)
            tables.append(elseTable)
            tables += make_tables_for_compoundStmt(p.elsestmt.stmt, else_scope, topTable=elseTable)
        else:
            tables += make_tables_for_stmt(p.elsestmt, else_scope)

    return tables


def make_tables_for_forstmt(p, scope, count):
    tables = []
    scope += " - for("+str(count)+")"
    if p.repeatstmt.stmttype == "compoundstmt":
        forTable = SymbolTable(scope)
        tables.append(forTable)
        tables += make_tables_for_compoundStmt(p.repeatstmt.stmt, scope, topTable=forTable)
    else:
        tables += make_tables_for_stmt(p.repeatstmt, scope)

    return tables

def make_tables_for_whilestmt(p, scope, count):
    tables = []
    scope += " - while("+str(count)+")"
    if p.repeatstmt.stmttype == "compoundstmt":
        whileTable = SymbolTable(scope)
        tables.append(whileTable)
        tables += make_tables_for_compoundStmt(p.repeatstmt.stmt, scope, topTable=whileTable)
    else:
        tables += make_tables_for_stmt(p.repeatstmt, scope)

    return tables

def make_tables_for_switchstmt(p, scope, count):
    tables = []
    scope += " - switch("+str(count)+")"
    for (intnum, stmtlist, break_exist) in p.caselist.cases.cases:
        newscope = scope + "case("+str(intnum)+")"
        tables += make_tables_for_stmtlist(stmtlist, newscope)

    if p.caselist.default is not None:
        newscope = scope + "defaultcase"
        tables += make_tables_for_stmtlist(p.caselist.default.stmtlist, newscope)

    return tables








