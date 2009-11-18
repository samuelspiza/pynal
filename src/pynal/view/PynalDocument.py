# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtOpenGL
from PyQt4.QtCore import SIGNAL

import QtPoppler

import pynal.control.tools as tools
import pynal.models.Config as Config
from pynal.view.DocumentPage import DocumentPage
import pynal.view.Backgrounds as Backgrounds

class PynalDocument(QtGui.QGraphicsView):
    """
    Document widget displayed in the QTabWidget.

    Attributes:
    dpi      -- The current dpi used to render the background of pages.
    pages    -- The list of DocumentPage objects of this document.
    document -- The Poppler Document used as the background
                source.
    """

    def __init__(self, source_file=None, parent=None):
        """
        Create a new PynalDocument for the given file.

        Parameters:
        source_file -- String path to the pdf that is to be displayed.
        parent      -- the parent widget of this widget.
        """
        QtGui.QGraphicsView.__init__(self, parent)
        self.setCursor(tools.current_tool.cursor)

        #Needed for proper rendering of selection box
        self.setViewportUpdateMode(self.FullViewportUpdate)

        self.configure_scene()

        self.dpi = Config.pdf_base_dpi

        self.pages = []

        if Config.get_bool("Rendering", "use_opengl"):
            self.setViewport(QtOpenGL.QGLWidget())

        if source_file is not None:
            self.document = QtPoppler.Poppler.Document.load(source_file)
            self.document.setRenderHint(QtPoppler.Poppler.Document.Antialiasing and
                                        QtPoppler.Poppler.Document.TextAntialiasing)

            # This might want to be moved into an own thread
            # (when numPages is over a certain threshold?)
            for page_number in range(0, self.document.numPages()):
                    self.append_new_page(page_number,
                        Backgrounds.pdf_page(self.document.page(page_number)))

                # Note that the pdf pages are not rendered
                # now. That happens when the page is to be
                # displayed / cached for displaying.

        else:
            self.append_new_page() # Add an empty page.

    def dpi_scaling(self):
        """
        Return the scaling factor of the current and base dpi.

        TODO: mapper function to centralize calculations with this value.
        """
        return self.dpi / Config.pdf_base_dpi

    def zoom(self, value):
        """
        Set the dpi to the given value and resize the components accordingly.
        """
        if self.dpi == value:
            return
        self.dpi = value
        print "dpi now:", self.dpi
        for page in self.pages:
            page.update_bounding_rect()

        rect = QtCore.QRectF(self.pages[0].boundingRect().topLeft(),
                             self.pages[-1].boundingRect().bottomRight())

        self.scene().setSceneRect(rect)

    def configure_scene(self):
        """ Create and configure the scene. """
        self.setScene(QtGui.QGraphicsScene(self))
        self.scene().setBackgroundBrush(QtGui.QBrush(QtCore.Qt.gray))
        self.setRenderHint(QtGui.QPainter.Antialiasing)

    def current_page(self):
        """
        The page that has the current focus. This can be the centered or
        last clicked page.
        """
        return self.items(self.contentsRect().center())[-1]

    def append_new_page(self, prevpage=None, bg_source=None):
        """
        Create an empty page and append it to the end of the document.
        """
        if bg_source is None:
            bg_source = Backgrounds.checked_background()

        self.pages.append(DocumentPage(self, len(self.pages), bg_source))

    def mouseDoubleClickEvent(self, event):
        """
        Delegate the mouse events to the current tool.
        Event is also delegated to super to handle the event in case
        the tool calls event.ignore().
        """
        tools.current_tool.mouseDoubleClickEvent(event, self.scene())
        QtGui.QGraphicsView.mouseDoubleClickEvent(self, event)

    def mouseMoveEvent(self, event):
        """ Delegate the mouse events to the current tool. """
        tools.current_tool.mouseMoveEvent(event, self.scene())
        QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        """ Delegate the mouse events to the current tool. """
        tools.current_tool.mousePressEvent(event, self.scene())
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Delegate the mouse events to the current tool. """
        tools.current_tool.mouseReleaseEvent(event, self.scene())
        QtGui.QGraphicsView.mouseReleaseEvent(self, event)
