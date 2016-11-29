Errors = []

class ErrorInfo(object):
	def __init__(self, level, message, position):
		self.level = level
		self.message = message
		self.position = position


def warn(message, position):
	format_error('Warning', message, position)


def error(message, position):
	format_error('Error', message, position)


def format_error(level, message, position):
	Errors.append(ErrorInfo(level, message, position))


def find_column(input, lexpos):
	last_cr = input.rfind('\n', 0, lexpos)
	if last_cr < 0:
		last_cr = -1
	column = (lexpos - last_cr)
	return column


def inspect(input_data):
	for error in Errors:
		if type(error) is str:
			print(error)
		else:
			line_no, lexpos = error.position
			col_no = find_column(input_data, lexpos)
			print("%s: %s at Line %d, Column %d" % \
				(error.level, error.message, line_no, col_no))


def has_error():
	for error in Errors:
		if error.level == 'Error':
			return True
	return False
