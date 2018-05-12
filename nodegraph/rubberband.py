# =============================================================================
# Nodegraph-pyqt
#
# Everyone is permitted to copy and distribute verbatim copies of this
# document, but changing it is not allowed.
#
# For any questions, please contact: dsideb@gmail.com
#
# GNU LESSER GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
# =============================================================================

"""
Custom rubber band selection aimed at being more efficient than the
default one with a large numbers of items

"""

from . import QtCore, QtGui
# from .node import Node
# from .edge import Edge

# from constant import DEBUG


class RubberBand(QtGui.QGraphicsItem):

    """
    Draw outline of a rectangle (as a shape)

    """

    REPLACE_SELECTION = 1
    ADD_SELECTION = 2
    MINUS_SELECTION = 4
    TOGGLE_SELECTION = 8

    def __init__(self, init_pos, scene, outline=2):
        """Creates an instance of this class

        :param init_pos: Point of origin of the rubber band
        :type init_pos: :class:`QtCore.QPointF`

        :param scene: GraphicsScene that holds the source and target nodes
        :type scene: :class:`nodegraph.scene.Scene`

        :param outline: Width of the edge and arrow outline
        :type outline: int

        :returns: An instance of this class
        :rtype: :class:`nodegraph.rubberband.RubberBand`

        """
        QtGui.QGraphicsItem.__init__(self, parent=None, scene=scene)

        self._source_pos = init_pos
        self._mouse_pos = init_pos
        self._outline = outline
        self._shape = None
        self._selection_mode = self.REPLACE_SELECTION

        # Settings
        self.setZValue(10)

        # Update
        self._update()

    def _update(self):
        """Update internal properties

        """
        # Update path
        self._shape = QtGui.QPainterPath()
        poly = QtGui.QPolygonF([
            self._source_pos,
            QtCore.QPointF(self._mouse_pos.x(), self._source_pos.y()),
            self._mouse_pos,
            QtCore.QPoint(self._source_pos.x(), self._mouse_pos.y())
        ])
        self._shape.addPolygon(poly)
        self._shape.closeSubpath()

    def update(self):
        """Re-implement update of QtGraphicsItem

        """
        # Update internal containers
        self._update()

        QtGui.QGraphicsLineItem.update(self)

    def shape(self):
        """Re-implement shape method
        Return a QPainterPath that represents the bounding shape

        """
        return self._shape

    def boundingRect(self):
        """Re-implement bounding box method

        """
        # Infer bounding box from shape
        return self._shape.controlPointRect()

    def paint(self, painter, option, widget=None):
        """Re-implement paint method

        """
        # Define pen
        palette = (self.scene().palette() if self.scene()
                   else option.palette)
        pen = QtGui.QPen()
        pen.setBrush(palette.highlight())
        pen.setCosmetic(True)
        pen.setWidth(self._outline)
        pen.setStyle(QtCore.Qt.DashLine)

        # Draw Shape
        painter.setPen(pen)
        # painter.drawPath(self._shape)

        color = palette.highlight().color()
        color.setAlphaF(0.2)
        painter.setBrush(QtGui.QColor(color))
        painter.drawRect(self.shape().controlPointRect())

        return

    def refresh(self, mouse_pos=None, init_pos=None):
        """Update corner of rubber band defined by mouse pos

        :param mouse_pos: Scene position of the mouse
        :type mouse_pos: :class:`QtCore.QPointF`

        """
        if mouse_pos:
            self._mouse_pos = mouse_pos
        if init_pos:
            self._source_pos = init_pos

        # self.scene().setSelectionArea(self.shape(),
        #                               QtCore.Qt.ContainsItemBoundingRect)
        self.prepareGeometryChange()
        self.update()

    def update_scene_selection(self, operation=None, intersect=None):
        """Update scene selection from the current rubber band bounding box

        :param operation: Replace, add or remove from the current selection
        :type operation: int

        :param intersect:
            Specify how items are selected, by default the item bounding box
            must be fully contained
        :type intersect: :class:`QtCore.Qt.ItemSelectionMode`

        """
        operation = operation or self.REPLACE_SELECTION
        intersect = intersect or QtCore.Qt.ContainsItemBoundingRect

        if operation == self.ADD_SELECTION:
            current_selection = self.scene().selectedItems()
            self.scene().setSelectionArea(self.shape(), intersect)

            for item in current_selection:
                item.setSelected(True)

        elif operation == self.MINUS_SELECTION:
            items = self.scene().items(self.shape(), intersect)

            for item in items:
                item.setSelected(False)

        elif operation == self.TOGGLE_SELECTION:
            items = self.scene().items(self.shape(), intersect)

            for item in items:
                if item.isSelected():
                    item.setSelected(False)
                else:
                    item.setSelected(True)
        else:
            self.scene().setSelectionArea(self.shape(), intersect)
