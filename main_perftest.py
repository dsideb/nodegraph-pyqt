#!/usr/bin/env python

# import os
import sys
import random

# import networkx
from nodegraph.scene import Scene
from nodegraph.view import View

from Qt import QtWidgets


class NodeGraphDialog(QtWidgets.QMainWindow):

    """
    Handles top level dialog of Node grap

    """

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.parent = parent or self

        self.nodegraph = NodeGraphWidget("main", parent=self.parent)
        self.setCentralWidget(self.nodegraph)
        self.resize(800, 600)
        self.setWindowTitle("Node graph -")

        # center = self.nodegraph.graph_view.sceneRect().center()
        for i in range(0, 30):
            prev_node = None
            for j in range(0, 40):
                node = self.nodegraph.graph_scene.create_node(
                    "random%d%d%d" % (i, j, random.randint(1, 1000)),
                    inputs=["in", "add"])
                node.setPos(j * 350, i * 350)
                if prev_node:
                    edge = self.nodegraph.graph_scene.create_edge(
                        prev_node._output, node._inputs[0])
                prev_node = node


class NodeGraphWidget(QtWidgets.QWidget):

    """
    Handles node graph view

    """

    def __init__(self, name, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.name = name
        self.parent = parent

        self.graph_scene = Scene(parent=self.parent,
                                 nodegraph_widget=self)
        self.graph_view = View(self.graph_scene, parent=self.parent)
        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.graph_view)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dialog = NodeGraphDialog()
    dialog.show()

    sys.exit(app.exec_())
