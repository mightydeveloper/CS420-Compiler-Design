import AST
import SymbolTable
import ErrorCollector
import VR
import pdb

from collections import defaultdict

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

    def compile_stmtlist(self, p: AST.StmtList, scope: str):
        counts = defaultdict(int)

        for stmt in p.stmts:
            if stmt.stmttype == "assignstmt":
                self.compile_assign(stmt.stmt.assign, scope)
            elif stmt.stmttype == "callstmt":
                self.compile_call(stmt.stmt.call, scope)
            elif stmt.stmttype == "retstmt":
                self.compile_retstmt(stmt.stmt, scope)
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
