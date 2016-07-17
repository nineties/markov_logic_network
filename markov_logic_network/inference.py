# Compute probability P(f1|f2, mln) using specified method.
def simple_inference(mln, f1, f2):
    ground_atoms = mln.ground_atoms()
    ground_clauses = mln.ground_clauses()

    print(ground_atoms)
    print(ground_clauses)
    print(len(ground_clauses))

methods = {
    'simple': simple_inference
}
