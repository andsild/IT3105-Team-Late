#!/usr/bin/python

from graph_tool.all import *
import numpy as np
from ipdb import set_trace

""" Options for adjacent cells
    Currently horizontal and vertical direction, not diagonal
"""
colors = { "unused"     : [0, 0, 0, 1],
           "seen"       : [.0, 1, .0, 1],
           "obstacle"   : [1, 1, 1, 1],
           "start"      : [0, 0, 1, 1],
           "goal"       : [1, 0, 0, 1],
          }

class Network(object):
    def __init__(self, cords, directed=False):
        self.g = Graph(directed=directed)
        self.pos_map = self.g.new_vertex_property("vector<double>")
        self.states = self.g.new_vertex_property("vector<double>")
        self.cordDict = dict()

        for (x,y) in zip(cords[0], cords[1]):
            v = self.g.add_vertex()
            self.states[v] = colors["unused"]
            self.cordDict[(x,y)] = v

        self.pos_map.set_2d_array( cords )

        self.widget = GraphWidget(self.g, self.pos_map,
                    vertex_fill_color=self.states,
                    vertex_text = self.g.vertex_index,
                    vprops={"shape": "square",
                            "color": "white",
                            },
                   )
        self.update()

    def paint_node(self, src_index, color):
        self.states[self.g.vertex(src_index)] = color
        # self.update()

    def update(self):
        self.widget.regenerate_surface(lazy=False)
        self.widget.queue_draw()

    def clear(self):
       for v in self.g.vertices():
            self.states[v] = colors["unused"]
class Network2D(Network):
    def __init__(self, cords, dim):
        super(Network2D, self).__init__(cords)
        self.width, self.height = dim

    def map2d1d(self, posx, posy):
        return (self.width * posy) + posx

class NetworkTree(Network):
    def __init__(self):
        cords = np.array([ [0], [0] ])
        super(NetworkTree, self).__init__(cords)
        self.latest = self.g.vertex(self.g.num_vertices() - 1)

    def insertVertex(self, pos):
        v = self.g.add_vertex()
        self.pos_map[v] =  pos
        self.states[v] = colors["unused"]
        self.g.add_edge(self.latest, v)

class NetworkCSP(Network):
    def __init__(self, cords, edgemap, domain):
        super(NetworkCSP, self).__init__(cords, directed=False)

        # self.assignments = self.g.new_vertex_property("vector<int>")
        # for v in self.g.vertices():
        #     self.assignments[v] = domain

        for src, dest in edgemap:
            self.g.add_edge(self.g.vertex(dest), self.g.vertex(src))

# EOF
