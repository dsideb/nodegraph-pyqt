# =============================================================================
# Nodegraph-pyqt
#
# Everyone is permitted to copy and distribute verbatim copies of this
# document, but changing it is not allowed without permissions.
#
# For any questions, please contact: dsideb@gmail.com
#
# GNU LESSER GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
# =============================================================================

"""Node graph scene manager based on QGraphicsScene

"""
from Qt import QtCore, QtGui, QtWidgets

from .node import Node, NodeSlot
from .edge import Edge, InteractiveEdge
from .rubberband import RubberBand

from .constant import SCENE_WIDTH, SCENE_HEIGHT


class Scene(QtWidgets.QGraphicsScene):

    """
    Provides custom implementation of QGraphicsScene

    """

    def __init__(self, parent=None, nodegraph_widget=None):
        """Create an instance of this class

        """
        QtWidgets.QGraphicsScene.__init__(self, parent)
        self.parent = parent
        self._nodegraph_widget = nodegraph_widget
        self._nodes = []
        self._edges_by_hash = {}
        self._is_interactive_edge = False
        self._is_refresh_edges = False
        self._interactive_edge = None
        self._refresh_edges = {}
        self._rubber_band = None

        # Registars
        self._is_rubber_band = False
        self._is_shift_key = False
        self._is_ctrl_key = False
        self._is_alt_key = False
        self._is_left_mouse = False
        self._is_mid_mouse = False
        self._is_right_mouse = False

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
            self._interactive_edge = InteractiveEdge(
                source_slot,
                mouse_pos,
                scene=self,
                arrow=Edge.ARROW_STANDARD)
        else:
            # Re-use existing interactive edge
            self._interactive_edge.refresh(mouse_pos, source_slot)

    def stop_interactive_edge(self, connect_to=None):
        """Hide the interactive and create an edge between the source slot
        and the slot given by connect_to

        """
        self._is_interactive_edge = False
        if connect_to:
            eh = self._edges_by_hash  # shortcut
            source = self._interactive_edge._source_slot

            found = True
            if isinstance(connect_to, Node):
                found = False
                # Try to find most likely slot
                if source.family == NodeSlot.OUTPUT:
                    for slot in connect_to._inputs:
                        li = [h for h in eh if eh[h]._source_slot == slot or
                              eh[h]._target_slot == slot]
                        if not li:
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
            if (found and
                    source.family != target.family and
                    source.parent != target.parent and
                    not [h for h in eh if eh[h]._target_slot == source]):

                # TO DO: Check new edge isn't creating a loop, i.e that the
                # source node opposite slot(s) are(n't) connected to the target
                # node
                if source.family == NodeSlot.OUTPUT:
                    for aninput in source.parent._inputs:
                        pass
                else:
                    output = source.parent._output

                # print("Create edge from %s to %s" %
                #       (source._name, target._name))
                edge = self.create_edge(target, source)
            else:
                # TO DO: Send info to status bar
                pass

        # Delete item (to be sure it's not taken into account by any function
        # including but not limited to fitInView)
        self.removeItem(self._interactive_edge)
        self._interactive_edge = None

    def start_rubber_band(self, init_pos):
        """Create/Enable custom rubber band

        :param init_pos: Top left corner of the custom rubber band
        :type init_pos: :class:`QtCore.QPosF`

        """
        self._is_rubber_band = True
        if not self._rubber_band:
            # Create custom rubber band
            self._rubber_band = RubberBand(init_pos, scene=self)
        else:
            # Re-use existing rubber band
            self._rubber_band.refresh(mouse_pos=init_pos, init_pos=init_pos)

    def stop_rubber_band(self, intersect=None):
        """Hide the custom rubber band and if it contains node/edges select
        them

        """
        self._is_rubber_band = False

        # Select nodes and edges inside the rubber band
        if self._is_shift_key and self._is_ctrl_key:
            self._rubber_band.update_scene_selection(
                self._rubber_band.TOGGLE_SELECTION)
        elif self._is_shift_key:
            self._rubber_band.update_scene_selection(
                self._rubber_band.ADD_SELECTION)
        elif self._is_ctrl_key:
            self._rubber_band.update_scene_selection(
                self._rubber_band.MINUS_SELECTION)
        else:
            self._rubber_band.update_scene_selection(intersect)

        self.removeItem(self._rubber_band)
        self._rubber_band = None

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
        # self.removeItem(node)
        # index = self._nodes.index(node)
        # self._nodes.pop(index)

    def mousePressEvent(self, event):
        """Re-implements mouse press event

        :param event: Mouse event
        :type event: :class:`QtWidgets.QMouseEvent`

        """
        print("MOUSE PRESS SCENE!")
        if not self._is_interactive_edge:

            if not self.items(event.scenePos()):
                self.start_rubber_band(event.scenePos())

                if self._is_shift_key or self._is_ctrl_key:
                    event.accept()
                return
            else:
                if self._is_shift_key or self._is_ctrl_key:
                    # Mouse is above scene items and single click with modfiers
                    event.accept()

                    if self._is_shift_key and self._is_ctrl_key:
                        for item in self.items(event.scenePos()):
                            item.setSelected(not item.isSelected())
                    elif self._is_shift_key:
                        for item in self.items(event.scenePos()):
                            item.setSelected(True)
                    elif self._is_ctrl_key:
                        for item in self.items(event.scenePos()):
                            item.setSelected(False)

                    return
        else:
            # Items under mouse during edge creation, We may have to start an
            # interactive edge
            pass

        QtWidgets.QGraphicsScene.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """Re-implements mouse move event

        :param event: Mouse event
        :type event: :class:`QtWidgets.QMouseEvent`

        """
        buttons = event.buttons()

        if buttons == QtCore.Qt.LeftButton:

            QtWidgets.QGraphicsScene.mouseMoveEvent(self, event)

            # Edge creation mode?
            if self._is_interactive_edge:
                self._interactive_edge.refresh(event.scenePos())
            # Selection mode?
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
            return QtWidgets.QGraphicsScene.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Re-implements mouse release event

        :param event: Mouse event
        :type event: :class:`QtWidgets.QMouseEvent`

        """
        # buttons = event.buttons()
        connect_to = None

        # Edge creation mode?
        if self._is_interactive_edge:
            slot = None
            node = None
            for item in self.items(event.scenePos()):
                if isinstance(item, Node):
                    node = item
                    slot = node._hover_slot
                    break
            connect_to = slot if slot else node

            self.stop_interactive_edge(connect_to=connect_to)

        # Edge refresh mode?
        if self._is_refresh_edges:
            self._is_refresh_edges = False
            self._refresh_edges = []

        # Rubber band mode?
        if self._is_rubber_band:
            self.stop_rubber_band()

        QtWidgets.QGraphicsScene.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        """Re-implements doube click event

        :param event: Mouse event
        :type event: :class:`QtWidgets.QMouseEvent`

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
        """Return all edges of selected items

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

        r = {"move": edges_to_move, "refresh": edges_to_refresh}
        # print("move: %r\nrefresh: %r" % (edges_to_move, edges_to_refresh))
        return r

    def get_nodes_bbox(self, visible_only=True):
        """Return bounding box of all nodes in scene

        ..todo :
            This function could be refactored

        :param visible_only: If true, only evaluate visible NodeSlot
        :type visible_only: bool

        :returns: A bounding rectangle
        :rtype: :class:`QtCore.QrectF`

        """
        if not self._nodes:
            return QtCore.QRectF()

        min_x = SCENE_WIDTH / 2
        min_y = SCENE_HEIGHT / 2
        max_x = - min_x
        max_y = - min_y
        min_x_node = None
        min_y_node = None
        max_x_node = None
        max_y_node = None

        for node in self._nodes:
            if visible_only and not node.isVisible():
                continue

            if node.x() < min_x:
                min_x = node.x()
                min_x_node = node
            if node.y() < min_y:
                min_y = node.y()
                min_y_node = node
            if node.x() > max_x:
                max_x = node.x()
                max_x_node = node
            if node.y() > max_y:
                max_y = node.y()
                max_y_node = node

        top_left = QtCore.QPointF(
            min_x + min_x_node.boundingRect().topLeft().x(),
            min_y + min_y_node.boundingRect().topLeft().y())
        bottom_right = QtCore.QPointF(
            max_x + max_x_node.boundingRect().bottomRight().x(),
            max_y + max_y_node.boundingRect().bottomRight().y())
        return QtCore.QRectF(top_left, bottom_right)
