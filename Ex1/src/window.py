#!/usr/bin/pyton

from gi.repository import Gtk as gtk, GObject
import sys

from ipdb import set_trace

class Handler:
    def __init__(self, inter_object):
        self.inter_object = inter_object
    def on_key_press(self, __, data):
        # print data.keyval
        if data.keyval == 113 or data.keyval == 81: # Q key
            gtk.main_quit();
            sys.exit(0);

        if data.keyval == 112 or data.keyval == 80: # P key
            pass

        if data.keyval == 108 or data.keyval == 76: # S key
            self.btnStart()

    def onDeleteWindow(self, *args):
        gtk.main_quit(args)

    def btnStart(self, *args):
        func, problem, network, Q, D = self.inter_object.triggerStart()
        GObject.idle_add(func, network, problem, Q, D) 

def genWindow(widget, inter_object):
    builder = gtk.Builder()
    builder.add_from_file("src/gui.glade")
    builder.connect_signals(Handler(inter_object))

    builder.get_object("alignment1").add(widget)

    win = builder.get_object("window1")
    win.set_title("Rendering a-star on graph...")
    win.connect("delete_event", gtk.main_quit)
    win.show_all()

    return win
