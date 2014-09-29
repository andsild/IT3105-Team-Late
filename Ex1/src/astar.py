#!/usr/bin/python

from collections import deque
from heapq import heappush, heappop
from ipdb import set_trace
from time import sleep

""" Local search using A*
"""
def astar(network, problem, Q, D):
    numNodes = 0
    lenPath = 0

    if Q and not Q[0][1].isGoal():
        problem.updateStates(Q[0][1], None)
        _, curState = heappop(Q)
        # print "I am at " + str(curState)

        numNodes += 1
        for n in problem.genNeighbour(curState):
            if n.index in D:
                state = D[n.index]
                if not state.betterThanOther(n):
                    state.pred = curState
                continue
            D[n.index] = n
            # print "\t see feasible neighbour: " + str(n)
            heappush(Q, (n.cost_to_goal, n))

        sleep(0.1)
        return True
    # while curState.pred:
    #     curState = curState.pred
  #     lenPath += 1
    problem.destructor(Q)
    return False

class Problem(object):
    def __init__(self, network):
        self.network = network
    def triggerStart(self):
        raise NotImplementedError("abstract class")
    def genNeighbour(self, state):
        raise NotImplementedError("abstract class")
    def destructor(self, Q):
        raise NotImplementedError("abstract class")
    def updateStates(self, new, cur):
        raise NotImplementedError("abstract class")

class State(object):
    def __init__(self, index, pred, func, funcArgs):
        self.index = index
        self.cost_to_goal = func(*funcArgs)
        if pred:
            self.pred = pred
            depth = pred.depth + 1
        else:
            self.pred = None
            depth = 0
        self.depth = depth
    def betterThanOther(self, other):
        return self.depth < other.depth
    def __str__(self):
        return str(self.index) + "\t " + str(self.cost_to_goal)

    def isEqual(self):
        return NotImplementedError("in state")

# EOF
