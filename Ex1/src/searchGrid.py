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
breadth_value = 0
depth_value = 0

""" The heuristic for 2d grid search
    Currently, itertools the manhattan distance from the current cartesian point
    to The global.
"""
def h(p, goal):
    return abs(goal[0] - p[0]) + abs(goal[1] - p[1])

""" The evaluation function for a given state in A* 2D-search.
    It try_Try_Except_Finallykes a heuristic function and adds the depth
"""
def f_search(p, depth, goal):
    return depth + h(p, goal)
''' The simple function for breadth firs search
'''
def bfs():
    global breadth_value
    print breadth_value
    breadth_value += 1
    return  breadth_value
''' The simple function for depth first search
'''
def dfs():
    global depth_value
    depth_value -= 1
    return depth_value

""" A state, per A*, to be used in search
    A* does not, in this implementation need any more properties than its superclass.
"""
class SearchState(State):
    def __init__(self, pos, goal_index, pred, depth,mode):
        if mode is "depth":
            super(SearchState, self).__init__(pos, pred,
                                    dfs, (pos, depth, goal_index))
        elif mode is "breadth":
            super(SearchState, self).__init__(pos, pred,
                                    bfs, (pos, depth, goal_index))
        else:
            super(SearchState, self).__init__(pos, pred,
                                    f_search, (pos, depth, goal_index))
        self.goal_index = goal_index

    def isGoal(self):
        return self.index == self.goal_index

    def __str__(self):
        return "State at pos %s and depth %d" % (str(self.index), self.depth)

""" A problem class for search that can be used by a local search
"""
class Search(Problem):
    def __init__(self, network, start, goal, dim, O,mode):
        super(Search, self).__init__(network)
        self.start = start
        self.goal = goal
        self.width, self.height = dim
        self.mode = mode
        """ The obstacle coordinates  """
        self.O = O

        network.paint_node(network.cordDict[self.goal[0], self.goal[1]],
                          colors["goal"])
        network.paint_node(network.cordDict[start[0], start[1]],
                          colors["start"])

    """ Send out the initial Q and implementations details
    """
    def triggerStart(self):
        start_state = SearchState(self.start, self.goal, None, 0, self.mode)

        Q = [(start_state.cost_to_goal, start_state)]
        D = { self.start : Q[0][1] }

        return astar, self, self.network, Q, D

    """ Generate neighbours from the current state
    """
    def genNeighbour(self, state):
        global ADJ_OP 
        x, y = state.index
        return [ SearchState((x+i,y+j), self.goal, state, state.depth+1, self.mode) \
                for i,j in ADJ_OP \
                    if x+i > -1 and y+j > -1 \
                    and x+i < self.width and y+j < self.height \
                    and (x+i, y+j) not in self.O]

    """ The function to be invoked at the end of a search
    """
    def destructor(self, final_state=None):
        self.network.paint_node(
            self.network.cordDict[self.goal[0], self.goal[1]], colors["goal"])
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
