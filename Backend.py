import AST
import SymbolTable
import ErrorCollector
import VR
import pdb

from collections import defaultdict
from typing import Union

class Compiler(object):
    def __init__(self, ast, tables):
        self.ast = ast
        self.tables = tables
        self.program = []
        self.fp = 0
        self.sp = 0

    def compile(self) -> str:
        self.area_setup()
        self.global_setup()
        self.program.append('')
        self.function_setup()
        self.program.append('')

        return '\n'.join(self.program)

    def area_setup(self):
        self.program.extend([
            'AREA\tFP',
            'AREA\tSP',
            'AREA\tRP',
            'AREA\tVR',
            'AREA\tMEM',
            'AREA\tGLOBAL'
        ])

    def global_setup(self):
        global_table = SymbolTable.find_symbol_table("GLOBAL", self.tables)
        index = 0
        for info in global_table.table:
            if info.role == 'variable':
                info.frame_index = index
                info.is_global = True
                if info.array is None:
                    index += 1
                else:
                    index += info.array

    def main_setup(self):
        self.program.extend([
            'MOVE\t0\tFP',
            'MOVE\t0\tSP',
        ])

    def function_setup(self):
        functions = self.ast.FuncList
        if functions is None:
            self.program.extend([
                'LAB\tSTART'
                'LAB\tEND'
            ])
        else:
            for function in functions.functions:
                func_name = function.name()

                # LABEL
                if func_name == 'main':
                    label_start = 'LAB\tSTART'
                    label_end = 'LAB\tEND'
                else:
                    label_start = 'LAB\tF_START_' + function.name()
                    label_end = 'LAB\tF_END_' + function.name()

                # Parameter position
                func_table = SymbolTable.find_symbol_table(func_name, self.tables)
                param_index = -1
                local_index = 1
                for info in func_table.table:
                    if info.role == 'parameter':
                        info.frame_index = param_index
                        param_index -= 1
                    elif info.role == 'variable':
                        info.frame_index = local_index
                        local_index += 1

                # Add function code
                self.program.append(label_start)
                if func_name == 'main':
                    self.main_setup()
                self.compile_stmtlist(function.comoundstmt.stmtlist, func_name)
                self.program.append(label_end)

    def compile_stmtlist(self, p: Union[AST.StmtList, AST.Stmt], scope: str):
        counts = defaultdict(int)

        if type(p) is AST.Stmt:
            stmts = StmtList()
            stmts.add_stmt(p)
        else:
            stmts = p.stmts

        for stmt in stmts:
            if stmt.stmttype == "assignstmt":
                self.compile_assign(stmt.stmt.assign, scope)
            elif stmt.stmttype == "callstmt":
                self.compile_call(stmt.stmt.call, scope)
            elif stmt.stmttype == "retstmt":
                self.compile_retstmt(stmt.stmt, scope)
            elif stmt.stmttype == "whilestmt":
                counts["while"] += 1
                self.compile_whilestmt(stmt.stmt, scope, counts["while"])
            elif stmt.stmttype == "forstmt":
                counts["for"] += 1
                self.compile_forstmt(stmt.stmt, scope, counts["for"])
            elif stmt.stmttype == "ifstmt":
                counts["if"] += 1
                self.compile_ifstmt(stmt.stmt, scope, counts["if"])
            elif stmt.stmttype == "switchstmt":
                counts["switch"] += 1
                self.compile_switchstmt(stmt.stmt, scope, counts["switch"])
            elif stmt.stmttype == "compoundstmt":
                counts["compound"] += 1
                self.compile_compoundstmt(stmt.stmt, scope, counts["compound"])
            else: # Semicolon case
                continue

    def compile_whilestmt(self, p: AST.WhileStmt, scope: str, count):
        scope_while = scope + " - while("+str(count)+")"
        scope_label = scope_while.replace(' - ', '_')\
                        .translate(str.maketrans('()0123456789', '__abcdefghij'))
        label_start = 'WHILE_START_' + scope_label
        label_end = 'WHILE_END_' + scope_label

        self.program.append('LAB\t' + label_start)
        if p.style == 'while':
            reg_test = self.compile_expr(p.conditionexpr, scope)
            self.program.append('JMPZ\t{}@\t{}'.format(reg_test, label_end))

        if p.repeatstmt.stmttype == "compoundstmt":
            repeatstmt = p.repeatstmt.stmt
        else:
            repeatstmt = AST.StmtList()
            repeatstmt.add_stmt(p.repeatstmt)

        self.compile_compoundstmt(repeatstmt, scope_while, 1)

        if p.style == 'dowhile':
            reg_test = self.compile_expr(p.conditionexpr, scope)
            self.program.append('JMPZ\t{}@\t{}'.format(reg_test, label_end))

        self.program.append('JMP\t' + label_start)
        self.program.append('LAB\t' + label_end)


    def compile_forstmt(self, p: AST.ForStmt, scope: str, count):
        scope_for = scope + " - for("+str(count)+")"
        scope_label = scope_for.replace(' - ', '_')\
                        .translate(str.maketrans('()0123456789', '__abcdefghij'))
        label_start = 'FOR_START_' + scope_label
        label_end = 'FOR_END_' + scope_label

        # inital assign first
        self.compile_assign(p.initial_assign, scope)
        # loop start
        self.program.append('LAB\t' + label_start)

        reg_test = self.compile_expr(p.conditionexpr, scope)
        self.program.append('JMPZ\t{}@\t{}'.format(reg_test, label_end))

        if p.repeatstmt.stmttype == "compoundstmt":
            repeatstmt = p.repeatstmt.stmt
        else:
            repeatstmt = AST.StmtList()
            repeatstmt.add_stmt(p.repeatstmt)

        self.compile_compoundstmt(repeatstmt, scope_for, 1)
        self.compile_assign(p.assign, scope)
        self.program.append('JMP\t' + label_start)
        self.program.append('LAB\t' + label_end)

    def compile_ifstmt(self, p: AST.IfStmt, scope: str, count):
        scope_base = scope + " - if("+str(count)+")"
        label_start = 'IF_START_' + label_style(scope_base)
        label_then = 'IF_THEN_' + label_style(scope_base)
        label_else = 'IF_ELSE_' + label_style(scope_base)
        label_end = 'IF_END_' + label_style(scope_base)

        self.program.append('LAB\t' + label_start)

        # conditional expr
        reg_test = self.compile_expr(p.conditionexpr, scope)

        self.program.extend([
            'JMPZ\t{}@\t{}'.format(reg_test, label_else),
            'JMP\t' + label_then
        ])

        # Then clause body
        self.program.append('LAB\t' + label_then)

        if_scope = scope_base+"(if)"
        if p.thenstmt.stmttype == "compoundstmt":
            thenstmt = p.thenstmt.stmt.stmtlist
        else:
            thenstmt = p.thenstmt.stmt

        self.compile_stmtlist(thenstmt, if_scope)
        self.program.append('JMP\t' + label_end)

        # Else clause body
        self.program.append('LAB\t' + label_else)
        if p.elsestmt is not None:
            else_scope = scope_base+"(else)"

            if p.elsestmt.stmttype == "compoundstmt":
                elsestmt = p.elsestmt.stmt.stmtlist
            else:
                elsestmt = p.elsestmt.stmt

            self.compile_stmtlist(elsestmt, else_scope)
        self.program.append('LAB\t' + label_end)

    def compile_switchstmt(self, p: AST.SwitchStmt, scope: str, count):
        pass

    def compile_compoundstmt(self, p: AST.CompoundStmt, scope: str, count):
        pass

    def compile_assign(self, assign: AST.Assign, scope: str):
        table = SymbolTable.find_all_variables(scope, self.tables)
        info = SymbolTable.find_symbol(str(assign.id), table)
        reg_num = VR.new_reg()
        reg_addr = 'VR({})'.format(reg_num)

        addr = 0
        # store variable index in area to new register
        if info.is_global:
            area = 'GLOBAL'
        else:
            area = 'MEM'
            # store current fp to addr store
            addr += self.fp
        addr += info.frame_index
        self.program.append('MOVE\t{}\t{}'.format(addr, reg_addr))

        if assign.assigntype == 'array':
            reg_level = self.compile_expr(assign.level, scope)
            self.program.append('ADD\t{0}@\t{1}@\t{0}'.format(reg_addr, reg_level))

        # get register address containing value
        reg_reval = self.compile_expr(assign.reval, scope)

        self.program.append('MOVE\t{}@\t{}({}@)'.format(reg_reval, area, reg_addr))

    def compile_call(self, call: AST.Call, scope: str):
        if str(call.id) == 'printf' and call.arglist is not None:
            reg_value = self.compile_expr(call.arglist.args[0], scope)
            self.program.append('WRITE\t{}@'.format(reg_value))

    def compile_retstmt(self, stmt: AST.RetStmt, scope: str):
        reg = self.compile_expr(stmt.expr, scope)
        self.program.append('MOVE\t{}@\tRP'.format(reg))

    def compile_expr(self, expr: AST.Expr, scope: str) -> str:
        # returns register number
        if expr.expr_type == 'intnum':
            reg_num = VR.new_reg()
            reg = 'VR({})'.format(reg_num)
            self.program.append('MOVE\t{}\t{}'.format(expr.operand1, reg))
            return reg
        elif expr.expr_type == 'floatnum':
            reg_num = VR.new_reg()
            reg = 'VR({})'.format(reg_num)
            self.program.append('MOVE\t{}\t{}'.format(expr.operand1, reg))
            return reg
        elif expr.expr_type == 'id':
            table = SymbolTable.find_all_variables(scope, self.tables)
            info = SymbolTable.find_symbol(str(expr.operand1), table)
            reg_num = VR.new_reg()
            reg_addr = 'VR({})'.format(reg_num)

            addr = 0
            # store variable index in area to new register
            if info.is_global:
                area = 'GLOBAL'
            else:
                area = 'MEM'
                # store current fp to addr store
                addr += self.fp
            addr += info.frame_index

            # load value to reg_addr
            self.program.append('MOVE\t{}({})@\t{}'.format(area, addr, reg_addr))
            return reg_addr
        elif expr.expr_type == 'arrayID':
            table = SymbolTable.find_all_variables(scope, self.tables)
            info = SymbolTable.find_symbol(str(expr.idval), table)
            reg_num = VR.new_reg()
            reg_addr = 'VR({})'.format(reg_num)

            addr = 0
            # store variable index in area to new register
            if info.is_global:
                area = 'GLOBAL'
            else:
                area = 'MEM'
                # store current fp to addr store
                addr += self.fp
            addr += info.frame_index
            self.program.append('MOVE\t{}\t{}'.format(addr, reg_addr))

            reg_level = self.compile_expr(expr.idIDX, scope)
            self.program.append('ADD\t{0}@\t{1}@\t{0}'.format(reg_addr, reg_level))

            # load value to reg_addr
            self.program.append('MOVE\t{}({}@)@\t{}'.format(area, reg_addr, reg_addr))
            return reg_addr
        else:
            return -9999

# LABEL allows only alphabets and underscore
def label_style(scope: str) -> str:
    return scope.replace(' - ', '_')\
            .translate(str.maketrans('()0123456789', '__abcdefghij'))
