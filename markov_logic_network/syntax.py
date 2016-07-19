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

# === The Syntax ===

from ply import lex

tokens = (
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

# variable ::= an identifier starts with lower alphabet
# constant ::= an identifier starts with upper alphabet
# function ::= variable


# === Parser ===

# A parser for first order logic (FOL).

# term ::= <variable>   (starts with lower alphabet)
#        | <constants>  (starts with upper alphabet)
#        | <variable> '(' <term> ',' ... ')'
# atomic ::= <predicate> '(' <term> ',' ... ')' (predicate starts with upper alphabet)
# formula1 ::= <atomic>
#            | 'not' <formula1>
#            | 'forall' <variable> ... <formula1>
#            | 'exists' <variable> ... <formula1>
#            | '(' <formula> ')'
# formula2 ::= <formula1> ( ('and' | 'or') <formula1> )*
# formula ::= <formula2>
#           | <formula2> '=>' <formula2>
#           | <formula2> '<=>' <formula2>

Forall = namedtuple('Forall', 'xs f')
Exists = namedtuple('Exists', 'xs f')
Not = namedtuple('Not', 'f')
And = namedtuple('And', 'f1 f2')
Or = namedtuple('Or', 'f1 f2')
Imply = namedtuple('Imply', 'f1 f2')
Equiv = namedtuple('Equiv', 'f1 f2')
Atom = namedtuple('Atom', 'pred args')
Apply = namedtuple('Apply', 'fun args')

class UnknownToken(Exception):
    'Unknown Token Error'

class InvalidSyntax(Exception):
    'Invalid Syntax Error'

def lex(s):
    if s[0].isalpha():
        for i in range(len(s)):
            if not s[i].isalnum():
                return s[:i], s[i:].lstrip()
        return s, ''

    if s[0] in '.,()':
        return s[0], s[1:].lstrip()
    elif s[:2] == '=>':
        return '=>', s[2:].lstrip()
    elif s[:3] == '<=>':
        return '<=>', s[3:].lstrip()
    else:
        raise UnknownToken(s[0])

def tokenize(s):
    s = s.lstrip()

    tokens = []
    while True:
        t, s = lex(s)
        tokens.append(t)
        if not s:
            break
    return tokens

def is_word(tok):
    return tok.isalnum() and tok not in ['not', 'forall', 'exists', 'and', 'or']

def is_variable(tok):
    return is_word(tok) and tok[0].islower()

def is_constant(tok):
    return is_word(tok) and tok[0].isupper()

def expect(tokens, e):
    if not tokens or tokens[0] != e:
        raise InvalidSyntax('{} is expected'.format(e))
    tokens.pop(0)

def lookahead(tokens):
    if tokens:
        return tokens[0]

def parse_variable(tokens):
    if not is_variable(lookahead(tokens)):
        raise InvalidSyntax('Variable symbol is expected')
    return tokens.pop(0)

def parse_constant(tokens):
    if not is_constant(lookahead(tokens)):
        raise InvalidSyntax('Constant symbol is expected')
    return tokens.pop(0)

def parse_term(tokens):
    x = lookahead(tokens)
    if not is_word(x):
        raise InvalidSyntax('Variables, constants or function symbols are expected')
    tokens.pop(0)
    if is_variable(x) and lookahead(tokens) == '(':
        tokens.pop(0)
        if lookahead(tokens) == ')':
            tokens.pop(0)
            return Apply(x, [])

        args = []
        while True:
            args.append(parse_term(tokens))
            if lookahead(tokens) == ')':
                tokens.pop(0)
                return Apply(x, tuple(args))
            expect(tokens, ',')
    else:
        return x

def parse_atomic(tokens):
    p = parse_constant(tokens)
    expect(tokens, '(')
    if lookahead(tokens) == ')':
        tokens.pop(0)
        return Atom(p, [])
    args = []
    while True:
        args.append(parse_term(tokens))
        if lookahead(tokens) == ')':
            tokens.pop(0)
            return Atom(p, tuple(args))
        expect(tokens, ',')

def parse_variables(tokens):
    xs = []
    while True:
        if is_variable(lookahead(tokens)):
            xs.append(tokens.pop(0))
        else:
            break
    if not xs:
        raise InvalidSyntax('Variables are required: {}'.format(lookahead(tokens)))
    return tuple(xs)

def parse_formula1(tokens):
    t = lookahead(tokens)
    if t == '(':
        tokens.pop(0)
        f = parse_formula_(tokens)
        expect(tokens, ')')
        return f
    elif t == 'not':
        tokens.pop(0)
        return Not(f=parse_formula1(tokens))
    elif t in ['forall', 'exists']:
        tokens.pop(0)
        xs = parse_variables(tokens)
        f = parse_formula1(tokens)
        if t == 'forall':
            return Forall(xs, f)
        else:
            return Exists(xs, f)
    else:
        return parse_atomic(tokens)

def parse_formula2(tokens):
    f1 = parse_formula1(tokens)
    while True:
        if lookahead(tokens) in ['and', 'or']:
            t = tokens.pop(0)
            f2 = parse_formula1(tokens)
            if t == 'and':
                f1 = And(f1, f2)
            else:
                f1 = Or(f1, f2)
        else:
            return f1

def parse_formula_(tokens):
    f1 = parse_formula2(tokens)
    if lookahead(tokens) in ['=>', '<=>']:
        t = tokens.pop(0)
        f2 = parse_formula2(tokens)
        if t == '=>':
            return Imply(f1, f2)
        else:
            return Equiv(f1, f2)
    return f1

def parse_formula(text):
    tokens = tokenize(text)
    f = parse_formula_(tokens)
    if tokens:
        raise InvalidSyntax('Unexpected token: {}'.format(tokens[0]))
    return f

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

Forall.__repr__ = formula_to_s
Exists.__repr__ = formula_to_s
Not.__repr__ = formula_to_s
And.__repr__ = formula_to_s
Or.__repr__ = formula_to_s
Imply.__repr__ = formula_to_s
Equiv.__repr__ = formula_to_s
Atom.__repr__ = formula_to_s
Apply.__repr__ = formula_to_s

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
