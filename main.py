#!/usr/bin/python
from lexer import lexer
from parser import parser
import sys
import getopt
import logging
from SymbolTable import *
from visitor import *


__author__ = 'Young Seok Kim'
# Student ID : 20121022


def testLexer(lexer, read_data):
    lexer.input(read_data)
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)


def testParser(parser, read_data):
    logging.basicConfig(
        level=logging.DEBUG,
        filename="parselog.txt",
        filemode="w",
        format="%(filename)10s:%(lineno)4d:%(message)s"
    )
    log = logging.getLogger()
    result = parser.parse(read_data, tracking=True, debug=log)
    return result

# #files = ["samjo_example0.c"]
# files = ["naldo_test1.c", "naldo_test3.c", "naldo_test5.c", "naldo_test7.c", "samjo_example0.c","samjo_example2.c", "naldo_test2.c", "naldo_test4.c", "samjo_example1.c"]
# #wrongfiles = ["naldo_test6.c", "samjo_error.c"]
# #files = []

# directory = "cs420-testcase/"
#
# for filename in files:
#     with open(directory+filename, 'r') as f:
#         print("Start of ", directory+filename)
#         read_data = f.read()
#
#         ## Lex test
#         #testLexer(lexer, read_data)
#
#         ## YACC test
#         testParser(parser, read_data)
#         print("End of", directory+filename)





try:
    myopts, args = getopt.getopt(sys.argv[1:], "l:p:s:")
except getopt.GetoptError as e:
    print(str(e))
    print("Usage: %s -l inputFileName.c " % sys.argv[0])
    print("     : %s -p inputFileName.c " % sys.argv[0])
    print("     : %s -s inputFileName.c " % sys.argv[0])
    sys.exit(2)

if not (len(sys.argv) == 3):
    print("Error: invalid arguments")
    print("Usage: %s -l inputFileName.c " % sys.argv[0])
    print("     : %s -p inputFileName.c " % sys.argv[0])
    print("     : %s -s inputFileName.c " % sys.argv[0])
    sys.exit(2)


for option, filename in myopts:
    if option == '-l':
        with open(filename) as f:
            read_data = f.read()
            testLexer(lexer, read_data)
    elif option == '-p':
        with open(filename) as f:
            read_data = f.read()
            result = testParser(parser, read_data)
            with open('tree.txt', 'w') as ASTf:
                ASTf.write(result.printast())
            with open('table.txt', 'w') as Tablef:
                tables = generate_symbol_table(result)
                # Make output string from symbol table list
                outputstr = ""
                for tb in tables:
                    if len(tb.table) == 0:
                        continue
                    outputstr += str(tb) + "\n"
                # Write table information string to the table.txt file
                Tablef.write(outputstr)

            print("parsing done!")
    elif option == '-s':
        with open(filename) as f:
            read_data = f.read()
            result = testParser(parser, read_data)      # result is the root node
            with open('table.txt', 'w') as Tablef:
                tables = generate_symbol_table(result)
                # Make output string from symbol table list
                outputstr = ""
                for tb in tables:
                    if len(tb.table) == 0:
                        continue
                    outputstr += str(tb) + "\n"
                # Write table information string to the table.txt file
                Tablef.write(outputstr)
            visit_program(result, tables)
            ErrorCollector.inspect(read_data)
            if not ErrorCollector.has_error():
                with open('tree.txt', 'w') as ASTf:
                    ASTf.write(result.printast())



        # with open(filename) as f:
        #     read_data = f.read()
        #     result = testParser(parser, read_data)
        #     t = SymbolTable("GLOBAL")
        #     print("Now printing symbol table1")
        #     print(str(t))
        #     print("symboltable done!")


