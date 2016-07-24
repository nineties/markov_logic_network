import sys
import os
libpath = os.path.join(os.path.dirname(__file__), '../markov_logic_network')
sys.path.append(libpath)

from nose.tools import assert_raises, eq_, ok_
from nose.tools import assert_not_equal as ne_

import syntax
from syntax import *

# === Parsing ===

def test_node():
    A = syntax._node('A', 'x y')
    B = syntax._node('B', 'x y')
    eq_(A(0,1), A(0,1))
    ne_(A(0,1), A(1,2))
    ne_(A(0,1), B(0,1))

def test_lex_variable():
    ok_(all(tok.type == 'VARIABLE' for tok in tokenize('xyz xYZ xYZ0_')))

def test_lex_constant():
    ok_(all(tok.type == 'CONSTANT' for tok in tokenize('Xyz XYZ XYZ0_')))

def test_lex_float():
    a, b = list(tokenize('3.141592653589 1.0e-5'))
    eq_(float(a.value), 3.141592653589)
    eq_(float(b.value), 1.0e-5)

def test_lex_operator():
    tokens = list(tokenize('<=>=>=><=>'))
    eq_(tokens[0].type, 'EQUIV')
    eq_(tokens[1].type, 'IMPLY')
    eq_(tokens[2].type, 'IMPLY')
    eq_(tokens[3].type, 'EQUIV')

def test_lex_reserved():
    tokens = list(tokenize('not and or forall exists'))
    eq_(tokens[0].type, 'NOT')
    eq_(tokens[1].type, 'AND')
    eq_(tokens[2].type, 'OR')
    eq_(tokens[3].type, 'FORALL')
    eq_(tokens[4].type, 'EXISTS')

@raises(LexError)
def test_lex_error():
    list(tokenize('abcd;'))

def test_parse_term():
    eq_(parse_term('x'), 'x')
    eq_(parse_term('X'), 'X')
    eq_(parse_term('f(x,y,z)'), Apply('f', ('x', 'y', 'z')))

def test_parse_atomic_formula():
    eq_(parse_formula('P()'), Atom('P',()))
    eq_(parse_formula('P(x)'), Atom('P',('x',)))
    eq_(parse_formula('P(x,y,z)'), Atom('P',('x','y','z')))
    eq_(parse_formula('P(f())'), Atom('P',(Apply('f',()),)))
    eq_(parse_formula('P(f(x,g(y)))'), Atom('P',(Apply('f',('x',Apply('g',('y',)))),)))

def test_parse_primary_formula():
    P = Atom('P', ())
    Q = Atom('Q', ())
    eq_(parse_formula('not P()'), Not(P))
    eq_(parse_formula('forall x P()'), Forall(('x',),P))
    eq_(parse_formula('forall x y z P()'), Forall(('x','y','z'),P))
    eq_(parse_formula('exists x P()'), Exists(('x',),P))
    eq_(parse_formula('exists x y z P()'), Exists(('x','y','z'),P))
    eq_(parse_formula('(P() => Q())'), Imply(P, Q))

def test_parse_secondary_formula():
    P = Atom('P', ())
    Q = Atom('Q', ())
    R = Atom('R', ())
    eq_(parse_formula('P() and Q()'), And(P, Q))
    eq_(parse_formula('P() or Q()'), Or(P, Q))
    eq_(parse_formula('P() and Q() or R()'), Or(And(P, Q), R))

def test_parse_formula():
    P = Atom('P', ())
    Q = Atom('Q', ())
    eq_(parse_formula('P() => Q()'), Imply(P, Q))
    eq_(parse_formula('P() <=> Q()'), Equiv(P, Q))

# === Pretty Printing ===

def test_print_term():
    eq_(str(parse_term('x')), 'x')
    eq_(str(parse_term('f(x,y,z)')), 'f(x,y,z)')
    eq_(str(parse_term('f(x, y, z)')), 'f(x,y,z)')

def test_print_atomic_formula():
    eq_(str(parse_formula('P(x, y, z)')), 'P(x,y,z)')
    eq_(str(parse_formula('P(f(a,b),x,y,z)')),'P(f(a,b),x,y,z)')

def test_print_primary_formula():
    eq_(str(parse_formula('not P()')), 'not P()')
    eq_(str(parse_formula('forall x y P(x, y)')), 'forall x y P(x,y)')
    eq_(str(parse_formula('exists x y P(x, y)')), 'exists x y P(x,y)')
    eq_(str(parse_formula('not (P() => Q())')), 'not (P() => Q())')

def test_print_secomdary_formula():
    eq_(str(parse_formula('P() and Q()')), 'P() and Q()')
    eq_(str(parse_formula('P() and Q() and R()')), 'P() and Q() and R()')
    eq_(str(parse_formula('P() and (Q() and R())')), 'P() and (Q() and R())')
    eq_(str(parse_formula('P() or Q()')), 'P() or Q()')
    eq_(str(parse_formula('P() or Q() or R()')), 'P() or Q() or R()')
    eq_(str(parse_formula('P() or (Q() or R())')), 'P() or (Q() or R())')

def test_print_formula():
    eq_(str(parse_formula('P() => Q()')), 'P() => Q()')
    eq_(str(parse_formula('P() <=> Q()')), 'P() <=> Q()')
    eq_(str(parse_formula('P() => Q() and R()')), 'P() => Q() and R()')
    eq_(str(parse_formula('P() => (Q() => R())')), 'P() => (Q() => R())')

def test_parser_error():
    assert_raises(ParserError, parse_formula, 'P() =>')
    assert_raises(ParserError, parse_formula, 'P() => x')
    assert_raises(ParserError, parse_formula, 'P() => Q() <=> R()')
    assert_raises(ParserError, parse_formula, 'forall P()')
    assert_raises(ParserError, parse_formula, 'P(x,y,')

# === Evaluation ===

def test_eval():
    eq_(eval_term({'x': 'A'}, ['A'], parse_term('x')), 'A')
    eq_(eval_term({'f': lambda : 'A'}, ['A'], parse_term('f()')), 'A')
    eq_(eval_term({'f': lambda x: x}, ['A'], parse_term('f(A)')), 'A')

def test_eval_error():
    assert_raises(EvaluationError, eval_term, {'x': 'y'}, ['A'], parse_term('x'))
    assert_raises(EvaluationError, eval_term, {'x': 'B'}, ['A'], parse_term('x'))
