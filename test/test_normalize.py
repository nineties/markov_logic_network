import sys
import os
libpath = os.path.join(os.path.dirname(__file__), '../markov_logic_network')
sys.path.append(libpath)

from nose.tools import eq_

from syntax import *
from normalize import *
import normalize as n

f = parse_formula
t = parse_term

def test_remove_arrows():
    eq_(n._remove_arrows(f('P() => Q()')), f('not P() or Q()'))
    eq_(n._remove_arrows(f('not (P() => Q())')), f('not(not P() or Q())'))
    eq_(n._remove_arrows(f('forall x (P() => Q())')), f('forall x (not P() or Q())'))
    eq_(n._remove_arrows(f('exists x (P() => Q())')), f('exists x (not P() or Q())'))
    eq_(n._remove_arrows(f('P() <=> Q()')), f('(not P() or Q()) and (P() or not Q())'))

def test_rename_term():
    eq_(n._rename_term(t('x'), {'x': 'A'}), t('A'))
    eq_(n._rename_term(t('B'), {'x': 'A'}), t('B'))
    eq_(n._rename_term(t('f(x)'), {'x': 'A'}), t('f(A)'))

def test_uniquify():
    eq_(n._uniquify(f('forall x P(x)'),[0]), f('forall x0 P(x0)'))
    eq_(n._uniquify(f('exists x P(x)'),[0]), f('exists x0 P(x0)'))
    eq_(n._uniquify(f('forall x y P(x, y)'),[0]), f('forall x0 x1 P(x0, x1)'))
    eq_(n._uniquify(f('forall x y P(x, y) and exists z Q(z)'),[0]),
            f('forall x0 x1 P(x0, x1) and exists x2 Q(x2)'))
    eq_(n._uniquify(f('forall x y P(x, A, y)'),[0]), f('forall x0 x1 P(x0, A, x1)'))
    eq_(n._uniquify(f('forall x exists y P(x, y)'),[0]), f('forall x0 exists x1 P(x0, x1)'))
    eq_(n._uniquify(f('forall x P(f(x))'),[0]), f('forall x0 P(f(x0))'))
