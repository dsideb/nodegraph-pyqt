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
    * NodeEdge
    * NodeInteractiveEdge

"""

from PySide import QtCore, QtGui

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
        self._last_visible_pos = self.pos()
        self._bbox = None # cache container

        self.setFlags(QtGui.QGraphicsItem.ItemIsMovable |
                      QtGui.QGraphicsItem.ItemIsSelectable)
                     # QtGui.QGraphicsItem.ItemSendsGeometryChanges)

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
        """ Update slots position

        """
        slot_height = self._slot_radius*2 + self._outline
        base_y = self._height/2 + self._label_height/2 + self._outline/2

        # Update output
        init_y = base_y - slot_height/2
        self._output.setPos(self._width - self._slot_radius, init_y)

        # Update inputs
        init_y = base_y - slot_height*len(self._inputs)/2
        for i, _input in enumerate(self._inputs):
            self._inputs[i].setPos(-self._slot_radius, init_y+ slot_height*i)

        # Update bounding box
        self._bbox = QtCore.QRectF(-self._outline/2,
                                        -self._outline/2,
                                        self._width + self._outline,
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
            # TODO: Find a less expensive way (has an impact on redraw)
        #     self._output.setSelected(True)
        #     for _input in self._inputs:
        #         _input.setSelected(True)
        # else:

        #     self._output.setSelected(False)
        #     for _input in self._inputs:
        #         _input.setSelected(False)

        # Let's draw
        painter.save()

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


        # Hide/show slot
        if lod >= 0.15:
            for child in self.childItems():
                child.setVisible(True)
        else:
            for child in self.childItems():
                child.setVisible(False)

        painter.restore()
        return


    def mouseMoveEvent(self, event):
        """

        """
        buttonState = event.buttons()

        # # # Drag view while moving nodes
        # # if event.modifiers() & QtCore.Qt.ControlModifier:
        # #     print("toto")

        # if buttonState == QtCore.Qt.LeftButton:
        #     if not visible_rect.contains(mouse_pos.x(), mouse_pos.y()):
        #         # Tag this node for full redraw
        #         pass

        # Call normal behavior
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)

        return


    def itemChange(self, change, value):
        """Re-implement ancestor method that allows for changes notifications

        """
        # For a selected item, if its position is change, check it stays in the
        # visible area of the view
        if (self.isSelected() and self.scene()
            and change == QtGui.QGraphicsItem.ItemPositionChange):
            view = self.scene().views()[0]

            visible_rect = view.mapToScene(view.rect()).boundingRect()
            if (not visible_rect.contains(value.x()+self._width/2,
                                          value.y()+self._height/2)):
                return self._last_visible_pos
            else:
                self._last_visible_pos = self.pos()

        return value


class NodeSlot(QtGui.QGraphicsItem):

    """
    Base class for edge slot

    """

    INPUT = 0
    OUTPUT = 1

    def __init__(self, name, scene, family=None, radius=10, outline=6,
        label=None, parent=None):
        """Instance this class

        """
        QtGui.QGraphicsItem.__init__(self, parent=parent, scene=scene)
        self._name = name
        self._family = family or self.INPUT
        self._radius = radius
        self._outline = outline
        self._label = label
        self._lod = 1
        self._bbox = None # cache container

        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        # Create text label if required
        if self._label:
            self.build_label()

        self._update()

    @property
    def family(self):
        """Return the family of the slot

        """
        return self._family


    def _update(self):
        """Update this node slot

        """
        self._bbox = QtCore.QRect(- self._outline/2,
                                  - self._outline/2,
                                  self._radius*2 + self._outline,
                                  self._radius*2 + self._outline)


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

        painter.save()
        painter.setBrush(fill_brush)
        painter.setPen(QtGui.QPen(outline_brush, self._outline))

        # Draw slot
        if self._lod >= 0.35:
            painter.drawEllipse(QtCore.QRectF(0,
                                              0,
                                              self._radius*2,
                                              self._radius*2))
        else:
            painter.drawRect(QtCore.QRectF(0,
                                           0,
                                           self._radius*2 - self._radius/3,
                                           self._radius*2 - self._radius/3))

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

        painter.restore()
        return


    def mousePressEvent(self, event):
        """Re-implement mouse press event

        """
        buttons = event.buttons()
        modifiers = event.modifiers()

        if buttons == QtCore.Qt.LeftButton:
            # msg = ("%s (%s) slot %s pressed!" %
            #        (self.parentItem()._name, self._family, self._name))
            # print(msg)
            mouse_pos = self.mapToScene(event.pos())
            self.scene().start_interactive_edge(self, mouse_pos)

        QtGui.QGraphicsItem.mousePressEvent(self, event)


    def build_label(self):
        """

        """
        width = self.parentItem()._width/2 - self._radius - self._outline
        height = self._radius*2
        return NodeSlotLabel(self._name, width, height, self._label, self)


class NodeSlotLabel(QtGui.QGraphicsSimpleTextItem):

    """
    Handles drawing of a node slot label

    """

    LABEL_LEFT = 1
    LABEL_RIGHT = 2

    def __init__(self, text, width, height, mode, parent=None):
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

        # Let's draw
        painter.save()

        # Draw label
        painter.setFont(self.font())
        painter.setPen(self.pen())
        painter.drawText(self.boundingRect(), alignment, self._text)

        # Draw debug
        if DEBUG:
            painter.setBrush(QtGui.QBrush())
            painter.setPen(QtGui.QColor(255, 0, 255))
            painter.drawRect(self.boundingRect())

        painter.restore()
        return


class NodeEdge(QtGui.QGraphicsLineItem):

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
        :returns: An instance of this class
        :rtype: :class:`nodegraph.node.NodeEdge`

        """
        QtGui.QGraphicsLineItem.__init__(self, parent=None, scene=scene)

        self._source_slot = source_slot
        self._target_slot = target_slot
        self._outline = outline
        self._arrow = arrow
        # Cache container for polygon
        self._arrow_polygon = self._get_arrow_polygon()
        self._lod = 1

        # Set tooltip
        tooltip = ("%s(%s)  >> %s(%s)" %
                   (source_slot.parentItem()._name, source_slot._name,
                    target_slot.parentItem()._name, target_slot._name))
        self.setToolTip(tooltip)

        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)

        self.setAcceptHoverEvents(True)
        self.setZValue(-10)

        # Update line
        self.setLine(self._get_line())


    def _get_line(self):
        # Resolve start and end point from current source and target position
        start = (self._source_slot.parentItem().pos() +
                 self._source_slot.pos() +
                 self._source_slot.boundingRect().center())
        end = (self._target_slot.parentItem().pos() +
               self._target_slot.pos() +
               self._target_slot.boundingRect().center())

        return QtCore.QLineF(start, end)


    def _get_arrow_polygon(self):
        """Return arrow polygon

        """
        height = 4
        width = height*3/4
        thick = height/2
        if self._arrow & self.ARROW_STANDARD:
            return QtGui.QPolygonF([QtCore.QPointF(height, 0),
                                    QtCore.QPointF(- height, - width),
                                    QtCore.QPointF(- height, width),
                                    QtCore.QPointF(height, 0)])
        elif self._arrow & self.ARROW_SLIM:
            return QtGui.QPolygonF([QtCore.QPointF(thick/2, 0),
                                    QtCore.QPointF(- thick, - width),
                                    QtCore.QPointF(- thick*2, - width),
                                    QtCore.QPointF(- thick/2, 0),
                                    QtCore.QPointF(- thick*2, width),
                                    QtCore.QPointF(- thick, width)])


    def shape(self):
        """Re-implement shape method
        Return a QPainterPath that represents the bounding shape

        """
        width = 1/self._lod if self._outline*self._lod < 1 else self._outline
        norm = self.line().unitVector().normalVector()
        norm = width*3*QtCore.QPointF(norm.x2()-norm.x1(),
                                          norm.y2()-norm.y1())

        path = QtGui.QPainterPath()
        poly = QtGui.QPolygonF([self.line().p1() - norm,
                                self.line().p1() + norm,
                                self.line().p2() + norm,
                                self.line().p2() - norm])
        path.addPolygon(poly)
        path.closeSubpath()

        return path


    def boundingRect(self):
        """Re-implement bounding box method

        """
        # Update line
        self.setLine(self._get_line())

        # Infer bounding box from shape
        return self.shape().controlPointRect()


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
        self.setPen(QtGui.QPen(brush, width))

        # Let's draw!
        painter.save()

        # Draw line
        painter.setPen(self.pen())
        painter.drawLine(self.line())

        # Draw arrow if needed
        if self._arrow and self._lod > 0.15:
           # Construct arrow
            matrix = QtGui.QMatrix()
            matrix.rotate(-self.line().angle())
            matrix.scale(width, width)
            poly = matrix.map(self._arrow_polygon)
            vec = self.line().unitVector()
            vec = (self.line().length()/2)*QtCore.QPointF(vec.x2() - vec.x1(),
                                                          vec.y2() - vec.y1())
            poly.translate(self.line().x1(), self.line().y1())
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

        painter.restore()
        return


class NodeInteractiveEdge(NodeEdge):

    """Draw an edge where one one the end point is the currrent mouse pos

    """

    def __init__(self, source_slot, mouse_pos, scene, outline=2, arrow=None):
        """Creates an instance of this class

            :param source: (<QPointF)
                Source position
            :param target: (<QPointF>)
                Target position
            :param scene: (<NodeGraphScene>)
                GraphicsScene that holds the source and target nodes
            :returns: (<NodeEdge>)

        """
        QtGui.QGraphicsLineItem.__init__(self, parent=None, scene=scene)

        self._source_slot = source_slot
        self._mouse_pos = mouse_pos
        self._outline = outline
        self._arrow = arrow
        # Cache container for polygon
        self._arrow_polygon = self._get_arrow_polygon()
        self._lod = 1

        self.setZValue(-10)

        # Update line
        self.setLine(self._get_line())


    def _get_line(self):
        start = self._mouse_pos
        end = (self._source_slot.parentItem().pos() +
               self._source_slot.pos() +
               self._source_slot.boundingRect().center())
        if self._source_slot.family & NodeSlot.OUTPUT:
            start = end
            end = self._mouse_pos
        return QtCore.QLineF(start, end)


    def refresh(self, mouse_pos, source_slot=None):
        self._mouse_pos = mouse_pos
        if source_slot:
            self._source_slot = source_slot
        self.setLine(self._get_line())
