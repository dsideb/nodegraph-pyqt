# Resolve python Qt flavor
try:
    from PySide import QtGui, QtCore, QtOpenGL
except:
    from PyQt4 import QtGui, QtCore, QtOpenGL
