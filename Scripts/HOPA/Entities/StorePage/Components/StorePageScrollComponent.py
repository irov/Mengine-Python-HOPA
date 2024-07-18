from HOPA.Entities.StorePage.Components.StorePageBaseComponent import StorePageBaseComponent
from Foundation.Entities.MovieVirtualArea.VirtualArea import VirtualArea
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager


MOVIE_VA = "Movie2_VirtualArea"
MOVIE_ARROW = "Movie2_Arrow"
SOCKET_TOUCH = "touch"
SLOT_CONTENT = "content"


class StorePageScrollComponent(StorePageBaseComponent):

    def __init__(self, page):
        super(StorePageScrollComponent, self).__init__(page)
        self.virtual_area = None
        # movie with slot 'content' on which Movie2_Content will be attached and horizontal scroll will be enabled
        self._va_movie = None
        self._va_bounds = None
        self._va_total_width = 0
        self._va_total_height = 0
        self._columns_count = self.page.ColumnsCount
        self._button_counter_x = 0
        self._button_counter_y = 0

    def _check(self):
        if self.object.hasObject(MOVIE_VA) is False:
            Trace.log("Entity", 0, "StorePage [{}] not found {!r} in Demon inside Group {!r}".format(
                self.page.PageID, MOVIE_VA, self.object.parent.getName()))
            return False
        return True

    def _run(self):
        self.initVirtualArea()

    def _cleanUp(self):
        self.page.content.returnToParent()

        self._va_movie = None
        self._va_bounds = None
        self._va_total_width = 0
        self._va_total_height = 0
        self._columns_count = 0
        self._button_counter_x = 0
        self._button_counter_y = 0

        self._cancelDragEndTC()
        self.virtual_area.onFinalize()
        self.virtual_area = None

    # --- scroll -------------------------------------------------------------------------------------------------------

    def adjustButtonHorizontal(self, button):
        """ used for VA to calculate correct total_width and place draggable buttons """

        node = button.movie.getEntityNode()
        node.setLocalPosition((self._va_total_width, 0))

        bounds = button.movie.getCompositionBounds()
        width = bounds.maximum.x - bounds.minimum.x

        self._va_total_width += width

    def adjustButtonVertical(self, button):
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
        va_movie = self.object.getObject(MOVIE_VA)
        va_bounds = va_movie.getCompositionBounds()
        va_width = va_bounds.maximum.x - va_bounds.minimum.x

        # Calculating full offset width (empty space)
        offset_x_dynamic_full = va_width - (self._columns_count * button_width)

        # Re-define self._columns_count (obj 'ColumnsCount' const) and re-calculate new dynamic offset for X dimension,
        # because with current self._columns_count objects would not fit in the VA width
        if offset_x_dynamic_full < 0:
            buttons_width_raw = 0
            columns_counter = 0

            while buttons_width_raw <= va_width:
                buttons_width_raw += button_width
                columns_counter += 1

            columns_count_new = columns_counter - 1

            Trace.msg_err(
                "{!r} has not enough width to place {!r} in {} columns. "
                "Auto-changing columns count to {}. "
                "Please, change {!r} param to {}!!!".format(
                    va_movie.getName(), button.movie.getName(), self._columns_count, columns_count_new,
                    "ColumnsCount",
                    columns_count_new))

            self._columns_count = columns_count_new
            offset_x_dynamic_full = va_width - (self._columns_count * button_width)

        # Calculating one offset part width (to insert inbetween objects)
        offset_x_dynamic_part = offset_x_dynamic_full / (self._columns_count + 1)

        # 1 version dynamic offset for X dimension (dumber)
        # offset_x_dynamic_part = offset_x_dynamic_full / (self._columns_count - 1)
        # button_pos_x += offset_x_dynamic_part * self._button_counter_x - offset_x_dynamic_part

        # 2 version dynamic offset for X dimension (smarter)
        button_pos_x += offset_x_dynamic_part * self._button_counter_x

        # Define static offset for Y dimension
        button_pos_y += self.page.OffsetY * self._button_counter_y - self.page.OffsetY

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
        if self._button_counter_x == self._columns_count:
            self._button_counter_x = 0

    def initVirtualArea(self):
        self._va_movie = self.object.getObject(MOVIE_VA)
        self._va_bounds = self._va_movie.getCompositionBounds()
        self.virtual_area = VirtualArea()
        self.virtual_area.onInitialize(dragging_mode=self.page.ScrollMode, enable_scale=False, disable_drag_if_invalid=False)

        self._setupVirtualArea()
        if self.isScrollNeeded() is False:
            # TODO: fix error - VirtualArea width/height must be less than Content ()
            self._va_movie.setInteractive(False)
        else:
            self._setArrowEnable(self.page.AllowArrow)

    def _setupVirtualArea(self):
        if self._va_movie.hasSocket(SOCKET_TOUCH) is False:
            Trace.log("Entity", 0, "StorePage [{}] not found socket {!r} in {!r}".format(
                self.page.PageID, SOCKET_TOUCH, self._va_movie.getName()))
            return
        if self._va_movie.hasMovieSlot(SLOT_CONTENT) is False:
            Trace.log("Entity", 0, "StorePage [{}] not found slot {!r} in {!r}".format(
                self.page.PageID, SLOT_CONTENT, self._va_movie.getName()))
            return

        socket = self._va_movie.getSocket(SOCKET_TOUCH)
        slot = self._va_movie.getMovieSlot(SLOT_CONTENT)

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
        entity.setSocketHandle(SOCKET_TOUCH, "button", False)
        entity.setSocketHandle(SOCKET_TOUCH, "enter", False)
        entity.setSocketHandle(SOCKET_TOUCH, "move", False)

        # content size
        width, height = self.calculateContentSize()
        self.virtual_area.set_content_size(0.0, 0.0, width, height)

        # callbacks
        self.virtual_area.on_drag_start += self._cbDragStart
        self.virtual_area.on_drag += self._cbDrag
        self.virtual_area.on_drag_end += self._cbDragEnd

    def _setArrowEnable(self, value):
        if self.object.hasObject(MOVIE_ARROW) is False:
            if value is True:
                Trace.log("Entity", 0, "StorePage [{}] not found {!r} in Demon inside Group {!r}".format(
                    self.page.PageID, MOVIE_ARROW, self.object.parent.getName()))
            return

        movie = self.object.getObject(MOVIE_ARROW)
        current_state = movie.getEnable()

        if value is True and current_state is False:
            movie.setEnable(True)
        elif value is False and current_state is True:
            movie.setEnable(False)

    def _setArrowAlpha(self, value):
        if value < 0.0 or value > 1.0:
            return

        movie = self.object.getObject(MOVIE_ARROW)
        if movie is None:
            return

        alpha_value = 1.0 - value

        if movie.getAlpha() == alpha_value:
            return

        movie.setAlpha(alpha_value)

    def calculateContentSize(self):
        bb = self._va_bounds
        width = bb.maximum.x - bb.minimum.x
        height = bb.maximum.y - bb.minimum.y

        if self.page.ScrollMode == "horizontal":
            width = self._va_total_width
        elif self.page.ScrollMode == "vertical":
            height = self._va_total_height

        return width, height

    def isScrollNeeded(self):
        bb = self._va_bounds
        width = bb.maximum.x - bb.minimum.x
        height = bb.maximum.y - bb.minimum.y

        if self.page.ScrollMode == "horizontal":
            if self._va_total_width > width:
                return True
        elif self.page.ScrollMode == "vertical":
            if self._va_total_height > height:
                return True

        return False

    def _cbDragStart(self):
        GuardBlockInput.enableBlockSocket(True)

    def _cbDrag(self, x, y):
        if self.page.AllowArrow is True:
            self._setArrowAlpha(y)

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
