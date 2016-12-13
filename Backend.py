import AST
import SymbolTable
import ErrorCollector
import VR

class Compiler(object):
	def __init__(self, ast, tables):
		self.ast = ast
		self.tables = tables
		self.program = []

	def compile(self) -> str:
		self.area_setup()
		self.global_setup()
		self.program.append('')
		self.function_setup()

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
		for (index, info) in enumerate(global_table.table):
			info.stack_index = index

	def function_setup(self):
		functions = self.ast.FuncList
		if functions is None:
			self.programe.extend([
				'LABEL\tSTART'
				'LABEL\tEND'
				])
		else:
			for function in functions.functions:
				func_name = function.name()

				if func_name == 'main':
					label_start = 'LABEL\tSTART'
					label_end =	'LABEL\tEND'
				else:
					label_start = 'LABEL\tF_START_' + function.name()
					label_end = 'LABEL\tF_END_' + function.name()

				self.program.extend([label_start, label_end])