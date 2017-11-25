#==============================================================================
# Nodegraph-pyqt
#
# Everyone is permitted to copy and distribute verbatim copies of this
# document, but changing it is not allowed.
#
# For any questions, please contact: dsideb@gmail.com
#
# GNU LESSER GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
#==============================================================================

"""
Node graph scene manager based on QGraphicsScene

"""
from . import QtCore, QtGui

from .node import Node, NodeSlot
from .edge import Edge, InteractiveEdge
from .rubberband import RubberBand


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
        self._edges_by_hash = {}
        self._is_interactive_edge = False
        self._is_refresh_edges = False
        self._interactive_edge = None
        self._refresh_edges = {}
        self._rubber_band = None
        self._is_rubber_band = False
        self._is_shift_key = False
        self._is_ctrl_key = False
        self._is_alt_key = False

        # Redefine palette
        self.setBackgroundBrush(QtGui.QColor(60, 60, 60))
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor(210, 210, 210))
        palette.setColor(QtGui.QPalette.HighlightedText,
                         QtGui.QColor(255, 255, 255))
        palette.setColor(QtGui.QPalette.BrightText,
                         QtGui.QColor(80, 180, 255))
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(5, 5, 5))
        palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(20, 20, 20))
        self.setPalette(palette)

        self.selectionChanged.connect(self._onSelectionChanged)

    @property
    def nodes(self):
        """Return all nodes

        """
        return self._nodes


    @property
    def is_interactive_edge(self):
        """Return status of interactive edge mode

        """
        return self._is_interactive_edge


    @property
    def edges_by_hash(self):
        """Return a list of edges as hash

        """
        return self._edges_by_hash


    def create_node(self, name, inputs=["in"], parent=None):
        """Create a new node

        """
        node = Node(name, self, inputs=inputs, parent=parent)
        self._nodes.append(node)
        return node


    def create_edge(self, source, target):
        """Create a new edge

        """
        edge = Edge(source, target, self, arrow=Edge.ARROW_STANDARD)
        self._edges_by_hash[edge.hash] = edge
        return edge


    def start_interactive_edge(self, source_slot, mouse_pos):
        """Create an edge between source slot and mouse position

        """
        self._is_interactive_edge = True
        if not self._interactive_edge:
            # Create interactive edge
            self._interactive_edge = InteractiveEdge(source_slot,
                    mouse_pos,
                    scene=self,
                    arrow=Edge.ARROW_STANDARD)
        else:
            # Re-use existing interactive edge
            self._interactive_edge.refresh(mouse_pos, source_slot)
            self._interactive_edge.setVisible(True)


    def stop_interactive_edge(self, connect_to=None):
        """Hide the interactive and create an edge between the source slot
        and the slot given by connect_to

        """
        if connect_to:
            eh = self._edges_by_hash # shprtcut
            source = self._interactive_edge._source_slot

            found = True
            if isinstance(connect_to, Node):
                found = False
                # Try to find most likely slot
                if source.family == NodeSlot.OUTPUT:
                    for slot in connect_to._inputs:
                        l = [h for h in eh if eh[h]._source_slot == slot
                             or eh[h]._target_slot == slot]
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
                and source.parent != target.parent
                and not [h for h in eh if eh[h]._target_slot == source]):


                # TO DO: Check new edge isn't creating a loop, i.e that the
                # source node opposite slot(s) are(n't) connected to the target
                # node
                if source.family == NodeSlot.OUTPUT:
                    for aninput in source.parent._inputs:
                        pass
                else:
                    output = source.parent._output

                #print("Create edge from %s to %s" %(source._name, target._name))
                edge = self.create_edge(target, source)
            else:
                #TO DO: Send info to status bar
                pass

        self._is_interactive_edge = False
        self._interactive_edge.setVisible(False)


    def start_rubber_band(self, init_pos):
        self._is_rubber_band = True
        if not self._rubber_band:
            # Create custom rubber band
            self._rubber_band = RubberBand(init_pos, scene=self)
        else:
            # Re-use existing rubber band
            self._rubber_band.refresh(mouse_pos=init_pos, init_pos=init_pos)
            self._rubber_band.setVisible(True)


    def stop_rubber_band(self):
        """Hide the custom rubber band and if it contains node/edges select
        them

        """
        self._is_rubber_band = False
        self._rubber_band.setVisible(False)

        # Select nodes and edges inside the rubber band
        if self._is_shift_key:
            self._rubber_band.update_scene_selection(
                self._rubber_band.ADD_SELECTION)
        elif self._is_ctrl_key:
            self._rubber_band.update_scene_selection(
                self._rubber_band.MINUS_SELECTION)
        else:
            self._rubber_band.update_scene_selection()


    def delete_selected(self):
        """Delete selected nodes and edges

        """
        nodes = []
        edges = []
        for i in self.selectedItems():
            if isinstance(i, Node):
                nodes.append(i)
            if isinstance(i, Edge):
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


    def mousePressEvent(self, event):

        if not self._is_interactive_edge:

            if not self.items(event.scenePos()):
                self.start_rubber_band(event.scenePos())

            if self._is_shift_key or self._is_ctrl_key:
                event.accept()
                return

        QtGui.QGraphicsScene.mousePressEvent(self, event)


    def mouseMoveEvent(self, event):
        """Re-implements mouse move event

        """
        buttons = event.buttons()

        if buttons == QtCore.Qt.LeftButton:

            QtGui.QGraphicsScene.mouseMoveEvent(self, event)

            # Edge creation mode?
            if self._is_interactive_edge:
                self._interactive_edge.refresh(event.scenePos())
            elif self._is_rubber_band:
                self._rubber_band.refresh(event.scenePos())
            elif self.selectedItems():
                if not self._is_refresh_edges:
                    self._is_refresh_edges = True
                    self._refresh_edges = self._get_refresh_edges()
                for ahash in self._refresh_edges["move"]:
                    self._edges_by_hash[ahash].refresh_position()
                for ahash in self._refresh_edges["refresh"]:
                    self._edges_by_hash[ahash].refresh()
        else:
            return QtGui.QGraphicsScene.mouseMoveEvent(self, event)


    def mouseReleaseEvent(self, event):
        """

        """
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

        # Edge refresh mode?
        if self._is_refresh_edges:
            self._is_refresh_edges = False
            self._refresh_edges = []

        # Rubber band mode?
        if self._is_rubber_band:
            self.stop_rubber_band()

        QtGui.QGraphicsScene.mouseReleaseEvent(self, event)


    def mouseDoubleClickEvent(self, event):
        """Re-implements doube click event

        """
        selected = self.items(event.scenePos())

        if len(selected) == 1:
            print("Edit Node %s" % selected[0]._name)


    def _onSelectionChanged(self):
        """Re-inplements selection changed event

        """
        if self._is_refresh_edges:
            self._refresh_edges = self._get_refresh_edges()


    def _get_refresh_edges(self):
        """

        """
        edges = set()
        nodes = set()
        edges_to_move = []
        edges_to_refresh = []

        for item in self.selectedItems():
            if isinstance(item, Node):
                edges |= item.edges
                nodes.add(item.name)

        # Distinghish edges where both ends are selected from the rest
        for edge in edges:
            if self._edges_by_hash[edge].is_connected_to(nodes):
                edges_to_move.append(edge)
            else:
                edges_to_refresh.append(edge)

        r = {"move":edges_to_move, "refresh":edges_to_refresh}
        #print("move: %r\nrefresh: %r" % (edges_to_move, edges_to_refresh))
        return r
