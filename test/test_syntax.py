import sys
import os
libpath = os.path.join(os.path.dirname(__file__), '../markov_logic_network')
sys.path.append(libpath)

from nose.tools import raises

import syntax

def test_node():
    A = syntax._node('A', 'x y')
    B = syntax._node('B', 'x y')
    assert(A(0,1) == A(0,1))
    assert(A(0,1) != A(1,2))
    assert(A(0,1) != B(0,1))

def test_lex_variable():
    assert(all(tok.type == 'VARIABLE' for tok in syntax.tokenize('xyz xYZ xYZ0_')))

def test_lex_constant():
    assert(all(tok.type == 'CONSTANT' for tok in syntax.tokenize('Xyz XYZ XYZ0_')))

def test_lex_float():
    a, b = list(syntax.tokenize('3.141592653589 1.0e-5'))
    assert(float(a.value) == 3.141592653589)
    assert(float(b.value) == 1.0e-5)

def test_lex_operator():
    tokens = list(syntax.tokenize('<=>=>=><=>'))
    assert(tokens[0].type == 'EQUIV')
    assert(tokens[1].type == 'IMPLY')
    assert(tokens[2].type == 'IMPLY')
    assert(tokens[3].type == 'EQUIV')

@raises(syntax.LexError)
def test_lex_error():
    list(syntax.tokenize('abcd;'))
