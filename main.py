# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import sys

try:
    from PyQt4.QtGui import QApplication
except ImportError:
    from PySide.QtGui import QApplication

from mainwindow import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = MainWindow()
    mw.read_settings()
    mw.show()

    sys.exit(app.exec_())
