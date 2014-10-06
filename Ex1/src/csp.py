#!/usr/bin/python
from string import lowercase
from copy import deepcopy
from ipdb import set_trace
import numpy as np
from sympy import *
from itertools import chain, product, repeat, izip
from operator import add

from astar import State, Problem

def pairwise(iterable):
    a = iter(iterable)
    return izip(a,a)

def f_csp(depth, domains):
    return depth + h_csp(domains)

""" Size of domain -1, summed together
"""
def h_csp(domains):
    promise = sum(len(vi.domain)-1 for vi in domains)
    # violated = len(list(x for x in domains if len(x) == 0))

    return promise

OPERATORS = {
    "+"  : add,
    ">=" : GreaterThan,
    "<=" : LessThan,
    ">"  : StrictGreaterThan,
    "<"  : StrictLessThan,
}

class CNET(object):
    def __init__(self, num_vars, size_domain):
        self.domains = [ VertexInstance(index, range(size_domain), self) \
                                for index in range(num_vars)]
        # self.variables = range(len(domains))
        self.constraints = [ [] for _ in range(num_vars) ]

        symbol_list = [ x for x in chain(lowercase,
                                [ x+y for (x,y) in \
                                product(lowercase, (str(x) for x in range(10)))])] \
                                [:num_vars]
        self.symvars = symbols(' '.join(symbol_list))
        self.sym_dict = dict()
        self.sym_to_index = dict()
        for index,s in enumerate(self.symvars):
            self.sym_dict[str(s)] = s
            self.sym_to_index[str(s)] = index

    def getConstraint(self, vertex):
        ret = self.constraints[vertex]
        return ret

    def getDomainSize(self):
        if self.domains:
            if len(self.domains) > 0:
                return len(self.domains[0].domain)
        return -1

    def readLP(self, line):
        objects = line.split()
        operators = [ ] 

        symbol_in_func = []
        fval = 0
        for word in objects:
            if word in OPERATORS:
                operators.append(OPERATORS[word])
                continue
            for letter in word:
                # if letter is a number
                constant = 1
                if ord(letter) > 48 and ord(letter) < 58:
                    constant = int(letter)
                if letter in self.sym_dict:
                    symbol_in_func.append(constant * self.sym_dict[letter])
                    continue
                fval = constant


        lhs = None
        if len(operators) < 2:
            lhs = symbol_in_func[0]
        else:
            op_list = [ op(pair_var) for (pair_var,op) in zip(pairwise(symbol_in_func), operators)]
            lhs = op_list[0]
            for expr in op_list[:1]:
                lhs += expr

        lhs_sym, rhs_sym = symbols("lhs rhs")
        rhs = lambdify( (lhs_sym, rhs_sym), operators[-1](lhs_sym, rhs_sym))

        lc = LPConstraint(lhs, rhs, symbol_in_func, self)

    def readCanonical(self, line):
        variables = line.split()
        alphabet = list(lowercase)
        symvars = symbols(' '.join([alphabet.pop() for x in variables]))
        D = dict()
        lambdafunc = lambdify(symvars, Ne(*symvars))
        for symv,v in zip(symvars, variables):
            D[symv] = int(v)
        c = Constraint(lambdafunc,
                       [ (symv, int(v)) for (symv, v) in zip(symvars, variables)], 
                       D, self)

        for var in variables:
            self.constraints[int(var)].append(c) # redundant set of pointers,
                                              # but fast lookup
    def getRootState(self):
        return CSPState(None, [li.copy() for li in self.domains], None, None)
        # return CSPState(None, [deepcopy(li) for li in self.domains], None, None)

    def __getitem__(self, index):
        if type(index) == Constraint:
            for c in self.constraints:
                if c == self.constraints:
                    return c
            return None
        if type(index) == str:
            return self.sym_to_index[index]
        return self.domains[index]

class CSPState(State):
    def __init__(self, pred, domains, constraints, newPaint):
        self.domains = domains
        self.constraints = constraints
        if pred:
            super(CSPState, self).__init__(id(self), pred,
                                           f_csp, (pred.depth + 1, domains))
        else:
            super(CSPState, self).__init__(id(self), pred,
                                           f_csp, (0, domains))
        self.newPaint = newPaint

    def isGoal(self):
        assigned = [ len(vi.domain) == 1 for vi in self.domains]
        print assigned
        return all(assigned)

    def getUnassigned_Nonrandom(self):
        unassigned = [ index for index,vi in enumerate(self.domains) \
               if len(vi.domain) > 1 ]
        if len(unassigned) > 0:
            return unassigned[0]
        return self.genRandomVertex()
    
    def getUnassigned(self):
        #TODO: make random
        unassigned = [ index for index,vi in enumerate(self.domains) \
               if len(vi.domain) > 1 ]
        if len(unassigned) > 0:
            return unassigned[np.random.randint(0, len(unassigned))]

    def copy(self):
        doms = self.domains or []
        cons = self.constraints or []

        return CSPState(self, [ var.copy() for var in doms ],
                        [ c for c in cons], self.newPaint)

    def __getitem__(self, index):
        if type(index) == Symbol:
            return self.domains[self.cnet[str(index)]]
        return self.domains[index]



class VertexInstance(object):
    def __init__(self, index, domain, caller):
        self.index = index
        self.domain = domain
        self.cnet = caller

    def copy(self):
        return VertexInstance(self.index, [v for v in self.domain], self.cnet)

    def getCnetSelf(self):
        return self.cnet[self.index]

    def makeAssumption(self, domainIndex):
        self.domain = [self.cnet[self.index].domain[domainIndex]]

class Constraint(object):
    """ This is the CI relative to the assignment text
    """
    def __init__(self, function, vi_list, sym_to_variable, caller):
        """ Pointer to VI """
        self.vi_list = vi_list
        """ Pointer to CNET """
        self.function = function   
        self.sym_to_variable = sym_to_variable

        self.cnet = caller
        self.list_state = []

    def addState(self, state):
        self.list_state.append(state)

    def getCnetSelf(self):
        return self.cnet[self]

    def getAdjacent(self, vertex, state):
        return [ state[index] for (_,index) in self.vi_list \
                if index is not vertex]

    def canSatisfy(self, state):
        self.addState(state)
        can_satisfy = False
        arg_list = [ state[self.sym_to_variable[symv]].domain for symv,_ in self.vi_list ]
        for tup in product(*arg_list):
            if self.function(*tup):
                can_satisfy = True
                break
        return can_satisfy

class LPConstraint(Constraint):
    """ Similar to the other constraint except that in order to evaluate
        the constraint you will need to evaluate two expressions.
        E.g. to evalute "a + b <= 1", you need to evaluate both "a + b" and 
        "lhs <= rhs"
    """
    def __init__(self, lhs_func, rhs_func, vi_list, caller):
        self.lhs_func = lhs_func
        super(LPConstraint, self).__init__(rhs_func, vi_list, None, caller)

    def canSatisfy(self, state):
        self.addState(state)
        can_satisfy = False
        arg_list = [ state[self.sym_to_variable[symv]].domain for symv,_ in self.vi_list ]


def revise(variable, constraint, state):
    revised = False
    copy_domain = [x for x in variable.domain]
    for value in variable.domain:
        variable.makeAssumption(value)
        if not constraint.canSatisfy(state):
            copy_domain.remove(value)
            revised = True
    variable.domain = copy_domain
    return revised

def AC_3(cnet, state, vertex):
    Q = []
    for c in cnet.getConstraint(vertex):
        for vi in c.getAdjacent(vertex, state):
            Q.append((vi, c))
    while Q:
        v, c = Q.pop()
        origDomain = v.domain
        if revise(v, c, state):
            if len(v.domain) == 0:
                return False

            for c in cnet.getConstraint(v.index):
                for vi in c.getAdjacent(v.index, state):
                    Q.append((vi, c))
    return True

#EOF
