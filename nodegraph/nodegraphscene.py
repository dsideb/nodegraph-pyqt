#==============================================================================
#
#  Insert gnu license here
#
#==============================================================================

"""
Node graph scene manager based on QGraphicsScene

"""
from . import QtCore, QtGui

from .node import Node, NodeSlot, NodeEdge, NodeInteractiveEdge


class NodeGraphScene(QtGui.QGraphicsScene):

    """
    Provides custom implementation of QGraphicsScene

    """

    def __init__(self, parent=None, nodegraph_widget=None):
        """Create an instance of this class

        """
        QtGui.QGraphicsScene.__init__(self, parent)
        self.parent = parent
        self._nodegraph_widget = nodegraph_widget
        self._nodes = []
        self._edges = []
        self._is_interactive_edge = False
        self._interactive_edge = None

        # Redefine palette
        self.setBackgroundBrush(QtGui.QColor(60, 60, 60))
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(220, 220, 220))
        palette.setColor(QtGui.QPalette.HighlightedText,
                         QtGui.QColor(255, 255, 255))
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(5, 5, 5))
        palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(20, 20, 20))
        self.setPalette(palette)


    @property
    def nodes(self):
        """Return all nodes

        """
        return self._nodes


    @property
    def edges(self):
        """Return all edges

        """
        return self._edges


    def create_node(self, name, inputs=["in"], parent=None):
        """Create a new node

        """
        node = Node(name, self, inputs=inputs, parent=parent)
        self._nodes.append(node)
        return node


    def create_edge(self, source, target):
        """Create a new edge

        """
        edge = NodeEdge(source, target, self, arrow=NodeEdge.ARROW_STANDARD)
        self._edges.append(edge)
        return edge


    def start_interactive_edge(self, source_slot, mouse_pos):
        """Create an edge between source slot and mouse position

        """
        self._is_interactive_edge = True
        if not self._interactive_edge:
            # Create interactive edge
            self._interactive_edge = NodeInteractiveEdge(source_slot,
                    mouse_pos,
                    scene=self,
                    arrow=NodeEdge.ARROW_STANDARD)
        else:
            # Re-use existing interactive edge
            self._interactive_edge.refresh(mouse_pos, source_slot)
            self._interactive_edge.setVisible(True)


    def stop_interactive_edge(self, connect_to=None):
        """Hide the interactive and create an edge between the source slot
        and the slot given by connect_to

        """
        if connect_to:
            source = self._interactive_edge._source_slot

            found = True
            if isinstance(connect_to, Node):
                found = False
                # Try to find most likely slot
                if source.family == NodeSlot.OUTPUT:
                    for slot in connect_to._inputs:
                        l = [e for e in self._edges if e._source_slot == slot
                             or e._target_slot == slot]
                        if not l:
                            connect_to = slot
                            found = True
                            break
                else:
                    connect_to = connect_to._output
                    found = True

            # Resolve direction
            target = connect_to

            if source.family == NodeSlot.OUTPUT:
                source = connect_to
                target = self._interactive_edge._source_slot

            # Validate the connection
            if (found
                and source.family != target.family
                and source.parentItem() != target.parentItem()
                and not [e for e in self._edges if e._target_slot == source]):


                # TO DO: Check new edge isn't creating a loop, i.e that the
                # source node opposite slot(s) are(n't) connected to the target
                # node
                if source.family == NodeSlot.OUTPUT:
                    for aninput in source.parentItem()._inputs:
                        pass
                else:
                    output = source.parentItem()._output
                    #print([e for e in self._edges if e._source_slot == output])



                print("Create edge from %s to %s" %(source._name, target._name))
                edge = self.create_edge(target, source)
            else:
                #TO DO: Send info to status bar
                pass

        self._is_interactive_edge = False
        self._interactive_edge.setVisible(False)


    def delete_selected(self):
        """Delete selected nodes and edges

        """
        nodes = []
        edges = []
        for i in self.selectedItems():
            if isinstance(i, Node):
                nodes.append(i)
            if isinstance(i, NodeEdge):
                edges.append(i)

        print("Node(s) to delete: %s" % [n._name for n in nodes])
        print("Edge(s) to delete: %r" % edges)
        for node in self.selectedItems():
            # TODO: Collect all edges for deletion or reconnection
            pass
        # Delete node(s)
        #self.removeItem(node)
        #index = self._nodes.index(node)
        #self._nodes.pop(index)


    def mouseMoveEvent(self, event):
        buttons = event.buttons()

        if buttons == QtCore.Qt.LeftButton:
            # Edge creation mode?
            if self._is_interactive_edge:
                self._interactive_edge.refresh(event.scenePos())

        QtGui.QGraphicsScene.mouseMoveEvent(self, event)


    def mouseReleaseEvent(self, event):
        buttons = event.buttons()

        # Edge creation mode?
        if self._is_interactive_edge:

            slot = None
            node = None
            for item in self.items(event.scenePos()):
                if isinstance(item, NodeSlot):
                    slot = item
                    break
                if isinstance(item, Node):
                    node = item
            connect_to = slot if slot else node

            self.stop_interactive_edge(connect_to=connect_to)

        QtGui.QGraphicsScene.mouseReleaseEvent(self, event)


    def mouseDoubleClickEvent(self, event):
        selected = self.items(event.scenePos())

        if len(selected) == 1:
            print("Edit Node %s" % selected[0]._name)
