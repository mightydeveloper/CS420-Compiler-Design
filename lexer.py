## Lexer (Tokenizer) implementation
## 20121022 Young Seok Kim



import ply.lex as lex
#from ply.lex import TOKEN



#
# def build(**kwargs):
#     """ Builds the lexer from the specification. Must be
#         called after the lexer object is created.
#         This method exists separately, because the PLY
#         manual warns against calling lex.lex inside
#         __init__
#     """
#     lexer = lex.lex(object=self, **kwargs)
#
# def input(text):
#     self.lexer.input(text)
#
# def printTokens(self):
#     # Tokenize
#     while True:
#         tok = self.lexer.token()
#         if not tok:
#             break  # No more input
#         print(tok)
#
# def generateTokens(self, text):
#     self.lexer.input(text)
#     tokens = []
#     # Tokenize
#     while True:
#         tok = self.lexer.token()
#         if not tok:
#             break  # No more input
#         tokens.append(tok)
#     return tokens

# def reset_lineno(self):
#     """ Resets the internal line number counter of the lexer.
#     """
#     self.lexer.lineno = 1

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule
def t_error(t):
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
for keyword in keywords:
    keyword_map[keyword.lower()] = keyword

# List of token names.
tokens = keywords + (
    # Identifiers
    'ID',

    # Types
    # 'INTTYPE', 'FLOATTYPE' # already in keywords

    # Unary operator
    # 'UNOP',

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

# Ignore space and tabs and newline
t_ignore = ' \t'

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


def t_FLOATNUM(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t


def t_INTNUM(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = keyword_map.get(t.value, "ID")
    # if t.type == 'ID' and self.type_lookup_func(t.value):
    #     t.type = "TYPEID"
    return t


# Build lexer
lexer = lex.lex()