#!/usr/bin/python

from ipdb import set_trace
from astar import State, Problem, astar
from csp import *

class Ngram(Problem):
    def __init__(self, network, cnet, rows, columns):
        super(Ngram, self).__init__(network)
        self.cnet = cnet
        self.nodes_count = 0
        self.rows = rows
        self.columns = columns

    """ Send out the initial Q and implementations details
    """
    def triggerStart(self):
        self.network.clear()
        start_state = self.cnet.getRootState()
        start_state.new_paint = start_state[0]

        Q = [(start_state.cost_to_goal, start_state)]
        D = dict()
        D[start_state.index] = start_state

        return astar, self, self.network, Q, D

    """ Generate neighbours from the current state
    """
    def genNeighbour(self, state):
        

    """ The function to be invoked at the end of a search
    """
    def destructor(self, final_state=None):
        print "Nodes generated --->",self.nodes_count
        self.network.update()

    """ Paint nodes after iteration in local search
        @param new is the lates state entered
        @param cur is the state before param new
    """
    def updateStates(self, new, cur):
        g = self.network.states.get_graph()
        # If the new state is a direct successor of the previous state,
        # the paint job is simple: only paint one more node
        # otherwise, traverse back, "unpaint", and add the new path
        if new.pred != cur:
            # Clear old path
            travQ = [cur]
            while travQ:
                s = travQ.pop()
                if s and s.pred:
                    travQ = [s.pred]
                    self.network.states[g.vertex(
                        self.network.cordDict[s.index[0], s.index[1]])] \
                            = colors["unused"]
            # Color new
            travQ = [new]
            while travQ:
                s = travQ.pop()
                if s.pred:
                    travQ = [s.pred]
                    self.network.states[g.vertex(
                        self.network.cordDict[s.index[0], s.index[1]])] \
                            = colors["seen"]
        else:
            self.network.states[g.vertex(
                self.network.cordDict[new.index[0], new.index[1]])] \
                    = colors["seen"]
        self.network.update()
            

# EOF
