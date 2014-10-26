#!/usr/bin/python

from ipdb import set_trace
from gi.repository import Gtk as gtk
import numpy as np

from searchGrid import *
from csp import *
from graphColoring import *
from network import *
from LP import *
from flowPuzzle import *
from window import genWindow

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

    indexMap = np.array([ np.array([float(x) \
                                    for x in line.split()][1:]) \
                         for line in inData[1:nv+1]])
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

    return n.widget, prob

def flowParams(filename):
    in_data = open(filename)
    in_data = [map(int, line.split()) for line in in_data.read().split("\n")]
    in_data.pop()

    positions = []
    xLine = []
    yLine = []

    width, height = in_data[0][::-1]

    tmp_D = set()
    for node,start_x,start_y,end_x,end_y in in_data[1:]:
        positions.append((start_x, start_y, end_x, end_y))
        tmp_D.add((start_x,start_y))
        tmp_D.add((end_x,end_y))

    for y in range(height):
        for x in range(width):
            xLine.append(x)
            yLine.append(y)

    cords = np.array( [xLine, yLine] )
    COLORS = [ x for x in color_pool.values() \
          if x is not color_pool["black"] and x is not color_pool["white"]]\
        [:len(positions)]

    cords = np.array( [xLine, yLine] )
    n = Network2D(cords, (width, height))
    cnet = CNET(n.g.num_vertices(), len(positions))

    # CENTER MASS
    for y in range(1,height-1):
        for x in range(1,width-1):
            cells = [n.map2d1d(posx,posy) for posx,posy in \
                    [ (x,y), (x+1,y), (x-1,y), (x,y+1), (x,y-1)]]
            if (x,y) not in tmp_D:
                cnet.addLessThan(cells,  \
                            "abs(A - B) - abs(abs(A-B)-1)"
                            "+ abs(A - C) - abs(abs(A-C)-1)"
                            "+ abs(A - D) - abs(abs(A-D)-1)"
                            "+ abs(A - E) - abs(abs(A-E)-1)",
                            0)
            else:
                cnet.addLessThan(cells, \
                            "abs(A - B) - abs(abs(A-B)-1)"
                            "+ abs(A - C) - abs(abs(A-C)-1)"
                            "+ abs(A - D) - abs(abs(A-D)-1)"
                            "+ abs(A - E) - abs(abs(A-E)-1)",
                            2)


    # LEFT BORDER
    for y in range(1,height-1):
        cells = [n.map2d1d(posx,posy) for posx,posy in \
                [ (0,y), (0,y+1), (0,y-1), (1,y)]]
        if (0,y) not in tmp_D:
            cnet.addLessThan(cells,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)"
                        "+ abs(A - D) - abs(abs(A-D)-1)",
                        -1)
        else:
            cnet.addLessThan(cells,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)"
                        "+ abs(A - D) - abs(abs(A-D)-1)",
                        1)
    # RIGHT BORDER
        cells = [n.map2d1d(posx,posy) for posx,posy in \
                [ (width-1,y), (width-1,y+1), (width-1,y-1), (width-2,y)]]
        if (width-1,y) not in tmp_D:
            cnet.addLessThan(cells,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)"
                        "+ abs(A - D) - abs(abs(A-D)-1)",
                        -1)
        else:
            cnet.addLessThan(cells,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)"
                        "+ abs(A - D) - abs(abs(A-D)-1)",
                        1)

    # UPPER BORDER
    for x in range(1,width-1):
        cells = [n.map2d1d(posx,posy) for posx,posy in \
                [ (x,0), (x+1,0), (x-1,0), (x,1)]]
        if (x,0) not in tmp_D:
            cnet.addLessThan(cells,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)"
                        "+ abs(A - D) - abs(abs(A-D)-1)",
                        -1)
        else:
            cnet.addLessThan(cells,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)"
                        "+ abs(A - D) - abs(abs(A-D)-1)",
                        1)
    # LOWER BORDER
        cells = [n.map2d1d(posx,posy) for posx,posy in \
                [ (x,height-1), (x+1,height-1), (x-1,height-1), (x,height-2)]]
        if (x,height-1) not in tmp_D:
            cnet.addLessThan(cells,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)"
                        "+ abs(A - D) - abs(abs(A-D)-1)",
                        -1)
        else:
            cnet.addLessThan(cells,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)"
                        "+ abs(A - D) - abs(abs(A-D)-1)",
                        1)

    corner_cells = [ [((posx,posy),n.map2d1d(posx,posy)) for posx,posy in [ (0,0), (0,1), (1,0)]],
                    [((posx,posy),n.map2d1d(posx,posy)) for posx,posy in [ (width-1,0), (width-2,0), (width-1,1)]],
                    [((posx,posy),n.map2d1d(posx,posy)) for posx,posy in [ (width-1,height-1), (width-1,height-2), (width-2,height-1)]],
                    [((posx,posy),n.map2d1d(posx,posy)) 
                        for posx,posy in [ (0,height-1), (0,height-2), (1,height-1)]],
                ]
    for tup in corner_cells:
        corner = [x[1] for x in tup]
        if tup[0][0] not in tmp_D:
            cnet.addLessThan(corner,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)",
                        -2)
        else:
            cnet.addLessThan(corner,  \
                        "abs(A - B) - abs(abs(A-B)-1)"
                        "+ abs(A - C) - abs(abs(A-C)-1)",
                        0)

    prob = FlowPuz(n, cnet, positions, (width,height), COLORS)
    
    return n.widget, prob

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
    elif type_of_func == "FLOWPUZ":
        widget, problem = flowParams(sys.argv[2])

    else:
        print "Unsupported function.."
        exit(1)

    gui = genWindow(widget, problem)
    gtk.main()

# EOF
