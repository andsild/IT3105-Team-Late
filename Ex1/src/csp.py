#!/usr/bin/python

from copy import deepcopy
from heapq import heappop
from ipdb import set_trace
import numpy as np
from itertools import product
from string import ascii_lowercase

from time import sleep

from astar import State, Problem, astar

K = 4 # trivial initial example, later it should be integer 2..10

# If the color scheme is wrong, there will be runtimeerrors.. just saying
color_pool = {  "black"     : [0, 0, 0, 1],
            "white"     : [1, 1, 1, 1],
            "red"       : [1, 0, 0, 1],
            "green"     : [.0, 1, .0, 1],
            "blue"      : [0, 0, 1, 1],
            "yellow"    : [1, .75, 0, 1],
            "lightblue" : [0, 1, .75, 1],
        }

COLORS = [ x for x in color_pool.values() \
          if x is not color_pool["black"] and x is not color_pool["white"]][:K]

def f_csp(depth, domains):
    return depth + h_csp(domains)

def h_csp(domains):
    assigned = len(list(x for x in domains if len(x) == 1))
    promise = sum(len(x) for x in domains)
    violated = len(list(x for x in domains if len(x) == 0))

    return promise - assigned -  violated


class CSPState(State):
    def __init__(self, pred, domains, newPaint):
        self.domains = domains
        if pred:
            super(CSPState, self).__init__(id(self), pred,
                                           f_csp, (pred.depth + 1, domains))
        else:
            super(CSPState, self).__init__(id(self), pred,
                                           f_csp, (0, domains))
        self.newPaint = newPaint
    
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

class Constraint(object):
    def __init__(self, function, variables):
        self.variables = variables
        self.function = function

    def revise(self, domains):
        #TODO: there is a difference between when the domain has been
        # changed and when there is no valid solution
        # e.g. you might fail a test because the sizes of the domains
        # are the same
        #
        # Hence, I support the idea of making domains a class, with "haschanged"
        # or something.. could return two boolean flags

        domain_list = [ domains[var] for var in self.variables ]
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

class CSPColoring(Problem):
    def __init__(self, network, colors, constraints):
        super(CSPColoring, self).__init__(network)
        self.constraints = constraints
        self.colors = colors

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


    def triggerStart(self):
        self.network.clear()
        node_index = np.random.randint(low=0, high=self.network.g.num_vertices())
        # XXX
        color_index = np.random.randint(low=0, high=len(self.colors))
        # XXX:
        node_index = 1
        color_index = 0
        print "Starting with vertex %d  as color %s" % (node_index, "blue")

        start_node = self.network.g.vertex(node_index)
        start_color = self.colors[color_index]

        init_domains = [ [c for c in range(len(self.colors))] \
                            for v in self.network.g.vertices()]

        start_state = CSPState(None, init_domains, (start_node, start_color))

        init_domains[node_index] = [color_index]
        self.AC_3(start_state, node_index)

        #TODO: this Q is similar in all "problem" classes
        Q = [(start_state.cost_to_goal, start_state)]
        D = dict()
        D[start_state.index] = start_state

        # self.network.update()
        self.network.paint_node(start_node, start_color)

        return astar, self, self.network, Q, D

    def genNeighbour(self, state):
        """ A neighbour is a state S from the current state,
            where the domain of a variable has been reduced from a domain
            of size > 1 to the singleton set

        """
        new_vertex = state.genRandomVertex()
        print "picking %s as new for neigh" % (str(new_vertex))
        if new_vertex is not None:
            return self.AC_3(state, new_vertex)
        return []

    def destructor(self, Q):
        if Q:
            _, state = heappop(Q)
            for index,dom in enumerate(state.domains):
                if len(dom) == 1:
                    self.network.paint_node(index, COLORS[dom[0]])
        print "FINISHED"

    def updateStates(self, new, cur):
        if new.pred == cur:
            self.network.paint_node(*new.getLatestAddition())
        else:
            # TODO: re-check EVERYTHING
            for index,dom in enumerate(new.domains):
                if len(dom) == 1:
                    self.network.paint_node(index, COLORS[dom[0]])
                else:
                    self.network.paint_node(index, color_pool["black"])

            # self.network.paint_node(*new.getLatestAddition())
        # self.network.update()

    def solve(self):
        for e in self.network.g.edges():
            print self.network.domains[e.source()]

        start_node, start_color = self.assume()
        self.network.paint_node(start_node, start_color)

        Q = [start_node]

        while Q:
            cur = Q.pop()
            for e in start_node.out_edges():
                c = self.getColor(cur, e.target())
                if c:
                    self.network.states[e.target()] = self.colors[c]
                    self.network.update()
                Q.append(e.target())

            return True
        return False

    def getColor(self, src, dest):
        if self.network.domains[dest] \
        and self.network.states[dest] not in self.network.domains[src]:
            return self.network.domains[dest] \
                    [np.random.randint(low=0,
                                       high=len(self.network.domains[dest]))]
        return None



    def assume(self):
        pass

#EOF
