#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import io

from PySide.QtGui import *
from PySide.QtCore import *

from mainwindow_ui import Ui_MainWindow
from common import *


logger = get_logger('main_window')


class MainWindow(QMainWindow, QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('dev_window')

        # Все действия к прикрепляемым окнам поместим в меню
        for dock in self.findChildren(QDockWidget):
            self.ui.menuDockWindow.addAction(dock.toggleViewAction())

        # Все действия к toolbar'ам окнам поместим в меню
        for tool in self.findChildren(QToolBar):
            self.ui.menuTools.addAction(tool.toggleViewAction())

        # Выполнение кода в окне "Выполнение скрипта"
        self.ui.button_exec.clicked.connect(self.exec_script)

    def exec_script(self):
        has_selected = self.ui.code.textCursor().hasSelection()
        if has_selected:
            # http://doc.qt.io/qt-4.8/qtextcursor.html#selectedText
            # Note: If the selection obtained from an editor spans a line break, the text will contain a
            # Unicode U+2029 paragraph separator character instead of a newline \n character. Use QString::replace()
            # to replace these characters with newlines.
            code = self.ui.code.textCursor().selectedText()
            code = code.replace('\u2029', '\n')
        else:
            code = self.ui.code.toPlainText()

        exec(code.strip())

    def slog(self, *args, **kwargs):
        """Функция для добавления текста в виджет-лог, находящегося на форме."""

        try:
            # Используем стандартный print для печати в строку
            str_io = io.StringIO()
            kwargs['file'] = str_io
            kwargs['end'] = ''

            print(*args, **kwargs)

            text = str_io.getvalue()
            self.ui.simple_log.appendPlainText(text)

        except Exception as e:
            self.ui.simple_log.appendPlainText(str(e))

    def read_settings(self):
        # TODO: при сложных настройках, лучше перейти на json или yaml
        config = QSettings(CONFIG_FILE, QSettings.IniFormat)
        self.restoreState(config.value('MainWindow_State'))
        self.restoreGeometry(config.value('MainWindow_Geometry'))

    def write_settings(self):
        config = QSettings(CONFIG_FILE, QSettings.IniFormat)
        config.setValue('MainWindow_State', self.saveState())
        config.setValue('MainWindow_Geometry', self.saveGeometry())

    def closeEvent(self, *args, **kwargs):
        self.write_settings()
        super().closeEvent(*args, **kwargs)
