# -*- coding: utf-8 -*-
'''
'''
from PyQt4 import QtGui
from PyQt4 import QtCore

import pynal.control.actions as actions
import pynal.view.Backgrounds as Backgrounds

class PageControl(QtGui.QGraphicsItem):
    '''
    A control panel/toolbar below every page for quick access to
    page manipulation and management actions.
    '''

    def __init__(self, parent):
        '''
        Creates a new PageControl for the given page.

        Parameters:
          parent -- The DocumentPage that is controlled by this panel.
        '''
        QtGui.QGraphicsItem.__init__(self, parent)
        self.setZValue(0)
        self._bounding = None
        self.toolbar = None

        toolbar_widget = QtGui.QToolBar("page controls")

        # TODO: make these user configurable (or is that too KDE?) -> #17
        toolbar_widget.addAction(actions.toolbar("page_new_after", callable=self.parentItem().append))
        toolbar_widget.addAction(actions.toolbar("page_up", callable=self.parentItem().move_up))
        toolbar_widget.addAction(actions.toolbar("page_down", callable=self.parentItem().move_down))
        toolbar_widget.addAction(actions.toolbar("page_remove", callable=self.parentItem().remove))
        toolbar_widget.addAction(actions.toolbar("page_duplicate", callable=self.parentItem().duplicate))
        toolbar_widget.addSeparator()
        toolbar_widget.addAction(actions.toolbar("page_bg_plain", callable=self.plain_bg))
        toolbar_widget.addAction(actions.toolbar("page_bg_checked", callable=self.checked_bg))
        self.toolbar_widget = toolbar_widget

#        self._size = QtCore.QSizeF(toolbar_widget.size() / 4)
        self._size = QtCore.QSizeF(100, 30)

    def sizeF(self):
        """ Return the size of this control panel. """
        return self._size

    def reposition_toolbar(self):
        """ Move the toolbar QGraphicsProxyItem below the page. """
        return self.toolbar.setPos(  self.toolbar.size().width() / -2
                                   + self.parentItem().boundingRect().width() / 2,
                                    self.parentItem().boundingRect().height())

    def plain_bg(self):
        """ Set the background to plain. """
        parent = self.parentItem()
        parent.bg_source = Backgrounds.empty_background(size=parent.bg_source.sizeF())
        parent.background_is_dirty = True

    def checked_bg(self):
        """ Set the background to checked. """
        parent = self.parentItem()
        parent.bg_source = Backgrounds.checked_background(size=parent.bg_source.sizeF())
        parent.background_is_dirty = True

    def update_bounding_rect(self):
        """
        Move the panel to the bottom of the page.
        Called after the page has been resized due to a zoom event
        and the physical size in the scene has changed so the panel
        has to be relocated.
        """

        #TODO: these values and the whole bounding_rect should be related to the toolbar
        self._bounding = QtCore.QRectF(QtCore.QPointF(0, 0),
                                        self.sizeF())

        if self.toolbar is not None:
            self.reposition_toolbar()

    def boundingRect(self):
        """
        Return the bounding box of the control panel.
        """
        return self._bounding

    def paint(self, painter, option, widget=None):
        """
        Nothing to paint as all paintables are children of this item.

        This method is used as the notification to start rendering this
        page's background and pre-caching following/previous pages.
        """
        if self.toolbar is None:
            toolbar_item = QtGui.QGraphicsProxyWidget(self)
            toolbar_item.setWidget(self.toolbar_widget)
            self.toolbar = toolbar_item
            self.reposition_toolbar()
