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

def test_assign_term():
    eq_(n._assign_term(t('x'), {'x': 'A'}), t('A'))
    eq_(n._assign_term(t('B'), {'x': 'A'}), t('B'))
    eq_(n._assign_term(t('f(x)'), {'x': 'A'}), t('f(A)'))

def test_assign():
    eq_(n._assign(f('P(x)'), {'x': 'A'}), f('P(A)'))
    eq_(n._assign(f('not P(x)'), {'x': 'A'}), f('not P(A)'))
    eq_(n._assign(f('P(x) and Q(y)'), {'x': 'A', 'y': 'B'}), f('P(A) and Q(B)'))
    eq_(n._assign(f('P(x) or Q(y)'), {'x': 'A', 'y': 'B'}), f('P(A) or Q(B)'))
    eq_(n._assign(f('forall x P(x)'), {'x': 'A'}), f('forall x P(A)'))
    eq_(n._assign(f('exists x P(x)'), {'x': 'A'}), f('exists x P(A)'))

def test_uniquify():
    eq_(n._uniquify(f('forall x P(x)'),[0]), f('forall x0 P(x0)'))
    eq_(n._uniquify(f('exists x P(x)'),[0]), f('exists x0 P(x0)'))
    eq_(n._uniquify(f('forall x y P(x, y)'),[0]), f('forall x0 x1 P(x0, x1)'))
    eq_(n._uniquify(f('forall x y P(x, y) and exists z Q(z)'),[0]),
            f('forall x0 x1 P(x0, x1) and exists x2 Q(x2)'))
    eq_(n._uniquify(f('forall x y P(x, A, y)'),[0]), f('forall x0 x1 P(x0, A, x1)'))
    eq_(n._uniquify(f('forall x exists y P(x, y)'),[0]), f('forall x0 exists x1 P(x0, x1)'))
    eq_(n._uniquify(f('forall x P(f(x))'),[0]), f('forall x0 P(f(x0))'))

def test_move_neg():
    eq_(n._move_neg(f('not P()')), f('not P()'))
    eq_(n._move_neg(f('not not P()')), f('P()'))
    eq_(n._move_neg(f('not (P() and Q())')), f('not P() or not Q()'))
    eq_(n._move_neg(f('not (P() or Q())')), f('not P() and not Q()'))
    eq_(n._move_neg(f('not forall x P(x)')), f('exists x not P(x)'))
    eq_(n._move_neg(f('not exists x P(x)')), f('forall x not P(x)'))

def test_remove_exists():
    eq_(n._remove_exists(f('exists x P(x)'), ['A', 'B']), f('P(A) or P(B)'))
    eq_(n._remove_exists(f('exists x not P(x)'), ['A', 'B']), f('not P(A) or not P(B)'))
    eq_(n._remove_exists(f('exists x (P(x) and Q(x))'), ['A', 'B']),
            f('(P(A) and Q(A)) or (P(B) and Q(B))'))
    eq_(n._remove_exists(f('exists x (P(x) or Q(x))'), ['A', 'B']),
            f('(P(A) or Q(A)) or (P(B) or Q(B))'))
    eq_(n._remove_exists(f('exists x y P(x, y)'), ['A', 'B']),
            f('P(A,A) or P(A,B) or P(B,A) or P(B,B)'))

def test_remove_forall():
    eq_(n._remove_forall(f('forall x P(x)')), f('P(x)'))
    eq_(n._remove_forall(f('forall x forall y P(x,y)')), f('P(x, y)'))
    eq_(n._remove_forall(f('forall x P(x) and forall y Q(y)')), f('P(x) and Q(y)'))
    eq_(n._remove_forall(f('forall x P(x) or forall y Q(y)')), f('P(x) or Q(y)'))

def test_move_or():
    eq_(n._move_or(f('P(x)')), [[f('P(x)')]])
    eq_(n._move_or(f('P(x) or Q(y)')), [[f('P(x)'), f('Q(y)')]])
    eq_(n._move_or(f('P(x) and Q(y)')), [[f('P(x)')], [f('Q(y)')]])
    eq_(n._move_or(f('(P(x) and Q(y)) or R(x)')),
            [[f('P(x)'), f('R(x)')], [f('Q(y)'), f('R(x)')]])
    eq_(n._move_or(f('P(x) or (Q(y) and R(x))')),
            [[f('P(x)'), f('Q(y)')], [f('P(x)'), f('R(x)')]])

def test_move_and():
    eq_(n._move_and(f('P(x)')), [[f('P(x)')]])
    eq_(n._move_and(f('P(x) or Q(y)')), [[f('P(x)')], [f('Q(y)')]])
    eq_(n._move_and(f('P(x) and Q(y)')), [[f('P(x)'), f('Q(y)')]])
    eq_(n._move_and(f('(P(x) or Q(y)) and R(x)')),
            [[f('P(x)'), f('R(x)')], [f('Q(y)'), f('R(x)')]])
    eq_(n._move_and(f('P(x) and (Q(y) or R(x))')),
            [[f('P(x)'), f('Q(y)')], [f('P(x)'), f('R(x)')]])


def test_cnf():
    formula = f('forall x (Smokes(x) => Cancer(x))')
    constants = ['A', 'B']
    cnf = ConjunctiveNormalForm(formula, constants)
    eq_(cnf.to_formula(), f('not Smokes(x) or Cancer(x)'))

    formula = f('forall x (exists y Friends(x, y) => not Smokes(x))')
    constants = ['A', 'B']
    cnf = ConjunctiveNormalForm(formula, constants)
    eq_(cnf.to_formula(), f('not Friends(x, y) or not Smokes(x)'))

    formula = f('forall x (not Smokes(x) => exists y Friends(x, y))')
    constants = ['A', 'B']
    cnf = ConjunctiveNormalForm(formula, constants)
    eq_(cnf.to_formula(), f('Smokes(x) or Friends(x,A) or Friends(x,B)'))

def test_dnf():
    formula = f('forall x not (Smokes(x) => Cancer(x))')
    constants = ['A', 'B']
    dnf = DisjunctiveNormalForm(formula, constants)
    eq_(dnf.to_formula(), f('Smokes(x) and not Cancer(x)'))

    formula = f('forall x (exists y Friends(x, y) <=> not Smokes(x))')
    constants = ['A']
    dnf = DisjunctiveNormalForm(formula, constants)
    eq_(dnf.to_formula(), f('''
    not Friends(x,y) and Friends(x,A) or (not Friends(x,y) and Smokes(x)) or
    (not Smokes(x) and Friends(x,A)) or (not Smokes(x) and Smokes(x))
    '''))
