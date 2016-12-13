reg_index = 0

def new_reg():
	global reg_index
	result = reg_index
	reg_index += 1
	return result
