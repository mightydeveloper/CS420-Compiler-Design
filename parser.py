## Yacc (Parser) implementation
## 20121022 Young Seok Kim

import AST
import ply.yacc as yacc
from lexer import tokens
import logging

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")
    print("p :", p.value, p.type, p.lineno)
    parser.errok()

## Grammar productions
# This is equivalent to epsilon
def p_empty(p):
    """ empty :
    """
    pass


def p_program(p):
    """ program : decllist funclist
                | decllist
                | funclist
                | empty
    """
    if len(p) == 3:
        p[0] = AST.Program(p[1], p[2])
    else:
        if isinstance(p[1], AST.DecList):
            p[0] = AST.Program(p[1])
        elif isinstance(p[1], AST.FuncList):
            p[0] = AST.Program(None, p[1])
        else:
            p[0] = AST.Program()


def p_decllist(p):
    """ decllist : declaration
                 | decllist declaration
    """
    # TODO : not sure if p[1] will be evaluated first
    if len(p) == 2:
        p[0] = AST.DecList()
        p[0].add_decl(p[1])
    else:
        p[1].add_decl(p[2])
        p[0] = p[1]


def p_funclist(p):
    """ funclist : function
                 | funclist function
    """
    # TODO : not sure if p[1] will be evaluated first
    if len(p) == 2:
        p[0] = AST.FuncList()
        p[0].add_function(p[1])
    else:
        p[1].add_function(p[2])
        p[0] = p[1]


def p_declaration(p):
    """ declaration : type identlist SEMI
    """
    p[0] = AST.Declaration(p[1], p[2])


def p_identlist(p):
    """ identlist : identifier
                  | identlist COMMA identifier
    """
    if len(p) == 2:
        p[0] = AST.IdentList([p[1]])
    else:
        p[1].add_identifier(p[3])
        p[0] = p[1]


def p_identifier(p):
    """ identifier : ID
                   | ID LBRACKET INTNUM RBRACKET
    """
    if len(p) == 2:
        p[0] = AST.Identifier(p[1])
    else:
        p[0] = AST.Identifier(p[1], p[3], idtype="array")


def p_function(p):
    """ function : type ID LPAREN RPAREN compoundstmt
                 | type ID LPAREN paramlist RPAREN compoundstmt
    """
    if len(p) == 6:
        p[0] = AST.Function(p[1], p[2], p[5])
    else:
        p[0] = AST.Function(p[1], p[2], p[6], p[4])


def p_paramlist(p):
    """ paramlist : type identifier
                  | paramlist COMMA type identifier
    """
    if len(p) == 3:
        p[0] = AST.ParamList()
        p[0].addparam(p[1], p[2])
    else:
        p[1].addparam(p[3], p[4])
        p[0] = p[1]


def p_type(p):
    """ type : INT
             | FLOAT
    """
    if p[1] == "int":
        p[0] = AST.Type("INT")
    elif p[1] == "float":
        p[0] = AST.Type("FLOAT")
    else:
        print("Error in p_type!!!")


def p_compoundstmt(p):
    """ compoundstmt : LBRACE decllist stmtlist RBRACE
                     | LBRACE stmtlist RBRACE
    """
    if len(p) == 5:
        p[0] = AST.CompoundStmt(p[3], p[2])
    else:
        p[0] = AST.CompoundStmt(p[2])


def p_stmtlist(p):
    """ stmtlist : stmtlist stmt
                 | empty
    """
    if len(p) == 3:
        p[1].add_stmt(p[2])
        p[0] = p[1]
    else:
        p[0] = AST.StmtList()


def p_stmt(p):
    """ stmt : assignstmt
             | callstmt
             | retstmt
             | whilestmt
             | forstmt
             | ifstmt
             | switchstmt
             | compoundstmt
             | SEMI
    """
    if p[1] == ";":
        p[0] = AST.Semi()
    else:
        p[0] = p[1]


def p_assignstmt(p):
    """ assignstmt : assign SEMI
    """
    p[0] = AST.AssignStmt(p[1])


def p_assign(p):
    """ assign : ID LBRACKET expr RBRACKET ASSIGN expr
               | ID ASSIGN expr
    """
    if len(p) == 7:
        p[0] = AST.Assign("array", p[1], p[6], leval=p[3])
    else:
        p[0] = AST.Assign("non-array", p[1], p[3])


def p_callstmt(p):
    """ callstmt : call SEMI
    """
    p[0] = AST.CallStmt(p[1])


def p_call(p):
    """ call : ID LPAREN arglist RPAREN %prec FUNC
             | ID LPAREN RPAREN %prec FUNC
    """
    if len(p) == 5:
        p[0] = AST.Call(p[1], p[3])
    else:
        p[0] = AST.Call(p[1])


def p_retstmt(p):
    """ retstmt : RETURN expr SEMI
                | RETURN SEMI
    """
    if len(p) == 4:
        p[0] = AST.RetStmt(p[2])
    else:
        p[0] = AST.RetStmt()


def p_whilestmt(p):
    """ whilestmt : WHILE LPAREN expr RPAREN stmt
                  | DO stmt WHILE LPAREN expr RPAREN SEMI
    """
    if len(p) == 6:
        p[0] = AST.WhileStmt("while", p[3], p[5])
    else:
        p[0] = AST.WhileStmt("dowhile", p[5], p[2])


def p_forstmt(p):
    """ forstmt : FOR LPAREN assign SEMI expr SEMI assign RPAREN stmt
    """
    p[0] = AST.ForStmt(p[3], p[5], p[7], p[9])


def p_ifstmt(p):
    """ ifstmt : IF LPAREN expr RPAREN stmt %prec ONLYIF
               | IF LPAREN expr RPAREN stmt ELSE stmt
    """
    if len(p) == 6:
        p[0] = AST.IfStmt(p[3], p[5])
    else:
        p[0] = AST.IfStmt(p[3], p[5], p[7])


def p_switchstmt(p):
    """ switchstmt : SWITCH LPAREN identifier RPAREN LBRACE caselist RBRACE
    """
    p[0] = AST.SwitchStmt(p[3], p[6])


def p_caselist(p):
    """ caselist : case default
    """
    p[0] = AST.CaseList(p[1], p[2])


def p_case(p):
    """ case : case CASE INTNUM COLON stmtlist BREAK SEMI
             | case CASE INTNUM COLON stmtlist
             | empty
    """
    if len(p) == 8:
        p[1].add_case(p[3], p[5], True)
        p[0] = p[1]
    elif len(p) == 6:
        p[1].add_case(p[3], p[5])
        p[0] = p[1]
    else:
        p[0] = AST.Case()


def p_default(p):
    """ default : DEFAULT COLON stmtlist BREAK SEMI
                | DEFAULT COLON stmtlist
                | empty
    """
    if len(p) == 6:
        p[0] = AST.CaseDefault(p[3], break_exist=True)
    elif len(p) == 4:
        p[0] = AST.CaseDefault(p[3])
    else:
        p[0] = None


def p_expr(p):
    """ expr : unop expr %prec UNOP
             | expr EQ expr
             | expr NE expr
             | expr LT expr
             | expr LE expr
             | expr GT expr
             | expr GE expr
             | expr PLUS expr
             | expr MINUS expr
             | expr TIMES expr
             | expr DIVIDE expr
             | call
             | INTNUM
             | FLOATNUM
             | ID
             | ID LBRACKET expr RBRACKET
             | LPAREN expr RPAREN
    """
    if len(p) == 5:
        p[0] = AST.Expr("arrayID", idval=p[1], idIDX=p[3])
    elif len(p) == 4:
        if p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = AST.Expr("binop", operator=p[2], operand1=p[1], operand2=p[3])
    elif len(p) == 3:
        p[0] = AST.Expr("unop", operand1=p[2])
    elif len(p) == 2:
        if (isinstance(p[1], AST.Call)):
            p[0] = AST.Expr("call", operand1=p[1])
        elif (isinstance(p[1], int)):
            p[0] = AST.Expr('intnum', operand1=p[1])
        elif (isinstance(p[1], float)):
            p[0] = AST.Expr("floatnum", operand1=p[1])
        else: # ID case
            p[0] = AST.Expr("id", operand1=p[1])


def p_unop(p):
    """ unop : MINUS
    """
    p[0] = p[1]

# def p_binop(p):
#     """ binop : PLUS
#               | MINUS
#               | TIMES
#               | DIVIDE
#               | LT
#               | LE
#               | GT
#               | GE
#               | EQ
#               | NE
#     """
#     pass

def p_arglist(p):
    """ arglist : expr
                | arglist COMMA expr
    """
    if len(p) == 2:
        p[0] = AST.ArgList(p[1])
    else:
        p[1].addarg(p[3])
        p[0] = p[1]


# Within the precedence declaration, tokens are ordered from lowest to highest precedence
precedence = (
    ('nonassoc', 'ONLYIF'),                 # else has more precedence then only if
    ('nonassoc', 'ELSE'),
    ('right', 'ASSIGN'),                    # Assignment
    ('left', 'EQ', 'NE'),                   # Equality operators
    ('left', 'LT', 'LE', 'GT', 'GE'),       # Relational operators
    ('left', 'PLUS', 'MINUS'),              # Addition and Subtraction
    ('left', 'TIMES', 'DIVIDE'),            # Multiplication and division
    ('right', 'UNOP'),                      # Unary minus
    ('left', 'FUNC'),                       # Function call
)

# logging.basicConfig(
#     level = logging.DEBUG,
#     filename = "parselog.txt",
#     filemode = "w",
#     format = "%(filename)10s:%(lineno)4d:%(message)s"
# )
# log = logging.getLogger()

# Build the parser
parser = yacc.yacc(start='program', debug=True)
