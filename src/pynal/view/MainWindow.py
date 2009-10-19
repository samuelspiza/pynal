# -*- coding: utf-8 -*-
import os

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import SIGNAL

from pynal.control import actions
from pynal.models import Config
from pynal.control.mainWindow import MainWindowControl

class MainWindow(QtGui.QMainWindow):
    '''
    Uh, the main window. Contains more or less useful toolbars, menus and
    a heroic status bar.

    Oh and some place to display the actual journaling area...
    '''

    def __init__(self):
        """
        Creates a new MainWindow.
        """
        QtGui.QMainWindow.__init__(self)
        self.control = MainWindowControl(self)

        self.setWindowTitle("Pynal")

        self.createTabWidget()
        self.createMenuBar()
        self.createToolbar()

        self.resize(Config.window_width, Config.window_height)

        self.control.start()

    def createToolbar(self):
        bar = self.addToolBar("File operations")
        bar.addAction(actions.toolbar("new_file_action"))
        bar.addAction(actions.toolbar("open_file_action"))
        bar.addAction(actions.toolbar("save_file_action"))
        bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        zoombar = self.addToolBar("Scaling")
        zoombar.addAction(actions.toolbar("doc_zoom_in"))
        zoombar.addAction(actions.toolbar("doc_zoom_100"))
        zoombar.addAction(actions.toolbar("doc_zoom_out"))
        zoombar.addAction(actions.toolbar("doc_zoom_fit"))
        zoombar.addAction(actions.toolbar("doc_zoom_width"))

    def createMenuBar(self):
        menu = self.menuBar()
        file = menu.addMenu("&File")
        file.addAction(actions.menu("exit_app_action"))

    def createTabWidget(self):
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setDocumentMode(True)
        self.connect(self.tabWidget, SIGNAL("tabCloseRequested(int)"), self.close)
        self.setCentralWidget(self.tabWidget)

    def rotate(self):
        """ Rotate the position of the tabs. """
        pos = (self.tabs.tabPosition() + 1) % 4
        self.tabWidget.setTabPosition(pos)

    def close(self, index):
        """
        Closes a tab.

        No idea if there is more work needed to dispose the widgets and
        QtPoppler.Document that lived in this tab.
        """
        self.tabWidget.removeTab(index)
