#!/usr/bin/env python

#import os
import sys
import random

#import networkx
try:
    from PySide import QtGui
except:
    from PyQt4 import QtGui

from nodegraph.nodegraphscene import NodeGraphScene
from nodegraph.nodegraphview import NodeGraphView

class NodeGraphDialog(QtGui.QMainWindow):

    """
    Handles top level dialog of Node grap

    """

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.parent = parent or self

        self.nodegraph = NodeGraphWidget("main", parent=self.parent)
        self.setCentralWidget(self.nodegraph)
        self.resize(800, 600)
        self.setWindowTitle("Node graph -")

        center = self.nodegraph.graph_view.sceneRect().center()
        for i in range(0, 30):
            prev_node = None
            for j in range(0, 40):
                node = self.nodegraph.graph_scene.create_node(
                    "random%d" % random.randint(1, 1000000),
                    inputs=["in", "add"])
                node.setPos(j*350, i*350)
                if prev_node:
                    edge = self.nodegraph.graph_scene.create_edge(
                            prev_node._output, node._inputs[0])
                prev_node = node


class NodeGraphWidget(QtGui.QWidget):

    """
    Handles node graph view

    """

    def __init__(self, name, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.name = name
        self.parent = parent

        self.graph_scene = NodeGraphScene(parent=self.parent,
                                          nodegraph_widget=self)
        self.graph_view = NodeGraphView(self.graph_scene, parent=self.parent)
        self.horizontal_layout = QtGui.QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.graph_view)


if __name__ == "__main__":
    app = QtGui.QApplication([])
    dialog = NodeGraphDialog()
    dialog.show()

    sys.exit(app.exec_())
