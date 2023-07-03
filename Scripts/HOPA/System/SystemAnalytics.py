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
        self.last_fixed_timestamp = None
        self._total_played_minutes = 0.0

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

        if self.last_fixed_timestamp is None:
            self.last_fixed_timestamp = Mengine.getTime()

    def _onRun(self):
        def _cb(arg, attr, getter):
            save = getter(arg)
            if save not in self.__dict__[attr]:
                self.__dict__[attr].append(save)
            return False

        self.addObserver(Notificator.onEnigmaPlay, _cb, "unlocked_enigmas",
                         lambda enigma: enigma.getParam("EnigmaName"))

        return True

    def _onSave(self):
        save = {
            "unlocked_enigmas": self.unlocked_enigmas,
            "total_played_minutes": self.__getPlayedMinutes(),
        }
        return save

    def _onLoad(self, save):
        self.unlocked_enigmas = save.get("unlocked_enigmas", [])
        self._total_played_minutes = save.get("total_played_minutes", 0.0)

    def __getCurrentEnigmaName(self):
        scene_name = SystemItemPlusScene.getOpenItemPlusName() or SceneManager.getCurrentSceneName()
        enigma_name = EnigmaManager.getSceneActiveEnigmaName(scene_name)
        return str(enigma_name)

    def __updateTotalPlayedMinutes(self):
        if self.last_fixed_timestamp is None:
            self.last_fixed_timestamp = Mengine.getTime()

        played_seconds = Mengine.getTime() - self.last_fixed_timestamp
        played_minutes = played_seconds / 60.0
        self._total_played_minutes += played_minutes

        self.last_fixed_timestamp = Mengine.getTime()

    def __getPlayedMinutes(self):
        self.__updateTotalPlayedMinutes()
        return round(self._total_played_minutes, 2)

    def addDefaultAnalytics(self):
        super(SystemAnalytics, self).addDefaultAnalytics()

        # key: [identity, check_method, params_method]
        default_analytics = {
            # mini-games
            "enigma_start":
                [Notificator.onEnigmaPlay,
                    lambda enigma: enigma.getParam("EnigmaName") not in self.unlocked_enigmas,
                    lambda enigma: {"name": enigma.getParam("EnigmaName")}],
            "enigma_reset":
                [Notificator.onEnigmaReset, None, lambda: {"name": self.__getCurrentEnigmaName()}],
            "enigma_skip":
                [Notificator.onEnigmaSkip, None, lambda: {"name": self.__getCurrentEnigmaName()}],
            "enigma_complete":
                [Notificator.onEnigmaComplete, None, lambda enigma: {"name": enigma.getParam("EnigmaName")}],
            # other
            "complete_game":
                [Notificator.onGameComplete, None, lambda *_, **__: {"played_minutes": self.__getPlayedMinutes()}],
            "complete_location":
                [Notificator.onLocationComplete, None,
                    lambda scene_name: {"name": scene_name, "played_minutes": self.__getPlayedMinutes()}],
            # cutscene
            "cutscene_start":
                [Notificator.onCutSceneStart, None, lambda name: {"name": name}],
            "cutscene_skip":
                [Notificator.onCutSceneSkip, None, lambda name: {"name": name}],
            "cutscene_complete":
                [Notificator.onCutSceneComplete, None, lambda name: {"name": name}],
        }

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

        if SceneManager.hasScene("Store"):
            default_analytics["open_store"] = [Notificator.onSceneEnter,
                lambda scene_name: scene_name == "Store", lambda *_, **__: {}]
            default_analytics["store_first_visit"] = [Notificator.onSceneEnter,
                lambda scene_name: scene_name == "Store" and scene_name not in self.unlocked_scenes,
                lambda scene_name: {"name": scene_name, "played_minutes": self.__getPlayedMinutes()}]

        for event_key, (identity, check_method, params_method) in default_analytics.items():
            self.addAnalytic(event_key, identity, check_method=check_method, params_method=params_method)

    def _addIgnoreLogList(self):
        ignore_list = ["paragraph_start", "paragraph_complete"]
        for event_key in ignore_list:
            self.addIgnoreLogEventKey(event_key)
