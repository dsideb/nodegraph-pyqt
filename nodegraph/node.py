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
Base node definition including

    * Node
    * NodeSlot
    * NodeSlotLabel

"""
from . import QtCore, QtGui

from constant import DEBUG

class Node(QtGui.QGraphicsItem):

    """
    Base class for node graphic item

    As nuch as possible, everything is drawn in the node paint function for
    performance reasons.

    """

    def __init__(self, name, scene, inputs=["in"], parent=None):
        """Create an instance of this class

        """
        QtGui.QGraphicsItem.__init__(self, parent=parent, scene=scene)
        self._name = name
        self._width = 160
        self._height = 130
        self._outline = 6
        self._slot_radius = 10
        self._label_height = 34
        self._bbox = None # cache container
        self._round_slot = None
        self._rect_slot = None
        self._hover_slot = False

        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable |
                      QtGui.QGraphicsItem.ItemIsSelectable)

        self.setAcceptHoverEvents(False)

        # Build output slot
        self._output = NodeSlot("out", self, family=NodeSlot.OUTPUT)

        # Build input slots
        self._inputs = []
        for slot_name in inputs:
            aninput = NodeSlot(slot_name, self)
            self._inputs.append(aninput)

        # Update internal containers
        self._update()


    @property
    def name(self):
        """Return the family of the slot

        """
        return self._name


    def _update(self):
        """ Update slots internal properties

        """
        slot_height = self._slot_radius*2 + self._outline
        base_y = self._height/2 + self._label_height/2 + self._outline/2

        # Update base slot bounding box
        self._draw_slot = QtCore.QRectF(0, 0, self._slot_radius*2,
                                        self._slot_radius*2)
        # Update output
        init_y = base_y - slot_height/2
        self._output.rect = QtCore.QRectF(self._draw_slot).translated(
            self._width - self._slot_radius, init_y)

        # # Update inputs
        init_y = base_y - slot_height*len(self._inputs)/2
        for i, _input in enumerate(self._inputs):
            self._inputs[i].rect = QtCore.QRectF(self._draw_slot).translated(
                -self._slot_radius, init_y+ slot_height*i)

        # Update bounding box
        self._bbox = QtCore.QRectF(
                -self._outline/2 -self._slot_radius,
                -self._outline/2,
                self._width + self._outline + self._slot_radius*2,
                self._height + self._outline)


    def boundingRect(self):
        """Return a QRect that represents the bounding box of the node.
        Here that sould be the bounding box of the primary shape of the node.

        """
        return self._bbox


    def paint(self, painter, option, widget=None):
        """Re-implement paint method

        """
        #print("Redraw %s" % self._name)
        lod = option.levelOfDetailFromTransform(painter.worldTransform())

        # Resolve fill, text and outlines brush
        fill_brush = self.scene().palette().button()
        text_brush = self.scene().palette().text()
        if option.state & QtGui.QStyle.State_Selected:
            fill_brush = self.scene().palette().highlight()
            text_brush = self.scene().palette().highlightedText()

        # Set brush and pen, then start drawing
        painter.setBrush(self.scene().palette().buttonText())
        painter.setPen(QtGui.QPen(fill_brush, self._outline))

        # Draw primary shape
        painter.drawRect(0, 0, self._width, self._height)

        # Draw label background
        # TODO: Color should be based on node type
        painter.setBrush(QtGui.QColor(90, 90, 140))
        painter.setPen(QtCore.Qt.NoPen)
        label_rect = QtCore.QRectF(self._outline/2,
                                   self._outline/2,
                                   self._width - self._outline,
                                   self._label_height - self._outline/2)
        painter.drawRect(label_rect)

        # Draw text
        if lod >= 0.4:
            font = QtGui.QFont("Arial", 14)
            font.setStyleStrategy(QtGui.QFont.ForceOutline)
            painter.setFont(font)
            painter.setPen(QtGui.QPen(text_brush, 1))
            painter.scale(1, 1)
            painter.drawText(label_rect, QtCore.Qt.AlignCenter, self._name)


        # Draw slots
        if lod >= 0.15:
            self.setAcceptHoverEvents(True)
            painter.setBrush(self.scene().palette().text())
            painter.setPen(QtGui.QPen(fill_brush, self._outline))

            if self._hover_slot:
                # Hover color should be driven by slot type
                painter.setBrush(self.scene().palette().highlightedText())

            if lod >= 0.35:
                # Draw output (Ellipse)
                painter.drawEllipse(self._output._rect)

                # Draw input (Ellipse)
                for aninput in self._inputs:
                    painter.drawEllipse(aninput.rect)
            else:
                # Draw output (Rectangle)
                painter.drawRect(self._output._rect)

                # Drae input (Rectangle)
                for aninput in self._inputs:
                    painter.drawRect(aninput.rect)
        else:
            self.setAcceptHoverEvents(False)

        # Draw slot labels
        if lod >= 0.5:
            font = QtGui.QFont("Arial", 11)
            font.setStyleStrategy(QtGui.QFont.ForceOutline)
            painter.setFont(font)
            painter.setPen(QtGui.QPen(self.scene().palette().text(), 1))

            width = self._width/2 - self._slot_radius - self._outline
            height = self._slot_radius*2

            # Output
            alignment = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight
            rect = QtCore.QRectF(self._width/2, self._output._rect.top(),
                                  width, height)
            painter.drawText(rect, alignment, "out")
            # painter.setBrush(QtCore.Qt.NoBrush)
            # painter.drawRect(rect)

            # Input
            alignment = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft
            for aninput in self._inputs:
                rect = QtCore.QRectF(self._slot_radius + self._outline,
                                     aninput._rect.top(),
                                     width,
                                     height)
                painter.drawText(rect, alignment, aninput.name)
                # painter.setBrush(QtCore.Qt.NoBrush)
                # painter.drawRect(rect)

        # Draw debug
        if DEBUG:
            painter.setBrush(QtGui.QBrush())
            painter.setPen(QtGui.QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

        return


    def hoverMoveEvent(self, event):
        """

        """
        if self._output._rect.contains(event.pos()):
            self._update_hover_slot(True)
        else:
            self._update_hover_slot(False)

        # Call normal behavior
        QtGui.QGraphicsItem.hoverMoveEvent(self, event)

        return


    def mousePressEvent(self, event):
        """

        """
        buttons = event.buttons()
        modifiers = event.modifiers()

        if buttons == QtCore.Qt.LeftButton:

            if self._output._rect.contains(event.pos()):
                mouse_pos = self.mapToScene(event.pos())
                self.scene().start_interactive_edge(self._output, mouse_pos)
                event.accept()
                return
            for aninput in self._inputs:
                if aninput._rect.contains(event.pos()):
                    mouse_pos = self.mapToScene(event.pos())
                    self.scene().start_interactive_edge(aninput, mouse_pos)
                    event.accept()
                    return

        QtGui.QGraphicsItem.mousePressEvent(self, event)


    def mouseMoveEvent(self, event):
        """

        """
        buttons = event.buttons()
        modifiers = event.modifiers()

        if buttons == QtCore.Qt.LeftButton:
            if self.scene().is_interactive_edge:
                # Edge creation mode, consumming event
                event.accept()
                return

        QtGui.QGraphicsItem.mouseMoveEvent(self, event)


    def _update_hover_slot(self, slot):
        if slot == self._hover_slot:
            # No change
            return

        self._hover_slot = slot
        self.update()


class NodeSlot(object):

    """
    Base class for edge slot

    """

    INPUT = 0
    OUTPUT = 1

    def __init__(self, name, parent, family=None):
        """Instance this class

        """
        #QtGui.QGraphicsItem.__init__(self, parent=parent, scene=scene)
        self._name = name
        self.parent = parent
        self._family = family or self.INPUT
        self._rect = None


    @property
    def name(self):
        """Return the family of the slot

        """
        return self._name


    @property
    def family(self):
        """Return the family of the slot

        """
        return self._family


    @property
    def rect(self):
        """Return bounding box of slot

        """
        return self._rect


    @rect.setter
    def rect(self, value):
        """ Set property rect

            :param value: class::`QtCore.QRectF`
        """
        self._rect = value


    @property
    def center(self):
        """Return center point of the slot in scene coordinates

        """
        return self.parent.mapToScene(self._rect.center())

