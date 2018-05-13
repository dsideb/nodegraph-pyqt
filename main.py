#!/usr/bin/env python

# import os
import sys

# import networkx
from thirdparty.Qt import QtWidgets

from nodegraph.scene import Scene
from nodegraph.view import View


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
        cam = self.nodegraph.graph_scene.create_node("camera")
        cam.setPos(-200, -150)
        model = self.nodegraph.graph_scene.create_node(
            "combine",
            inputs=["mesh1", "mesh2", "camera"])
        model.setPos(150, 0)
        edge = self.nodegraph.graph_scene.create_edge(
            cam._output,
            model._inputs[0])

        test = self.nodegraph.graph_scene.create_node("test")
        test.setPos(-400, 150)
        egde = self.nodegraph.graph_scene.create_edge(
            test._output,
            model._inputs[1])


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
