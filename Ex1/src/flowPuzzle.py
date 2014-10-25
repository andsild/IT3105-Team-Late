#!/usr/bin/python

from ipdb import set_trace

from astar import *
from graphColoring import color_pool


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


class FlowPuz(Problem):
    def __init__(self, network, cnet, positions, dim, COLORS, mode="flowpuz"):
        super(FlowPuz, self).__init__(network)
        self.colors = [x for x in COLORS]

        self.width, self.height = dim
        self.mode = mode
        self.cnet = cnet
        self.nodes_count = 0
        """ The obstacle coordinates  """
        COLORS = [ x for x in color_pool.values() \
                if x is not color_pool["black"] and x is not color_pool["white"]]

        for (sx,sy,ex,ey) in positions:
            c = COLORS.pop()
            network.paint_node(network.cordDict[sx,sy], c)
            network.paint_node(network.cordDict[ex,ey], c)

        dim = self.width * self.height
        if self.width % 2 == 0:
            self.diag = [0] * ((dim / 2) + (self.width / 2))
        else:
            self.diag = [0] * ((dim / 2) + (self.width+1 / 2))
        self.copy = [0] * dim
        i = 1
        for w in range(1,self.width):
            self.diag[i] = w
            for h in range(1,w+1):
                i += 1
                self.diag[i] = w+(h * (self.width-1))
            i+= 1

        self.diag += [(dim-1) - x for x in self.diag[:-self.width-1][::-1]]
        self.it_next = [0] * len(self.diag)
        for cur,nxt in pairwise(self.diag):
            self.it_next[cur] = nxt
        print self.diag
        print self.it_next
            

    """ Send out the initial Q and implementations details
    """
    def triggerStart(self):
        # self.network.clear()

        start_state = self.cnet.getRootState()
        start_state.new_paint = start_state[0] # START AT ZERO
        # self.solver.AC_3(start_state, node_index)
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
            new_state = state.copy()
            new_state[new_vertex].makeAssumption(value)
            new_state.new_paint = new_state[new_vertex]
            print new_vertex
            # new_state.new_paint = 
            # if AC_3(self.cnet, new_state, new_vertex):
            #     yield new_state
            yield new_state
            sleep(1.0)
            break

    """ The function to be invoked at the end of a search
    """
    def destructor(self, final_state=None):
        print "Nodes generated --->",self.nodes_count
        self.network.paint_node(
            self.network.cordDict[self.goal[0], self.goal[1]], colors["goal"])
        self.network.update()

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

def tryConnection(p1, p2):
    if outOfMap \
    or connectedWith(p1, p2) or isConnected(p1) or isConnected(p2) \
    or causesLoop:
        return False
    
    return True

def validate():
    # ensure the entire board is valid
    pass

def checkForSE():
    return True

# def chooseCon(point):
#     if isPathStartOrEnd(pos1):
#         if notConnected(point):
#             if not point.parent.isConnedtedEast():
#                 try East:
#                     pass
#                 raise:
#                     pass
#             if checkForSE(point):
#                 try South:
#                     pass
#                 raise: pass
#             else: # north, west
#                 # keep going
#                 pass
#     else: #  not connected, just another interior point
#         pass
#
#
#
#            
#
#
#
#
#
#

# EOF
