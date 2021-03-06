'Markov Logic Network model'

from syntax import *

class MarkovLogicNetwork(object):
    'A markov logic network is a set of formulas and weights'
    def __init__(self):
        self.mln = []

    def load(self, text):
        'Load Markov Logic Network Model'
        self.mln = parse_mln(text)

    def train(self, world, facts):
        pass

    def query(self, world, query):
        pass


#from itertools import product
#from syntax import *
#import cnf
#import inference
#
#class InvalidLogicalForm(Exception):
#    'Invaalid Logical Form Error'
#
#class InvalidModel(Exception):
#    'Invalid Markov Logic Network Model'
#
#def predicates(clauses):
#    atoms = {}  # a map from predicates to their arity.
#    for clause, _, _, _ in clauses:
#        for f in clause:
#            if f.pred in atoms and atoms[f.pred] != len(f.args):
#                raise InvalidLogicalForm('Arity of {} mismatch'.format(f.pred))
#            atoms[f.pred] = len(f.args)
#    return atoms
#
#def ground_atoms(predicates, constants):
#    return [
#        Atom(pred, args)
#        for pred, arity in predicates.items()
#        for args in product(constants, repeat=arity)
#        ]
#
#def check_constants(constants):
#    for c in constants:
#        if not is_constant(c):
#            raise InvalidModel('{} is not a valid constant'.format(c))
#
#class MarkovLogicNetwork(object):
#    def __init__(self, formulas, constants, functions={}):
#        # Parse formulas
#        self.formulas = [(parse_formula(f), w) for f, w in formulas]
#
#        check_constants(constants)
#        self.constants = constants
#
#        self.functions = functions
#
#        # Convert formulas to conjunctive normal forms (clausal forms)
#        self.clauses = []
#        for f, w in self.formulas:
#            self.clauses.extend(cnf.translate(f, w, self.constants))
#
#        self.predicates = predicates(self.clauses)
#
#    def __str__(self):
#        return '\n'.join('{}: {}'.format(f, w) for f, w in self.formulas)
#
#    def ground_atoms(self):
#        return ground_atoms(self.predicates, self.constants)
#
#    def ground_clauses(self):
#        return [
#            ([eval_atom(atom, dict(zip(xs, cs)), self.functions) for atom in atoms],
#                neg, [], w)
#            for atoms, neg, xs, w in self.clauses
#            for cs in product(self.constants, repeat=len(xs))
#            ]
#
#    def query(self, text, method='simple'):
#        pass
#
#if __name__ == '__main__':
#    mln = MarkovLogicNetwork(
#            formulas = [
#                ('forall x P(f(x)) and forall y Q(y)', 0.1),
#                ('forall x y z (Friends(x, y) and Friends(y, z) => Friends(x, z))', 0.7),
#                ('forall x (not exists y Friends(x, y) => Smokes(x))', 2.3),
#                ('forall x (Smokes(x) => Cancer(x))', 1.5),
#                ('forall x y (Friends(x, y) => (Smokes(x) <=> Smokes(y)))', 2.2)
#                ],
#            constants = ['Anna', 'Bob'],
#            functions = {'f': lambda x: 'Anna'},
#            )
#
#    print(mln.query('P(Smokes(Anna))'))
