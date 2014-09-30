sym_to_variable  = dict()
variables = line.split()
symvars = symbols(...variables)
lambdafunc =lambdify(symvars, Ne(*symvars))
for symv,v in zip(symvars, variables):
    sym_to_variable[symv] = int(v)
c = Constraint(lambdafunc, (symsvars,variables), D, CNET)
