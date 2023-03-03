from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from Foundation.Systems.SystemAnalytics import SystemAnalytics as SystemAnalyticsBase
from HOPA.EnigmaManager import EnigmaManager
from HOPA.System.SystemItemPlusScene import SystemItemPlusScene
from HOPA.ZoomManager import ZoomManager


class SystemAnalytics(SystemAnalyticsBase):

    def _onParams(self, params):
        self.unlocked_scenes = []
        self.unlocked_zooms = []
        self.unlocked_enigmas = []
        self.used_paragraphs = []
        self.start_game_timestamp = None

    def _onInitialize(self):
        super(SystemAnalytics, self)._onInitialize()

        def _getExtraParams():
            params = {
                "current_scene": str(SceneManager.getCurrentSceneName()),
                "previous_scene": str(SceneManager.getPrevSceneName()),
                "current_zoom": str(ZoomManager.getZoomOpenGroupName())
            }
            return params

        self.addExtraAnalyticParams(_getExtraParams)
        self._addIgnoreLogList()

    def _onRun(self):
        def _cb(arg, attr, getter):
            save = getter(arg)
            if save not in self.__dict__[attr]:
                self.__dict__[attr].append(save)
            return False

        self.addObserver(Notificator.onEnigmaPlay, _cb, "unlocked_enigmas",
                         lambda enigma: enigma.getParam("EnigmaName"))
        self.addObserver(Notificator.onSceneEnter, _cb, "unlocked_scenes", lambda scene_name: scene_name)
        self.addObserver(Notificator.onZoomOpen, _cb, "unlocked_zooms", lambda group_name: group_name)
        self.addObserver(Notificator.onParagraphComplete, _cb, "used_paragraphs", lambda paragraph_id: paragraph_id)

        return True

    def _onSave(self):
        if self.start_game_timestamp is None:
            self.start_game_timestamp = Mengine.getTime()

        save = {
            "unlocked_enigmas": self.unlocked_enigmas,
            "unlocked_scenes": self.unlocked_scenes,
            "unlocked_zooms": self.unlocked_zooms,
            "used_paragraphs": self.used_paragraphs,
            "start_game_timestamp": self.start_game_timestamp,
        }
        return save

    def _onLoad(self, save):
        self.unlocked_enigmas = save.get("unlocked_enigmas", [])
        self.unlocked_scenes = save.get("unlocked_scenes", [])
        self.unlocked_zooms = save.get("unlocked_zooms", [])
        self.used_paragraphs = save.get("used_paragraphs", [])
        self.start_game_timestamp = save.get("start_game_timestamp", Mengine.getTime())

    def __getCurrentEnigmaName(self):
        scene_name = SystemItemPlusScene.getOpenItemPlusName() or SceneManager.getCurrentSceneName()
        enigma_name = EnigmaManager.getSceneActiveEnigmaName(scene_name)
        return str(enigma_name)

    def __getPlayedMinutes(self):
        if self.start_game_timestamp is None:
            self.start_game_timestamp = Mengine.getTime()

        played_seconds = Mengine.getTime() - self.start_game_timestamp
        played_minutes = round(played_seconds / 60.0, 2)
        return played_minutes

    def addDefaultAnalytics(self):
        super(SystemAnalytics, self).addDefaultAnalytics()

        # key: [identity, check_method, params_method]
        default_analytics = {
            # mini-games ---------
            "enigma_start":
                [Notificator.onEnigmaPlay,
                    lambda enigma: enigma.getParam("EnigmaName") not in self.unlocked_enigmas,
                    lambda enigma: {"name": enigma.getParam("EnigmaName")}],
            "enigma_reset":
                [Notificator.onEnigmaReset, None,
                    lambda: {"name": self.__getCurrentEnigmaName()}],
            "enigma_skip":
                [Notificator.onEnigmaSkip, None,
                    lambda: {"name": self.__getCurrentEnigmaName()}],
            "enigma_complete":
                [Notificator.onEnigmaComplete, None,
                    lambda enigma: {"name": enigma.getParam("EnigmaName")}],
            "complete_HO":
                [Notificator.onHOGDragDropComplete, None,
                    lambda: {"name": str(SceneManager.getCurrentSceneName())}],
            # items --------------
            "item_pick":
                [Notificator.onInventoryAppendInventoryItem, None,
                    lambda item: {"name": item.getName()}],
            "item_use":
                [Notificator.onInventoryItemTake, None,
                    lambda item: {"name": item.getName()}],
            "item_invalid_use":
                [Notificator.onInventoryItemInvalidUse, None,
                    lambda item, obj: {"name": item.getName(), "invalid_object": obj.getName()}],
            # paragraphs ---------
            "paragraph_start":
                [Notificator.onParagraphRun,
                    lambda paragraph_id: paragraph_id not in self.used_paragraphs,
                    lambda paragraph_id: {"name": paragraph_id}],
            "paragraph_complete":
                [Notificator.onParagraphComplete,
                    lambda paragraph_id: paragraph_id not in self.used_paragraphs,
                    lambda paragraph_id: {"name": paragraph_id}],
            # other -------------
            "store_first_visit":
                [Notificator.onSceneEnter,
                    lambda scene_name: scene_name == "Store" and scene_name not in self.unlocked_scenes,
                    lambda scene_name: {"name": scene_name, "played_minutes": self.__getPlayedMinutes()}],
            "scene_first_visit":
                [Notificator.onSceneEnter,
                    lambda scene_name: scene_name is not None and scene_name not in self.unlocked_scenes,
                    lambda scene_name: {"name": scene_name, "played_minutes": self.__getPlayedMinutes()}],
            "zoom_first_visit":
                [Notificator.onZoomOpen,
                    lambda group_name: group_name is not None and group_name not in self.unlocked_zooms,
                    lambda group_name: {"name": group_name, "played_minutes": self.__getPlayedMinutes()}],
            "open_store":
                [Notificator.onSceneEnter,
                    lambda scene_name: scene_name == "Store", lambda *_, **__: {}],
            "complete_game":
                [Notificator.onGameComplete, None,
                    lambda *_, **__: {"played_minutes": self.__getPlayedMinutes()}],
            "complete_location":
                [Notificator.onLocationComplete, None,
                    lambda scene_name: {"name": scene_name, "played_minutes": self.__getPlayedMinutes()}],
            "seen_cutscene":
                [Notificator.onCutScenePlay, None,
                    lambda cut_scene_name, _: {"name": cut_scene_name}], }

        if DemonManager.hasDemon("Hint"):
            hint = DemonManager.getDemon("Hint")
            hint_human_actions = {
                hint.ACTION_EMPTY_USE: "EMPTY_USE",
                hint.ACTION_REGULAR_USE: "REGULAR_USE",
                hint.ACTION_MIND_USE: "MIND_USE",
                hint.ACTION_NO_RELOAD_USE: "NO_RELOAD_USE",
            }
            default_analytics["hint_click"] = [
                Notificator.onHintClick, None, lambda _, valid, action_id: {
                    "valid": valid, "action": hint_human_actions.get(action_id, action_id)
                }]

        for event_key, (identity, check_method, params_method) in default_analytics.items():
            self.addAnalytic(event_key, identity, check_method=check_method, params_method=params_method)

    def _addIgnoreLogList(self):
        ignore_list = ["paragraph_start", "paragraph_complete"]
        for event_key in ignore_list:
            self.addIgnoreLogEventKey(event_key)
