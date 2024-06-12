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
        self.offset_y = None
        self._button_counter_x = 0
        self._button_counter_y = 0

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
        self.offset_y = None
        self._button_counter_x = 0
        self._button_counter_y = 0

    # --- scroll -------------------------------------------------------------------------------------------------------

    def adjustButton(self, button):
        """
        Info: Used for VA to calculate correct total_height and setup buttons in defined number of columns.
        Abbreviations:
        `VA` or `va` - virtual area
        `pos` - position
        """

        # Define button height, width
        button_bounds = button.movie.getCompositionBounds()
        button_width = Utils.getBoundingBoxWidth(button_bounds)
        button_height = Utils.getBoundingBoxHeight(button_bounds)

        # Adding new button, increasing buttons counter for X dimension (row)
        self._button_counter_x += 1

        # If this is first button in a row, increasing buttons counter for Y dimension (column)
        if self._button_counter_x == 1:
            self._button_counter_y += 1

        # Define button X, Y positions using counters, width, height
        button_pos_x = button_width * self._button_counter_x - button_width / 2
        button_pos_y = button_height * self._button_counter_y - button_height / 2

        # Define dynamic offset for X dimension
        va_movie = self.object.getObject("Movie2_VirtualArea")
        va_bounds = va_movie.getCompositionBounds()
        va_width = va_bounds.maximum.x - va_bounds.minimum.x

        # Calculating full offset width (empty space)
        offset_x_dynamic_full = va_width - (self.columns_count * button_width)

        # Re-define self.columns_count (Demon 'ColumnsCount' param) and re-calculate new dynamic offset for X dimension,
        # because with current self.columns_count objects would not fit in the VA width
        if offset_x_dynamic_full < 0:
            buttons_width_raw = 0
            columns_counter = 0

            while buttons_width_raw <= va_width:
                buttons_width_raw += button_width
                columns_counter += 1

            columns_count_new = columns_counter - 1

            Trace.msg_err(
                "{!r} has not enough width to place {!r} in {!r} columns. "
                "Auto-changing columns count to {!r}. "
                "Please, change {!r} param to {!r}!!!".format(
                    va_movie.getName(), button.movie.getName(), self.columns_count, columns_count_new, "ColumnsCount",
                    columns_count_new))

            self.columns_count = columns_count_new
            offset_x_dynamic_full = va_width - (self.columns_count * button_width)

        # Calculating one offset part width (to insert inbetween objects)
        offset_x_dynamic_part = offset_x_dynamic_full / (self.columns_count + 1)

        # 1 version dynamic offset for X dimension (dumber)
        # dynamic_offset_x_one = dynamic_offset_x_all / (self.columns_count - 1)
        # pos_x += dynamic_offset_x_one * self._button_counter_x - dynamic_offset_x_one

        # 2 version dynamic offset for X dimension (smarter)
        button_pos_x += offset_x_dynamic_part * self._button_counter_x

        # Define static offset for Y dimension
        button_pos_y += self.offset_y * self._button_counter_y - self.offset_y

        # Set node local position
        node = button.movie.getEntityNode()
        node.setLocalPosition((
            button_pos_x,
            button_pos_y
        ))

        # If this is first button in a row, re-defining VA total height by object position + half-height
        if self._button_counter_x == 1:
            self._va_total_height = button_pos_y + (button_height / 2)

        # If this is last button in a row, resetting buttons X dimension counter
        if self._button_counter_x == self.columns_count:
            self._button_counter_x = 0

    def initVirtualArea(self):
        self._va_movie = self.object.getObject("Movie2_VirtualArea")
        self._va_bounds = self._va_movie.getCompositionBounds()
        self.virtual_area = VirtualArea()
        self.virtual_area.onInitialize(dragging_mode=self.scroll_mode, enable_scale=False, disable_drag_if_invalid=False)

        self._setupVirtualArea()
        if self.isScrollNeeded() is False:
            self._va_movie.setInteractive(False)

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
