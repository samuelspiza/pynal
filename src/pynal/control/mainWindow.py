# -*- coding: utf-8 -*-
"""
Module containing the MainWindowControl class.
"""
import os

from PyQt4 import QtGui
from PyQt4 import QtCore

from pynal.control import actions
from pynal.view.PynalDocument import *

class MainWindowControl(QtCore.QObject):
    """
    Provides slots for actions coming from or working with a MainWindow object.

    Extends the QObject for convenient access to tr() and connect().
    """

    def __init__(self, window):
        """ Creates a new MainWindowControl. """
        QtCore.QObject.__init__(self)
        self.window = window
        actions.init(self, window)

    def start(self):
        """
        Called when the window has been set up and is ready to receive
        commands. E.g. opening documents.

        This can be extended to auto-reopen documents that were open
        when pynal was closed the last time.
        """
        for file in Config.open_files:
            filename = os.path.basename(str(file))
            self.window.tabWidget.addTab(PynalDocument(file), filename)
        Config.open_files[:] = [] # Clear the list

    def open_file(self):
        """
        Open a dialog to let the user choose pdf files and open
        them in tabs.
        """
        files = QtGui.QFileDialog.getOpenFileNames(
                   self.window, self.tr("Open PDF file"), "", "PDF (*.pdf)")
        if not files:
            return

        for file in files:
            filename = os.path.basename(str(file))
            self.window.tabWidget.addTab(PynalDocument(file), filename)

    def close_document(self, index):
        """
        Closes a tab.

        No idea if there is more work needed to dispose the widgets and
        QtPoppler.Document that lived in this tab.
        """
        tabwidget = self.window.tabWidget

        tabwidget.removeTab(index)

        # When only one tab is displayed hide the tabBar.
        if tabwidget.count() < 2:
            tabwidget.tabBar().hide()

    def save_file(self):
        """ Save the current document. """
        pass

    def new_file(self):
        """ Create a new document. """
        self.window.tabWidget.addTab(PynalDocument(), "New Document")

    def exit(self):
        """ Exit the application. """
        pass

    def zoom_width(self):
        """ Zoom the current document to the width of the focused page. """
        pass

    def zoom_original(self):
        """ Zoom the current document to 100%. """
        pass

    def zoom_fit(self):
        """ Zoom the current document to fit the focused page. """
        pass

    def zoom_in(self):
        """ Zoom in :D. """
        pass

    def zoom_out(self):
        """ Zoom out :D. Step depends on current scale or config..."""
        pass
