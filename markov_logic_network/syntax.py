'Syntax Tree for first order logic'

from pprinter import *
from collections import namedtuple
from io import StringIO

__all__ = [
    'LexError', 'ParserError', 'EvaluationError',
    'Imply', 'Equiv', 'And', 'Or', 'Forall', 'Exists', 'Not', 'Atom', 'Apply',
    'tokenize', 'parse_mln', 'parse_formula', 'parse_term', 'eval_term'
    ]

# === A Class for Tree Nodes ===

def _eq_node(self, other):
    return type(self) == type(other) and tuple.__eq__(self, other)

def _ne_node(self, other):
    return not _eq_node(self, other)

def _gt_node(self, other):
    n1 = type(self).__name__
    n2 = type(other).__name__
    return n1 > n2 or (n1 == n2 and tuple.__gt__(self, other))

def _ge_node(self, other):
    n1 = type(self).__name__
    n2 = type(other).__name__
    return n1 >= n2 or (n1 == n2 and tuple.__ge__(self, other))

def _lt_node(self, other):
    n1 = type(self).__name__
    n2 = type(other).__name__
    return n1 < n2 or (n1 == n2 and tuple.__lt__(self, other))

def _le_node(self, other):
    n1 = type(self).__name__
    n2 = type(other).__name__
    return n1 <= n2 or (n1 == n2 and tuple.__le__(self, other))

def _node(name, fields):
    klass = namedtuple(name, fields)
    klass.__eq__ = _eq_node
    klass.__ne__ = _ne_node
    klass.__gt__ = _gt_node
    klass.__ge__ = _ge_node
    klass.__lt__ = _lt_node
    klass.__le__ = _le_node
    return klass

# === Exceptions ===

class LexError(Exception):
    'Lexical Error'

class ParserError(Exception):
    'Syntactical Error'

class EvaluationError(Exception):
    'Evaluation Error'

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
    'VARIABLE', 'CONSTANT', 'FLOAT',
    'NOT', 'AND', 'OR', 'FORALL', 'EXISTS',
    'EQUIV', 'IMPLY', 'COLON', 'COMMA', 'LPAREN', 'RPAREN',
)

reserved = {
    'not': 'NOT', 'and': 'AND', 'or': 'OR', 'forall': 'FORALL', 'exists': 'EXISTS'
}

def t_VARIABLE(t):
    r'[a-z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'VARIABLE')
    return t

t_CONSTANT = r'[A-Z][a-zA-Z0-9_]*'
t_EQUIV = r'<=>'
t_IMPLY = r'=>'
t_COLON = r':'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_FLOAT = r'[+-]?[0-9]+(\.([0-9]+)?)?([eE][+-]?[0-9]+)?'

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

def p_error(p):
    if p:
        raise ParserError('Syntax error at token: {}'.format(p.type))
    else:
        raise ParserError('Syntax error at EOF')

def p_mln(p):
    '''
    mln : mln_entry
        | mln_entry mln
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_mln_entry(p):
    '''
    mln_entry : formula COLON float
              | formula
    '''
    if len(p) == 2:
        p[0] = (p[1], 0.0)
    else:
        p[0] = (p[1], p[3])

def p_float(p):
    'float : FLOAT'
    p[0] = float(p[1])

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

# Build the parsers

_mln_parser = yacc.yacc(start='mln')
_formula_parser = yacc.yacc(start='formula')
_term_parser = yacc.yacc(start='term')

def parse_mln(text):
    return _mln_parser.parse(text)

def parse_formula(text):
    return _formula_parser.parse(text)

def parse_term(text):
    return _term_parser.parse(text)

INDENT = 4

# === Pretty Printing ===
def pp_formula(f):
    if isinstance(f, Imply) or isinstance(f, Equiv):
        op = '=>' if isinstance(f, Imply) else '<=>'
        return nest(INDENT, [
            pp_secondary_formula(f.f1),
            nl(' '), op, nl(' '),
            pp_secondary_formula(f.f2)
            ])
    else:
        return pp_secondary_formula(f)

def pp_secondary_formula(f):
    if isinstance(f, And) or isinstance(f, Or):
        op = 'and' if isinstance(f, And) else 'or'
        return nest(INDENT, [
            pp_secondary_formula(f.f1),
            nl(' '), op, nl(' '),
            pp_primary_formula(f.f2)
            ])
    else:
        return pp_primary_formula(f)

def pp_primary_formula(f):
    if isinstance(f, Atom):
        return pp_atomic_formula(f)
    elif isinstance(f, Not):
        return ['not ', pp_primary_formula(f.f)]
    elif isinstance(f, Forall) or isinstance(f, Exists):
        qual = 'forall' if isinstance(f, Forall) else 'exists'
        return nest(INDENT, [
            qual, ' ', weave(f.xs, ' '), nl(' '),
            pp_primary_formula(f.f)
            ])
    else:
        return nest(INDENT, ['(', nl(), pp_formula(f), nl(), ')'])

def pp_atomic_formula(f):
    return nest(INDENT, [
        f.pred, '(', nl(),
        weave(map(pp_term, f.args), [',', nl()]),
        nl(), ')'])

def pp_term(t):
    if isinstance(t, Apply):
        return nest(INDENT, [
            t.fun, '(', nl(),
            weave(map(pp_term, t.args), [',', nl()]),
            nl(), ')'])
    else:
        return t

def formula_to_s(f):
    return pprint_s(breakable(pp_formula(f)))

def term_to_s(t):
    return pprint_s(breakable(pp_term(t)))

Imply.__repr__ = formula_to_s
Equiv.__repr__ = formula_to_s
And.__repr__ = formula_to_s
Or.__repr__ = formula_to_s
Forall.__repr__ = formula_to_s
Exists.__repr__ = formula_to_s
Not.__repr__ = formula_to_s
Atom.__repr__ = formula_to_s
Apply.__repr__ = term_to_s

# === Evaluation ===

def eval_term(env, C, term):
    if isinstance(term, str):
        r = env.get(term, term)
    else:
        args = [eval_term(env, C, t) for t in term.args]
        r = env[term.fun](*args)
    if r not in C:
        raise EvaluationError('Not a constant value: {}'.format(r))
    return r
