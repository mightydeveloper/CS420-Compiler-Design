from lexer import lexer
from parser import parser

def testLexer(lexer, read_data):
    lexer.input(read_data)
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)

def testParser(parser, read_data):
    result = parser.parse(read_data, tracking=True)
    print(result)


#files = ["samjo_example0.c"]
files = ["naldo_test1.c", "naldo_test3.c", "naldo_test5.c", "naldo_test7.c", "samjo_example0.c","samjo_example2.c", "naldo_test2.c", "naldo_test4.c", "samjo_example1.c"]
#wrongfiles = ["naldo_test6.c", "samjo_error.c"]
#files = []

directory = "cs420-testcase/"

for filename in files:
    with open(directory+filename, 'r') as f:
        print("Start of ", directory+filename)
        read_data = f.read()

        ## Lex test
        #testLexer(lexer, read_data)

        ## YACC test
        testParser(parser, read_data)
        print("End of", directory+filename)

