#!/usr/bin/python

from ipdb import set_trace
from astar import State, Problem, astar
from csp import *

class Ngram(Problem):
    def __init__(self, network, cnet, p_rows, p_cols, colors):
        super(Ngram, self).__init__(network)
        self.cnet = cnet
        self.p_rows = p_rows
        self.p_cols = p_cols
        self.colors = colors
        self.mode = "Ngrams"

    """ Send out the initial Q and implementations details
    """
    def triggerStart(self):
        self.nodes_gen = 1
        self.nodes_exp = 1
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
        self.nodes_exp += 1
        new_vertex = state.getUnassigned_Nonrandom()  # VERTEX NUMBERING
        # STARTS AT TOP COL, THEN PROCEEDS TO RIGHT THEN EACH ROW FROM..
        print "selecting %d which can get domain %s " \
            %  (new_vertex, str(state[new_vertex].domain))
        for index,value in enumerate(state[new_vertex].domain):
            print "Assuming value %s" % (str(value))
            new_state = state.copy()
            # new_state[new_vertex].makeAssumption(index, True)
            new_state[new_vertex].makeAssumption(value)
            if AC_3_NGRAM(self.cnet, new_state, new_vertex):
                self.nodes_gen += 1
                yield new_state

    """ The function to be invoked at the end of a search
    """
    def destructor(self, final_state=None):
        print "Nodes expanded --->",self.nodes_exp
        print "Nodes generated --->",self.nodes_gen
        if final_state:
            for vi in final_state.domains:
                if len(vi.domain) == 1:
                    for val in vi.domain[0]:
                        if val > 0:
                            self.network.paint_node(val-1,self.colors["green"])
                        else:
                            self.network.paint_node(abs(val)-1,self.colors["black"])

        self.network.update()
        print'FINISHED'

    """ Paint nodes after iteration in local search
        @param new is the lates state entered
        @param cur is the state before param new
    """
    def updateStates(self, new, cur):
        for vi in new.domains:
            if len(vi.domain) == 1:
                for val in vi.domain[0]:
                    if val > 0:
                        self.network.paint_node(val-1,self.colors["green"])
                    else:
                        self.network.paint_node(abs(val)-1,self.colors["black"])
        self.network.update()
# EOF
