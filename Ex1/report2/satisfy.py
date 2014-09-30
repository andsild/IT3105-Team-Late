self.addState(state)
can_satisfy = False
arg_list = ... # ordered list of possible domain value in the constraint
for tup in product(*arg_list):
    if self.function(*tup):
        can_satisfy = True
        break
return can_satisfy

