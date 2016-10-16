## Yacc (Parser) implementation
## 20121022 Young Seok Kim


import ply.yacc as yacc
from lexer import tokens


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
    pass

def p_decllist(p):
    """ decllist : declaration
                 | decllist declaration
    """
    pass

def p_funclist(p):
    """ funclist : function
                 | funclist function
    """
    pass

def p_declaration(p):
    """ declaration : type identlist SEMI
    """
    pass

def p_identlist(p):
    """ identlist : identifier
                  | identlist COMMA identifier
    """
    pass

def p_identifier(p):
    """ identifier : ID
                   | ID LBRACKET INTNUM RBRACKET
    """
    pass

def p_function(p):
    """ function : type ID LPAREN RPAREN compoundstmt
                 | type ID LPAREN paramlist RPAREN compoundstmt
    """
    pass

def p_paramlist(p):
    """ paramlist : type identifier
                  | paramlist COMMA type identifier
    """
    pass

def p_type(p):
    """ type : INT
             | FLOAT
    """
    pass

def p_compoundstmt(p):
    """ compoundstmt : LBRACE decllist stmtlist RBRACE
                     | LBRACE stmtlist RBRACE
    """
    pass

def p_stmtlist(p):
    """ stmtlist : stmtlist stmt
                 | empty
    """
    pass

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
    pass

def p_assignstmt(p):
    """ assignstmt : assign SEMI
    """
    pass

def p_assign(p):
    """ assign : ID LBRACKET expr RBRACKET ASSIGN expr
               | ID ASSIGN expr
    """
    pass

def p_callstmt(p):
    """ callstmt : call SEMI
    """
    pass

def p_call(p):
    """ call : ID LPAREN arglist RPAREN %prec FUNC
             | ID LPAREN RPAREN %prec FUNC
    """
    pass

def p_retstmt(p):
    """ retstmt : RETURN expr SEMI
                | RETURN SEMI
    """
    pass

def p_whilestmt(p):
    """ whilestmt : WHILE LPAREN expr RPAREN stmt
                  | DO stmt WHILE LPAREN expr RPAREN SEMI
    """
    pass

def p_forstmt(p):
    """ forstmt : FOR LPAREN assign SEMI expr SEMI assign RPAREN stmt
    """
    pass

def p_ifstmt(p):
    """ ifstmt : IF LPAREN expr RPAREN stmt %prec ONLYIF
               | IF LPAREN expr RPAREN stmt ELSE stmt
    """
    pass

def p_switchstmt(p):
    """ switchstmt : SWITCH LPAREN identifier RPAREN LBRACE caselist RBRACE
    """
    pass

def p_caselist(p):
    """ caselist : case default
    """
    pass

def p_case(p):
    """ case : case CASE INTNUM COLON stmtlist BREAK SEMI
             | case CASE INTNUM COLON stmtlist
             | empty
    """
    pass

def p_default(p):
    """ default : DEFAULT COLON stmtlist BREAK SEMI
                | DEFAULT COLON stmtlist
                | empty
    """
    pass

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
    pass

def p_unop(p):
    """ unop : MINUS
    """

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
    pass


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


# Build the parser
parser = yacc.yacc(start='program')