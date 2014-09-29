#!/usr/bin/python
#coding: utf-8

from ipdb import set_trace
from itertools import izip_longest, chain, repeat, product
import numpy as np
import sys

from astar import *
from window import *

colors = { "unused"     : [0, 0, 0, 1],
           "seen"       : [.0, 1, .0, 1],
           "obstacle"   : [1, 1, 1, 1],
           "start"      : [0, 0, 1, 1],
           "goal"       : [1, 0, 0, 1],
          }


ADJ_OP = [ (0, -1), (-1, 0),
           (0, 1), (1, 0)]

def h(p, goal):
    return abs(goal[0] - p[0]) + abs(goal[1] - p[1])

def f_search(p, depth, goal):
    return depth + h(p, goal)

class SearchState(State):
    def __init__(self, pos, goal_index, pred, depth):
        super(SearchState, self).__init__(pos, pred, depth,
                                    f_search, (pos, 0, goal_index))

class Search(Problem):
    def __init__(self, network, start, goal, dim, O):
        super(Search, self).__init__(network)
        self.start = start
        self.goal = goal
        # self.goal_index = cordHash(goal)
        self.width, self.height = dim
        self.O = O

        network.paint_node(network.cordDict[self.goal[0], self.goal[1]],
                          colors["goal"])
        network.paint_node(network.cordDict[start[0], start[1]],
                          colors["start"])

    def triggerStart(self):
        start_state = SearchState(self.start, self.goal, None, 0)

        Q = [(start_state.cost_to_goal, start_state)]
        D = { self.start : Q[0][1] }
        return astar, self, self.network, Q, D

    def genNeighbour(self, state):
        global ADJ_OP
        x, y = state.index
        return [ SearchState((x+i,y+j), self.goal, state, state.depth+1) \
                for i,j in ADJ_OP \
                    if x+i > -1 and y+j > -1 \
                    and x+i < self.width and y+j < self.height \
                    and (x+i, y+j) not in self.O]

    def destructor(self):
        self.network.paint_node(
            self.network.cordDict[self.goal[0], self.goal[1]], colors["goal"])
        self.network.update()

    def updateStates(self, new, cur):
        g = self.network.states.get_graph()
        if new.pred != cur:
            # Clear old path
            travQ = [cur]
            while travQ:
                s = travQ.pop()
                if s.pred:
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
