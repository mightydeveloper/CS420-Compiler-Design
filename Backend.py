import pdb
import re

import AST
import SymbolTable
import ErrorCollector
import VR
import visitor

from collections import defaultdict
from typing import Union

class Compiler(object):
    def __init__(self, ast, tables):
        self.ast = ast
        self.tables = tables
        self.program = []
        # virtual stack pointer used for stack size measurement
        self.vsp = 0

        # stack size per function
        self.stack_sizes = {}

    def compile(self) -> str:
        self.area_setup()
        self.global_setup()
        self.program.append('')
        self.function_setup()
        self.program.append('')
        self.return_phase_setup()

        # set proper stack pointer
        if 'main' in self.stack_sizes:
            sp = self.stack_sizes['main']
            sp_cmd = 'MOVE\t0\tSP'
            sp_index = self.program.index(sp_cmd)
            self.program.insert(sp_index, 'MOVE\t{}\tSP'.format(sp))
            self.program.remove(sp_cmd)

        # set proper stack size
        for i in range(len(self.program)):
            match = re.search('ADD\t([A-Za-z][A-Za-z0-9_]*)\tSP@\tSP', self.program[i])
            if match is not None:
                func_name = match.groups()[0]
                self.program[i] = 'ADD\t{}\tSP@\tSP'.format(self.stack_sizes[func_name])
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
                if info.array is None:
                    index += 1
                else:
                    index += info.array

    def local_setup(self, scope: str):
        local_table = SymbolTable.find_symbol_table(scope, self.tables)
        if local_table is None:
            return

        for info in local_table.table:
            if info.role == 'variable':
                self.vsp += 1
                info.frame_index = self.vsp
                if info.array is not None:
                    self.vsp += info.array - 1

    def main_setup(self):
        self.program.extend([
            'MOVE\t0\tFP',
            'MOVE\t0\tSP',
            'MOVE\t0\tMEM',
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
                # reset virtual stack
                self.vsp = 0
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

                local_index = 0
                for info in func_table.table:
                    if info.role == 'variable':
                        local_index += 1
                        info.frame_index = local_index
                        if info.array is not None:
                            local_index += info.array - 1
                self.vsp += local_index

                # FP(-1) is reserved for return addr
                param_index = -1
                for info in reversed(func_table.table):
                    if info.role == 'parameter':
                        if info.array is None:
                            param_index -= 1
                        else:
                            param_index -= info.array
                        info.frame_index = param_index

                # Add function code
                self.program.append(label_start)
                if func_name == 'main':
                    self.main_setup()
                self.compile_stmtlist(function.comoundstmt.stmtlist, func_name)
                if func_name == 'main':
                    self.program.append('LAB\tEXIT')
                self.program.append(label_end)
                self.stack_sizes[func_name] = self.vsp

    def return_phase_setup(self):
        reg_return = 'VR({})'.format(VR.new_reg())
        self.program.extend([
            'LAB\tRETURN_PHASE',
            'JMPZ\tFP@\tEXIT',
            'MOVE\tFP@\tSP',
            'MOVE\tMEM(FP@)@\tFP',
            'SUB\tSP@\t1\tSP',
            'JMP\tMEM(SP@)@',
            ''
        ])

    def compile_stmtlist(self, p: Union[AST.StmtList, AST.Stmt], scope: str):
        counts = defaultdict(int)

        if type(p) is AST.Stmt:
            stmts = [p]
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
        scope_label = label_style(scope_while)
        label_start = 'WHILE_START_' + scope_label
        label_end = 'WHILE_END_' + scope_label

        self.program.append('LAB\t' + label_start)
        if p.style == 'while':
            reg_test = self.compile_expr(p.conditionexpr, scope)
            self.program.append('JMPZ\t{}@\t{}'.format(reg_test, label_end))

        if p.repeatstmt.stmttype == "compoundstmt":
            self.local_setup(scope_while)
            repeatstmt = p.repeatstmt.stmt.stmtlist
        else:
            repeatstmt = p.repeatstmt

        self.compile_stmtlist(repeatstmt, scope_while)

        if p.style == 'dowhile':
            reg_test = self.compile_expr(p.conditionexpr, scope)
            self.program.append('JMPZ\t{}@\t{}'.format(reg_test, label_end))

        self.program.append('JMP\t' + label_start)
        self.program.append('LAB\t' + label_end)


    def compile_forstmt(self, p: AST.ForStmt, scope: str, count):
        scope_for = scope + " - for("+str(count)+")"
        scope_label = label_style(scope_for)
        label_start = 'FOR_START_' + scope_label
        label_end = 'FOR_END_' + scope_label

        # inital assign first
        self.compile_assign(p.initial_assign, scope)
        # loop start
        self.program.append('LAB\t' + label_start)

        reg_test = self.compile_expr(p.conditionexpr, scope)
        self.program.append('JMPZ\t{}@\t{}'.format(reg_test, label_end))

        if p.repeatstmt.stmttype == "compoundstmt":
            self.local_setup(scope_for)
            repeatstmt = p.repeatstmt.stmt.stmtlist
        else:
            repeatstmt = p.repeatstmt

        self.compile_stmtlist(repeatstmt, scope_for)
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
            self.local_setup(if_scope)
            thenstmt = p.thenstmt.stmt.stmtlist
        else:
            thenstmt = p.thenstmt

        self.compile_stmtlist(thenstmt, if_scope)
        self.program.append('JMP\t' + label_end)

        # Else clause body
        self.program.append('LAB\t' + label_else)
        if p.elsestmt is not None:
            else_scope = scope_base+"(else)"

            if p.elsestmt.stmttype == "compoundstmt":
                self.local_setup(else_scope)
                elsestmt = p.elsestmt.stmt.stmtlist
            else:
                elsestmt = p.elsestmt

            self.compile_stmtlist(elsestmt, else_scope)
        self.program.append('LAB\t' + label_end)

    def compile_switchstmt(self, p: AST.SwitchStmt, scope: str, count):
        scope_switch = scope + " - switch("+str(count)+")"
        label_start = 'SWITCH_START_' + label_style(scope)
        label_default = 'SWITCH_DEFAULT_' + label_style(scope)
        label_end = 'SWITCH_END_' + label_style(scope)

        # load id value
        if p.id.idtype == 'array':
            id_expr = AST.Expr('arrayID', idval=p.id.id,
                                idIDX=AST.Expr('intnum', operand1=p.id.intnum))
        else:
            id_expr = AST.Expr('id', operand1=p.id.id)

        reg_id = self.compile_expr(id_expr, scope)

        reg_test = 'VR({})'.format(VR.new_reg())

        # branching table first
        for (intnum, _, _) in p.caselist.cases.cases:
            scope_case = scope_switch + "case("+str(intnum)+")"
            label_case = 'SWITCH_CASE_' + label_style(scope_case+str(intnum))
            self.program.extend([
                'MOVE\t{}\t{}'.format(intnum, reg_test),
                'SUB\t{0}@\t{1}@\t{0}'.format(reg_test, reg_id),
                'JMPZ\t{}@\t{}'.format(reg_test, label_case)
            ])

        if p.caselist.default is None:
            self.program.append('JMP\t' + label_end)
        else:
            self.program.append('JMP\t' + label_default)

        # case body
        for (intnum, stmtlist, break_exist) in p.caselist.cases.cases:
            scope_case = scope_switch + "case("+str(intnum)+")"
            label_case = 'SWITCH_CASE_' + label_style(scope_case+str(intnum))
            self.program.append('LAB\t' + label_case)
            self.compile_stmtlist(stmtlist, scope_case)
            if break_exist:
                self.program.append('JMP\t' + label_end)

        if p.caselist.default is not None:
            self.program.append('LAB\t' + label_default)
            scope_default = scope_switch + "defaultcase"
            self.compile_stmtlist(p.caselist.default.stmtlist, scope_default)
            if p.caselist.default.break_exist:
                self.program.append('JMP\t' + label_end)

        self.program.append('LAB\t' + label_end)

    def compile_compoundstmt(self, p: AST.CompoundStmt, scope: str, count):
        scope += " - compound(" + str(count) + ")"
        self.local_setup(scope)
        self.compile_stmtlist(p.stmtlist, scope)

    def compile_assign(self, assign: AST.Assign, scope: str):
        table = SymbolTable.find_all_variables(scope, self.tables)
        info = SymbolTable.find_symbol(str(assign.id), table)
        reg_num = VR.new_reg()
        reg_addr = 'VR({})'.format(reg_num)

        # store variable index in area to new register
        if info.is_global:
            area = 'GLOBAL'
        else:
            area = 'MEM'

        self.program.append('MOVE\tFP@\t{}'.format(reg_addr))
        self.program.append('ADD\t{0}@\t{1}\t{0}'.format(reg_addr, info.frame_index))

        if assign.assigntype == 'array':
            reg_leval = self.compile_expr(assign.leval, scope)
            self.program.append('ADD\t{0}@\t{1}@\t{0}'.format(reg_addr, reg_leval))

        # get register address containing value
        reg_reval = self.compile_expr(assign.reval, scope)

        self.program.append('MOVE\t{}@\t{}({}@)'.format(reg_reval, area, reg_addr))

    def compile_call(self, call: AST.Call, scope: str):
        func_name = str(call.id)

        if func_name == 'printf':
            reg_value = self.compile_expr(call.arglist.args[0], scope)
            self.program.append('WRITE\t{}@'.format(reg_value))

        elif func_name == 'scanf':
            # Find argment symbol
            table = SymbolTable.find_all_variables(scope, self.tables)
            param = call.arglist.args[0]
            if param.expr_type == 'arrayID':
                info = SymbolTable.find_symbol(str(param.idval), table)
            else:
                info = SymbolTable.find_symbol(str(param.operand1), table)

            # read to buffer register
            reg_buf = 'VR({})'.format(VR.new_reg())
            if info.symtype in ['int', 'INT']:
                self.program.append('READI\t' + reg_buf)
            else:
                self.program.append('READF\t' + reg_buf)

            # store variable index in area to new register
            if info.is_global:
                area = 'GLOBAL'
            else:
                area = 'MEM'

            # get variable address
            reg_addr = 'VR({})'.format(VR.new_reg())
            self.program.append('MOVE\tFP@\t{}'.format(reg_addr))
            self.program.append('ADD\t{0}@\t{1}\t{0}'.format(reg_addr, info.frame_index))

            if param.expr_type == 'arrayID':
                reg_leval = self.compile_expr(param.idIDX, scope)
                self.program.append('ADD\t{0}@\t{1}@\t{0}'.format(reg_addr, reg_leval))

            # store value to memory
            self.program.append('MOVE\t{}@\t{}({}@)'.format(reg_buf, area, reg_addr))
        else:
            func_def = SymbolTable.find_function(func_name, self.tables)
            label_return = 'RETURN_{}'.format(call.line_position[1])

            self.program.append('ADD\t1\tSP@\tSP')
            for (arg, spec) in zip(call.arglist.args, func_def.params.paramlist):
                reg_val = self.compile_expr(arg, scope)
                ident = spec[1]
                if ident.idtype == 'array':
                    # Get address parsing string register address
                    first_index = int(re.search('([0-9]+)', reg_val).groups()[0])
                    for i in range(ident.intnum):
                        self.program.append('MOVE\tVR({})@\tMEM(SP@)'.format(first_index + i))
                        self.program.append('ADD\t1\tSP@\tSP')
                else:
                    self.program.append('MOVE\t{}@\tMEM(SP@)'.format(reg_val))
                    self.program.append('ADD\t1\tSP@\tSP')
            self.program.extend([
                'MOVE\t{}\tMEM(SP@)'.format(label_return),
                'ADD\t1\tSP@\tSP',
                'MOVE\tFP@\tMEM(SP@)',
                'MOVE\tSP@\tFP',
                'ADD\t{}\tSP@\tSP'.format(func_name), # changed at compile step
                'JMP\tF_START_' + func_name,
                'LAB\t' + label_return
            ])


    def compile_retstmt(self, stmt: AST.RetStmt, scope: str):
        reg = self.compile_expr(stmt.expr, scope)
        self.program.append('MOVE\t{}@\tRP'.format(reg))
        self.program.append('JMP\tRETURN_PHASE')

    def compile_expr(self, expr: Union[AST.Expr, AST.TypeCast], scope: str, recursion=False) -> str:
        if not recursion:
            visitor.visit_expr(expr, scope, self.tables)

        # returns register number
        if type(expr) == AST.TypeCast:
            reg = self.compile_expr(expr.expr, scope, True)
            if expr.cast_type == 'int':
                self.program.append('F2I\t{0}@\t{0}'.format(reg))
            else:
                self.program.append('I2F\t{0}@\t{0}'.format(reg))
            return reg
        elif expr.expr_type == 'intnum':
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

            # store variable index in area to new register
            if info.is_global:
                area = 'GLOBAL'
            else:
                area = 'MEM'

            self.program.append('MOVE\tFP@\t{}'.format(reg_addr))
            self.program.append('ADD\t{0}@\t{1}\t{0}'.format(reg_addr, info.frame_index))

            # load value to reg_addr
            self.program.append('MOVE\t{}({}@)@\t{}'.format(area, reg_addr, reg_addr))
            return reg_addr
        elif expr.expr_type == 'arrayID':
            table = SymbolTable.find_all_variables(scope, self.tables)
            info = SymbolTable.find_symbol(str(expr.idval), table)
            reg_num = VR.new_reg()
            reg_addr = 'VR({})'.format(reg_num)

            # store variable index in area to new register
            if info.is_global:
                area = 'GLOBAL'
            else:
                area = 'MEM'

            self.program.append('MOVE\tFP@\t{}'.format(reg_addr))
            self.program.append('ADD\t{0}@\t{1}\t{0}'.format(reg_addr, info.frame_index))

            reg_leval = self.compile_expr(expr.idIDX, scope, True)
            self.program.append('ADD\t{0}@\t{1}@\t{0}'.format(reg_addr, reg_leval))

            # load value to reg_addr
            self.program.append('MOVE\t{}({}@)@\t{}'.format(area, reg_addr, reg_addr))
            return reg_addr
        elif expr.expr_type == 'paren':
            reg = self.compile_expr(expr.operand1, scope, True)
            return reg
        elif expr.expr_type == 'unop':
            reg = self.compile_expr(expr.operand1, scope, True)
            if expr.return_type() == 'int':
                self.program.append('MUL\t-1\t{0}@\t{0}'.format(reg))
            else:
                self.program.append('FMUL\t-1.0\t{0}@\t{0}'.format(reg))
            return reg
        elif expr.expr_type == 'binop' and expr.operator in ['+', '-', '*', '/']:
            reg_out = 'VR({})'.format(VR.new_reg())
            reg_lhs = self.compile_expr(expr.operand1, scope, True)
            reg_rhs = self.compile_expr(expr.operand2, scope, True)

            if expr.return_type() == 'int':
                type_prefix = ''
            elif expr.return_type() == 'float':
                type_prefix = 'F'
            else:
                raise Exception('Expr return type unknown')

            if expr.operator == '+':
                op = 'ADD'
            elif expr.operator == '-':
                op = 'SUB'
            elif expr.operator == '*':
                op = 'MUL'
            elif expr.operator == '/':
                op = 'DIV'
            else:
                op = ''
                raise Exception('Expr operator is wrong: ' + expr.operator)

            self.program.append('{}{}\t{}@\t{}@\t{}'.format(type_prefix, op, reg_lhs, reg_rhs, reg_out))
            return reg_out
        elif expr.expr_type == 'binop' and expr.operator in ['==', '!=', '>=', '>', '<', '<=']:
            reg_out = 'VR({})'.format(VR.new_reg())
            reg_lhs = self.compile_expr(expr.operand1, scope, True)
            reg_rhs = self.compile_expr(expr.operand2, scope, True)

            label_true = 'COMP_TRUE_' + label_style(reg_out)
            label_false = 'COMP_FALSE_' + label_style(reg_out)
            label_end = 'COMP_END_' + label_style(reg_out)

            if expr.operand1.return_type() == 'int':
                op = 'SUB'
            elif expr.operand1.return_type() == 'float':
                op = 'FSUB'
            else:
                raise Exception('Expr return type unknown')

            self.program.append('{}\t{}@\t{}@\t{}'.format(op, reg_lhs, reg_rhs, reg_out))

            if expr.operator == '==':
                self.program.extend([
                    'JMPZ\t{}@\t{}'.format(reg_out, label_true),
                    'JMP\t' + label_false
                ])
            elif expr.operator == '!=':
                self.program.extend([
                    'JMPZ\t{}@\t{}'.format(reg_out, label_false),
                    'JMP\t' + label_true
                ])
            elif expr.operator == '>=':
                self.program.extend([
                    'JMPZ\t{}@\t{}'.format(reg_out, label_true),
                    'JMPN\t{}@\t{}'.format(reg_out, label_false),
                    'JMP\t' + label_true
                ])
            elif expr.operator == '>':
                self.program.extend([
                    'JMPZ\t{}@\t{}'.format(reg_out, label_false),
                    'JMPN\t{}@\t{}'.format(reg_out, label_false),
                    'JMP\t' + label_true
                ])
            elif expr.operator == '<':
                self.program.extend([
                    'JMPZ\t{}@\t{}'.format(reg_out, label_false),
                    'JMPN\t{}@\t{}'.format(reg_out, label_true),
                    'JMP\t' + label_false
                ])
            elif expr.operator == '<=':
                self.program.extend([
                    'JMPZ\t{}@\t{}'.format(reg_out, label_true),
                    'JMPN\t{}@\t{}'.format(reg_out, label_true),
                    'JMP\t' + label_false
                ])
            else:
                op = ''
                raise Exception('Expr operator is wrong: ' + expr.operator)

            self.program.extend([
                'LAB\t' + label_true,
                'MOVE\t1\t' + reg_out,
                'JMP\t' + label_end,
                'LAB\t' + label_false,
                'MOVE\t0\t' + reg_out,
                'LAB\t' + label_end
            ])
            return reg_out
        elif expr.expr_type == 'call':
            self.compile_call(expr.operand1, scope)
            reg_out = 'VR({})'.format(VR.new_reg())
            self.program.append('MOVE\tRP@\t' + reg_out)
            return reg_out
        else:
            return -9999

# LABEL allows only alphabets and underscore
def label_style(scope: str) -> str:
    return scope.replace(' - ', '_')\
            .translate(str.maketrans('()0123456789', '__abcdefghij'))
