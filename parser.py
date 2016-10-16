import ply.yacc as yacc

#from ply.plyparser import PLYParser, Coord, ParseError

class MiniCParser(object):

    ## Grammar productions
    # This is equivalent to epsilon
    def p_empty(self, p):
        """ empty :
        """
        pass

    def p_program(self, p):
        """ program : decllist funclist
                    | decllist
                    | funclist
                    | empty
        """
        pass

    def p_decllist(self, p):
        """ decllist : declaration
                     | decllist declaration
        """
        pass

    def p_funclist(self,p):
        """ funclist : function
                     | funclist function
        """
        pass

    def p_declaration(self, p):
        """ declaration : type identlist SEMI
        """
        pass

    def p_identlist(self, p):
        """ identlist : identifier
                      | identlist COMMA identifier
        """
        pass

    def p_identifier(self, p):
        """ identifier : ID
                       | ID LBRACKET INTNUM RBRACKET
        """
        pass

    def p_function(self, p):
        """ function : type ID LPAREN RPAREN compoundstmt
                     | type ID LPAREN paramlist RPAREN compoundstmt
        """
        pass

    def p_paramlist(self, p):
        """ paramlist : type identifier
                      | paramlist COMMA type identifier
        """
        pass

    def p_type(self, p):
        """ type : INT
                 | FLOAT
        """
        pass

    def p_compoundstmt(self, p):
        """ compoundstmt : LBRACE decllist stmtlist RBRACE
                         | LBRACE stmtlist RBRACE
        """
        pass

    def p_stmtlist(self, p):
        """ stmtlist : stmtlist stmt
                     | empty
        """
        pass

    def p_stmt(self, p):
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

    def p_assignstmt(self, p):
        """ assignstmt : assign SEMI
        """
        pass

    def p_assign(self, p):
        """ assign : ID LBRACKET expr RBRACKET ASSIGN expr
                   | ID ASSIGN expr
        """
        pass

    def p_callstmt(self, p):
        """ callstmt : call SEMI
        """
        pass

    def p_call(self, p):
        """ call : ID LPAREN arglist RPAREN
                 | ID LPAREN RPAREN
        """
        pass

    def p_retstmt(self, p):
        """ retstmt : RETURN expr SEMI
                    | RETURN SEMI
        """
        pass

    def p_whilestmt(self, p):
        """ whilestmt : WHILE LPAREN expr RPAREN stmt
                      | DO stmt WHILE LPAREN expr RPAREN SEMI
        """
        pass

    def p_forstmt(self, p):
        """ forstmt : FOR LPAREN assign SEMI expr SEMI assign RPAREN stmt
        """
        pass

    def p_ifstmt(self, p):
        """ ifstmt : IF LPAREN expr RPAREN stmt ELSE stmt
                   | IF LPAREN expr RPAREN stmt
        """
        pass

    def p_switchstmt(self, p):
        """ switchstmt : SWITCH LPAREN identifier RPAREN LBRACKET caselist RBRACKET
        """
        pass

    def p_caselist(self, p):
        """ caselist : case default
        """
        pass

    def p_case(self, p):
        """ case : case CASE INTNUM COLON stmtlist BREAK SEMI
                 | case CASE INTNUM COLON stmtlist
                 | empty
        """
        pass

    def p_default(self, p):
        """ default : DEFAULT COLON stmtlist BREAK SEMI
                    | DEFAULT COLON stmtlist
                    | empty
        """
        pass

    def p_expr(self, p):
        """ expr : UNOP expr
                 | expr binop expr
                 | call
                 | INTNUM
                 | FLOATNUM
                 | ID
                 | ID LBRACKET expr RBRACKET
                 | LPAREN expr RPAREN
        """
        pass

    def p_binop(self, p):
        """ binop : PLUS
                  | MINUS
                  | TIMES
                  | DIVIDE
                  | LT
                  | LE
                  | GT
                  | GE
                  | EQ
                  | NE
        """
        pass


    def p_arglist(self, p):
        """ arglist : expr
                    | arglist COMMA expr
        """
        pass


    # Within the precedence declaration, tokens are ordered from lowest to highest precedence
    precedence = (
        ('right', 'ASSIGN'),                    # Assignment
        ('left', 'EQ', 'NE'),                   # Equality operators
        ('left', 'LT', 'LE', 'GT', 'GE'),       # Relational operators
        ('left', 'PLUS', 'MINUS'),              # Addition and Subtraction
        ('left', 'TIMES', 'DIVIDE'),            # Multiplication and division
        ('right', 'UNMINUS'),                   # Unary minus
        # FIXME ! ('left', ),                             # Function call

    )


