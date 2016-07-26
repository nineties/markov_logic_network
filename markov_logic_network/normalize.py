'Translators from FOL formula to CNF or DNF'

from syntax import *
from itertools import product
from functools import reduce

__all__ = ['ConjunctiveNormalForm', 'DisjunctiveNormalForm']

class ConjunctiveNormalForm(object):
    def __init__(self, formula, constants):
        self.original = formula
        self.clauses = _conjunctive_normal_form(formula, constants)

    def to_formula(self):
        return reduce(And, [reduce(Or, clause) for clause in self.clauses])

    def __str__(self):
        return str(self.to_formula())

class DisjunctiveNormalForm(object):
    def __init__(self, formula, constants):
        self.original = formula
        self.clauses = _disjunctive_normal_form(formula, constants)

    def to_formula(self):
        return reduce(Or, [reduce(And, clause) for clause in self.clauses])

    def __str__(self):
        return str(self.to_formula())

def _conjunctive_normal_form(f, C):
    '''
    Translate given formula to conjunctive normal form.

    f: a formula of first order logic.
    C: list of constants

    The result will be a list (conjunctive) of lists (disjunctions)
    '''
    f = _uniquify(f, [0])
    f = _remove_arrows(f)
    f = _move_neg(f)
    f = _remove_exists(f, C)
    f = _remove_forall(f)
    return  _move_or(f)

def _disjunctive_normal_form(f, C):
    '''
    Translate given formula to disjunctive normal form.

    f: a formula of first order logic.
    C: list of constants

    The result will be a list (disjunctions) of lists (conjuctions)
    '''
    f = _uniquify(f, [0])
    f = _remove_arrows(f)
    f = _move_neg(f)
    f = _remove_exists(f, C)
    f = _remove_forall(f)
    return _move_and(f)

def _uniquify(f, n, d={}):
    'Uniquify bound variables'
    if isinstance(f, Forall) or isinstance(f, Exists):
        d = d.copy()
        for x in f.xs:
            d[x] = 'x' + str(n[0])
            n[0] += 1
        return f._replace(xs=tuple(d[x] for x in f.xs), f=_uniquify(f.f, n, d))
    elif isinstance(f, Not):
        return Not(_uniquify(f.f, n, d))
    elif isinstance(f, And) or isinstance(f, Or):
        return f._replace(f1=_uniquify(f.f1, n, d), f2=_uniquify(f.f2, n, d))
    elif isinstance(f, Atom):
        return Atom(f.pred, tuple(_assign_term(t, d) for t in f.args))
    return f

def _assign_term(t, d):
    'Substitute variables using given map d'
    if isinstance(t, str):
        return d.get(t, t)
    else:
        return Apply(t.fun, tuple(_assign_term(t, d) for t in t.args))

def _assign(f, d):
    if isinstance(f, Forall) or isinstance(f, Exists):
        return f._replace(f=_assign(f.f, d))
    elif isinstance(f, Not):
        return Not(_assign(f.f, d))
    elif isinstance(f, And) or isinstance(f, Or):
        return f._replace(f1=_assign(f.f1, d), f2=_assign(f.f2, d))
    else:
        return Atom(f.pred, tuple(_assign_term(t, d) for t in f.args))

def _remove_arrows(f):
    "Remove '=>' and '<=>' from given formula"
    if isinstance(f, Forall) or isinstance(f, Exists):
        return f._replace(f=_remove_arrows(f.f))
    elif isinstance(f, Not):
        return f._replace(f=_remove_arrows(f.f))
    elif isinstance(f, And) or isinstance(f, Or):
        return f._replace(f1=_remove_arrows(f.f1), f2=_remove_arrows(f.f2))
    if isinstance(f, Imply):
        return Or(Not(_remove_arrows(f.f1)), _remove_arrows(f.f2))
    elif isinstance(f, Equiv):
        return And(Or(Not(_remove_arrows(f.f1)), _remove_arrows(f.f2)),
                   Or(_remove_arrows(f.f1), Not(_remove_arrows(f.f2))))
    else:
        return f

def _move_neg(f):
    'Move negation operator inwards'
    if isinstance(f, Forall) or isinstance(f, Exists):
        return f._replace(f=_move_neg(f.f))
    elif isinstance(f, And) or isinstance(f, Or):
        return f._replace(f1=_move_neg(f.f1), f2=_move_neg(f.f2))
    elif isinstance(f, Atom):
        return f
    elif isinstance(f.f, Forall):
        return Exists(f.f.xs, _move_neg(Not(f.f.f)))
    elif isinstance(f.f, Exists):
        return Forall(f.f.xs, _move_neg(Not(f.f.f)))
    elif isinstance(f.f, Not):
        return _move_neg(f.f.f)
    elif isinstance(f.f, And):
        return Or(_move_neg(Not(f.f.f1)), _move_neg(Not(f.f.f2)))
    elif isinstance(f.f, Or):
        return And(_move_neg(Not(f.f.f1)), _move_neg(Not(f.f.f2)))
    else:
        return f

def _remove_exists(f, C):
    'Replace exists "x F(x)" to "F(C1) or F(C2) or ... or F(Cn)"'
    if isinstance(f, Forall):
        return Forall(f.xs, _remove_exists(f.f, C))
    elif isinstance(f, Exists):
        fs = [ _assign(f.f, dict(zip(f.xs, cs))) for cs in product(C, repeat=len(f.xs)) ]
        return reduce(Or, fs)
    elif isinstance(f, And) or isinstance(f, Or):
        return f._replace(f1=_remove_exists(f.f1, C), f2=_remove_exists(f.f2, C))
    else:
        return f

def _remove_forall(f):
    'Replace forall x F(x) to F(x)'
    if isinstance(f, Forall):
        return _remove_forall(f.f)
    elif isinstance(f, And) or isinstance(f, Or):
        return f._replace(f1=_remove_forall(f.f1), f2=_remove_forall(f.f2))
    else:
        return f

def _move_or(f):
    '''Move OR operator inwards
    The result will be a list (conjuctions) of lists (disjunctions)
    '''
    if isinstance(f, And):
        return _move_or(f.f1) + _move_or(f.f2)
    elif isinstance(f, Or):
        return [ f1 + f2 for f1, f2 in product(_move_or(f.f1), _move_or(f.f2)) ]
    else:
        return [[f]]

def _move_and(f):
    '''Move AND operator inwards
    The result will be a list (disjunctions) of lists (conjuctions)
    '''
    if isinstance(f, Or):
        return _move_and(f.f1) + _move_and(f.f2)
    elif isinstance(f, And):
        return [ f1 + f2 for f1, f2 in product(_move_and(f.f1), _move_and(f.f2)) ]
    else:
        return [[f]]
