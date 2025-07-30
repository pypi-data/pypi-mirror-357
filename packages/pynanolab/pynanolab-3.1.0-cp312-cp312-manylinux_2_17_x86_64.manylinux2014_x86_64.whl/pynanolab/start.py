#!/usr/bin/env
# -*- coding: UTF-8 -*-
# Copyright (C) @2022 Shaochuang Liu. All right Reserved.
# @Author:wnight
# @FileName:start.py
# @DateTime:2022/5/20 13:19
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

from pynanolab.pynanolabgui import PyNanoLab, SplashPanel
from pynanolab.widget.nanoporetoolbox.nanoporewidget import NanoporeToolBox

def getlogfilepath():
    sysstr = platform.system()
    filename = "PyNanoLab" + datetime.datetime.now().strftime('%H%M%S') + ".log"
    if (sysstr == "Windows"):
        logfile = os.path.join(os.environ['APPDATA'], "PyNanoLab", "log", filename).replace("\\", "/")
    elif (sysstr == "Linux"):
        logfile = os.path.join(os.environ['HOME'], '.PyNanoLab', "log", filename)
    elif (sysstr == "Darwin"):
        logfile = os.path.join(os.environ['HOME'], '.PyNanoLab', "log", filename)
    else:
        return filename
    if not os.path.exists(os.path.dirname(logfile)):
        os.makedirs(os.path.dirname(logfile))
    else:
        loglist = glob(os.path.dirname(logfile) + "/*.log")
        loglist.sort(key=lambda x: os.path.getmtime(x))
        if len(loglist) > 10:
            for log in loglist[:len(loglist) - 10]:
                os.remove(log)
    # 初始化自动保存文件夹， 保留最后10项
    backupDir = os.path.join(os.path.abspath(os.path.dirname(logfile) + os.path.sep + ".."), "backup")
    if os.path.exists(backupDir):
        backuplist = glob(backupDir + "/*.pnl")
        if len(backuplist) > 10:
            for backfile in backuplist[:len(backuplist) - 10]:
                os.remove(backfile)
    else:
        os.makedirs(backupDir)
    return logfile

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] [%(module)s %(funcName)s][line:%(lineno)d]----%(message)s",
                    handlers=[logging.FileHandler(getlogfilepath()), logging.StreamHandler()])
logger = logging.getLogger(__name__)


class MyProxyStyle(QProxyStyle):
    pass

    def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):

        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return 40
        else:
            return QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option, widget)


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

    # Windows only: hide console window
    hide_console()

    QFontDatabase.addApplicationFont(":/fonts/webdings.ttf")
    QFontDatabase.addApplicationFont(":/fonts/times.ttf")
    QFontDatabase.addApplicationFont(":/fonts/wqy-microhei.ttc")
    QFontDatabase.addApplicationFont(":/fonts/SourceHanSansCN-Regular.otf")
    QFontDatabase.addApplicationFont(":/fonts/SourceHanSansCN-Bold.otf")
    #QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)

    #QQuickWindow.setGraphicsApi(QSGRendererInterface.OpenGL)
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    process = psutil.Process(app.applicationPid())
    app.setStyle("Fusion")

    movie = QMovie(":/blue/1.gif")
    splash = SplashPanel(movie)
    app.processEvents()

    splash.show()
    splash.showMessage(f"In progress Open PyNanolab ......",
                       Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
    mainWindow = PyNanoLab()
    mainWindow.pid = process
    if len(sys.argv) > 1:
        file = sys.argv[1]
        splash.showMessage(f"In progress Open Project {file}",
                           Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
        if os.path.isfile(file) and os.path.exists(file):
            if file.endswith(".pnl"):
                # splash.showMessage(f"In progress Open Project {file}")
                mainWindow.loadproject(file)
    mainWindow.showNormal()
    mainWindow.updatemem()
    mainWindow.raise_()

    splash.finish(mainWindow)
    splash.deleteLater()
    sys.exit(app.exec_())

# def runnptb():
#     hide_console()
#
#     QFontDatabase.addApplicationFont(":/fonts/webdings.ttf")
#     QFontDatabase.addApplicationFont(":/fonts/times.ttf")
#     QFontDatabase.addApplicationFont(":/fonts/wqy-microhei.ttc")
#     QFontDatabase.addApplicationFont(":/fonts/SourceHanSansCN-Regular.otf")
#     QFontDatabase.addApplicationFont(":/fonts/SourceHanSansCN-Bold.otf")
#
#     #QQuickWindow.setGraphicsApi(QSGRendererInterface.OpenGL)
#     app = QApplication.instance()
#     if app is None:
#         app = QApplication(sys.argv)
#     app.setStyle("Fusion")
#     movie = QMovie(":/blue/1.gif")
#     splash = SplashPanel(movie)
#     app.processEvents()
#
#     splash.show()
#     splash.showMessage(f"In progress Open Nanopore ToolBox ......",
#                        Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
#
#     info = {'rootitem': 'Folder1', 'childitem': 'Table', 'itemname': -1}
#     mainWindow = NanoporeToolBox(info = info)
#     mainWindow.showNormal()
#     mainWindow.raise_()
#     splash.finish(mainWindow)
#     splash.deleteLater()
#

if __name__ == '__main__':
    run()
