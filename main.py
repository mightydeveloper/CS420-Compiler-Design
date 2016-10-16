from lexer import MiniCLexer
from parser import MiniCParser

lexer = MiniCLexer()
lexer.build()

parser = MiniCParser()

files = ["samjo_example0.c"]
#files = ["naldo_test1.c", "naldo_test3.c", "naldo_test5.c", "naldo_test7.c", "samjo_example0.c",
#         "samjo_example2.c", "naldo_test2.c", "naldo_test4.c", "naldo_test6.c", "samjo_error.c", "samjo_example1.c"]
directory = "cs420-testcase/"
for filename in files:
    with open(directory+filename, 'r') as f:
        read_data = f.read()
        ## LEXER tokernizer test
        # print(directory+filename, "file opend!")
        # lexer.input(read_data)
        # lexer.printTokens()
        # print(directory+filename, "File done!\n")

        ## YACC test
        res = parser.parse(read_data)
        print(res)


