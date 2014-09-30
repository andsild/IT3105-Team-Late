#!/usr/bin/python
from string import lowercase
from copy import deepcopy
from ipdb import set_trace
import numpy as np
from sympy import *
from itertools import product

from astar import State, Problem

def f_csp(depth, domains):
    return depth + h_csp(domains)

""" Size of domain -1, summed together
"""
def h_csp(domains):
    assigned = len(list(x for x in domains if len(x) == 1))
    promise = sum(len(x) for x in domains)
    violated = len(list(x for x in domains if len(x) == 0))

    return promise - assigned -  violated

class CNET(object):
    def __init__(self, num_vars, init_domain):
        self.domains = [ VertexInstance(index, [x for x in init_domain]) \
                                for index in range(num_vars)]
        # self.variables = range(len(domains))
        self.constraints = [ [] for _ in range(num_vars) ]

    def getConstraint(self, vertex, caller):
        ret = self.constraints[vertex]
        ret.addVI(caller)
        return ret


    def readCanonical(self, line):
        variables = line.split()
        mapped_vars = [ index for index,_ in enumerate(variables) ]
        alphabet = list(lowercase)
        symvars = symbols(' '.join([alphabet.pop() for x in variables]))

        lambdafunc = lambdify(symvars, Ne(*symvars))

        for var in mapped_vars:
            self.constraints[var].append(lambdafunc)

    # def addConstraint(self, function, variable_indexes):
    #     c = Constraint(l, [self.domains[i] for i in variable_indexes])
    #
    #     for i in variable_indexes:
    #         self.domains[i].append(



class CSPState(State):
    """ This will be the VI per the assignment text
    """
    def __init__(self, pred, domains, newPaint):
        self.domains = domains
        if pred:
            super(CSPState, self).__init__(id(self), pred,
                                           f_csp, (pred.depth + 1, domains))
        else:
            super(CSPState, self).__init__(id(self), pred,
                                           f_csp, (0, domains))
        self.newPaint = newPaint

    def isGoal(self):
        return self.cost_to_goal == -1
    
    def genRandomVertex(self):
        #TODO: make random
        ret = [ index for index,dom in enumerate(self.domains) \
               if len(dom) > 1 ]
        if not ret:
            # return None
            return np.random.randint(low=0, high=len(self.domains))
        return ret[0]

    def getLatestAddition(self):
        return self.newPaint

class VertexInstance(object):
    def __init__(self, index, domain):
        self.index = index
        self.domain = domain

    def copy(self):
        return VertexInstance(self.index, [v for v in domain])

class Constraint(object):
    """ This is the CI relative to the assignment text
    """
    def __init__(self, function, variables):
        """ Pointer to VI """
        self.variables = variables 
        """ Pointer to CNET constraint """
        self.function = function   

        self.list_vi = []

    def addVI(self, vi):
        self.list_vi.append(vi)

    def revise(self, vi):
        #TODO: there is a difference between when the domain has been
        # changed and when there is no valid solution
        # e.g. you might fail a test because the sizes of the domains
        # are the same
        #
        # Hence, I support the idea of making domains a class, with "haschanged"
        # or something.. could return two boolean flags

        domain_list = [ vi.domains[var] for var in self.variables ]
        can_confine = False

        setme = [ index for index,x in enumerate(domain_list) if len(x) == 1 ]
        if len(setme) == 0:
            return []
        use_node = setme[0]

        confined = []

        print self.variables
        print domain_list
        print "set use_node to %d" % (use_node) 
        for tup in product(*domain_list): # all possible domain mappings
            indexes = range(len(tup))
            if not self.function(*tup):
                for mapped_index, index in enumerate(self.variables):
                    if mapped_index is use_node: continue
                    confined.append(index)
                    domain_list[mapped_index].remove(tup[mapped_index])
                    can_confine = True

        print domain_list
        return confined

class CSPSolver(object):
    def __init__(self, constraints):
        self.constraints = constraints

    def rec_narrow(self, new_vertex, dom_copy):
        Q = [new_vertex]
        color_trans = [ [ k for x in LIST for k,v in color_pool.iteritems() \
                        if v == COLORS[x] ] for LIST in dom_copy ]
        while Q:
            new_vertex = Q.pop()
            print "\t checking %d ..." % (new_vertex),
            print " residuals are " + str(color_trans)
            constraints = self.constraints[new_vertex]
            Q += [ node for revised_list in \
                    [c.revise(dom_copy) for c in constraints] \
                    for node in revised_list]
            color_trans = [ [ k for x in LIST for k,v in color_pool.iteritems() \
                            if v == COLORS[x] ] for LIST in dom_copy ]
            if any(list(len(x) == 0 for x in dom_copy)):
                print " FAILED, residuals are " + str(color_trans)
                return False
            print " residuals are " + str(color_trans)
        return True

    def AC_3(self, state, new_vertex):
        for val in state.domains[new_vertex]:
            dom_copy = [ deepcopy(li) for li in state.domains]
            dom_copy[new_vertex] = [val]
            color_trans = [ [ k for x in LIST for k,v in color_pool.iteritems() \
                             if v == COLORS[x] ] for LIST in dom_copy ]
            print "Doing vertex %d with %s" % (new_vertex, color_trans[new_vertex][0])

            # if any(c.revise(new_vertex, dom_copy) for c in constraints):
            #     # check if we fucked any domain to zero

            if not self.rec_narrow(new_vertex, dom_copy):
                continue
            print " PASSED, residuals are " + str(color_trans)

            # We know we constrained the domain, but did a valid solution remain?

            new_state = CSPState(state, dom_copy, (new_vertex, COLORS[val]))
            if all( [len(x) == 1 for x in dom_copy] ):
                print "setting terminating condition true pre-emptive"
                new_state.cost_to_goal = -1
            yield new_state

#EOF
