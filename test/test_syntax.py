import sys
import os
libpath = os.path.join(os.path.dirname(__file__), '../markov_logic_network')
sys.path.append(libpath)

from nose.tools import raises

import syntax
from syntax import *

def test_node():
    A = syntax._node('A', 'x y')
    B = syntax._node('B', 'x y')
    assert(A(0,1) == A(0,1))
    assert(A(0,1) != A(1,2))
    assert(A(0,1) != B(0,1))

def test_lex_variable():
    assert(all(tok.type == 'VARIABLE' for tok in tokenize('xyz xYZ xYZ0_')))

def test_lex_constant():
    assert(all(tok.type == 'CONSTANT' for tok in tokenize('Xyz XYZ XYZ0_')))

def test_lex_float():
    a, b = list(tokenize('3.141592653589 1.0e-5'))
    assert(float(a.value) == 3.141592653589)
    assert(float(b.value) == 1.0e-5)

def test_lex_operator():
    tokens = list(tokenize('<=>=>=><=>'))
    assert(tokens[0].type == 'EQUIV')
    assert(tokens[1].type == 'IMPLY')
    assert(tokens[2].type == 'IMPLY')
    assert(tokens[3].type == 'EQUIV')

def test_lex_reserved():
    tokens = list(tokenize('not and or forall exists'))
    assert(tokens[0].type == 'NOT')
    assert(tokens[1].type == 'AND')
    assert(tokens[2].type == 'OR')
    assert(tokens[3].type == 'FORALL')
    assert(tokens[4].type == 'EXISTS')

@raises(LexError)
def test_lex_error():
    list(tokenize('abcd;'))

def test_parse_atomic_formula():
    assert(parse_formula('P()') == Atom('P',()))
    assert(parse_formula('P(x)') == Atom('P',('x',)))
    assert(parse_formula('P(x,y,z)') == Atom('P',('x','y','z')))
    assert(parse_formula('P(f())') == Atom('P',(Apply('f',()),)))
    assert(parse_formula('P(f(x,g(y)))') == Atom('P',(Apply('f',('x',Apply('g',('y',)))),)))

def test_parse_primary_formula():
    P = Atom('P', ())
    Q = Atom('Q', ())
    assert(parse_formula('not P()') == Not(P))
    assert(parse_formula('forall x P()') == Forall(('x',),P))
    assert(parse_formula('forall x y z P()') == Forall(('x','y','z'),P))
    assert(parse_formula('exists x P()') == Exists(('x',),P))
    assert(parse_formula('exists x y z P()') == Exists(('x','y','z'),P))
    assert(parse_formula('(P() => Q())') == Imply(P, Q))

def test_parse_secondary_formula():
    P = Atom('P', ())
    Q = Atom('Q', ())
    R = Atom('R', ())
    assert(parse_formula('P() and Q()') == And(P, Q))
    assert(parse_formula('P() or Q()') == Or(P, Q))
    assert(parse_formula('P() and Q() or R()') == Or(And(P, Q), R))

def test_parse_formula():
    P = Atom('P', ())
    Q = Atom('Q', ())
    assert(parse_formula('P() => Q()') == Imply(P, Q))
    assert(parse_formula('P() <=> Q()') == Equiv(P, Q))
