from parser import *
from itertools import product
from functools import reduce

class InvalidFormula(Exception):
    'Invalid Logical Formula'

def translate(f, C):
    f = remove_arrows(f)
    f = uniquify(f, [0], {})
    f = move_neg(f)
    f = remove_exists(f, C)
    f = remove_forall(f)
    f = move_and(f)
    return f

# Remove => and <=>
def remove_arrows(f):
    if isinstance(f, Forall) or isinstance(f, Exists):
        return f.__class__(f.xs, remove_arrows(f.f))
    elif isinstance(f, Not):
        return f.__class__(remove_arrows(f.f))
    elif isinstance(f, And) or isinstance(f, Or):
        return f.__class__(remove_arrows(f.f1), remove_arrows(f.f2))
    if isinstance(f, Imply):
        return Or(Not(remove_arrows(f.f1)), remove_arrows(f.f2))
    elif isinstance(f, Equiv):
        return And(Or(Not(remove_arrows(f.f1)), remove_arrows(f.f2)),
                   Or(remove_arrows(f.f1), Not(remove_arrows(f.f2))))
    else:
        return f

# Uniquify variables
def uniquify(f, i, d):
    if isinstance(f, Forall) or isinstance(f, Exists):
        d = d.copy()
        for x in f.xs:
            d[x] = 'x' + str(i[0])
            i[0] += 1
        return f.__class__([d[x] for x in f.xs], uniquify(f.f, i, d))
    elif isinstance(f, Not):
        return Not(uniquify(f.f, i, d))
    elif isinstance(f, And) or isinstance(f, Or):
        return f.__class__(uniquify(f.f1, i, d), uniquify(f.f2, i, d))
    elif isinstance(f, Atom):
        return Atom(f.pred, [rename_term(t, d) for t in f.args])
    return f

def rename(f, d):
    if isinstance(f, Forall) or isinstance(f, Exists):
        return f.__class__(f.xs, rename(f.f, d))
    elif isinstance(f, Not):
        return Not(rename(f.f, d))
    elif isinstance(f, And) or isinstance(f, Or):
        return f.__class__(rename(f.f1, d), rename(f.f2, d))
    else:
        assert(isinstance(f, Atom))
        return Atom(f.pred, [rename_term(t, d) for t in f.args])

def rename_term(t, d):
    if isinstance(t, str):
        return d.get(t, t)
    else:
        assert(isinstance(f, Apply))
        return Apply(f.fun, [rename_term(t, d) for t in f.args])

# Move negation inwards
def move_neg(f):
    if isinstance(f, Forall) or isinstance(f, Exists):
        return f.__class__(f.xs, move_neg(f.f))
    elif isinstance(f, And) or isinstance(f, Or):
        return f.__class__(move_neg(f.f1), move_neg(f.f2))
    elif isinstance(f, Atom):
        return f
    else:
        assert(isinstance(f, Not))
        if isinstance(f.f, Forall):
            return Exists(f.f.xs, move_neg(Not(f.f.f)))
        elif isinstance(f.f, Exists):
            return Forall(f.f.xs, move_neg(Not(f.f.f)))
        elif isinstance(f.f, Not):
            return move_neg(f.f.f)
        elif isinstance(f.f, And):
            return Or(move_neg(Not(f.f.f1)), move_neg(Not(f.f.f2)))
        elif isinstance(f.f, Or):
            return And(move_neg(Not(f.f.f1)), move_neg(Not(f.f.f2)))
        else:
            return f

# Replace exists x F(x) to F(C1) or F(C2) or ... or F(Cn)
def remove_exists(f, C):
    if isinstance(f, Forall):
        return Forall(f.xs, remove_exists(f.f, C))
    elif isinstance(f, Exists):
        fs = [ rename(f.f, dict(zip(f.xs, cs)))
                for cs in product(C, repeat=len(f.xs)) ]
        return reduce(lambda f1, f2: Or(f1, f2), fs)
    elif isinstance(f, And) or isinstance(f, Or):
        return f.__class__(remove_exists(f.f1, C), remove_exists(f.f2, C))
    else:
        # Since 'Not' is in innermost position, not necessary to see its argument.
        assert(isinstance(f, Atom) or isinstance(f, Not))
        return f

# Replace forall x F(x) to F(x)
def remove_forall(f):
    if isinstance(f, Forall):
        return f.f
    elif isinstance(f, And) or isinstance(f, Or):
        return f.__class__(remove_forall(f.f1), remove_forall(f.f2))
    else:
        # Since 'Not' is in innermost position, not necessary to see its argument.
        assert(isinstance(f, Atom) or isinstance(f, Not))
        return f

# Move conjunction operator outisde
# The output is a list (conjuctions) of lists (disjunctions)
def move_and(f):
    if isinstance(f, And):
        return move_and(f.f1) + move_and(f.f2)
    elif isinstance(f, Or):
        return [ f1 + f2
            for f1, f2 in product(move_and(f.f1), move_and(f.f2)) ]
    else:
        assert(isinstance(f, Atom) or isinstance(f, Not))
        return [[f]]
