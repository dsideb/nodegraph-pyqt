#==============================================================================
# GNU LESSER GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
#
# Everyone is permitted to copy and distribute verbatim copies of this license
# document, but changing it is not allowed.
#
# Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
#==============================================================================

"""
Edge definition including:

    * Edge
    * InteractiveEdge

"""
import sha

from . import QtCore, QtGui

from constant import DEBUG
from polygons import ARROW_STANDARD, ARROW_SLIM
from .node import NodeSlot

class Edge(QtGui.QGraphicsItem):

    """
    Node Edge base class that displays a directed line between two slots
    of a source and target node

    """

    ARROW_STANDARD = 1
    ARROW_SLIM = 2

    def __init__(self, source_slot, target_slot, scene, outline=2, arrow=None):
        """Creates an instance of this class

        :param source: Source slot (should be a output one)
        :type source: :class:`nodegraph.node.NodeSlot`

        :param target: Target slot (should be an input one)
        :type target: :cLass:`nodegraph.node.NodeSlot`

        :param scene: GraphicsScene that holds the source and target nodes
        :type scene: :class:`nodegraph.nodegraphscene.NodeGraphScene`

        :param outline: Width of the edge and arrow outline
        :type outline: int

        :param arrow: Define type of arrow. By default, no arrow is drawn
        :type arrow: int

        :returns: An instance of this class
        :rtype: :class:`nodegraph.edge.Edge`

        """
        QtGui.QGraphicsItem.__init__(self, parent=None, scene=scene)

        self._source_slot = source_slot
        self._target_slot = target_slot
        self._outline = outline
        self._arrow = arrow
        self._lod = 1
        self._hash = ("%s.%s >> %s.%s" %
                      (source_slot.parent._name, source_slot._name,
                       target_slot.parent._name, target_slot._name))
        self._shape = None
        self._line = None

        # Set tooltip
        self.setToolTip(self._hash)

        # Hash the hash
        self._hash = sha.sha(self._hash).hexdigest()

        # Reference hash in nodes slot
        source_slot.edge = self._hash
        target_slot.edge = self._hash

        # Settings
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-10)

        # Update
        self.update()


    @property
    def hash(self):
        """Return the unique of this edge

        """
        return self._hash


    def _update_line(self):
        """Resolve start and end point from current source and target position

            :returns: A qt line object
            :rtype: :class:`QtCore.QLineF`

        """
        start = QtCore.QPointF(0, 0)
        end = self._target_slot.center - self._source_slot.center

        self._line = QtCore.QLineF(start, end)


    def _update(self):
        """Update internal properties

        """
        # Update position
        self.setPos(self._source_slot.center)

        # Update line
        self._update_line()


    def update(self):
        """Re-implement update of QtGraphicsItem

        """
        # Update internal containers
        self._update()

        # Update path
        width = 1/self._lod if self._outline*self._lod < 1 else self._outline
        norm = self._line.unitVector().normalVector()
        norm = width*3*QtCore.QPointF(norm.x2()-norm.x1(),
                                          norm.y2()-norm.y1())

        self._shape = QtGui.QPainterPath()
        poly = QtGui.QPolygonF([self._line.p1() - norm,
                                self._line.p1() + norm,
                                self._line.p2() + norm,
                                self._line.p2() - norm])
        self._shape.addPolygon(poly)
        self._shape.closeSubpath()

        QtGui.QGraphicsLineItem.update(self)


    def shape(self):
        """Re-implement shape method
        Return a QPainterPath that represents the bounding shape

        """
        return self._shape


    def boundingRect(self):
        """Re-implement bounding box method

        """
        # Update node
        #self.update()

        # Infer bounding box from shape
        return self._shape.controlPointRect()


    def paint(self, painter, option, widget=None):
        """Re-implement paint method

        """
        # Update level of detail
        self._lod = option.levelOfDetailFromTransform(painter.worldTransform())

        # Update brush
        palette = (self.scene().palette() if self.scene()
                   else option.palette)
        brush = palette.text()
        if option.state & QtGui.QStyle.State_Selected:
            brush = palette.highlight()
        elif option.state & QtGui.QStyle.State_MouseOver:
            color = brush.color().darker(250)
            brush.setColor(color)

        # Update unit width
        width = 1/self._lod if self._outline*self._lod < 1 else self._outline

        # Draw line
        painter.setPen(QtGui.QPen(brush, width))
        painter.drawLine(self._line)

        # Draw arrow if needed
        if self._arrow and self._lod > 0.15:
           # Construct arrow
            matrix = QtGui.QMatrix()
            matrix.rotate(-self._line.angle())
            matrix.scale(width, width)

            if self._arrow & self.ARROW_STANDARD:
                poly = matrix.map(ARROW_STANDARD)
            elif self._arrow & self.ARROW_SLIM:
                poly = matrix.map(ARROW_SLIM)

            vec = self._line.unitVector()
            vec = (self._line.length()/2)*QtCore.QPointF(vec.x2() - vec.x1(),
                                                          vec.y2() - vec.y1())
            poly.translate(self._line.x1(), self._line.y1())
            poly.translate(vec.x(), vec.y())

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(brush)
            painter.drawPolygon(poly)

        # Draw debug
        if DEBUG:
            painter.setBrush(QtGui.QBrush())
            painter.setPen(QtGui.QColor(255, 0, 0))
            painter.drawPath(self.shape())

            painter.setPen(QtGui.QColor(0, 255, 0))
            painter.drawRect(self.boundingRect())

        return


    def refresh(self, source_slot=None, target_slot=None):
        """Update start/end position if provided and force
        redraw

        :param source_slot: Source slot (output or input)
        :type source_slot: :class:`nodegraph.node.NodeSlot`
        :param target_slot: Source slot (output or input)
        :type target_slot: :class:`nodegraph.node.NodeSlot`

        """
        if source_slot:
            self._source_slot = source_slot
        if target_slot:
            self._target_slot = target_slot
        self.prepareGeometryChange()
        self.update()


class InteractiveEdge(Edge):

    """Draw an edge where one one the end point is the currrent mouse pos

    """

    def __init__(self, source_slot, mouse_pos, scene, outline=2, arrow=None):
        """Creates an instance of this class

        :param source: Source slot (should be a output one)
        :type source: :class:`nodegraph.node.NodeSlot`
        :param mouse_pos: Current scene position for mouse
        :type mouse: :class:`QtCore.QPointF`
        :param scene: GraphicsScene that holds the source and target nodes
        :type scene: :class:`nodegraph.nodegraphscene.NodeGraphScene`
        :param outline: Width of the edge and arrow outline
        :type outline: int
        :param arrow: Define type of arrow. By default, no arrow is drawn
        :type arrow: int

        :returns: An instance of this class
        :rtype: :class:`nodegraph.edge.InteractiveEdge`

        """
        QtGui.QGraphicsItem.__init__(self, parent=None, scene=scene)

        self._source_slot = source_slot
        self._mouse_pos = mouse_pos
        self._outline = outline
        self._arrow = arrow
        self._lod = 1
        self._shape = None
        self._line = None

        self.setZValue(-10)

        # Update line
        self.update()


    def _update_line(self):
        """Re-implement function that updates edge line definition

        """
        start = QtCore.QPoint(0, 0)
        if self._source_slot.family & NodeSlot.OUTPUT:
            end = self._mouse_pos - self._source_slot.center
        else:
            end = self._source_slot.center - self._mouse_pos

        self._line = QtCore.QLineF(start, end)


    def _update(self):
        """Re-implement function that updates internal container

        """
        if self._source_slot.family & NodeSlot.OUTPUT:
            position = self._source_slot.center
        else:
            position = self._mouse_pos

        # Update position
        self.setPos(position)

        # Update line
        self._update_line()


    def refresh(self, mouse_pos, source_slot=None):
        """Re-implement function that updates start/end position and force
        redraw

        :param mouse_pos: Scene position of the mouse
        :type mouse_pos: :class:`QtCore.QPointF`
        :param source_slot: Source slot (output or input)
        :type source_slot: :class:`nodegraph.node.NodeSlot`

        """
        self._mouse_pos = mouse_pos
        if source_slot:
            self._source_slot = source_slot
        self.prepareGeometryChange()
        self.update()
