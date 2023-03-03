from Foundation.Entities.MovieVirtualArea.VirtualArea import VirtualArea
from HOPA.Entities.StorePage.Components.StorePageBaseComponent import StorePageBaseComponent


class StorePageScrollComponent(StorePageBaseComponent):

    def __init__(self, page):
        super(StorePageScrollComponent, self).__init__(page)

        self.virtual_area = None
        # movie with slot 'content' on which Movie2_Content will be attached and horizontal scroll will be enabled
        self._va_movie = None
        self._va_bounds = None
        self._va_total_width = 0

    def _check(self):
        if self.object.hasObject("Movie2_VirtualArea") is False:
            Trace.log("Entity", 0,
                      "StorePage [{}] not found Movie2_VirtualArea in demon inside group '{}'".format(self.page.PageID,
                                                                                                      self.object.parent.getName()))
            return False
        return True

    def _run(self):
        self.initVirtualArea()

    def _cleanUp(self):
        self.page.content.returnToParent()

        self._va_movie = None
        self._va_bounds = None
        self._va_total_width = 0

        self.virtual_area.onFinalize()
        self.virtual_area = None

    # --- scroll -------------------------------------------------------------------------------------------------------

    def adjustButton(self, button):
        """ used for VA to calculate correct total_width and place draggable buttons """

        node = button.movie.getEntityNode()
        node.setLocalPosition((self._va_total_width, 0))

        bounds = button.movie.getCompositionBounds()
        width = bounds.maximum.x - bounds.minimum.x

        self._va_total_width += width

    def initVirtualArea(self):
        self._va_movie = self.object.getObject("Movie2_VirtualArea")
        self._va_bounds = self._va_movie.getCompositionBounds()
        self.virtual_area = VirtualArea()
        self.virtual_area.onInitialize(dragging_mode='horizontal', enable_scale=False, disable_drag_if_invalid=False)

        if self.isScrollNeeded() is True:
            self._setupVirtualArea()

    def _setupVirtualArea(self):
        if self._va_movie.hasSocket("touch") is False:
            Trace.log("Entity", 0, "StorePage [{}] not found socket {!r} in {}".format(self.page.PageID, "touch",
                                                                                       self._va_movie.getName()))
            return
        if self._va_movie.hasMovieSlot("content") is False:
            Trace.log("Entity", 0, "StorePage [{}] not found slot {!r} in {}".format(self.page.PageID, "content",
                                                                                     self._va_movie.getName()))
            return

        socket = self._va_movie.getSocket("touch")
        slot = self._va_movie.getMovieSlot("content")

        bb = self._va_bounds
        vp_width = (bb.maximum.x - bb.minimum.x)
        vp_height = (bb.maximum.y - bb.minimum.y)
        self.virtual_area.setup_viewport(0, 0, vp_width, vp_height)

        slot.addChild(self.virtual_area._root)
        node = self.page.content.getEntityNode()
        node.removeFromParent()
        self.virtual_area.add_node(node)

        # setup sockets handle for scroll
        self.virtual_area.init_handlers(socket)
        self._va_movie.setInteractive(True)

        virtual_area_socket = self.virtual_area.get_socket()
        virtual_area_socket.setDefaultHandle(False)

        entity = self._va_movie.getEntity()
        entity.setSocketHandle("touch", "button", False)
        entity.setSocketHandle("touch", "enter", False)
        entity.setSocketHandle("touch", "move", False)

        # content size
        width, height = self.calculateContentSize()
        self.virtual_area.set_content_size(0.0, 0.0, width, height)

    def calculateContentSize(self):
        bb = self._va_bounds
        width = self._va_total_width
        height = bb.maximum.y - bb.minimum.y
        # print round(width, 2), round(height, 2)
        return width, height

    def isScrollNeeded(self):
        bb = self._va_bounds
        width = bb.maximum.x - bb.minimum.x
        if self._va_total_width > width:
            return True
        return False
