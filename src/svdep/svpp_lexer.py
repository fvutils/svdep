

import ply.lex as lex

tokens = (
    'INCLUDE',
    'STRING',
    'ID',
    'OP',
    'DIRECTIVE',
    'COMMENTSL'
)

#    r'//.*$'

#t_STRING = r"'([^\\']+|\\'|\\\\)*'"
# r'"([^"\n]|(\\"))*"$'
def t_STRING(t):
    # A SystemVerilog string literal: opening '"', then any run of
    #   - an escape sequence  (\\. -- e.g. \" \\ \n)
    #   - a line continuation (\\ followed by a newline; '.' doesn't match \n)
    #   - any ordinary character that isn't a quote, backslash, or newline
    # then the closing '"'. This stops at the first *unescaped* quote (so it is
    # not greedy across multiple literals) and correctly spans multi-line strings
    # that use '\'-newline continuation (e.g. UVM's uvm_reg_map.svh).
    r'"(\\.|\\\n|[^"\\\n])*"'
    t.value = t.value[1:-1]
    return t
def t_DIRECTIVE(t):
    r'`[a-zA-Z0-9][a-zA-Z0-9_]*|`'
    t.value = t.value[1:]
    return t
#t_INCLUDE = r'`include'
t_ID = r'[$_a-zA-Z0-9][_a-zA-Z0-9]*'
#t_ID = 'a'

def t_COMMENTSL(t):
#    r'(/\\(.|\n)*?\\/)|(//.*)'
    r'//.*\n'
    pass

def t_COMMENT(t):
    r'/\*.*?\*/'
    pass

def t_BACKSLASH(t):
    r'\\'
    pass

literals = [';', ':', "'", ',', '+', '-', '*', '/', '%', '^', '=', '&', '|', '#', '@', '!', '?', '~', '.']
#t_OP = r'([;:\',+-*/])'
#t_OP = r';:\',+-*/'

#t_ignore = ' \t\n;:\',+-*\\/%^=&|#@!?~.()[]{}<>\0169\0174' + chr(65533)
#t_ignore = ' \t\n;:\',+-*\\/%^=&|#@!?~.()[]{}<>'+chr(65533)
t_ignore = ' \t\n()[]{}<>'+chr(65533)

def t_error(t):
    # This is a dependency scanner, not a full parser: an unrecognized character
    # must not abort the whole collection build. Skip it and carry on so we still
    # find every `include directive in the file.
    t.lexer.skip(1)

def mk_lexer(**kwargs):
    return lex.lex(**kwargs)


