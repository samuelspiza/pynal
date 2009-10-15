# -*- coding: utf-8 -*-
import os

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import SIGNAL

from pynal.view.PynalDocument import *
import pynal.models.Config as Config
import pynal.control.actions as actions

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
        actions.init(self)
        self.setWindowTitle("Pynal")

        self.createTabWidget()
        self.createMenuBar()
        self.createToolbar()

        self.resize(Config.window_width, Config.window_height)

    def createToolbar(self):
        bar = self.addToolBar("title")
        bar.addAction(actions.new_file_action)
        bar.addAction(actions.open_file_action)
        bar.addAction(actions.save_file_action)
        bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

    def createMenuBar(self):
        pass

    def createTabWidget(self):
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setDocumentMode(True)
        self.connect(self.tabWidget, SIGNAL("tabCloseRequested(int)"), self.close)
        self.setCentralWidget(self.tabWidget)

    def createAction(self, text, slot, icon=None):
        """ Convenience method to create actions for the menu. """
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(iconloader.find_icon(icon, 32)))

        self.connect(action, SIGNAL("triggered()"), slot)
        return action

    def open_file(self):
        """
        Open a dialog to let the user choose pdf files and open
        them in tabs.
        """
        files = QtGui.QFileDialog.getOpenFileNames(self, "Open PDF file",
                                                    "", "PDF (*.pdf)")
        if not files:
            return

        for file in files:
            filename = os.path.basename(str(file))
            self.tabWidget.addTab(PynalDocument(file), filename)

    def rotate(self):
        """ Rotate the position of the tabs. """
        pos = (self.tabs.tabPosition() + 1) % 4
        self.tabs.setTabPosition(pos)

    def save_file(self):
        pass

    def new_file(self):
        pass

    def close(self, index):
        """
        Closes a tab.

        No idea if there is more work needed to dispose the widgets and
        QtPoppler.Document that lived in this tab.
        """
        self.tabs.removeTab(index)
