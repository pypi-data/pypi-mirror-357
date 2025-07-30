#!/usr/bin/env
# -*- coding: UTF-8 -*-
# @Author:wnight
# @FileName:start.py
# @DateTime:2025/6/20 20:45
# @SoftWare: PyCharm
# You are not expected to understand this


import os
# os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-gpu"
# os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
import sys
from glob import glob
import logging
import datetime
import platform
import psutil
from PySide6.QtGui import QMovie, QFontDatabase
#from PySide6.QtQuick import QQuickWindow, QSGRendererInterface
from PySide6.QtCore import Qt, QCoreApplication
import matplotlib
matplotlib.use('QtAgg')
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)  # 必须放在QApplication 之前
# from PySide6.QtNfc import
from PySide6.QtWidgets import QApplication, QProxyStyle, QStyle
from pynanolab.ui.stylesheet.mplresource.mplcmap import initcmap
initcmap()

from pynanolab.pynanolabgui import SplashPanel
from pynanolab.widget.nanoporetoolbox.nanoporewidget import NanoporeToolBox

def hide_console():
    if sys.platform.startswith("win") and os.getenv("PYTHON_CONSOLE_HIDE") != "0":
        try:
            import ctypes
            whnd = ctypes.windll.kernel32.GetConsoleWindow()
            if whnd:
                ctypes.windll.user32.ShowWindow(whnd, 0)  # 0 = SW_HIDE
        except Exception:
            pass

def run():
    hide_console()

    QFontDatabase.addApplicationFont(":/fonts/webdings.ttf")
    QFontDatabase.addApplicationFont(":/fonts/times.ttf")
    QFontDatabase.addApplicationFont(":/fonts/wqy-microhei.ttc")
    QFontDatabase.addApplicationFont(":/fonts/SourceHanSansCN-Regular.otf")
    QFontDatabase.addApplicationFont(":/fonts/SourceHanSansCN-Bold.otf")

    #QQuickWindow.setGraphicsApi(QSGRendererInterface.OpenGL)
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setStyle("Fusion")
    movie = QMovie(":/blue/1.gif")
    splash = SplashPanel(movie)
    app.processEvents()

    splash.show()
    splash.showMessage(f"In progress Open Nanopore ToolBox ......",
                       Qt.AlignHCenter | Qt.AlignBottom, Qt.white)

    info = {'rootitem': 'Folder1', 'childitem': 'Table', 'itemname': -1}
    mainWindow = NanoporeToolBox(info = info)
    mainWindow.showNormal()
    mainWindow.raise_()
    splash.finish(mainWindow)
    splash.deleteLater()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()