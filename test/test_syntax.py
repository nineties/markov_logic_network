import sys
import os
libpath = os.path.join(os.path.dirname(__file__), '../markov_logic_network')
sys.path.append(libpath)

import syntax

def test_node():
    A = syntax._node('A', 'x y')
    B = syntax._node('B', 'x y')
    assert(A(0,1) == A(0,1))
    assert(A(0,1) != A(1,2))
    assert(A(0,1) != B(0,1))
