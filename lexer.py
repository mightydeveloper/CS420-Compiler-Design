import ply.lex as lex
from ply.lex import TOKEN



class MiniCLexer(object):
    """
    """

    def build(self, **kwargs):
        """ Builds the lexer from the specification. Must be
            called after the lexer object is created.
            This method exists separately, because the PLY
            manual warns against calling lex.lex inside
            __init__
        """
        self.lexer = lex.lex(object=self, **kwargs)

    def input(self, text):
        self.lexer.input(text)

    def printTokens(self):
        # Tokenize
        while True:
            tok = self.lexer.token()
            if not tok:
                break  # No more input
            print(tok)

    def generateTokens(self, text):
        self.lexer.input(text)
        tokens = []
        # Tokenize
        while True:
            tok = self.lexer.token()
            if not tok:
                break  # No more input
            tokens.append(tok)
        return tokens

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1


    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Reserved keywords
    keywords = (
        'INT',
        'FLOAT',
        'RETURN',
        'DO',
        'WHILE',
        'FOR',
        'IF',
        'ELSE',
        'SWITCH',
        'CASE',
        'BREAK',
        'DEFAULT',
    )

    keyword_map = {}

    # List of token names.
    tokens = keywords + (
        # Identifiers
        'ID',

        # Types
        # 'INTTYPE', 'FLOATTYPE' # already in keywords

        # Unary operator
        'UNOP',

        # Operatiors
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',

        'ASSIGN',

        # Deliminartors
        'LPAREN', 'RPAREN',
        'LBRACE', 'RBRACE',
        'LBRACKET', 'RBRACKET',
        'COMMA',
        'SEMI',
        'COLON',

        # Constants
        'INTNUM', 'FLOATNUM',
    )

    # Ignore space and tabs
    t_ignore = ' \t'

    t_UNOP= r'-'

    t_PLUS   = r'\+'
    t_MINUS  = r'-'
    t_TIMES  = r'\*'
    t_DIVIDE = r'/'

    t_LT = r'<'
    t_GT = r'>'
    t_LE = r'<='
    t_GE = r'>='
    t_EQ = r'=='
    t_NE = r'!='

    t_ASSIGN = r'='

    # Delimeters
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'


    t_COMMA = r','
    t_SEMI = r';'
    t_COLON = r':'

    def t_INTNUM(self, t):
        r'[0-9]+'
        t.value = int(t.value)
        return t

    def t_FLOATNUM(self, t):
        r'[0-9]+\.[0-9]+'
        t.value = float(t.value)
        return t

    def t_ID(self, t):
        r'[A-Za-z][A-Za-z0-9_]*'
        t.type = self.keyword_map.get(t.value, "ID")
        # if t.type == 'ID' and self.type_lookup_func(t.value):
        #     t.type = "TYPEID"
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

