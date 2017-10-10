#==============================================================================
#
#  Insert gnu license here
#
#==============================================================================

"""
Polygons used in Node graph

"""

from . import QtCore, QtGui


height = 4
width = height*3/4
thick = height/2

ARROW_SLIM = QtGui.QPolygonF([QtCore.QPointF(thick/2, 0),
                              QtCore.QPointF(- thick, - width),
                              QtCore.QPointF(- thick*2, - width),
                              QtCore.QPointF(- thick/2, 0),
                              QtCore.QPointF(- thick*2, width),
                              QtCore.QPointF(- thick, width)])

ARROW_STANDARD = QtGui.QPolygonF([QtCore.QPointF(height, 0),
                                  QtCore.QPointF(- height, - width),
                                  QtCore.QPointF(- height, width),
                                  QtCore.QPointF(height, 0)])
