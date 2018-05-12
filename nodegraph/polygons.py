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
Polygons used in Node graph

"""

from . import QtCore, QtGui


height = 4
width = height * 3 / 4
thick = height / 2

ARROW_SLIM = QtGui.QPolygonF([QtCore.QPointF(thick / 2, 0),
                              QtCore.QPointF(- thick, - width),
                              QtCore.QPointF(- thick * 2, - width),
                              QtCore.QPointF(- thick / 2, 0),
                              QtCore.QPointF(- thick * 2, width),
                              QtCore.QPointF(- thick, width)])

ARROW_STANDARD = QtGui.QPolygonF([QtCore.QPointF(height, 0),
                                  QtCore.QPointF(- height, - width),
                                  QtCore.QPointF(- height, width),
                                  QtCore.QPointF(height, 0)])
