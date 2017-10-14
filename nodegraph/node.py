#==============================================================================
#
#  Insert gnu license here
#
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

        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable |
                      QtGui.QGraphicsItem.ItemIsSelectable)

        self.setAcceptHoverEvents(False)

        # Build output slot
        self._output = NodeSlot("out", scene,
                                family=NodeSlot.OUTPUT,
                                radius=self._slot_radius,
                                outline=self._outline,
                                label=NodeSlotLabel.LABEL_LEFT,
                                parent=self)

        # Build input slots
        self._inputs = []
        for slot_name in inputs:
            aninput = NodeSlot(slot_name, scene,
                               radius=self._slot_radius,
                               outline=self._outline,
                               label=NodeSlotLabel.LABEL_RIGHT,
                               parent=self)
            self._inputs.append(aninput)

        self._update()


    def _update(self):
        """ Update slots internal properties

        """
        slot_height = self._slot_radius*2 + self._outline
        base_y = self._height/2 + self._label_height/2 + self._outline/2

        # Update output
        init_y = base_y - slot_height/2
        self._output_pos = QtCore.QPointF(self._width - self._slot_radius,
                                          init_y)

        # # Update inputs
        # init_y = base_y - slot_height*len(self._inputs)/2
        # for i, _input in enumerate(self._inputs):
        #     self._inputs[i].setPos(-self._slot_radius, init_y+ slot_height*i)

        self._draw_slot = QtCore.QRectF(0, 0, self._slot_radius*2,
                                        self._slot_radius*2)

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
            font = QtGui.QFont("Arial", 12)
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

            if lod >= 0.35:
                # Draw output (Ellipse)
                rect = QtCore.QRectF(self._draw_slot)
                rect.moveTo(self._output_pos)
                painter.drawEllipse(rect)

                # Draw input (Ellipse)
                # for aninput in self._inputs:
                #     rect = QtCore.QRect(self._draw_slot)
                #     rect.moveTo(self._inputs)
            else:
                # Draw output (Rectangle)
                rect = QtCore.QRectF(self._draw_slot)
                rect.moveTo(self._output_pos)
                painter.drawRect(rect)
        else:
            self.setAcceptHoverEvents(False)

        # Draw slot labels
        if lod >= 0.6:
            font = QtGui.QFont("Arial", 10)
            font.setStyleStrategy(QtGui.QFont.ForceOutline)
            painter.setFont(font)
            painter.setPen(QtGui.QPen(self.scene().palette().text(), 1))

            width = self._width/2 - self._slot_radius - self._outline
            height = self._slot_radius*2

            # Output
            alignment = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight
            rect = QtCore.QRectF(self._width/2, self._output_pos.y(),
                                  width, height)
            painter.drawText(rect, alignment, "out")

            # Input
            #alignment = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft
            #rect = QtCore.QRectF(height + self._outline, 0, width, height)
            #painter.drawText(rect, alignment, "in")

        # Draw debug
        if DEBUG:
            painter.setBrush(QtGui.QBrush())
            painter.setPen(QtGui.QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

        return


    def hoverMoveEvent(self, event):
        """

        """
        rect = QtCore.QRectF(self._draw_slot)
        rect.moveTo(self._output_pos)

        if rect.contains(event.pos()):
            print("Hover slot")

        # Call normal behavior
        QtGui.QGraphicsItem.hoverMoveEvent(self, event)

        return


    def mousePressEvent(self, event):
        """

        """
        buttons = event.buttons()
        modifiers = event.modifiers()

        if buttons == QtCore.Qt.LeftButton:
            rect = QtCore.QRectF(self._draw_slot)
            rect.moveTo(self._output_pos)

            if rect.contains(event.pos()):
                print("Click on slot")
                mouse_pos = self.mapToScene(event.pos())
                self.scene().start_interactive_edge(self._output, mouse_pos)
                event.accept()

                return None

        QtGui.QGraphicsItem.mousePressEvent(self, event)

class NodeSlot(object):

    """
    Base class for edge slot

    """

    INPUT = 0
    OUTPUT = 1

    def __init__(self, name, scene, family=None, radius=10, outline=6,
        label=None, parent=None):
        """Instance this class

        """
        #QtGui.QGraphicsItem.__init__(self, parent=parent, scene=scene)
        self._name = name
        self._family = family or self.INPUT
        self._radius = radius
        self._outline = outline
        self._label = None
        self._lod = 1
        self._bbox = None # cache container
        self._round_slot = None
        self._rect_slot = None

        #self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        #self.setAcceptHoverEvents(True)

        # Create text label if required
        #if self._label:
        #    self.build_label()

        self._update()

    @property
    def family(self):
        """Return the family of the slot

        """
        return self._family


    def _update(self):
        """Update node slot

        """
        self._bbox = QtCore.QRectF(- self._outline/2,
                                   - self._outline/2,
                                   self._radius*2 + self._outline,
                                   self._radius*2 + self._outline)

        self._draw_rect = QtCore.QRectF(0, 0, self._radius*2, self._radius*2)


    def boundingRect(self):
        """Return a QRectF that represents the bounding box.
        Here that sould be the bounding box of the slot.

        """
        return self._bbox


    def paint(self, painter, option, widget=None):
        """Re-implement paint function

        """
        # Resolve level of detail
        self._lod = option.levelOfDetailFromTransform(painter.worldTransform())

        # Resolve fill brush
        fill_brush = self.scene().palette().text()
        outline_brush = self.scene().palette().button()
        if option.state & QtGui.QStyle.State_Selected:
            outline_brush = self.scene().palette().highlight()
        if option.state & QtGui.QStyle.State_MouseOver:
            fill_color = fill_brush.color().darker(250)
            fill_brush.setColor(fill_color)

        painter.setBrush(fill_brush)
        painter.setPen(QtGui.QPen(outline_brush, self._outline))

        # Draw slot
        if self._lod >= 0.35:
            painter.drawEllipse(self._draw_rect)
        else:
            painter.drawRect(self._draw_rect)

        # Hide/show label
        if self._label:
            if self._lod >= 0.6:
                for child in self.childItems():
                    child.setVisible(True)
            else:
                for child in self.childItems():
                    child.setVisible(False)

        # Draw debug
        if DEBUG:
            painter.setBrush(QtGui.QBrush())
            painter.setPen(QtGui.QColor(0, 0, 255))
            painter.drawRect(self.boundingRect())

        return


    # def mousePressEvent(self, event):
    #     """Re-implement mouse press event

    #     """
    #     buttons = event.buttons()
    #     modifiers = event.modifiers()

    #     if buttons == QtCore.Qt.LeftButton:
    #         # msg = ("%s (%s) slot %s pressed!" %
    #         #        (self.parentItem()._name, self._family, self._name))
    #         # print(msg)
    #         mouse_pos = self.mapToScene(event.pos())
    #         self.scene().start_interactive_edge(self, mouse_pos)

    #     QtGui.QGraphicsItem.mousePressEvent(self, event)


    # def build_label(self):
    #     """

    #     """
    #     width = self.parentItem()._width/2 - self._radius - self._outline
    #     height = self._radius*2
    #     return NodeSlotLabel(self._name, width, height, self._label, self)


class NodeSlotLabel(QtGui.QGraphicsSimpleTextItem):

    """
    Handles drawing of a node slot label

    """

    LABEL_LEFT = 1
    LABEL_RIGHT = 2

    def __init__(self, text, width, height, mode, parent=None):
        """Instance this class

        """
        QtGui.QGraphicsSimpleTextItem.__init__(self, text, parent=parent)

        self._text = text
        self._width = width
        self._height = height
        self._outline = parent._outline
        self._mode = mode

        font = QtGui.QFont("Arial", 10)
        font.setStyleStrategy(QtGui.QFont.ForceOutline)
        self.setFont(font)
        self.setPen(QtGui.QPen(self.scene().palette().text(), 1))


    def boundingRect(self):
        """Return a QRectF that represents the bounding box.
        Here that sould be the bounding box label

        """
        if self._mode & self.LABEL_RIGHT:
            rect = QtCore.QRectF(self._height + self._outline, 0,
                                 self._width, self._height)
        elif self._mode & self.LABEL_LEFT:
            rect = QtCore.QRectF(- self._width -self._outline, 0,
                                 self._width, self._height)
        return rect


    def paint(self, painter, option, widget=None):
        """Re-implement paint method

        """
        if self._mode & self.LABEL_RIGHT:
            alignment = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft
        elif self._mode & self.LABEL_LEFT:
            alignment = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight

        # Draw label
        painter.setFont(self.font())
        painter.setPen(self.pen())
        painter.drawText(self.boundingRect(), alignment, self._text)

        # Draw debug
        if DEBUG:
            painter.setBrush(QtGui.QBrush())
            painter.setPen(QtGui.QColor(255, 0, 255))
            painter.drawRect(self.boundingRect())

        return
