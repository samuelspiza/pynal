#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Displays page objects with pdf as backgrounds within the scene.

Explores ways to work with single and multiple pages, adding and removing
them, zooming on pages, iterating over them, changing their order.
'''
import sys
import os

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL

import QtPoppler

class MainWindow(QtGui.QMainWindow):
    """ The MainWindow containing the QTabWidget and MenuBar. """
    def __init__(self):
        """ Initialize the content of the window. """
        QtGui.QMainWindow.__init__(self)

        tabBar = self.addToolBar("&Tabs")
        tabBar.addAction(self.createAction("New Document", self.newDocument))
        tabBar.addAction(self.createAction("Open PDF", self.loadPDF))
        tabBar.addAction(self.createAction("Rotate", self.rotate))

        docBar = self.addToolBar("&Document")
        docBar.addAction(self.createAction("Add Page", self.newPage))
        docBar.addAction(self.createAction("Remove Page", self.removePage))

        zoombar = self.addToolBar("&Scaling")
        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setMaximum(200)
        slider.setMinimum(10)
        slider.setValue(100)
        self.connect(slider, QtCore.SIGNAL("valueChanged(int)"), self.changeScale)
        zoombar.addWidget(slider)

        self.tabs = QtGui.QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.connect(self.tabs, SIGNAL("tabCloseRequested(int)"), self.close)

        self.setCentralWidget(self.tabs)


        self.resize(800, 700)

    def changeScale(self, scale):
        """
        Change the scaling of the current document.

        Called by the slider in the toolbar.
        """
        if self.tabs.currentWidget() is not None:
            self.tabs.currentWidget().changeScale(scale)

    def createAction(self, text, slot):
        """ Convenience method to create actions for the menu. """
        action = QtGui.QAction(text, self)
        self.connect(action, SIGNAL("triggered()"), slot)
        return action

    def newDocument(self):
        """ Create a new and empty document. """
        self.tabs.addTab(PynalDocument(), "new Doc")

    def newPage(self):
        """ Append an empty page to the current document. """
        doc = self.tabs.currentWidget()
        if doc is None:
            return

        doc.newPage()

    def removePage(self):
        """ Remove the page currently in focus. """
        doc = self.tabs.currentWidget()
        if doc is None:
            return

        doc.removePage()

    def loadPDF(self):
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
            self.tabs.addTab(PynalDocument(file), filename)

    def rotate(self):
        """ Rotate the position of the tabs. """
        pos = (self.tabs.tabPosition() + 1) % 4
        self.tabs.setTabPosition(pos)

    def close(self, index):
        """
        Closes a tab.

        No idea if there is more work needed to dispose the widgets and
        QtPoppler.Document that lived in this tab.
        """
        self.tabs.removeTab(index)

class PynalDocument(QtGui.QGraphicsView):
    """ Document widget displayed in the QTabWidget. """

    def __init__(self, source_file=None, parent=None):
        """
        Create a new PynalDocument for the given file.

        parameters:
        source_file -- String path to the pdf that is to be displayed.
        parent -- the parent widget of this widget.
        """
        QtGui.QGraphicsView.__init__(self, parent)
        self.pages = [] # List to manage the page objects

        self.scene = QtGui.QGraphicsScene()
        self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray))
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setDragMode(self.ScrollHandDrag)

        if source_file is not None:
            self.source = source_file
            self.document = QtPoppler.Poppler.Document.load(self.source)
            self.document.setRenderHint(QtPoppler.Poppler.Document.Antialiasing and
                                    QtPoppler.Poppler.Document.TextAntialiasing)

            self.thread = PdfLoaderThread(self.document, self.scene)
            self.connect(self.thread, SIGNAL("output(QImage, int)"), self.addPage)

            self.thread.start()

        self.scaleValue = 1.0

    def changeScale(self, scale):
        """
        Change the scaling of the scene.

        Parameters:
        scale -- the scaling in %.
        """
        self.scaleValue = scale / 100.0
        self.resetMatrix()
        self.scale(self.scaleValue, self.scaleValue)

    def newPage(self):
        """ Create an empty page and append it after the last. """
        if len(self.pages) > 0: #calculate position on prev page if one exists
            dimensions = QtCore.QSizeF(self.pages[-1].boundingRect().size())
            topleft = QtCore.QPointF(-dimensions.width() / 2,
                                     self.pages[-1].boundingRect().bottom() + 100)
        else:
            dimensions = QtCore.QSizeF(800, 1200)
            topleft = QtCore.QPointF(-dimensions.width() / 2, 0)
        pos = QtCore.QRectF(topleft, dimensions)
        self.pages.append(PyPage(len(self.pages), self, pos))

    def addPage(self, image, i):
        """
        Callback method for the worker thread.

        Adds the created image as a pixmap to the scene.
        """
        pixmap = QtGui.QPixmap.fromImage(image)

        if len(self.pages) > 0: #calculate position on prev page if one exists
            topleft = QtCore.QPointF(-pixmap.width() / 2,
                                     self.pages[-1].boundingRect().bottom() + 100)
        else:
            topleft = QtCore.QPointF(-pixmap.width() / 2, 0)

        dimensions = QtCore.QSizeF(pixmap.width(), pixmap.height())
        pos = QtCore.QRectF(topleft, dimensions)
        page = PyPage(len(self.pages)+1, self, pos, background=pixmap)
        self.pages.append(page)


class PyPage(QtGui.QGraphicsItem):
    """
    A page within a PynalDocument.
    Contains a background and can be drawn on.
    """

    def __init__(self, pagenumber, document, pos, background=None):
        """
        Create a new page.

        Parameters:
        pagenumber - index of this page (first being 0)
        scene - the scene this page will be added to
        pos - QRectF specifying the position and dimension of this page
        background - the pixmap to use as a background (or None for white)
        """
        QtGui.QGraphicsItem.__init__(self, None, document.scene)
        self.bounding = pos
        self.document = document

        if background is not None:
            self.background = QtGui.QGraphicsPixmapItem(background, self)
            self.background.setPos(self.bounding.topLeft())

        else:
            self.background = QtGui.QGraphicsRectItem(self.bounding, self)
            self.background.setBrush(QtGui.QBrush(QtCore.Qt.white))

        self.background.setZValue(-1)

        self.pagenumber = pagenumber

        self.pagecontrol = PageControl(self)

    def boundingRect(self):
        """ Return the bounding box of the page. """
        return self.bounding

    def paint(self, painter, option, widget=None):
        """
        Explicitly painting all children is unneeded double work.

        read: retarded
        """
        pass

class PageControl(QtGui.QGraphicsItem):
    """
    A control bar below a page used to move, delete or create new
    pages after this.
    """
    def __init__(self, page):
        QtGui.QGraphicsItem.__init__(self, page)
        self.page = page
        top = self.page.boundingRect().bottom() + 20
        left = -100
        self.bounding = QtCore.QRectF(QtCore.QPointF(left, top),
                                      QtCore.QSizeF(200, 40))
        self.back = QtGui.QGraphicsRectItem(QtCore.QRectF(QtCore.QPointF(left, top),
                                      QtCore.QSizeF(200, 40)),
                                      self.page)

        self.newPageButton = DocButton("new", 20, self, self.addPage)
        self.moveUpButton = DocButton("up", 80, self, self.moveUp)
        self.moveDownButton = DocButton("down", 140, self, self.moveDown)

    def addPage(self):
        self.page.document.newPage()

    def moveUp(self):
        pass

    def moveDown(self):
        pass

    def boundingRect(self):
        """ Return the bounding box of the page. """
        return self.bounding

    def paint(self, painter, option, widget=None):
        """ Paint nothing in particular that isn't already getting painted. """
        pass

class DocButton(QtGui.QGraphicsItem):
    def __init__(self, label, offset, parent, action):
        QtGui.QGraphicsItem.__init__(self, parent)
        self.action = action
        top = parent.boundingRect().top()+5
        left = parent.boundingRect().left()
        self.setAcceptHoverEvents(True)
        self.background = QtGui.QGraphicsEllipseItem(
                            QtCore.QRectF(left + offset, top, 30, 30),
                            parent)
        self.background.setBrush(QtGui.QBrush(QtCore.Qt.red))

    def boundingRect(self):
        """ Return the bounding box of the page. """
        return self.background.boundingRect()

    def paint(self, painter, option, widget=None):
        """ Paint nothing in particular that isn't already getting painted. """
        pass

    def mousePressEvent(self, event):
        self.action()

    def hoverEnterEvent(self, event):
        """ The cursor entered the bounding rect of the control area. """
        self.background.setBrush(QtGui.QBrush(QtCore.Qt.yellow))

    def hoverLeaveEvent(self, event):
        """ The cursor left the bounding rect of the control area. """
        self.background.setBrush(QtGui.QBrush(QtCore.Qt.red))

class PdfLoaderThread(QtCore.QThread):
    """
    Creates QImages (or QPixmaps) from all pages in a given Poppler document.
    """
    def __init__(self, doc, scene):
        """
        Creates a new PdfLoaderThread.

        parameters:
            doc - the QtPoppler.Poppler.Document that is to be loaded.
            scene - the QGraphicsScene that will receive the QImages.
        """
        QtCore.QThread.__init__(self)

        self.doc = doc
        self.scene = scene

    def run(self):
        """ Creates the images and notifies the QGraphicsScene. """
        for i in range(0, self.doc.numPages()):
            image = self.doc.page(i).renderToImage(150, 150)
            self.emit(SIGNAL("output(QImage, int)"), image, i)
            if i > 10:
                break

app = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
