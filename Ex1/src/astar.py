#!/usr/bin/python

from collections import deque
from heapq import heappush, heappop
from ipdb import set_trace
from time import sleep

def propagate_path_improvements(old_bad, new_better):
    travQ = [old_bad]
    while travQ:
        cur = travQ.pop()
        if not cur.betterThanOther(new_better):
            old_parent = cur.setNewParent(new_better)
            travQ.append(old_parent)

""" Local search using A*
"""
def astar(network, problem, Q, D):
    numNodes = 0
    lenPath = 0

    # Q holds OPEN
    # D holds CLOSED

    if Q:
        problem.updateStates(Q[0][1], None)
        _, curState = heappop(Q)
        if curState.isGoal():
            problem.destructor(Q)
            return False
        # print "I am at " + str(curState)

        numNodes += 1
        # All nodes run "attach-and-eval" in neighbour generation
        for n in problem.genNeighbour(curState):
            if n.index in D: # seen before. 
                state = D[n.index]
                if not state.betterThanOther(n): # better?
                    # state.pred = curState
                    propagate_path_improvements(state, curState) # S = state, curState = X
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
        self.func = func
        self.funcArgs = funcArgs
        if pred:
            self.pred = pred
            depth = pred.depth + 1
        else:
            self.pred = None
            depth = 0
        self.depth = depth
        self.eval()
    def betterThanOther(self, other):
        return self.depth < other.depth
    def eval(self):
        self.cost_to_goal = self.func(*self.funcArgs)
    def __str__(self):
        return str(self.index) + "\t " + str(self.cost_to_goal)

    def setNewParent(self, new_parent):
        old_parent = self.pred
        self.eval()
        # self.__init__(self.index, new_parent, self.func, self.funcArgs)
        return old_parent

    def isEqual(self):
        return NotImplementedError("in state")

# EOF
