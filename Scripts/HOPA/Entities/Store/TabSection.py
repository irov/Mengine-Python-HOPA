from Foundation.Entities.MovieVirtualArea.VirtualArea import VirtualArea
from Foundation.TaskManager import TaskManager
from Foundation.GuardBlockInput import GuardBlockInput


class TabSection(object):

    def __init__(self, parent_group, parent_movie, params):
        self._parent_group = parent_group  # where all prototypes storages
        self._parent_movie = parent_movie  # parent movie of all created tabs
        self.params = params  # StoreManager.TabParam

        self.tabs = {}
        self.selected_tab = None
        self.back = None
        self._buttons = []

        self.tc_tabs_handler = None
        self.tc_back_handler = None

        self._observers = []

        self.virtual_area = VirtualArea()
        self.virtual_area.onInitialize(dragging_mode='vertical', enable_scale=False, disable_drag_if_invalid=False)
        self._va_bounds = None
        self._va_tabs_height = 0
        self._va_total_height = 0

    def create(self, ignored_pages=(), unvisited_pages=()):
        self._createBack()
        self._createTabs(ignored_pages, unvisited_pages)

        self.virtual_area.on_drag_start += self._cbDragStart
        self.virtual_area.on_drag_end += self._cbDragEnd

        self._observers.append(Notification.addObserver(Notificator.onStoreTabSectionClickedTab, self._cbTabClicked))

    def _createBack(self):
        if self._parent_movie.hasMovieSlot("back") is False:
            return False
        slot = self._parent_movie.getMovieSlot("back")

        back = Back()
        back.createButton(self._parent_group, slot)
        self.back = back

        self._buttons.append(back)

        height = back.getHeight()
        self._va_total_height += height

        return True

    def _createTabs(self, ignored_pages=(), unvisited_pages=()):
        if self._parent_movie.hasMovieSlot("content") is False:
            return False
        slot = self._parent_movie.getMovieSlot("content")

        slot_position = slot.getLocalPosition()
        self._va_total_height += slot_position.y

        tabs_params = sorted(self.params.values(), key=lambda tab: tab.index)
        for params in tabs_params:
            if params.page_id in ignored_pages:
                continue

            tab = Tab(params)
            tab.createButton(self._parent_group, slot)
            tab.setPosition((0, self._va_tabs_height))
            tab.setSelected(False)

            if tab.page_id in unvisited_pages:
                tab.setVisited(False)

            # update height
            height = tab.getHeight()
            self._va_tabs_height += height

            self.tabs[params.page_id] = tab
            self._buttons.append(tab)

        self._va_total_height += self._va_tabs_height

    def getTab(self, page_id):
        return self.tabs.get(page_id)

    def getFirstTab(self):
        first_tab = self._buttons[1]
        return first_tab

    def getSelected(self):
        return self.selected_tab

    def runTaskChain(self):
        if self.back is not None:
            self.tc_back_handler = TaskManager.createTaskChain(Name="TabSectionBackHandler", Repeat=True)
            with self.tc_back_handler as tc:
                tc.addScope(self.back.scopeInteract)

        if len(self.tabs) > 0:
            self.tc_tabs_handler = TaskManager.createTaskChain(Name="TabSectionsHandler", Repeat=True)
            with self.tc_tabs_handler as tc:
                for button, source_race in tc.addRaceTaskList(self.tabs.values()):
                    source_race.addScope(button.scopeInteract)

    def _cbTabClicked(self, tab):
        if self.selected_tab is not None:
            self.selected_tab.setSelected(False)
        tab.setSelected(True)
        self.selected_tab = tab
        return False

    # virtual area -----

    def setupViewport(self):
        bb = self._va_bounds
        self.virtual_area.setup_viewport(bb.minimum.x, bb.minimum.y, bb.maximum.x, bb.maximum.y)

    def setupVirtualArea(self, parent, slot_name="tabs", socket_name="touch"):
        self._va_bounds = parent.getCompositionBounds()

        if self.isScrollNeeded() is False:
            return

        socket = parent.getSocket(socket_name)
        slot = parent.getMovieSlot(slot_name)

        self.setupViewport()

        slot.addChild(self.virtual_area._root)
        node = self._parent_movie.getEntityNode()
        node.removeFromParent()
        self.virtual_area.add_node(node)

        # setup sockets handle for scroll
        self.virtual_area.init_handlers(socket)
        parent.setInteractive(True)

        virtual_area_socket = self.virtual_area.get_socket()
        virtual_area_socket.setDefaultHandle(False)

        content_entity = parent.getEntity()
        content_entity.setSocketHandle(socket_name, "button", False)
        content_entity.setSocketHandle(socket_name, "enter", False)
        content_entity.setSocketHandle(socket_name, "move", False)

        # content size
        width, height = self.calculateContentSize()
        self.virtual_area.set_content_size(0.0, 0.0, width, height)

    def update_va_size(self):
        width, height = self.calculateContentSize()
        self.virtual_area.set_content_size(0.0, 0.0, width, height)

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
            tc.addDelay(0.0)
            tc.addFunction(GuardBlockInput.enableBlockSocket, False)

    def _cancelDragEndTC(self):
        tc_name = "{}_DragEnd".format(self.__class__.__name__)
        if TaskManager.existTaskChain(tc_name):
            TaskManager.cancelTaskChain(tc_name)

    # remove tab -----

    def remove_tab(self, page_id):
        if page_id not in self.tabs:
            return

        self.cancelTaskChain()

        tab = self.getTab(page_id)
        if tab == self.selected_tab:
            self.selected_tab = None
        idx = self._buttons.index(tab)

        prev_tab_position = tab.getPosition()
        for next_tab in self._buttons[idx + 1:]:
            next_tab_position = next_tab.getPosition()
            next_tab.setPosition(prev_tab_position)
            prev_tab_position = next_tab_position

        height = tab.getHeight()
        self._va_total_height -= height
        self.update_va_size()

        self._buttons.remove(tab)
        self.tabs.pop(tab.page_id)

        if len(self.tabs) == 0:
            TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName=tab.params.group_name, Value=False)
        tab.destroy()

        self.runTaskChain()

    def cancelTaskChain(self):
        if self.tc_tabs_handler is not None:
            self.tc_tabs_handler.cancel()
            self.tc_tabs_handler = None

        if self.tc_back_handler is not None:
            self.tc_back_handler.cancel()
            self.tc_back_handler = None

    def cleanUp(self):
        for observer_id in self._observers:
            Notification.removeObserver(observer_id)
        self._observers = []

        self.cancelTaskChain()

        if self.back is not None:
            self.back.destroy()
            self.back = None

        for tab in self.tabs.values():
            tab.destroy()
        self.tabs = None
        self.selected_tab = None

        self._buttons = None

        if self.virtual_area is not None:
            self._parent_movie.returnToParent()

            self._cancelDragEndTC()
            self.virtual_area.onFinalize()
            self.virtual_area = None
            self._va_bounds = None

        self.params = None
        self._parent_movie = None
        self._parent_group = None


class Tab(object):
    PROTOTYPE_NAME = "Movie2Button_TabSwitch"
    RED_DOT_PROTOTYPE_NAME = "Movie2_RedDot"
    ALIAS_TITLE_ID = "$AliasStoreTabTitle"

    if _DEVELOPMENT is True:
        def __repr__(self):
            return "<Tab [{}-{}] {}>".format(self.page_id, self.selected, self.getPosition())

    def __init__(self, params):
        self.page_id = params.page_id
        self.params = params
        self.movie = None
        self.selected = params.selected
        self.visited = True
        self.red_dot = None
        self.env = self.page_id

    def createButton(self, group, slot):
        if group.hasPrototype(self.PROTOTYPE_NAME) is False:
            Trace.log("Entity", 0, "Store failed in create tab button - not found prototype {!r} in {!r}".format(self.PROTOTYPE_NAME, group.getName()))
            return False

        movie = group.generateObjectUnique("TabSwitcher_{}".format(self.page_id), self.PROTOTYPE_NAME, Enable=True)
        node = movie.getEntityNode()
        slot.addChild(node)

        movie.setTextAliasEnvironment(self.env)
        Mengine.setTextAlias(self.env, self.ALIAS_TITLE_ID, self.params.text_id)

        if self.params.idle_color is not None:
            idle_state = movie.entity.getStateMovie("Idle")
            idle_state.setupMovieTextColor(self.ALIAS_TITLE_ID, self.params.idle_color)

        selected_state = movie.entity.getStateMovie("Selected")
        if selected_state is not None and self.params.selected_color is not None:
            selected_state.setupMovieTextColor(self.ALIAS_TITLE_ID, self.params.selected_color)

        self.movie = movie

        red_dot_movie = group.generateObjectUnique("RedDot_{}".format(self.page_id), self.RED_DOT_PROTOTYPE_NAME)
        movie.addChildToSlot(red_dot_movie.getEntityNode(), "notify")
        self.red_dot = red_dot_movie
        self.setVisited(self.visited)

    def getHeight(self):
        bounds = self.movie.getCompositionBounds()
        height = bounds.maximum.y - bounds.minimum.y
        return height

    def setPosition(self, position):
        node = self.movie.getEntityNode()
        node.setLocalPosition(position)

    def getPosition(self):
        node = self.movie.getEntityNode()
        local_position = node.getLocalPosition()
        return local_position

    def setSelected(self, value):
        self.movie.setSelected(value)

    def setVisited(self, value):
        """ if tab is not visited - enable red dot on slot 'notify' """
        if self.red_dot is None:
            return

        state = not value

        self.red_dot.setEnable(state)
        self.visited = state

    def destroy(self):
        if self.red_dot is not None:
            node = self.red_dot.getEntityNode()
            self.movie.removeFromParentSlot(node, "notify")
            self.red_dot.onDestroy()
            self.red_dot = None

        if self.movie is not None:
            self.movie.removeFromParent()
            self.movie.onDestroy()
            self.movie = None

    def scopeInteract(self, source):
        source.addTask("TaskMovie2ButtonClick", Movie2Button=self.movie)
        source.addNotify(Notificator.onStoreTabSectionClickedTab, self)


class Back(object):
    PROTOTYPE_NAME = "Movie2Button_Back"

    if _DEVELOPMENT is True:
        def __repr__(self):
            return "<Back>"

    def __init__(self):
        self.movie = None

    def createButton(self, group, slot):
        movie = group.generateObjectUnique(self.PROTOTYPE_NAME, self.PROTOTYPE_NAME, Enable=True)
        node = movie.getEntityNode()
        slot.addChild(node)
        self.movie = movie

    def destroy(self):
        if self.movie is not None:
            self.movie.removeFromParent()
            self.movie.onDestroy()
            self.movie = None

    def scopeInteract(self, source):
        source.addTask("TaskMovie2ButtonClick", Movie2Button=self.movie)
        source.addNotify(Notificator.onStoreTabSectionClickedBack)

    def getHeight(self):
        bounds = self.movie.getCompositionBounds()
        height = bounds.maximum.y - bounds.minimum.y
        return height
