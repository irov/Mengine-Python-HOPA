from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager
from HOPA.StageManager import StageManager
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification

ALIAS_ENV = ""
ALIAS_TEXT_NAME = "$ID_LineSpeed"

class SystemDebugMenu(System):
    s_dev_to_debug = False
    s_is_showable = False

    s_easing_types = ["easyLinear", "easyIn", "easyOut", "easyInOut", "easySineIn", "easeSineOut", "easySineInOut", "easyQuadIn", "easyQuadOut", "easyQuadInOut", "easyCubicIn", "easyCubicOut", "easyCubicInOut", "easyQuartIn", "easyQuartOut", "easyQuartInOut", "easyQuintIn", "easyQuintOut", "easyQuintInOut", "easyExpoIn", "easyExpoOut", "easyExpoInOut", "easyCircIn", "easyCircOut", "easyCircInOut", "easyElasticIn", "easyElasticOut", "easyElasticInOut", "easyBackIn", "easyBackOut", "easyBackInOut",
        "easyBounceIn", "easyBounceOut", "easyBounceInOut", ]

    def __init__(self):
        super(SystemDebugMenu, self).__init__()
        self.__key_handler_id = None

        self.easing_index = -1

        self.cheat_tween_in_default_name = None
        self.cheat_tween_out_default_name = None

        self.cheat_tween_in_easing_type = None
        self.cheat_tween_out_easing_type = None

        self.mobileDebugButtonNode = None
        self.__click_counter = 0
        self.__scheduleID = None

        self._dtdWaitPHs_widgets = []
        self._dtdWaitPHs_paragraphs = []

    # ---- Mobile -----------------------------------------

    def __createMobileDebugButton(self):
        scene = SceneManager.getCurrentScene()
        if scene is None:
            return

        layer = scene.getMainLayer()

        button_size = DefaultManager.getDefaultTuple("DebugMenuMobileButtonSize", (75, 75), divider=", ")
        if SceneManager.getCurrentSceneName() == "DebugMenu":
            layer_size = layer.getSize()
            start_point = (0, layer_size.y - button_size[1])
        else:
            start_point = DefaultManager.getDefaultTuple("DebugMenuMobileButtonPosition", (0, 0), divider=", ")

        if self.mobileDebugButtonNode is None:
            polygon = [(0, 0), (button_size[0], 0), (button_size[0], button_size[1]), (0, button_size[1])]

            node = Mengine.createNode("HotSpotPolygon")
            node.setPolygon(polygon)
            node.setName("SocketDebugMenuTransition")
            node.setEventListener(onHandleMouseButtonEvent=self.__onMobileDebugClick)
            self.mobileDebugButtonNode = node
        else:
            self.mobileDebugButtonNode.removeFromParent()

        self.mobileDebugButtonNode.setWorldPosition(start_point)
        self.mobileDebugButtonNode.enable()
        layer.addChild(self.mobileDebugButtonNode)

    def __onMobileDebugClick(self, touchId, x, y, button, pressure, isDown, isPressed):
        if button != 0 or isDown is False:
            return True

        if self.__scheduleID is None:
            self.__attachSchedule()

        self.__click_counter += 1

        max_click = DefaultManager.getDefaultInt("DebugMenuMobileMaxClick", 5)
        if self.__click_counter >= max_click:
            self.__resetClicksCounter()
            self.__resolveDebugMenu()
        return True

    def __onSceneActivate(self, sceneName):
        if SceneManager.isDebugMenuBlocked(sceneName) is True:
            return False
        self.__resetClicksCounter()
        self.__createMobileDebugButton()
        return False

    def __onSchedule(self, ID, isRemoved):
        self.__resetClicksCounter()
        self.__scheduleID = None

    def __resetClicksCounter(self):
        self.__click_counter = 0
        if _DEVELOPMENT is True:
            Trace.msg("<SystemDebugMenu> clicks has been reset")

    def __attachSchedule(self):
        reset_time = DefaultManager.getDefaultFloat("DebugMenuMobileClickResetTime", 3) * 1000.0
        self.__scheduleID = Mengine.schedule(reset_time, self.__onSchedule)

    # ---- DevToDebug -----------------------------------------

    def initDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return
        if SystemDebugMenu.s_dev_to_debug is True:
            return
        SystemDebugMenu.s_dev_to_debug = True

        self._dtdAllParagraphsTab()
        self._dtdScenesTab()
        self._dtdItemsTab()
        self._dtdCheatsTab()
        self._dtdUserSettings()

        # temporary disabled:  # self._dtdWaitParagraphsTab()        # tab with current wait paragraphs

    def _dtdUserSettings(self):
        widgets_prefix = "w_user_settings_"
        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")

        widgets_ids = ["output", "set", "get", "save"]
        if any([tab.findWidget(w_id) is not None for w_id in widgets_ids]) is True:
            # already created
            return

        w_value = Mengine.createDevToDebugWidgetText(widgets_prefix + "output")
        w_value.setText("Here will be info about inputted user setting. "
                        "Do not forget to click `Save accounts` or `Save game` after change user settings")
        tab.addWidget(w_value)

        def _set_value(key, val):
            value_template = "Value of user setting '{}' is '{}'"
            text = value_template.format(key, val)
            w_value.setText(text)

        def _get(key):
            if Mengine.hasCurrentAccountSetting(key) is False:
                Trace.msg_err("[DevToDebug] key {!r} not exists".format(key))
                return
            value = Mengine.getCurrentAccountSetting(key)
            _set_value(key, value)

        w_get = Mengine.createDevToDebugWidgetCommandLine(widgets_prefix + "get")
        w_get.setTitle("Get value of user setting")
        w_get.setPlaceholder("for example: Name")
        w_get.setCommandEvent(_get)
        tab.addWidget(w_get)

        def _set_setting(text):
            params = text.split(" ")
            if len(params) != 2:
                Trace.msg_err("[DevToDebug] wrong len ({} != 2) for set user settings - syntax: <key> <value>".format(len(params)))
                return
            key, val = params

            if Mengine.hasCurrentAccountSetting(key) is False:
                Trace.msg_err("[DevToDebug] key {!r} not exists".format(key))
                return

            last_val = Mengine.getCurrentAccountSetting(key)
            Mengine.changeCurrentAccountSetting(key, unicode(val))
            _set_value(key, val)
            Trace.msg("[DevToDebug] User setting {!r} changed from {!r} to {!r}".format(key, last_val, val))

        w_set = Mengine.createDevToDebugWidgetCommandLine(widgets_prefix + "set")
        w_set.setTitle("Set user setting value")
        w_set.setPlaceholder("syntax: <key> <value>")
        w_set.setCommandEvent(_set_setting)
        tab.addWidget(w_set)

        w_save = Mengine.createDevToDebugWidgetButton(widgets_prefix + "save")
        w_save.setTitle("Save accounts")
        w_save.setClickEvent(Mengine.saveAccounts)
        tab.addWidget(w_save)

    def _dtdCheatsTab(self):
        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")

        if tab.findWidget("change_locale") is None:
            def _cbChangeLocale(lang):
                if Mengine.hasLocale(lang) is False:
                    Trace.msg_err("Wrong locale {!r}".format(lang))
                    return

                def cbOnSceneRestartChangeLocale(scene, isActive, isError):
                    if scene is None:
                        Mengine.setLocale(lang)
                        Trace.msg("Locale changed to {!r}".format(lang))

                Mengine.restartCurrentScene(True, cbOnSceneRestartChangeLocale)

            w_locale = Mengine.createDevToDebugWidgetCommandLine("change_locale")
            w_locale.setTitle("Change locale")
            w_locale.setPlaceholder("<locale (en, zh, ...)>")
            w_locale.setCommandEvent(_cbChangeLocale)
            tab.addWidget(w_locale)

    def _dtdItemsTab(self):
        tab = Mengine.addDevToDebugTab("Items")

        Inventory = DemonManager.getDemon("Inventory")
        items = ItemManager.getAllItems()

        # COMMAND LINE ITEM GETTER

        def _getItem(itemName):
            if itemName not in items:
                Trace.msg_err("Wrong item name {!r}".format(itemName))
                return
            TaskManager.runAlias("AliasInventoryAddInventoryItem", None, Inventory=Inventory, ItemName=itemName)

        w_item_fast = Mengine.createDevToDebugWidgetCommandLine("get_item_fast")
        w_item_fast.setTitle("Get item by name")
        w_item_fast.setPlaceholder("Syntax: <itemName>")
        w_item_fast.setCommandEvent(_getItem)
        tab.addWidget(w_item_fast)

        # GROUPING

        items_plus = []
        items_in_group = {}
        for item_params in items.values():
            if item_params.PlusScene is not None:
                # items with scene plus
                items_plus.append(item_params)
                continue
            # other items grouped by their Group
            group_name = item_params.itemGroupName or "No Group"
            items_in_group.setdefault(group_name, []).append(item_params)

        # CREATE WIDGETS

        def _createItemWidget(params):
            item_id = params.itemID
            w_item = Mengine.createDevToDebugWidgetButton(item_id)
            w_item.setTitle("{} ({})".format(item_id, Mengine.getTextFromID(params.textID)))
            w_item.setClickEvent(_getItem, item_id)
            tab.addWidget(w_item)

        def _createItemWidgets(params_list):
            for params in params_list:
                _createItemWidget(params)

        def _createTitleWidget(title):
            w_title = Mengine.createDevToDebugWidgetText(title)
            w_title.setText("**{}**:".format(title))
            tab.addWidget(w_title)

        # default items
        for group_name, group_items in sorted(items_in_group.items()):
            _createTitleWidget(group_name)
            _createItemWidgets(group_items)

        # items with PlusScene
        _createTitleWidget("Items+")
        _createItemWidgets(items_plus)

    def _dtdScenesTab(self):
        SCENE_TYPES = ["GameScene", "MG", "HOG", "ItemPlus", "CutScene", "Other"]  # also order

        def _get_scene_category(scene_name):
            base_scene_name = SceneManager.getSceneBase(scene_name)
            if "MG" in scene_name:
                return "MG"
            elif base_scene_name.startswith(("HOG", "Puzzle", "Mahjong")):
                return "HOG"
            elif scene_name.endswith("Plus"):
                return "ItemPlus"
            elif scene_name[:2].isdigit() is True:
                return "GameScene"
            elif "CutScene" == base_scene_name:
                return "CutScene"
            else:
                return "Other"

        # categorize scenes

        categorized_scenes = {scene_type: [] for scene_type in SCENE_TYPES}

        for scene_name in SceneManager.getScenes():
            scene_type = _get_scene_category(scene_name)
            categorized_scenes[scene_type].append(scene_name)

        for scene_type, scenes in categorized_scenes.items():
            categorized_scenes[scene_type] = sorted(scenes)

        # button cb function

        def _transition(scene_name):
            TransitionManager.changeScene(scene_name, fade=False)

        # create widgets

        tab = Mengine.addDevToDebugTab("Scenes")

        def _current_scene_name():
            scene_name = SceneManager.getCurrentSceneName()
            return "Current scene is **{}**".format(scene_name)

        w_cur_scene = Mengine.createDevToDebugWidgetText("current_scene")
        w_cur_scene.setText(_current_scene_name)
        tab.addWidget(w_cur_scene)

        for scene_type in SCENE_TYPES:
            SCENES = categorized_scenes[scene_type]
            if len(SCENES) == 0:
                continue

            title_widget_id = "%s_text_title" % scene_type
            w_title = Mengine.createDevToDebugWidgetText(title_widget_id)

            title_text = "**{}** ({} items):".format(scene_type, len(SCENES))
            w_title.setText(title_text)

            tab.addWidget(w_title)

            for scene_name in SCENES:
                button_widget_id = scene_name
                w_button = Mengine.createDevToDebugWidgetButton(button_widget_id)

                w_button.setTitle(scene_name)
                w_button.setClickEvent(_transition, scene_name)

                tab.addWidget(w_button)

        # description at the bottom:

        descr_texts = ["---", "Total number of scenes: **{}**".format(sum([len(x) for x in categorized_scenes.values()])), "All scene types: _{}_".format(", ".join(SCENE_TYPES))]
        w_descr = Mengine.createDevToDebugWidgetText("description")
        description = "\n".join(descr_texts)
        w_descr.setText(description)
        tab.addWidget(w_descr)

    def _dtdAllParagraphsTab(self):
        tab = Mengine.addDevToDebugTab("Paragraphs")

        # COMMAND LINE

        def _runPh(paragraph_id):
            Notification.notify(Notificator.onParagraphRun, paragraph_id)  # start paragraph

        w_fast = Mengine.createDevToDebugWidgetCommandLine("run_line_ph")
        w_fast.setTitle("Run paragraph")
        w_fast.setPlaceholder("Syntax: <paragraph_id>")
        w_fast.setCommandEvent(_runPh)
        tab.addWidget(w_fast)

        # BUTTONS

        if StageManager.hasCurrentStage() is False:
            def _cbStageInit(*args, **kwargs):
                self.__dtdAllParagraphsTab()
                return True

            self.addObserver(Notificator.onStageInit, _cbStageInit)
        else:
            self.__dtdAllParagraphsTab()  # tab with all stage paragraphs

    def __dtdAllParagraphsTab(self):
        tab = Mengine.getDevToDebugTab("Paragraphs")

        cur_stage = StageManager.getCurrentStage()
        scenario_chapter = cur_stage.getScenarioChapter()

        if scenario_chapter.scenarios is None:
            Trace.log("System", 0, "scenartio chapter None scenarios")
            return

        macro_widgets = {}  # "scenario": {"title": widget, "buttons": [widget, ...] }
        ph_widgets = {}  # "ph_id": [widget, ...]

        def _utilFindWidgetPh(dict_, paragraph_id):
            widgets = dict_.get("buttons", {})
            for widget in widgets:
                widget_id = str(widget.getId())
                if paragraph_id == widget_id.split("__")[1]:
                    return True
            return False

        def _runPh(paragraph_id):
            Notification.notify(Notificator.onParagraphRun, paragraph_id)  # start paragraph

        for scenario_runner in scenario_chapter.scenarios.values():
            scenario = scenario_runner.Scenario
            scenario_id = scenario.ScenarioID

            macro_widgets[scenario_id] = {"buttons": []}

            w_title = Mengine.createDevToDebugWidgetText(scenario_id)
            w_title.setText(scenario_id + ":")
            macro_widgets[scenario_id]["title"] = w_title

            for paragraphs in scenario.getWaitParagraphs():
                for ph in paragraphs.Paragraphs:
                    if _utilFindWidgetPh(macro_widgets[scenario_id], ph) or ph == cur_stage.Name:
                        continue

                    w_button = Mengine.createDevToDebugWidgetButton("{}__{}".format(scenario_id, ph))
                    w_button.setTitle(ph)
                    w_button.setClickEvent(_runPh, ph)
                    macro_widgets[scenario_id]["buttons"].append(w_button)

                    # remember all widgets that refer for one same paragraph - we'll disable them all after use one
                    if ph not in ph_widgets:
                        ph_widgets[ph] = []
                    ph_widgets[ph].append(w_button)

        # add widgets to tab

        for scenario_id, items in sorted(macro_widgets.items()):
            widgets = items["buttons"]
            if len(widgets) == 0:
                continue
            widgets = [items["title"]] + widgets
            for widget in widgets:
                tab.addWidget(widget)

    # -----------

    def __resolveDebugMenu(self):
        if SceneManager.isDebugMenuBlocked():
            return
        if SystemDebugMenu.s_is_showable:
            SystemDebugMenu.s_is_showable = False
            TransitionManager.changeToGameScene(fade=False)
        else:
            SystemDebugMenu.s_is_showable = True

            zoom_open_group = ZoomManager.getZoomOpenGroupName()

            demon_debug_menu = GroupManager.getObject("DebugMenu", "Demon_DebugMenu")
            demon_debug_menu.setParam("Zoom", zoom_open_group)

            TransitionManager.changeScene("DebugMenu", fade=False)

    def __getNextEasingType(self, easing_type):
        if easing_type not in SystemDebugMenu.s_easing_types:
            return None

        cur_index = SystemDebugMenu.s_easing_types.index(easing_type)

        new_index = cur_index + 1
        if new_index == len(SystemDebugMenu.s_easing_types):
            new_index = 0

        next_easing_type = SystemDebugMenu.s_easing_types[new_index]

        return next_easing_type

    def __getPrevEasingType(self, easing_type):
        if easing_type not in SystemDebugMenu.s_easing_types:
            return None

        cur_index = SystemDebugMenu.s_easing_types.index(easing_type)

        new_index = cur_index - 1
        if new_index < 0:
            new_index = len(SystemDebugMenu.s_easing_types) - 1

        next_easing_type = SystemDebugMenu.s_easing_types[new_index]

        return next_easing_type

    def __nextTweenInCheatDefault(self):
        if self.cheat_tween_in_default_name is None:
            return

        next_easing_type = self.__getNextEasingType(self.cheat_tween_in_easing_type)
        if next_easing_type is None:
            return

        self.cheat_tween_in_easing_type = next_easing_type

        DefaultManager.addDefault(self.cheat_tween_in_default_name, self.cheat_tween_in_easing_type)

        print("TWEEN NEXT '{}' = {}".format(self.cheat_tween_in_default_name, self.cheat_tween_in_easing_type))

    def __prevTweenInCheatDefault(self):
        if self.cheat_tween_in_default_name is None:
            return

        next_easing_type = self.__getPrevEasingType(self.cheat_tween_in_easing_type)
        if next_easing_type is None:
            return

        self.cheat_tween_in_easing_type = next_easing_type

        DefaultManager.addDefault(self.cheat_tween_in_default_name, self.cheat_tween_in_easing_type)

        print("TWEEN PREV '{}' = {}".format(self.cheat_tween_in_default_name, self.cheat_tween_in_easing_type))

    def __nextTweenOutCheatDefault(self):
        if self.cheat_tween_out_default_name is None:
            return

        next_easing_type = self.__getNextEasingType(self.cheat_tween_out_easing_type)
        if next_easing_type is None:
            return

        self.cheat_tween_out_easing_type = next_easing_type

        DefaultManager.addDefault(self.cheat_tween_out_default_name, self.cheat_tween_out_easing_type)

        print("TWEEN NEXT '{}' = {}".format(self.cheat_tween_out_default_name, self.cheat_tween_out_easing_type))

    def __prevTweenOutCheatDefault(self):
        if self.cheat_tween_out_default_name is None:
            return

        next_easing_type = self.__getPrevEasingType(self.cheat_tween_out_easing_type)
        if next_easing_type is None:
            return

        self.cheat_tween_out_easing_type = next_easing_type

        DefaultManager.addDefault(self.cheat_tween_out_default_name, self.cheat_tween_out_easing_type)

        print("TWEEN PREV '{}' = {}".format(self.cheat_tween_out_default_name, self.cheat_tween_out_easing_type))

    def __onGlobalHandleKeyEvent(self, event):
        if not Mengine.hasOption('cheats'):
            return

        if not event.isDown:
            return

        if SystemManager.hasSystem("SystemEditBox"):
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return

        if event.code == DefaultManager.getDefaultKey("DevCheatSaveGame", "VK_J"):
            Notification.notify(Notificator.oniOSApplicationWillResignActive)
        elif event.code == DefaultManager.getDefaultKey("DevCheatShowDebugMenu", "VK_TAB"):
            self.__resolveDebugMenu()
        elif event.code == DefaultManager.getDefaultKey("DevCheatPrintCursorPos", "VK_Z"):
            self.__printCursorPos()

        elif event.code == DefaultManager.getDefaultKey("CheatsNextTweenIn", "VK_G"):
            self.__nextTweenInCheatDefault()
        elif event.code == DefaultManager.getDefaultKey("CheatsPrevTweenIn", "VK_F"):
            self.__prevTweenInCheatDefault()
        elif event.code == DefaultManager.getDefaultKey("CheatsNextTweenOut", "VK_V"):
            self.__nextTweenOutCheatDefault()
        elif event.code == DefaultManager.getDefaultKey("CheatsPrevTweenOut", "VK_C"):
            self.__prevTweenOutCheatDefault()

        elif event.code == DefaultManager.getDefaultKey("CheatsUnlockBonusChapter"):
            Notification.notify(Notificator.onChapterOpen, "Bonus")

    def __printCursorPos(self):
        Trace.msg('[SystemDebugMenu] Current mouse position is: {}'.format(Mengine.getCursorPosition()))

    def __changeCurrentTweenOnTestScene(self, flag):
        time = 2000.0
        movie = GroupManager.getObject("LineSpeed", "Movie2_Block")
        entity_node = movie.getEntityNode()
        point = entity_node.getWorldPosition()

        point.x = 800

        from_point = (0.0, point.y)
        to_point = point

        easing_types_count = len(SystemDebugMenu.s_easing_types)

        if flag == "Next":
            self.easing_index += 1
        else:
            self.easing_index -= 1

        if self.easing_index < 0:
            self.easing_index = easing_types_count - 1
        elif self.easing_index == easing_types_count:
            self.easing_index = 0

        easing_type_name = SystemDebugMenu.s_easing_types[self.easing_index]

        Mengine.setTextAliasArguments(ALIAS_ENV, ALIAS_TEXT_NAME, easing_type_name)

        if TaskManager.existTaskChain("Debug_Tween_Move") is True:
            TaskManager.cancelTaskChain("Debug_Tween_Move")

        with TaskManager.createTaskChain(Name="Debug_Tween_Move", Repeat=False) as tc:
            tc.addTask("TaskNodeMoveTo", Node=entity_node, Time=time, From=from_point, To=to_point, Easing=easing_type_name)

    def __runTaskChain(self):
        if GroupManager.hasGroup("LineSpeed") is False:
            return

        with TaskManager.createTaskChain(Name="Debug_Tween", Repeat=True) as tc:
            with tc.addRaceTask(2) as (tc_left, tc_right):
                tc_left.addTask("TaskMovie2ButtonClick", GroupName='LineSpeed', Movie2ButtonName="Movie2Button_Left")
                tc_left.addFunction(self.__changeCurrentTweenOnTestScene, "Prev")

                tc_right.addTask("TaskMovie2ButtonClick", GroupName='LineSpeed', Movie2ButtonName="Movie2Button_Right")
                tc_right.addFunction(self.__changeCurrentTweenOnTestScene, "Next")

    def __initTweenCheat(self):
        cheat_candidates = [("CHEAT_TEST_TWEEN_ZOOM", "ZoomTweenIn", "ZoomTweenOut"), ("CHEAT_TEST_TWEEN_TRANSITION", "TransitionTweenIn", "TransitionTweenOut"), ("CHEAT_TEST_TWEEN_PICK", "PickEffectTween", "PickEffectTween"), ]

        for cheat_candidate_desc in cheat_candidates:
            cheat_key, tween_in_default_name, tween_out_default_name = cheat_candidate_desc

            is_cheat_enable = DefaultManager.getDefault(cheat_key, False)
            if is_cheat_enable:
                self.cheat_tween_in_default_name = tween_in_default_name
                self.cheat_tween_out_default_name = tween_out_default_name

                self.cheat_tween_in_easing_type = DefaultManager.getDefault(self.cheat_tween_in_default_name, "easyLinear")

                self.cheat_tween_out_easing_type = DefaultManager.getDefault(self.cheat_tween_out_default_name, "easyLinear")

                DefaultManager.addDefault(self.cheat_tween_in_default_name, self.cheat_tween_in_easing_type)
                DefaultManager.addDefault(self.cheat_tween_out_default_name, self.cheat_tween_out_easing_type)
                break

    def _onRun(self):
        super(SystemDebugMenu, self)._onRun()
        self.__key_handler_id = Mengine.addKeyHandler(self.__onGlobalHandleKeyEvent)

        Mengine.setTextAlias(ALIAS_ENV, ALIAS_TEXT_NAME, "ID_LineSpeed")
        Mengine.setTextAliasArguments(ALIAS_ENV, ALIAS_TEXT_NAME, " ")

        self.SceneTweenIn = DefaultManager.getDefault("TransitionTweenIn", "easyLinear")
        self.SceneTweenOut = DefaultManager.getDefault("TransitionTweenOut", "easyLinear")
        self.PickTween = DefaultManager.getDefault("PickEffectTween", "easyLinear")

        self.__initTweenCheat()

        self.__runTaskChain()

        if Mengine.hasTouchpad() is True and _DEVELOPMENT is True:
            self.addObserver(Notificator.onSceneActivate, self.__onSceneActivate)

        self.initDevToDebug()

        return True

    def _onStop(self):
        super(SystemDebugMenu, self)._onStop()
        if TaskManager.existTaskChain("Debug_Tween") is True:
            TaskManager.cancelTaskChain("Debug_Tween")

        if TaskManager.existTaskChain("Debug_Tween_Move") is True:
            TaskManager.cancelTaskChain("Debug_Tween_Move")

        if self.__key_handler_id:
            Mengine.removeGlobalHandler(self.__key_handler_id)
            self.__key_handler_id = None

        if self.mobileDebugButtonNode is not None:
            self.mobileDebugButtonNode.removeFromParent()
            Mengine.destroyNode(self.mobileDebugButtonNode)
            self.mobileDebugButtonNode = None

        self.cleanDevToDebug()

    def cleanDevToDebug(self):
        if self.existTaskChain("DTD_Paragraphs_UpdateButtons"):
            self.removeTaskChain("DTD_Paragraphs_Update")

        if self.existTaskChain("DTD_Paragraphs_WaitStage"):
            self.removeTaskChain("DTD_Paragraphs_WaitStage")

        if self.existTaskChain("DTD_WaitPHs_UpdateButtons"):
            self.removeTaskChain("DTD_WaitPHs_Update")

        if self.existTaskChain("DTD_WaitPHs_WaitStage"):
            self.removeTaskChain("DTD_WaitPHs_WaitStage")

        if self.existTaskChain("DTD_WaitPHs_Recreate"):
            self.removeTaskChain("DTD_WaitPHs_Recreate")