#!/usr/bin/python
from string import lowercase, uppercase
from ipdb import set_trace
import numpy as np
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from itertools import chain, product, repeat
from operator import add

from astar import State, Problem

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
        for s in self.symvars:
            self.sym_dict[str(s)] = s


    def getConstraint(self, vertex):
        ret = self.constraints[vertex]
        return ret

    def getDomainSize(self):
        if self.domains:
            if len(self.domains) > 0:
                return len(self.domains[0].domain)
        return -1

            
    def addLessThan(self,vertexes, function, eval_value):
        use_vars = sorted(filter(set(function).__contains__, set(uppercase)))
        symvars = symbols(' '.join(use_vars))
       # lambdafunc = parse_expr(function)
        lambdafunc = lambdify(symvars, LessThan(parse_expr(function),eval_value))
        D = {}
        for symv,v in zip(symvars, vertexes):
            D[symv] = v
        c = Constraint(lambdafunc,
                       [ (symv, int(v)) for (symv, v) in zip(symvars, vertexes)], 
                       D, self)
        for var in vertexes:
            self.constraints[var].append(c) # redundant set of pointers,
    
    def addLambda(self,vertexes,string, function, eval_value):
        use_vars = sorted(filter(set(string).__contains__, set(uppercase)))
        symvars = symbols(' '.join(use_vars))
        # lambdafunc = parse_expr(function)
        check = {}
        for v in symvars:
            check[(str(v))] = v
        D = {}
        for symv,v in zip(symvars, vertexes):
            D[symv] = v
        c = Constraint(function,
                       [ (symv, int(v)) for (symv, v) in zip(symvars, vertexes)], 
                       D, self)
        for var in vertexes:
            self.constraints[var].append(c) # redundant set of pointers,


    def addCons(self,vertexes, function, eval_value):
        use_vars = sorted(filter(set(function).__contains__, set(uppercase)))
        symvars = symbols(' '.join(use_vars))
        # lambdafunc = parse_expr(function)
        check = {}
        for v in symvars:
            check[(str(v))] = v
        lambdafunc = lambdify(symvars, Eq(eval_value,parse_expr(function)))
        # print lambdafunc(1,1,1,1,1)
        D = {}
        for symv,v in zip(symvars, vertexes):
            D[symv] = v
        c = Constraint(lambdafunc,
                       [ (symv, int(v)) for (symv, v) in zip(symvars, vertexes)], 
                       D, self)
        for var in vertexes:
            self.constraints[var].append(c) # redundant set of pointers,
    

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
    def getRootState(self, func=f_csp):
        return CSPState(None, [li.copy() for li in self.domains], None, None, func)

    def __getitem__(self, index):
        if type(index) == Constraint:
            for c in self.constraints:
                if c == self.constraints:
                    return c
            return None
        return self.domains[index]

class CNET3(CNET):
    def __init__(self, p_rows, p_cols):
        self.domains = []
        for index,item in enumerate(chain(p_cols, p_rows)):
            self.domains.append(VertexInstance(index,item,self))

        self.constraints = [ [] for _ in range(len(p_rows)+len(p_cols)) ]
        
        #func = "len(FiniteSet(A).intersect(FiniteSet(B)))"
        func = lambda A,B: len(A.intersection(B))

        for i in range(len(p_cols)):
            for j in range(len(p_cols),len(p_rows)+len(p_cols)):
                self.addLambda([i,j],"AB",func,1)
                # self.addCons([j,i],func,1)
        symbol_list = [ x for x in chain(lowercase,
                                [ x+y for (x,y) in \
                                product(lowercase, (str(x) for x in range(10)))])] \
                                [:len(p_rows)+len(p_cols)]
        self.symvars = symbols(' '.join(symbol_list))
        self.sym_dict = dict()
        for s in self.symvars:
            self.sym_dict[str(s)] = s

class CSPState(State):
    def __init__(self, pred, domains, constraints, new_paint, f_csp):
        self.domains = domains
        self.constraints = constraints
        self.func = f_csp
        if pred:
            super(CSPState, self).__init__(id(self), pred,
                                           f_csp, (pred.depth + 1, domains))
        else:
            super(CSPState, self).__init__(id(self), pred,
                                           f_csp, (0, domains))
        self.new_paint = new_paint

    def isGoal(self):
        assigned = [ len(vi.domain) == 1 for vi in self.domains]
        return all(assigned)

    def getUnassigned_Nonrandom(self):
        unassigned = [ (len(vi.domain),index) for index,vi in enumerate(self.domains) \
               if len(vi.domain) > 1 ]
        if len(unassigned) > 0:
            # return min(unassigned)[1]
            return unassigned[-1][1]
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
                        [ c for c in cons], self.new_paint, self.func)

    def __getitem__(self, index):
        return self.domains[index]

class VertexInstance(object):
    def __init__(self, index, domain, caller):
        self.index = index
        self.domain = domain
        self.cnet = caller

    def copy(self):
        if self.domain and type(self.domain[0]) == set:
            return VertexInstance(self.index, [set([x for x in v]) for v in self.domain], self.cnet)
        return VertexInstance(self.index, [v for v in self.domain], self.cnet)
        # return VertexInstance(self.index, [v for v in self.domain], self.cnet)

    def getCnetSelf(self):
        return self.cnet[self.index]

    def makeAssumption(self, domainIndex, is_index=False):
        if is_index:
            self.domain = [self.cnet[self.index].domain[domainIndex]]
        else:
            self.domain = [domainIndex]

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
        for vi in c.getAdjacent(vertex, state): # this can be used, vertex is assumed
            # print "%d is considered adjacent to %d" % (vi.index, vertex)
            Q.append((vi, c))
    origD = state[vertex].domain[0]
    while Q:
        v, c = Q.pop()
        origDomain = [x for x in v.domain]
        if revise(v, c, state):
            if len(v.domain) == 0:
                return False
            for c in cnet.getConstraint(v.index):
                for vi in c.getAdjacent(v.index, state):
                    Q.append((vi, c))
    return True

def revise_NGARM(variable, constraint, state):
    revised = False
    copy_domain = [ set([y for y in x]) for x in variable.domain]
    for index,value in enumerate(variable.domain): # FIXME: this index is wrong
        variable.makeAssumption(value, is_index=False)
        if not constraint.canSatisfy(state):
            copy_domain.remove(value)
            revised = True
    variable.domain = copy_domain
    return revised

def AC_3_NGRAM(cnet, state, vertex):
    Q = []
    for c in cnet.getConstraint(vertex):
        for vi in c.getAdjacent(vertex, state):
            Q.append((vi, c))
    while Q:
        v, c = Q.pop()
        if revise_NGARM(v, c, state):
            if len(v.domain) == 0:
                return False

            for c in cnet.getConstraint(v.index):
                for vi in c.getAdjacent(v.index, state):
                    Q.append((vi, c))

    return True

#EOF
