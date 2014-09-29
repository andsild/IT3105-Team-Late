#!/usr/bin/python

from ipdb import set_trace
import numpy as np
from sympy import *

from searchGrid import *
from csp import *
from network import *


def searchParams(filename):
    def retMarks(obs_cords):
        for line in obs_cords:
            start_x, start_y, width, height = line
            # width, height = width+1, height+1

            if height == 0 and width == 0:
                yield np.array( [] )
            if height == 0:
                height += 1
            if width == 0:
                width += 1

            yield np.array( [ list(y for x in range(start_y, start_y + height) for y in range(start_x, start_x + width)),
                            list(x for x in range(start_y, start_y + height) for y in range(start_x, start_x + width))]
                        )

    inData = open(filename)

    inData = inData.read().split("\n")
    inData = [ [int(num) for num in x.split()] for x in inData]
    inData.pop()

    width, height = inData[0]
    startX, startY = inData[1]
    goalX, goalY = inData[2]
    obs_cords = inData[3:]

    O = set()
    cords = np.array( [ list(y for x in range(height) for y in range(width)),
                        list(x for x in range(height-1, -1, -1) for y in range(width))]
                    )
    
    for (xCords, yCords) in retMarks(obs_cords):
        for (x,y) in zip(xCords, yCords):
            O.add((x,y))

    xLine, yLine = [], []
    for y in range(height):
        for x in range(width):
            if (x,y) in O:
                continue
            xLine.append(x)
            yLine.append(y)
    cords = np.array( [xLine, yLine] )

    network = Network2D(cords)
    s = Search(network, (startX, startY), (goalX, goalY), inData[0], O)

    return network.widget, s

def CSPParams(filename):
    global COLORS
    inData = open(filename)
    inData = inData.read().split("\n")
    inData.pop()

    nv, ne = [int(x) for x in inData[0].split()]

    indexMap = np.array([ np.array([float(x) for x in line.split()][1:]) for line in inData[1:nv+1]])
    xCords, yCords = [float(0)] * nv, [float(0)] * nv

    for index,line in enumerate(inData[1:nv+1]):
        _, x, y = line.split()
        xCords[index] = float(x)
        yCords[index] = float(y)
    edgeMap =  [ [int(x) for x in line.split()] for line in inData[nv+1:]]

    network = NetworkCSP(np.array([xCords, yCords]), edgeMap,
                         range(len(COLORS) -1))


    def checkEdge(src_index, src_li, dst_index, dst_li):
        return src_li[src_index] * -1 + dst_li[dst_index] * -1 < 0

    constraints = [ [] for _ in range(nv) ]

    for e in edgeMap:
        dom_1, dom_2 = symbols("d1 d2")
        l = lambdify((dom_1, dom_2), Ne(dom_1, dom_2))
        c = Constraint(l, e)
        constraints[e[0]].append(c)
        constraints[e[1]].append(c)
        
    s = CSPColoring(network, COLORS, constraints)

    return network.widget, s

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Did you forget params?"
        exit(1)

    widget, problem = None, None
    type_of_func = sys.argv[1].upper()
    if type_of_func == "CSP":
        widget, problem = CSPParams(sys.argv[2])
    elif type_of_func == "SEARCH":
        widget, problem = searchParams(sys.argv[2])
    else:
        print "Unsupported function.."
        exit(1)

    gui = genWindow(widget, problem)
    gtk.main()

# EOF
