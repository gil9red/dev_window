# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import sys
from PySide.QtGui import QApplication
from mainwindow import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = MainWindow()
    mw.resize(1300, 800)
    mw.read_settings()
    mw.show()

    sys.exit(app.exec_())
