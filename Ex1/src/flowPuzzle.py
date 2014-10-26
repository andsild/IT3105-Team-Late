#!/usr/bin/python

from ipdb import set_trace

from astar import *
from graphColoring import color_pool
from csp import *

def f_numberlink(depth, domains):
    return depth + h_numberlink(domains)

""" Size of domain -1, summed together
"""
def h_numberlink(domains):
    # promise = sum(len(vi.domain)-1 for vi in domains)
    promise = 0
    count = [0] * 50
    for vi in domains:
        lv = len(vi.domain)-1
        promise += len(vi.domain)-1
        if not lv:
            count[vi.domain[0]] += 1
    return promise


""" Start with closest pair of nodes?

    backtracking - start somewhere cool and abandon it as soon as
    you discover it is a weak solution : you are pruning the search tree
"""
from itertools import tee, izip
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def lookupColor(index):
    colors = [ y for x,y in color_pool.iteritems() \
            if y is not color_pool["black"] and y is not color_pool["white"]]
    colors.sort()
    for x,y in color_pool.iteritems():
        if y is colors[index]:
            return x

class FlowPuz(Problem):
    def __init__(self, network, cnet, positions, dim, COLORS, mode="flowpuz"):
        super(FlowPuz, self).__init__(network)
        self.colors = [ x for x in color_pool.values() \
                if x is not color_pool["black"] and x is not color_pool["white"]]
        self.colors.sort()

        self.width, self.height = dim
        self.mode = mode
        self.cnet = cnet
        self.nodes_count = 0
        """ The obstacle coordinates  """
        for index,(sx,sy,ex,ey) in enumerate(positions):
            cnet[network.map2d1d(sx,sy)].makeAssumption(index)
            cnet[network.map2d1d(ex,ey)].makeAssumption(index)
            network.paint_node(network.cordDict[sx,sy], self.colors[index])
            network.paint_node(network.cordDict[ex,ey], self.colors[index])
            # reduce their domain to singleton

        dim = self.width * self.height
        self.diag = [0] * dim
        # if self.width % 2 == 0:
        #     self.diag = [0] * ((dim / 2) + (self.width / 2))
        # else:
        #     self.diag = [0] * ((dim / 2) + (self.width+1 / 2))
        # self.copy = [0] * dim
        i = 1
        for w in range(1,self.width):
            self.diag[i] = w
            for h in range(1,w+1):
                i += 1
                self.diag[i] = w+(h * (self.width-1))
            i+= 1
        for h in range(1,self.height+1):
            use = (self.width-1) + (h * self.width)
            for pos in range(use,dim,self.width-1):
                self.diag[i] = pos
                i+= 1

        # self.diag += [(dim-1) - x for x in self.diag[:-self.width-1][::-1]]
        self.it_next = [0] * len(self.diag)
        for cur,nxt in pairwise(self.diag):
            self.it_next[cur] = nxt


    """ Send out the initial Q and implementations details
    """
    def triggerStart(self):
        # self.network.clear()

        start_state = self.cnet.getRootState(f_numberlink)
        start_state.new_paint = start_state[0] # START AT ZERO
        Q = [(start_state.cost_to_goal, start_state)]
        D = dict()
        D[start_state.index] = start_state

        return astar, self, self.network, Q, D

    """ Generate neighbours from the current state
    """
    def genNeighbour(self, state):
        # check newpaint, generate next..
        new_vertex = self.it_next[state.new_paint.index]
        for value in state[new_vertex].domain:
            print "vertex: %d\tassuming value %s " % (new_vertex, lookupColor(value))
            new_state = state.copy()
            new_state[new_vertex].makeAssumption(value, False)
            new_state.new_paint = new_state[new_vertex]
            if AC_3(self.cnet, new_state, new_vertex):
                yield new_state
            # yield new_state
            sleep(0.2)

    """ The function to be invoked at the end of a search
    """
    def destructor(self, final_state=None):
        print "Nodes generated --->",self.nodes_count
        if final_state:
            for vi in final_state.domains:
                if len(vi.domain) == 1:
                    self.network.paint_node(vi.index, self.colors[vi.domain[0]])
        self.network.update()
        print "FINISHED"

    """ Paint nodes after iteration in local search
        @param new is the lates state entered
        @param cur is the state before param new
    """
    def updateStates(self, new, cur):
        for vi in new.domains:
            if len(vi.domain) == 1:
                self.network.paint_node(vi.index, self.colors[vi.domain[0]])
            else:
                self.network.paint_node(vi.index, color_pool["black"])
        self.network.update()
# EOF
