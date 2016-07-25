import sys
import os
libpath = os.path.join(os.path.dirname(__file__), '../markov_logic_network')
sys.path.append(libpath)

from nose.tools import eq_

from syntax import *
from normalize import *
import normalize as n

p = parse_formula

def test_remove_arrows():
    eq_(n._remove_arrows(p('P() => Q()')), p('not P() or Q()'))
    eq_(n._remove_arrows(p('not (P() => Q())')), p('not(not P() or Q())'))
    eq_(n._remove_arrows(p('forall x (P() => Q())')), p('forall x (not P() or Q())'))
    eq_(n._remove_arrows(p('exists x (P() => Q())')), p('exists x (not P() or Q())'))
    eq_(n._remove_arrows(p('P() <=> Q()')), p('(not P() or Q()) and (P() or not Q())'))
