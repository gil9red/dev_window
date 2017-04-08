#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import io

try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except ImportError:
    from PySide.QtGui import *
    from PySide.QtCore import *

from mainwindow_ui import Ui_MainWindow
from common import *


logger = get_logger('main_window')


OUTPUT_LOGGER_STDOUT = OutputLogger(sys.stdout, OutputLogger.Severity.DEBUG)
OUTPUT_LOGGER_STDERR = OutputLogger(sys.stderr, OutputLogger.Severity.ERROR)

sys.stdout = OUTPUT_LOGGER_STDOUT
sys.stderr = OUTPUT_LOGGER_STDERR


CODE_EDITOR_BACKUP = 'code_editor.backup'

# TODO: перевести на английский


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

        try:
            self.code_editor = create_code_editor()
            self.ui.container_code_editor.setWidget(self.code_editor)
        except Exception as e:
            logger.exception("Error:")

            self.code_editor = QPlainTextEdit()
            self.ui.container_code_editor.setWidget(self.code_editor)

        self.write_code_to_editor()
        self.timer_save_code = QTimer()
        self.timer_save_code.setSingleShot(True)
        self.timer_save_code.setInterval(300)
        self.timer_save_code.timeout.connect(self.save_code_from_editor)

        self.code_editor.textChanged.connect(self.timer_save_code.start)

        OUTPUT_LOGGER_STDOUT.emit_write.connect(self.write_output)
        OUTPUT_LOGGER_STDERR.emit_write.connect(self.write_output)

    def save_code_from_editor(self):
        logger.debug('Save code from editor to file: %s. Start.', CODE_EDITOR_BACKUP)

        with open(CODE_EDITOR_BACKUP, mode='w', encoding='utf-8') as f:
            f.write(self.code_editor.toPlainText())

        logger.debug('Finish save code from editor.')

    def write_code_to_editor(self):
        logger.debug('Write code to editor in file: %s. Start.', CODE_EDITOR_BACKUP)

        try:
            with open(CODE_EDITOR_BACKUP, encoding='utf-8') as f:
                content = f.read()

                try:
                    self.code_editor.setPlainText(content, None, None)
                except:
                    self.code_editor.setPlainText(content)

        except Exception as e:
            logger.exception("Error:")

        logger.debug('Finish write code to editor.')

    def exec_script(self):
        try:
            has_selected = self.code_editor.textCursor().hasSelection()
            if has_selected:
                # http://doc.qt.io/qt-4.8/qtextcursor.html#selectedText
                # Note: If the selection obtained from an editor spans a line break, the text will contain a
                # Unicode U+2029 paragraph separator character instead of a newline \n character. Use QString::replace()
                # to replace these characters with newlines.
                code = self.code_editor.textCursor().selectedText()
                code = code.replace('\u2028', '\n').replace('\u2029', '\n')
            else:
                code = self.code_editor.toPlainText()

            exec(code.strip())

        except Exception as e:
            logger.exception("Error:")
            
            # Сохраняем в переменную
            import traceback
            tb = traceback.format_exc()

            last_error_message = str(e)
            last_detail_error_message = str(tb)

            message = last_error_message + '\n\n' + last_detail_error_message

            mb = QErrorMessage()
            mb.setWindowTitle('Error')
            # Сообщение ошибки содержит отступы, символы-переходы на следующую строку,
            # которые поломаются при вставке через QErrorMessage.showMessage, и нет возможности
            # выбрать тип текста, то делаем такой хак.
            mb.findChild(QTextEdit).setPlainText(message)

            mb.exec_()

    def write_output(self, text, severity):
        """Функция для добавления сообщения с указанием серьезности (Debug, Error)."""

        # save
        text_cursor = self.ui.output.textCursor()
        orig_fmt = text_cursor.charFormat()
        fmt = QTextCharFormat()

        # modify
        if severity == OutputLogger.Severity.ERROR:
            fmt.setFontWeight(QFont.DemiBold)
            fmt.setForeground(Qt.red)

        # append
        text_cursor.movePosition(QTextCursor.End)
        text_cursor.setCharFormat(fmt)
        text_cursor.insertText(text)

        # restore
        text_cursor.setCharFormat(orig_fmt)

    def clear_slog(self):
        self.ui.simple_log.clear()

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

    def closeEvent(self, event):
        self.write_settings()
        quit()
