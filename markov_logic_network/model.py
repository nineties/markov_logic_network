import parser
import cnf

class MarkovLogicNetwork(object):
    def __init__(self, formulas = []):
        self.formulas = []

        for f in formulas:
            self.add(f)

    def add(self, f, w):
        # Parse given formula (text) to parsed tree
        f = parser.parse(f)
        self.formulas.append((f,w))

        # Translate the tree to conjunctive normal form
        #self.clauses +=  cnf.translate(f, self.constants)
        #print(self.clauses)

    def __str__(self):
        return '\n'.join('{}: {}'.format(f, w) for f, w in self.formulas)

if __name__ == '__main__':
    mln = MarkovLogicNetwork()
    mln.add('forall x y z (Friends(x, y) and Friends(y, z) => Friends(x, z))', 0.7)
    mln.add('forall x (not exists y Friends(x, y) => Smokes(x))', 2.3)
    mln.add('forall x (Smokes(x) => Cancer(x))', 1.5)
    mln.add('forall x y (Friends(x, y) => (Smokes(x) <=> Smokes(y)))', 2.2)
    print(mln)
