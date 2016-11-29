# Symbol table generator implementation
# 20121022 Young Seok Kim

import ply.yacc as yacc
from lexer import tokens
import logging
# p should be given as program node
import itertools
from AST import *
from SymbolTable import *
import ErrorCollector
import pdb


def visit_program(p, tables):
    for function in p.FuncList.functions:
        visit_stmtlist(function.comoundstmt.stmtlist, str(function.id), tables)


def visit_compoundStmt(p, scope, tables, count=None):
    scope += " - " + "compound(" + str(count) + ")"
    visit_stmtlist(p.stmtlist, scope, tables)


# p should be given as StmtList Node
def visit_stmtlist(p, scope, tables):
    # initialize counts
    counts = {}
    counts["while"] = 0
    counts["for"] = 0
    counts["if"] = 0
    counts["switch"] = 0
    counts["compound"] = 0
    for stmt in p.stmts:
        if stmt.stmttype == "assignstmt":
            visit_assign(stmt.stmt.assign, scope, tables)
        elif stmt.stmttype == "callstmt":
            visit_call(stmt.stmt.call, scope, tables)
        elif stmt.stmttype == "retstmt":
            visit_retstmt(stmt.stmt, scope, tables)
        elif stmt.stmttype == "whilestmt":
            counts["while"] += 1
            visit_whilestmt(stmt.stmt, scope, tables, count=counts["while"])
        elif stmt.stmttype == "forstmt":
            counts["for"] += 1
            visit_forstmt(stmt.stmt, scope, tables, count=counts["for"])
        elif stmt.stmttype == "ifstmt":
            counts["if"] += 1
            visit_ifstmt(stmt.stmt, scope, tables, count=counts["if"])
        elif stmt.stmttype == "switchstmt":
            counts["switch"] += 1
            visit_switchstmt(stmt.stmt, scope, tables, count=counts["switch"])
        elif stmt.stmttype == "compoundstmt":
            counts["compound"] += 1
            visit_compoundStmt(stmt.stmt, scope, tables, count=counts["compound"])
        else: # Semicolon case
            continue
# p should be given as Stmt Node


def visit_stmt(p, scope, tables):
    if p.stmttype == "assignstmt":
        pass
    elif p.stmttype == "callstmt":
        pass
    elif p.stmttype == "retstmt":
        pass
    elif p.stmttype == "whilestmt":
        visit_whilestmt(p.stmt, scope, tables, count=1)
    elif p.stmttype == "forstmt":
        visit_forstmt(p.stmt, scope, tables, count=1)
    elif p.stmttype == "ifstmt":
        visit_ifstmt(p.stmt, scope, tables, count=1)
    elif p.stmttype == "switchstmt":
        visit_switchstmt(p.stmt, scope, tables, count=1)
    elif p.stmttype == "compoundstmt":
        visit_compoundStmt(p.stmt, scope, tables, count=1)
    else: # Semicolon case
        pass


def visit_retstmt(p: RetStmt, scope, tables):
    visit_expr(p.expr, scope, tables)
    func_name = scope.split(' - ')[0]
    func = find_function(func_name, tables)

    if func.type.type.lower() != p.expr.return_type():
        ErrorCollector.report("Warning: return type mismatch at " + func_name + p.position())


def visit_expr(p: Expr, scope, tables):
    p_type = p.expr_type

    if p_type == "unop" or p_type == "paren":
        visit_expr(p.operand1, scope, tables)
        p.set_return_type(p.operand1.return_type())
    elif p_type == "binop":
        visit_expr(p.operand1, scope, tables)
        visit_expr(p.operand2, scope, tables)


        if p.operand1.return_type() != p.operand2.return_type():
            a = p.operand1.return_type()
            b = p.operand2.return_type()
            ErrorCollector.report("Warning: binop operand type mismatch "+ a + " & " + b + " at " + p.position())

            if p.operator in ['+', '-', '*', '/']:
                p.set_return_type("float")
            else:
                p.set_return_type("int")
        else:
            if p.operator in ['+', '-', '*', '/']:
                p.set_return_type(p.operand1.return_type())
            else:
                p.set_return_type("int")

            # TODO generate type conversion node
    elif p_type == "id":
        # TODO : change operand1 -> idval
        table = find_all_variables(scope, tables)
        entry = find_symbol(p.operand1, table)
        if entry is None:
            ErrorCollector.report("Error: symbol not declared: " + str(p.operand1) + " at " + p.position())
            p.set_return_type('')
        else:
            p.set_return_type(entry[0])
    elif p_type == "arrayID":
        table = find_all_variables(scope, tables)
        entry = find_symbol(p.idval, table)
        if entry is None:
            ErrorCollector.report("Error: symbol not declared: " + str(p.idval) + " at " + p.position())
            p.set_return_type('')
        else:
            p.set_return_type(entry[0])
        visit_expr(p.idIDX, scope, tables)
        if p.idIDX.return_type() != "int":
            ErrorCollector.report("Warning: Array index is not integer type at " + p.position())
    elif p_type == "intnum":
        p.set_return_type("int")
    elif p_type == "floatnum":
        p.set_return_type("float")
    elif p_type == "call":
        visit_call(p.operand1, scope, tables)
        p.set_return_type(p.operand1.return_type())
    else:
        raise Exception("Uncatched expr type")

    return p.return_type()


def visit_call(p: Call, scope, tables):
    func = find_function(str(p.id), tables)
    if func is None:
        ErrorCollector.report("Error: Called undefined function at " + p.position())
        p.set_return_type('')
        return

    p.set_return_type(func.type.type.lower())
    if p.arglist is None and func.params is None:
        return

    if (p.arglist is None and func.params is not None) or (p.arglist is not None and func.params is None) \
            or (len(p.arglist.args) != len(func.params.paramlist)):
        ErrorCollector.report("Error: Called " + str(func.id) + " with wrong number of arguments at " + p.position())
        return

    for (arg, param) in itertools.zip_longest(p.arglist.args, func.params.paramlist):
        visit_expr(arg, scope, tables)
        if arg.return_type() != param[0].type.lower():
            ErrorCollector.report("Warning: Call parameter type mismatch at " + arg.position())


def visit_assign(p: Assign, scope, tables):
    table = find_all_variables(scope, tables)
    entry = find_symbol(str(p.id), table)

    if entry is None:
        ErrorCollector.report("Error: symbol not declared: " + str(p.id) + " at " + p.position())
        return

    visit_expr(p.reval, scope, tables)

    if entry[0] != p.reval.return_type():
        ErrorCollector.report("Warning: Assignment value type mismatch " + entry[0] + " & " + p.reval.return_type() + " at " + p.position())

    if p.assigntype == "non-array":
        if entry[2] is not None:
            ErrorCollector.report("Error: Array access to non-array variable at " + p.position())
    else:
        if entry[2] is None:
            ErrorCollector.report("Error: Non-array access to array variable at " + p.position())

        visit_expr(p.leval, scope, tables)
        if p.leval.return_type() != "int":
            ErrorCollector.report("Warning: Array index is not integer type at " + p.position())


def visit_ifstmt(p: IfStmt, scope, tables, count):
    scope += " - if("+str(count)+")"

    visit_expr(p.conditionexpr, scope, tables)
    if p.conditionexpr.return_type() != "int":
        ErrorCollector.report("Warning: If statement test expr return value is not integer at " + p.position())

    # If
    if_scope = scope + "(if)"
    if p.thenstmt.stmttype == "compoundstmt":
        visit_compoundStmt(p.thenstmt.stmt, if_scope, tables)
    else:
        visit_stmt(p.thenstmt, if_scope, tables)

    # Else
    else_scope = scope + "(else)"
    if p.elsestmt is not None:
        if p.elsestmt.stmttype == "compoundstmt":
            visit_compoundStmt(p.elsestmt.stmt, else_scope, tables)
        else:
            visit_stmt(p.elsestmt, else_scope, tables)


def visit_forstmt(p: ForStmt, scope, tables, count):
    scope += " - for("+str(count)+")"
    visit_expr(p.conditionexpr, scope, tables)
    if p.conditionexpr.return_type() != "int":
        ErrorCollector.report("Warning: For statement test expr return value is not integer at " + p.position())

    visit_assign(p.initial_assign, scope, tables)
    visit_assign(p.assign, scope, tables)

    if p.repeatstmt.stmttype == "compoundstmt":
        visit_compoundStmt(p.repeatstmt.stmt, scope, tables)
    else:
        visit_stmt(p.repeatstmt, scope, tables)


def visit_whilestmt(p: WhileStmt, scope, tables, count):
    scope += " - while("+str(count)+")"
    visit_expr(p.conditionexpr, scope, tables)
    if p.conditionexpr.return_type() != "int":
        ErrorCollector.report("Warning: While statement test expr return value is not integer at " + p.position())

    if p.repeatstmt.stmttype == "compoundstmt":
        visit_compoundStmt(p.repeatstmt.stmt, scope, tables)
    else:
        visit_stmt(p.repeatstmt, scope, tables)


def visit_switchstmt(p: SwitchStmt, scope, tables, count):
    scope += " - switch("+str(count)+")"

    table = find_all_variables(scope, tables)
    entry = find_symbol(str(p.id.id), table)

    if entry is None:
        ErrorCollector.report("Error: symbol not declared: " + str(p.id.id) + " at " + p.position())
    else:
        if entry[0] != "int":
            ErrorCollector.report("Warning: Switch identifier is not integer type at " + p.position())

        if entry[2] is None and p.id.idtype == "array":
            ErrorCollector.report("Error: Array access to non-array variable at " + p.position())
        elif entry[2] is not None and p.id.idtype == "non-array":
            ErrorCollector.report("Error: Non-array access to array variable at " + p.position())

    for (intnum, stmtlist, break_exist) in p.caselist.cases.cases:
        newscope = scope + "case("+str(intnum)+")"
        visit_stmtlist(stmtlist, newscope, tables)
    if p.caselist.default is not None:
        newscope = scope + "defaultcase"
        visit_stmtlist(p.caselist.default.stmtlist, newscope, tables)
