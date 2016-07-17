import pandas as pd
from itertools import product

# Compute probability P(f1|f2, mln) using specified method.
def simple_inference(mln, f1, f2):
    ground_atoms = mln.ground_atoms()
    ground_clauses = mln.ground_clauses()

    # Generate all configurations
    dim = len(ground_atoms)
    X = pd.DataFrame(columns=ground_atoms, data=list(product([1,0], repeat=dim)))
    print(X)

methods = {
    'simple': simple_inference
}
