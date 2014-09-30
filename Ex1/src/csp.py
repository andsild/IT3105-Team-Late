#!/usr/bin/python
from string import lowercase
from copy import deepcopy
from ipdb import set_trace
import numpy as np
from sympy import *
from itertools import product, repeat

from astar import State, Problem

def f_csp(depth, domains):
    return depth + h_csp(domains)

""" Size of domain -1, summed together
"""
def h_csp(domains):
    promise = sum(len(vi.domain)-1 for vi in domains)
    # violated = len(list(x for x in domains if len(x) == 0))

    return promise

class CNET(object):
    def __init__(self, num_vars, size_domain):
        self.domains = [ VertexInstance(index, range(size_domain), self) \
                                for index in range(num_vars)]
        # self.variables = range(len(domains))
        self.constraints = [ [] for _ in range(num_vars) ]

    def getConstraint(self, vertex):
        ret = self.constraints[vertex]
        return ret

    def getDomainSize(self):
        if self.domains:
            if len(self.domains) > 0:
                return len(self.domains[0].domain)
        return -1

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
        variable = self.domains[np.random.randint(low=0, high=len(self.domains))]
        # domain = np.random.randint(low=0, high=self.getDomainSize())
        # variable.makeAssumption(domain)

        return CSPState(None, [deepcopy(li) for li in self.domains], None, None)

    def __getitem__(self, index):
        if type(index) == Constraint:
            for c in self.constraints:
                if c == self.constraints:
                    return c
            return None
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
        return all(assigned)

    def genNotSoRandomVertex(self):
        unassigned = [ index for index,vi in enumerate(self.domains) \
               if len(vi.domain) > 1 ]
        if len(unassigned) > 0:
            return unassigned[0]
        return self.genRandomVertex()
    
    def genRandomVertex(self):
        #TODO: make random
        unassigned = [ index for index,vi in enumerate(self.domains) \
               if len(vi.domain) > 1 ]
        if len(unassigned) > 0:
            return unassigned[np.random.randint(0, len(unassigned))]

    def copy(self):
        doms = self.domains or []
        cons = self.constraints or []

        return CSPState(self, [ var.copy() for var in doms ],
                        [ c for c in cons], None)

    def __getitem__(self, index):
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
        self.domain = [deepcopy(self.cnet[self.index].domain[domainIndex])]

class Constraint(object):
    """ This is the CI relative to the assignment text
    """
    def __init__(self, function, vi_list, sym_to_variable, caller):
        """ Pointer to VI """
        self.vi_list = vi_list
        """ Pointer to CNET constraint """
        self.function = function   
        self.sym_to_variable = sym_to_variable

        self.cnet = caller
        self.list_state = []

    def addState(self, state):
        self.list_state.append(state)

    def getCnetSelf(self):
        return self.cnet[self]

    def getAdjacent(self, vertex, state):
        set_trace()
        return [ [state[v.index]] for v in state.domains \
                if v.index not in [ val for (_,val) in self.vi_list ] ]

    def narrow(self, state):
        self.addState(state)
        can_satisfy = False

        arg_list = [ state[self.sym_to_variable[symv]].domain for symv,_ in self.vi_list ]

        #TODO: this currently only works if position is not relevant
        # a constraint like x + 2y < 10 would not work because x,y is not different
        for tup in product(*arg_list):
            if self.function(*tup):
                can_satisfy = True
        return can_satisfy

# # domain_list = [ vi. for var in vi.variables ]
#
#         setme = [ index for index,x in enumerate(domain_list) if len(x) == 1 ]
#         if len(setme) == 0:
#             return []
#         use_node = setme[0]
#
#         confined = []
#
#         print self.variables
#         print domain_list
#         print "set use_node to %d" % (use_node) 
#         for tup in product(*domain_list): # all possible domain mappings
#             indexes = range(len(tup))
#             if not self.function(*tup):
#                 for mapped_index, index in enumerate(self.variables):
#                     if mapped_index is use_node: continue
#                     confined.append(index)
#                     domain_list[mapped_index].remove(tup[mapped_index])
#                     can_confine = True
#
#         print domain_list
#         return confined


def revise(variable, constraint, state):
    revised = False
    orig_domain = [x for x in variable.domain]
    for value in variable.domain:
        # vi_copy = VertexInstance(variable.index, [ value ], variable.cnet)
        variable.makeAssumption(value)
        if not constraint.narrow(state):
            orig_domain.remove(value)
            revised = True
    variable.domain = orig_domain
    return revised


def AC_3(cnet, state, vertex):
    Q = [(state[vertex],c) for c in cnet.getConstraint(vertex)]
    while Q:
        v, c = Q.pop()
        # Now all I have to do is to check the domain of v
        if revise(v, c, state):
            if len(v.domain) == 0:
                print "REDUCED"
                return False
            for neighbours in c.getAdjacent(v, state):
                Q += [(neighbours,c) for c in cnet.getConstraint(neighbours)]
    return True

    # def AC_3(self, state, new_vertex):
    #     for val in state.domains[new_vertex]:
    #         dom_copy = [ deepcopy(li) for li in state.domains]
    #         dom_copy[new_vertex] = [val]
    #         color_trans = [ [ k for x in LIST for k,v in color_pool.iteritems() \
    #                          if v == COLORS[x] ] for LIST in dom_copy ]
    #         print "Doing vertex %d with %s" % (new_vertex, color_trans[new_vertex][0])
    #
    #         # if any(c.revise(new_vertex, dom_copy) for c in constraints):
    #         #     # check if we fucked any domain to zero
    #
    #         if not self.rec_narrow(new_vertex, dom_copy):
    #             continue
    #         print " PASSED, residuals are " + str(color_trans)
    #
    #         # We know we constrained the domain, but did a valid solution remain?
    #
    #         new_state = CSPState(state, dom_copy, (new_vertex, COLORS[val]))
    #         if all( [len(x) == 1 for x in dom_copy] ):
    #             print "setting terminating condition true pre-emptive"
    #             new_state.cost_to_goal = -1
    #         yield new_state
    #
    #
# class CSPSolver(object):
#     def __init__(self, constraints):
#         self.constraints = constraints
#
#     def rec_narrow(self, new_vertex, dom_copy):
#         Q = [new_vertex]
#         color_trans = [ [ k for x in LIST for k,v in color_pool.iteritems() \
#                         if v == COLORS[x] ] for LIST in dom_copy ]
#         while Q:
#             new_vertex = Q.pop()
#             print "\t checking %d ..." % (new_vertex),
#             print " residuals are " + str(color_trans)
#             constraints = self.constraints[new_vertex]
#             Q += [ node for revised_list in \
#                     [c.revise(dom_copy) for c in constraints] \
#                     for node in revised_list]
#             color_trans = [ [ k for x in LIST for k,v in color_pool.iteritems() \
#                             if v == COLORS[x] ] for LIST in dom_copy ]
#             if any(list(len(x) == 0 for x in dom_copy)):
#                 print " FAILED, residuals are " + str(color_trans)
#                 return False
#             print " residuals are " + str(color_trans)
#         return True
#EOF
