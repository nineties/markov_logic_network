import sys
import os
libpath = os.path.join(os.path.dirname(__file__), '../markov_logic_network')
sys.path.append(libpath)

from nose.tools import eq_

from syntax import *
from model import *

f = parse_formula

def test_load():
    model = MarkovLogicNetwork()
    model.load('''
    forall x y z (Friends(x, y) and Friends(y, z) => Friends(x, z)) : 0.7
    forall x (not exists y Friends(x, y) => Smokes(x))              : 2.3
    ''')
    eq_(model.mln[0][0], f('forall x y z (Friends(x, y) and Friends(y, z) => Friends(x, z))'))
    eq_(model.mln[0][1], 0.7)
    eq_(model.mln[1][0], f('forall x (not exists y Friends(x, y) => Smokes(x))'))
    eq_(model.mln[1][1], 2.3)
