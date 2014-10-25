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
    # cnet = CNET(n.g.num_vertices(), len(positions))
    domain = [10,11,14,15] # 4
    cnet = CNET2(n.g.num_vertices(), domain) # one for each possible direction
    """ I make the strong assumption that the board if filled diagonally.
        There are a finite amount of choises: you can come in from north or 
        west. you can exit south or east. This gives four possible choises.

        AXIS: X ---> OUTGOING
        AXIS: Y |  INCOMING
        * *  S   E
     *  . .  2   3
     *  . .  .   .
     N  . . 10  11
     W  . . 14  15
     
     In other words, choosing value 10 means that incoming is N, outgoing is S
    """

    # cons1 : < 0
    # cons2 : > 0
    cons1_horiz = "A % 4 - ((B + 1) * 4)"
    cons2_horiz = "A % 4 - ((B) * 4)"
    """ this states that the neighbouring cell (A is left-most, B is right-adjacent)
        has to have the incoming degree respective to the left.
        Is A is going out east, incoming W is filtered from the domain B
    """

    # cons1 : < 0
    # cons2 : > 0
    cons1_vert = "B - ((A % 4)+1)*4"
    cons2_vert = "B - (A % 4)*4"
    """ this states that the neighbouring cell (A is upper, B is lower)
        has to have the incoming degree respective to the top
        Is A is going out east, incoming S is filtered from the domain B
    """

    # cons1 : <= 0
    cons1_diag = "(A % 4) - (B % 4) "
    """ this states that the neighbouring cell (A is upper right, B is i-1,j-1)
        cannot be such that both A and B direct flow to the same cell 
    """

    


    for y in range(1,height-1):
        for x in range(width):
            cells = [n.map2d1d(x,y) for x,y in \
                        [ (x,y), (x+1,y), (x-1,y), (x,y+1), (x,y-1)]]
            if (x,y) not in tmp_D:
               cnet.addCons(cells,  \
                             "X - (Y+1) * 4", 0)
                             # "abs(A - B) - abs(abs(A-B)-1)"
                             #  "+ abs(A - C) - abs(abs(A-C)-1)"
                             #  "+ abs(A - D) - abs(abs(A-D)-1)"
                             #  "+ abs(A - E) - abs(abs(A-E)-1)",
                             # 0)
            else:
                cnet.addCons(cells,  \
                             "abs(A - B) - abs(abs(A-B)-1)"
                              "+ abs(A - C) - abs(abs(A-C)-1)"
                              "+ abs(A - D) - abs(abs(A-D)-1)"
                              "+ abs(A - E) - abs(abs(A-E)-1)",
                             2)
    for x in range(1,width):
        cells = [n.map2d1d(x,y) for x,y in \
                    [ (x,0), (x+1,0), (x-1,0)]]
        if (x,0) not in tmp_D:
            cnet.addcons(cells,  \
                            "abs(a - b) - abs(abs(a-b)-1)"
                            "+ abs(a - c) - abs(abs(a-c)-1)"
                            "+ abs(a - d) - abs(abs(a-d)-1)",
                            1)
        else:
            cnet.addCons(cells,  \
                            "abs(A - B) - abs(abs(A-B)-1)"
                            "+ abs(A - C) - abs(abs(A-C)-1)"
                            "+ abs(A - D) - abs(abs(A-D)-1)"
                            "+ abs(A - E) - abs(abs(A-E)-1)",
                            2)
        cells = [n.map2d1d(x,y) for x,y in \
                    [ (x,height-1), (x+1,height-1), (x-1,height-1)]]
        if (x,height-1) not in tmp_D:
            cnet.addcons(cells,  \
                            "abs(a - b) - abs(abs(a-b)-1)"
                            "+ abs(a - c) - abs(abs(a-c)-1)"
                            "+ abs(a - d) - abs(abs(a-d)-1)",
                            1)
        else:
            cnet.addCons(cells,  \
                            "abs(A - B) - abs(abs(A-B)-1)"
                            "+ abs(A - C) - abs(abs(A-C)-1)"
                            "+ abs(A - D) - abs(abs(A-D)-1)"
                            "+ abs(A - E) - abs(abs(A-E)-1)",
                            2)



    prob = FlowPuz(n, cnet, positions, (width,height), COLORS)

# func tryConnection(paper *Paper, pos1 int, dirs int) bool {
#     // Extract the (last) bit which we will process in this call
#     dir := dirs & -dirs
#     pos2 := pos1 + paper.Vctr[dir]
#     end1, end2 := paper.end[pos1], paper.end[pos2]
#
#     // Check different sources arent connected
#     if paper.Table[end1] != EMPTY && paper.Table[end2] != EMPTY &&
#         paper.Table[end1] != paper.Table[end2] {
#         return false
#     }
#     // No loops
#     if end1 == pos2 && end2 == pos1 {
#         return false
#     }
#     // No tight corners (Just an optimization)
#     if paper.Con[pos1] != 0 {
#         dir2 := paper.Con[pos1+paper.Vctr[paper.Con[pos1]]]
#         dir3 := paper.Con[pos1] | dir
#         if DIAG[dir2] && DIAG[dir3] && dir2&dir3 != 0 {
#             return false
#         }
#     }
#
#     // Add the connection and a backwards connection from pos2
#     old1, old2 := paper.Con[pos1], paper.Con[pos2]
#     paper.Con[pos1] |= dir
#     paper.Con[pos2] |= MIR[dir]
#     // Change states of ends to connect pos1 and pos2
#     old3, old4 := paper.end[end1], paper.end[end2]
#     paper.end[end1] = end2
#     paper.end[end2] = end1
#
#     // Remove the done bit and recurse if nessecary
#     dir2 := dirs &^ dir
#     res := false
#     if dir2 == 0 {
#         res = chooseConnection(paper, paper.next[pos1])
#     } else {
#         res = tryConnection(paper, pos1, dir2)
#     }
#

        


    
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
