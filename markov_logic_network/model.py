import parser
import cnf

class MarkovLogicNetwork(object):
    def __init__(self, constants, formulas = []):
        self.constants = constants
        self.formulas = []
        self.clauses = []

        for f in formulas:
            self.add(f)

    def add(self, f):
        # Parse given formula (text) to parsed tree
        f = parser.parse(f)
        self.formulas.append(f)

        # Translate the tree to conjunctive normal form
        self.clauses +=  cnf.translate(f, self.constants)
        print(self.clauses)

if __name__ == '__main__':
    model = MarkovLogicNetwork(
        constants = ['A', 'B'],
        formulas = [
            'forall x (Smokes(x) or Smokes(x) => Cancer(x))',
            'forall x y (Friends(x, y) => (Smokes(x) <=> Smokes(y)))',
            'forall x (not exists y Friends(x, y) => Smokes(x))'
            ]
        )
