import parser
import cnf

class MarkovLogicNetwork(object):
    def __init__(self, formulas, constants):
        self.formulas = [(parser.parse(f), w) for f, w in formulas]
        self.constants = constants

    def __str__(self):
        return '\n'.join('{}: {}'.format(f, w) for f, w in self.formulas)

if __name__ == '__main__':
    mln = MarkovLogicNetwork(
            formulas = [
                ('forall x y z (Friends(x, y) and Friends(y, z) => Friends(x, z))', 0.7),
                ('forall x (not exists y Friends(x, y) => Smokes(x))', 2.3),
                ('forall x (Smokes(x) => Cancer(x))', 1.5),
                ('forall x y (Friends(x, y) => (Smokes(x) <=> Smokes(y)))', 2.2)],
            constants = ['A', 'B']
            )
    print(mln)
