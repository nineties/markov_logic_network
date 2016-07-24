"Syntax Tree for first order logic"

from collections import namedtuple
from io import StringIO

# === A Class for Tree Nodes ===

def _eq_node(self, other):
    return self.__class__ == other.__class__ and tuple.__eq__(self, other)
def _ne_node(self, other):
    return self.__class__ != other.__class__ or tuple.__ne__(self, other)

def _node(name, fields):
    klass = namedtuple(name, fields)
    klass.__eq__ = _eq_node
    klass.__ne__ = _ne_node
    return klass

# === Exceptions ===

class LexError(Exception):
    'Lexical Error'

class ParserError(Exception):
    'Syntactical Error'

# === The Syntax ===

Imply = _node('Imply', 'f1 f2')
Equiv = _node('Equiv', 'f1 f2')
And = _node('And', 'f1 f2')
Or = _node('Or', 'f1 f2')
Forall = _node('Forall', 'xs f')
Exists = _node('Exists', 'xs f')
Not = _node('Not', 'f')
Atom = _node('Atom', 'pred args')
Apply = _node('Apply', 'fun args')

from ply import lex

tokens = (
    'BEG_FORMULA',
    'VARIABLE', 'CONSTANT', 'FLOAT',
    'NOT', 'AND', 'OR', 'FORALL', 'EXISTS',
    'EQUIV', 'IMPLY', 'DOT', 'COMMA', 'LPAREN', 'RPAREN',
)

reserved = {
    'not': 'NOT', 'and': 'AND', 'or': 'OR', 'forall': 'FORALL', 'exists': 'EXISTS'
}

def t_VARIABLE(t):
    r'[a-z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'VARIABLE')
    return t

t_BEG_FORMULA = r'<FORMULA>'

t_CONSTANT = r'[A-Z][a-zA-Z0-9_]*'
t_EQUIV = r'<=>'
t_IMPLY = r'=>'
t_DOT = r'\.'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_FLOAT = r'[+-]?[0-9]+\.([0-9]+)?([eE][+-]?[0-9]+)?'

t_ignore = ' \t\r\n'

def t_error(t):
    raise LexError('Illegal character: {}'.format(t.value[0]))

lex.lex()   # Build the lexer

def tokenize(text):
    lex.input(text)
    while True:
        tok = lex.token()
        if not tok: break
        yield tok

from ply import yacc

def p_start(p):
    'start : BEG_FORMULA formula'
    p[0] = p[2]

def p_formula(p):
    '''
    formula : secondary_formula
            | secondary_formula IMPLY secondary_formula
            | secondary_formula EQUIV secondary_formula
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '=>':
        p[0] = Imply(p[1], p[3])
    else:
        p[0] = Equiv(p[1], p[3])

def p_secondary_formula(p):
    '''
    secondary_formula : primary_formula
                      | secondary_formula AND primary_formula
                      | secondary_formula OR primary_formula
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == 'and':
        p[0] = And(p[1], p[3])
    else:
        p[0] = Or(p[1], p[3])

def p_primary_formula(p):
    '''
    primary_formula : atomic_formula
                    | NOT primary_formula
                    | FORALL variables primary_formula
                    | EXISTS variables primary_formula
                    | LPAREN formula RPAREN
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif p[1] == 'not':
        p[0] = Not(p[2])
    elif p[1] == 'forall':
        p[0] = Forall(tuple(p[2]), p[3])
    elif p[1] == 'exists':
        p[0] = Exists(tuple(p[2]), p[3])
    else:
        p[0] = p[2]

def p_atomic_formula(p):
    'atomic_formula : predicate LPAREN terms RPAREN'
    p[0] = Atom(p[1], tuple(p[3]))

def p_variables(p):
    '''
    variables : variable
              | variable variables
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_terms(p):
    '''
    terms : 
          | term
          | term COMMA terms
    '''
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_params(p):
    '''
    params :
           | term
           | term COMMA params
    '''
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_term(p):
    '''
    term : variable
         | constant
         | function LPAREN params RPAREN
    '''
    if len(p) > 2:
        p[0] = Apply(p[1], tuple(p[3]))
    else:
        p[0] = p[1]

def p_variable(p):
    'variable : VARIABLE'
    p[0] = p[1]

def p_constant(p):
    'constant : CONSTANT'
    p[0] = p[1]

def p_predicate(p):
    'predicate : CONSTANT'
    p[0] = p[1]

def p_function(p):
    'function : VARIABLE'
    p[0] = p[1]

yacc.yacc() # Build the parser

def parse_formula(text):
    return yacc.parse(t_BEG_FORMULA+' '+text)

# === Pretty Printing ===
"""
# === Pretty Printing ===

def formula_to_s(f):
    sio = StringIO()
    print_formula(sio, f)
    return sio.getvalue()

def print_formula(sio, f):
    assert(f)
    if isinstance(f, Imply):
        print_formula2(sio, f.f1)
        sio.write(' => ')
        print_formula2(sio, f.f2)
    elif isinstance(f, Equiv):
        print_formula2(sio, f.f1)
        sio.write(' <=> ')
        print_formula2(sio, f.f2)
    else:
        print_formula2(sio, f)

def print_formula2(sio, f):
    if isinstance(f, And):
        print_formula1(sio, f.f1)
        sio.write(' and ')
        print_formula1(sio, f.f2)
    elif isinstance(f, Or):
        print_formula1(sio, f.f1)
        sio.write(' or ')
        print_formula1(sio, f.f2)
    else:
        print_formula1(sio, f)

def print_formula1(sio, f):
    if isinstance(f, Not):
        sio.write('not ')
        print_formula1(sio, f.f)
    elif isinstance(f, Forall):
        sio.write('forall ')
        sio.write(' '.join(f.xs))
        sio.write(' ')
        print_formula1(sio, f.f)
    elif isinstance(f, Exists):
        sio.write('exists ')
        sio.write(' '.join(f.xs))
        sio.write(' ')
        print_formula1(sio, f.f)
    elif isinstance(f, Atom):
        print_atomic(sio, f)
    else:
        sio.write('(')
        print_formula(sio, f)
        sio.write(')')

def print_atomic(sio, f):
    sio.write(f.pred)
    sio.write('(')
    for i, a in enumerate(f.args):
        print_term(sio, a)
        if i < len(f.args)-1:
            sio.write(', ')
    sio.write(')')

def print_term(sio, t):
    if isinstance(t, Apply):
        sio.write(t.fun)
        sio.write('(')
        for i, a in enumerate(t.args):
            print_term(sio, a)
            if i < len(t.args)-1:
                sio.write(', ')
        sio.write(')')
    else:
        sio.write(t)


# === Utilities ===

# Evaluate variables or function calls with given assignments.
# args: a map from variables to constants
def eval_atom(atom, env, funcs):
    return Atom(atom.pred, tuple(eval_term(t, env, funcs) for t in atom.args))

def eval_term(term, env, funcs):
    if isinstance(term, str):
        return env[term] if is_variable(term) else term
    else:
        f = eval(term.fun, {}, funcs)
        args = [eval_term(t, env, funcs) for t in term.args]
        return f(*args)

if __name__=='__main__':
    print(parse_formula('forall x (Smokes(x) => Cancer(x))'))
    print(parse_formula('forall x y (Friends(x, y) => (Smokes(x) <=> Smokes(y)))'))
"""
