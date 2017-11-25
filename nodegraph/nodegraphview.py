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
import random

from . import QtCore, QtGui, QtOpenGL

from .node import Node
from .constant import SCENE_WIDTH, SCENE_HEIGHT


class NodeGraphView(QtGui.QGraphicsView):

    """
    Provides custom implementation of QGraphicsView

    """

    def __init__(self, scene, parent=None):
        """Create an instance of this class

        :param scene: NodeGraphScene reference
        :type scene: :class:`nodegraph.nodegraphScene.NodeGraphScene`

        :param parent: Parent widget
        :type parent: mixed

        :returns: An instance of this class
        :rtype: :class:`nodegraph.nodegraphView.NodeGraphView`

        """
        QtGui.QGraphicsView.__init__(self, scene, parent)
        self._last_mouse_pos = QtCore.QPoint(0, 0)
        self._width = SCENE_WIDTH
        self._height = SCENE_HEIGHT
        self._scale = 1.0
        self._is_view_initialised = False

        # Set scene
        self.setScene(scene)

        # Set scene rectangle
        self.scene().setSceneRect(
            QtCore.QRectF(-self._width/2, -self._height/2,
                          self._width, self._height))

        # Enable OpenGL
        # GL_format = QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers)
        # viewport = QtOpenGL.QGLWidget(GL_format)
        # self.setViewport(viewport)

        # Settings
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        #self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        #self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.setViewportUpdateMode(
            QtGui.QGraphicsView.BoundingRectViewportUpdate)
        #self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setDragMode(QtGui.QGraphicsView.NoDrag)
        self.setRubberBandSelectionMode(QtCore.Qt.ContainsItemBoundingRect)
        # self.setSizePolicy(QtGui.QSizePolicy.Expanding,
        #                    QtGui.QSizePolicy.Expanding)

        # Init scene
        self.setInteractive(True)


    def fit_view(self, selected=False, padding=50):
        """Set view transform in order to fit all/selected nodes in scene.

        :param selected: If enabled, fit only selected nodes
        :type selected: bool

        :param padding: Add padding around the target rectangle
        :type padding: int

        """
        # Resolve rectangle we want to zoom to
        selection = self.scene().selectedItems()
        if selected and selection:
            scene_rect = self._get_selection_bbox(selection)
        else:
            scene_rect = self.scene().itemsBoundingRect()

        # Add a bit of padding
        scene_rect.adjust(-padding, -padding, padding, padding)

        # Compare ratio, find resulting scale
        view_ratio = float(self.size().width())/float(self.size().height())
        fit_ratio = scene_rect.width()/scene_rect.height()
        x_ratio = scene_rect.width()/float(self.size().width())
        y_ratio = scene_rect.height()/float(self.size().height())
        new_scale = 1/max(x_ratio, y_ratio)

        if new_scale >= 1:
            # Maximum zoom limit reached.
            # Let's translate to center of rect with reset scale
            self._scale = 1
            self.resetTransform()
            self.centerOn(scene_rect.center())
        elif new_scale < 0.1:
            # Minimum zoom limit reached.
            # Let's translate to center of rect and set zoom to limit
            if (self._scale) != 0.1:
                self._scale = 1
                self.resetTransform()
                self.scale_view(0.1)
            self.centerOn(scene_rect.center())
        else:
            # Fit to rectangle while keeping aspect ratio
            self._scale = new_scale
            self.fitInView(scene_rect, QtCore.Qt.KeepAspectRatio)


    def translate_view(self, offset):
        """Translate view by the given offset

        :param offset: Translate the view
        :type offset: :class:`QtCore.QPointF`

        """
        self.setInteractive(False)
        self.translate(offset.x(), offset.y())
        self.setInteractive(True)


    def scale_view(self, scale_factor, limits=True):
        """Scale the view with upper and lower limits if True

        :param scale_factor:
        :type scale_factor: number

        :param limits: If true, will limits scene scale
        :type limits: bool

        """
        new_scale = self._scale * scale_factor
        if limits and (new_scale >= 1.0 or new_scale < 0.1):
            # Respecting scaling limits
            if new_scale >= 1.0:
                self._scale = 1
                self.resetTransform()
                return False
            elif new_scale < 0.1:
                scale_factor = new_scale = 0.1
                self.resetTransform()

        # Update global scale
        self._scale = new_scale
        self.setInteractive(False)
        self.scale(scale_factor, scale_factor)
        self.setInteractive(True)
        return True


    def keyPressEvent(self, event):
        """Re-implement keyPressEvent from base class

        :param event: Key event
        :type event: :class:`QtGui.QKeyEvent`

        """
        modifiers = event.modifiers()

        # if event.key() == QtCore.Qt.Key_Alt:
        #     self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        #     #self.setInteractive(False)

        if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            self.scene().delete_selected()


        if modifiers & QtCore.Qt.ControlModifier:
            print("P# CTRL ON")
            self.scene()._is_ctrl_key = True

        if modifiers & QtCore.Qt.ShiftModifier:
            print("P# SHIFT ON")
            self.scene()._is_shift_key = True

        if modifiers & QtCore.Qt.AltModifier:
            print("P# ALT ON")
            self.scene()._is_alt_key = True
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)

        # TODO: Document these!
        if event.text() in ['-', '_']:
            self.scale_view(0.9)
        if event.text() in ['+', '=']:
            self.scale_view(1.1)
        if event.text() in ["f"]:
            self.fit_view(selected=True)
        if event.text() in ["a"]:
            self.fit_view(selected=False)
        # if event.text() in ['t']:
        #     self.toggle_enabled()
        if event.text() in ['c']:
            n = self.scene().create_node("random%d"
                                         % random.randint(1, 1000000),
                                         inputs=["in", "in1", "in2"])
            n.setPos(self.mapToScene(self._last_mouse_pos)
                     - n.boundingRect().center())

        if event.text() in ['o']:
            for node in self.scene().selectedItems():
                if isinstance(node, Node):
                    node._height -= 10
                    node.refresh()
        if event.text() in ['p']:
            for node in self.scene().selectedItems():
                if isinstance(node, Node):
                    node._height += 10
                    node.refresh()
        if event.text() in ['s']:
            print(self._scale)


    def keyReleaseEvent(self, event):
        """Re-implement keyReleaseEvent from base class

        :param event: Key event
        :type event: :class:`QtGui.QKeyEvent`

        """
        modifiers = event.modifiers()

        # if event.key() == QtCore.Qt.Key_Alt:
        #     # self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        #     self.setDragMode(QtGui.QGraphicsView.NoDrag)

        if not modifiers & QtCore.Qt.ControlModifier:
            print("R### CTRL OFF")
            self.scene()._is_ctrl_key = False

        if not modifiers & QtCore.Qt.ShiftModifier:
            print("R### SHIFT OFF")
            self.scene()._is_shift_key = False

        if not modifiers & QtCore.Qt.AltModifier:
            print("R### ALT OFF")
            self.scene()._is_alt_key = False
            self.setDragMode(QtGui.QGraphicsView.NoDrag)

        return


    # def mousePressEvent(self, event):

    #     # # Consumme event if we are adding to selection
    #     # if self.scene()._is_shift_key:
    #     #     event.accept()
    #     #     return

    #     # buttons = event.buttons()
    #     # modifiers = event.modifiers()

    #     # if buttons == QtCore.Qt.LeftButton:
    #     #     #print("Button pressed!")
    #     #     pass

    #     QtGui.QGraphicsView.mousePressEvent(self, event)


    def mouseMoveEvent(self, event):
        """Re-implement mouseMoveEvent from base class

        :param event: Mouse event
        :type event: :class:`QtGui.QMouseEvent`

        """
        #buttons = event.buttons()

        self._last_mouse_pos = event.pos()
        QtGui.QGraphicsView.mouseMoveEvent(self, event)


    # def mouseReleaseEvent(self, event):
    #     #print("View Button released!")

    #     # Edge creation mode?
    #     if self.scene()._is_interactive_edge:
    #         self.scene().stop_interactive_edge()

    #     QtGui.QGraphicsView.mouseReleaseEvent(self, event)


    def wheelEvent(self, event):
        """Re-implement wheelEvent from base class

        :param event: Wheel event
        :type event: :class:`QtGui.QWheelEvent`

        """
        delta = event.delta()
        #p = event.pos()

        scale_factor = pow(1.1, delta / 240.0)
        self.scale_view(scale_factor)
        event.accept()


    def showEvent(self, event):
        """Re-implent showEvent from base class

        :param event: Show event
        :type event: :class:`QtGui.QShowEvent`

        """
        if not self._is_view_initialised:
            self._is_view_initialised = True
            self.fit_view()
        QtGui.QGraphicsView.showEvent(self, event)


    def _get_selection_bbox(self, selection):
        """For a given selection of node return the bounding box

        :param selection: List of graphics item
        :type selection: List

        :returns: A Qt rectangle
        :rtype: :class:`QtCore.QRectF`

        """
        top_left = QtCore.QPointF(self._width, self._height)
        bottom_right = QtCore.QPointF(- self._width, - self._height)

        for node in [s for s in selection if isinstance(s, Node)]:
            bbox = node.boundingRect()
            top_left.setX(min(node.x() + bbox.left(), top_left.x()))
            top_left.setY(min(node.y() + bbox.top(), top_left.y()))
            bottom_right.setX(max(node.x() + bbox.right(),
                              bottom_right.x()))
            bottom_right.setY(max(node.y() + bbox.bottom(),
                              bottom_right.y()))
        return QtCore.QRectF(top_left, bottom_right)
