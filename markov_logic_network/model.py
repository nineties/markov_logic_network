from itertools import product
from parser import *
import cnf
import inference

class InvalidLogicalForm(Exception):
    'Invaalid Logical Form Error'

class InvalidModel(Exception):
    'Invalid Markov Logic Network Model'

def predicates(clauses):
    atoms = {}  # a map from predicates to their arity.
    for clause, _, _, _ in clauses:
        for f in clause:
            if f.pred in atoms and atoms[f.pred] != len(f.args):
                raise InvalidLogicalForm('Arity of {} mismatch'.format(f.pred))
            atoms[f.pred] = len(f.args)
    return atoms

def ground_atoms(predicates, constants):
    return [
        Atom(pred, list(args))
        for pred, arity in predicates.items()
        for args in product(constants, repeat=arity)
        ]

def check_constants(constants):
    for c in constants:
        if not is_constant(c):
            raise InvalidModel('{} is not a valid constant'.format(c))

class MarkovLogicNetwork(object):
    def __init__(self, formulas, constants):
        # Parse formulas
        self.formulas = [(parse(f), w) for f, w in formulas]

        check_constants(constants)
        self.constants = constants

        # Convert formulas to conjunctive normal forms (clausal forms)
        self.clauses = []
        for f, w in self.formulas:
            self.clauses.extend(cnf.translate(f, w, self.constants))

        self.predicates = predicates(self.clauses)

    def __str__(self):
        return '\n'.join('{}: {}'.format(f, w) for f, w in self.formulas)

    def ground_atoms(self):
        return ground_atoms(self.predicates, self.constants)

    def ground_clauses(self):
        print(self.clauses)

    def query(self, f1, f2, method='exact'):
        f1 = parse(f1)
        f2 = parse(f2)
        return inference.methods[method](self, f1, f2)

if __name__ == '__main__':
    mln = MarkovLogicNetwork(
            formulas = [
                ('forall x y z (Friends(x, y) and Friends(y, z) => Friends(x, z))', 0.7),
                ('forall x (not exists y Friends(x, y) => Smokes(x))', 2.3),
                ('forall x (Smokes(x) => Cancer(x))', 1.5),
                ('forall x y (Friends(x, y) => (Smokes(x) <=> Smokes(y)))', 2.2)],
            constants = ['Anna', 'Bob']
            )

    print(mln.query('Cancer(Anna)', 'Smokes(Bob)'))
