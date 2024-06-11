from HOPA.Entities.StorePage.Components.StorePageBaseComponent import StorePageBaseComponent
from Foundation.Entities.MovieVirtualArea.VirtualArea import VirtualArea
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager


class StorePageScrollVerticalComponent(StorePageBaseComponent):

    def __init__(self, page):
        super(StorePageScrollVerticalComponent, self).__init__(page)
        self.virtual_area = None
        self.scroll_mode = None
        # movie with slot 'content' on which Movie2_Content will be attached and horizontal scroll will be enabled
        self._va_movie = None
        self._va_bounds = None
        self._va_total_height = 0

        self.columns_count = None
        self.offset_x = None
        self.offset_y = None
        self._buttons_counter = 0

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
        self._va_total_height = 0

        self._cancelDragEndTC()
        self.virtual_area.onFinalize()
        self.virtual_area = None
        self.scroll_mode = None

        self.columns_count = None
        self.offset_x = None
        self.offset_y = None
        self._buttons_counter = 0

    # --- scroll -------------------------------------------------------------------------------------------------------

    def adjustButton(self, button):
        """ Used for VA to calculate correct total_height and place draggable buttons """

        bounds = button.movie.getCompositionBounds()
        height = Utils.getBoundingBoxHeight(bounds)
        width = Utils.getBoundingBoxWidth(bounds)

        pos_x = 0

        if self._buttons_counter % self.columns_count != 0:
            pos_x -= self.offset_x
        else:
            pos_x += self.offset_x

        node = button.movie.getEntityNode()
        node.setLocalPosition((width/2 + pos_x, height/2 + self._va_total_height))

        self._buttons_counter += 1
        self._va_total_height += height

    def initVirtualArea(self):
        self._va_movie = self.object.getObject("Movie2_VirtualArea")
        self._va_bounds = self._va_movie.getCompositionBounds()
        self.virtual_area = VirtualArea()
        self.virtual_area.onInitialize(dragging_mode=self.scroll_mode, enable_scale=False, disable_drag_if_invalid=False)

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

        # callbacks
        self.virtual_area.on_drag_start += self._cbDragStart
        self.virtual_area.on_drag_end += self._cbDragEnd

    def calculateContentSize(self):
        bb = self._va_bounds
        width = bb.maximum.x - bb.minimum.x
        height = self._va_total_height
        # print round(width, 2), round(height, 2)
        return width, height

    def isScrollNeeded(self):
        bb = self._va_bounds
        height = bb.maximum.y - bb.minimum.y
        if self._va_total_height > height:
            return True
        return False

    def _cbDragStart(self):
        GuardBlockInput.enableBlockSocket(True)

    def _cbDragEnd(self):
        if self.virtual_area.is_dragging() is False:
            return

        self._cancelDragEndTC()
        with TaskManager.createTaskChain(Name="{}_DragEnd".format(self.__class__.__name__)) as tc:
            tc.addDelay(0.0)  # ensure that we will receive use on socket event before disable block input
            tc.addFunction(GuardBlockInput.enableBlockSocket, False)

    def _cancelDragEndTC(self):
        tc_name = "{}_DragEnd".format(self.__class__.__name__)
        if TaskManager.existTaskChain(tc_name):
            TaskManager.cancelTaskChain(tc_name)
