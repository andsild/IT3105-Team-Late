#!/usr/bin/python

from ipdb import set_trace
import numpy as np

from searchGrid import *
from csp import *
from graphColoring import *
from network import *
from LP import *

""" The function resolving parameters for search problem
"""
def searchParams(filename, mode):
    """ Method for transformation of obsatcles to points
    """
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
    s = Search(network, (startX, startY), (goalX, goalY), inData[0], O, mode)

    return network.widget, s

""" The function resolving parameters for CSP problem
"""
def CSPParams(filename,n_colors):
    COLORS = [ x for x in color_pool.values() \
          if x is not color_pool["black"] and x is not color_pool["white"]][:int(n_colors)]
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

    constraints = [ [] for _ in range(nv) ]

    cnet = CNET(network.g.num_vertices(), int(n_colors))

    for e in inData[nv+1:]:
        cnet.readCanonical(e)

    s = Coloring(network, cnet, COLORS)

    return network.widget, s

def LPParams(filename):
    inData = open(filename)
    inData = inData.read().split("\n")
    inData.pop()

    network = NetworkTree()

    ob_func    = inData[0].split()
    num_vars   = len(ob_func) / 2
    max_or_min = ob_func[0]
    dom_size   = len(inData[-1].split()) - 1

    cnet = CNET(num_vars, dom_size)

    constraints = inData[1:-1]
    for c in inData[1:-1]:
        cnet.readLP(c)

    prob = LPSolver(network, cnet)

    return network.widget, prob

""" Main, it all starts here
"""
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Did you forget params?"
        exit(1)

    widget, problem = None, None
    type_of_func = sys.argv[1].upper()
    if type_of_func == "CSP":
        if len(sys.argv) > 3:
            widget, problem = CSPParams(sys.argv[2], sys.argv[3])
        else:
            exit(1)
    elif type_of_func == "SEARCH":
        if len(sys.argv) > 3:
            widget, problem = searchParams(sys.argv[2], sys.argv[3])
        else:
            widget1, problem1 = searchParams(sys.argv[2], "best")
            widget2, problem2 = searchParams(sys.argv[2], "depth")
            widget3, problem3 = searchParams(sys.argv[2], "breadth")

            gui1 = genWindow(widget1, problem1)
            gui2 = genWindow(widget2, problem2)
            gui3 = genWindow(widget3, problem3)
            gtk.main()
            exit(0)
    elif type_of_func == "LP":
        widget, problem = LPParams(sys.argv[2])
    else:
        print "Unsupported function.."
        exit(1)

    gui = genWindow(widget, problem)
    gtk.main()

# EOF
