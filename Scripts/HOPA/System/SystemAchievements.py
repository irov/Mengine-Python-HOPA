from Foundation.DefaultManager import DefaultManager
from Foundation.Notificator import Notificator
from Foundation.Providers.AchievementsProvider import AchievementsProvider
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.Systems.SystemAnalytics import SystemAnalytics
from Foundation.TaskManager import TaskManager
from Foundation.Utils import isCollectorEdition
from HOPA.AchievementManager import AchievementManager
from Notification import Notification


HOGS_HINT_ACTIONS = ['HintActionHOGItem', 'HintActionUseHOGFittingItem', 'HintActionDragDropItem']


class Achievement(object):
    """ in-game achievements (internal) """

    def __init__(self, params):
        self.name = params.name
        self.params = params
        self.task = params.task
        self.complete = False

    def setComplete(self, value):
        self.complete = value

    def isComplete(self):
        return self.complete

    def checkTaskComplete(self, steps):
        if self.task is None or self.params.steps_to_complete is None:
            return False

        if steps == self.params.steps_to_complete:
            return True
        return False

    def onStatUpdate(self, new_stat_value):
        """ when achievement's progress updated """
        if self.checkTaskComplete(new_stat_value) is True:
            Notification.notify(Notificator.onAchievementUnlocked, self.name)
            return True
        return False

    if _DEVELOPMENT is True:
        def __repr__(self):
            return "<{} {!r} [{}]>".format(self.__class__.__name__, self.name, self.complete)


class ExternalAchievement(Achievement):
    """ achievements for Apple GameCenter, Google play, etc """

    def __init__(self, params):
        super(ExternalAchievement, self).__init__(params)
        self.id = params.id
        self.task = params.task

    def increase(self, steps):
        AchievementsProvider.incrementAchievement(self.id, steps)
        return False

    def setComplete(self, value):
        if value is True:
            AchievementsProvider.unlockAchievement(self.id)
        super(ExternalAchievement, self).setComplete(value)

    def onStatUpdate(self, new_stat_value):
        """ when achievement's progress updated """
        if self.params.incremented is True:
            self.increase(1)
        if self.checkTaskComplete(new_stat_value) is True:
            Notification.notify(Notificator.onAchievementExternalUnlocked, self.id)
            return True
        return False


class SystemAchievements(System):
    s_achievements = {}
    s_external_achievements = {}

    s_stats_list = [
        "item_collect_complete_count",  # Collector
        "minigames_complete_count",  # PuzzleLover
        "hogs_complete_no_hint_count",  # ArgusEyed, Professional
        "scene_complete_no_hint_count",  # Discoverer
        # new params:
        "hint_used_count",
        "completed_locations",
        "unlocked_achievements",
        "completed_missions",
        "items_picked",
    ]

    def _onParams(self, _params):
        self.scenes_hog_hint_used = []  # ArgusEyed, Professional
        self.scenes_hint_used = []  # Discoverer

    def __createCheckMethod(self, stat_name):
        prefix = "_" + self.__class__.__name__  # access to private methods are with class name prefix
        check_fn_name = prefix + "__checkStat_{}".format(stat_name)

        __hardcode_checker = False
        if check_fn_name in dir(self):
            check_fn = self.__getattribute__(check_fn_name)
            if callable(check_fn):
                __hardcode_checker = True

        achievements_to_check = SystemAchievements.getAchievementsByTask(stat_name, not_completed=True)

        def _checkStat(self):
            # for hardcoded achievements
            if __hardcode_checker is True:
                check_fn()

            # current value of stat
            stat_value = self.__dict__[stat_name]

            # print "checkStat for {!r}. {}".format(stat_name, achievements_to_check)
            for achievement in achievements_to_check:
                if achievement.onStatUpdate(stat_value) is True:
                    achievements_to_check.remove(achievement)

        setattr(self, "_checkStat_{}".format(stat_name), _checkStat)

    def __checkEnable(self):
        ConfigAchievement = Mengine.getGameParamBool("Achievements", False)
        if ConfigAchievement is True:
            return True

        if isCollectorEdition() is False:
            return False

        return True

    def _onInitialize(self):
        self._addAnalytics()

    def _onRun(self):
        if self.__checkEnable() is False:
            return True

        self._createAchievements()
        for stat_name in SystemAchievements.s_stats_list:
            self.__dict__[stat_name] = 0
            self.__createCheckMethod(stat_name)

        self._setObservers()

        self._runCheats()
        self.__addDevToDebug()

        return True

    def _onFinalize(self):
        # fixme: if we add, then remove, then add - got error:
        #    DevToDebugService::onHttpRequestComplete[507] [DevToDebug] Connect response error:  data:
        #    {"detail":{"exception":"WidgetNotExist","descriptions":["Widget 'stat_item_collect_complete_count'
        #    not exist"],"details":{"path":["tabs","Achievements","widgets"],"index":"0"}}} [code 400] [id 15729]
        pass  # self.__remDevToDebug()

    def _setObservers(self):
        self.addObserver(Notificator.onAchievementUnlocked, self._cbAchievementUnlocked)
        self.addObserver(Notificator.onAchievementExternalUnlocked, self._cbAchievementExternalUnlocked)
        self.addObserver(Notificator.onAchievementProgress, self._cbAchievementProgress)

        self.addObserver(Notificator.onFinishItemCollect, self.__cbFinishItemCollect)  # Collector
        self.addObserver(Notificator.onHintClick, self.__cbHintClick)  # ArgusEyed/Professional, Discoverer
        self.addObserver(Notificator.onEnigmaComplete, self.__cbEnigmaComplete)  # ArgusEyed/Professional, PuzzleLover/JigsawPuzzle
        self.addObserver(Notificator.onHOGDragDropComplete, self.__HOGComplete)  # ArgusEyed/Professional
        self.addObserver(Notificator.onLocationComplete, self._cbLocationComplete)  # Discoverer

        self.addObserver(Notificator.onTasksClose, self._cbTaskClose)
        self.addObserver(Notificator.onInventoryAppendInventoryItem, self._cbItemPick)

    # Achievement Progress observer

    def _cbAchievementProgress(self, stat_name, value):
        """ increase achievement progress
            if stat is list: *value* would append to stat
            elif stat is numeric: stat """

        if stat_name not in self.__dict__:
            if _DEVELOPMENT is True:
                Trace.log("System", 0, "SystemAchievements: Not found initial stat {!r}, available is: {}".format(stat_name, self.s_stats_list))
            self.__dict__[stat_name] = 0

        self.__dict__[stat_name] += value
        if _DEVELOPMENT is True:
            Trace.msg("<SystemAchievements> increase {!r} by {}. Current={}".format(stat_name, value, self.__dict__[stat_name]))

        # here we call AchievementUnlock if it needed
        check_fn_name = "_checkStat_{}".format(stat_name)
        if check_fn_name not in dir(self):
            # we never call achievementUnlock for this param, coz we haven't method for it
            if _DEVELOPMENT is True:
                Trace.msg_err("SystemAchievement: no reaction on change achievement progress {!r}. Create method {}".format(stat_name, check_fn_name))
            return False

        check_fn = self.__getattribute__(check_fn_name)
        if callable(check_fn):
            check_fn(self)

        return False

    # --- HARDCODE achievements progress -------------------------------------------------------------------------------

    def __doHardcodeAchievementProgress(self, stat, achievement_name):
        achievement = SystemAchievements.getAchievement(achievement_name)
        if achievement is None:
            return

        steps_to_complete = achievement.params.steps_to_complete

        if self.__dict__.get(stat, 0) == steps_to_complete:
            Notification.notify(Notificator.onAchievementUnlocked, achievement_name)

    def __checkStat_item_collect_complete_count(self):
        self.__doHardcodeAchievementProgress("item_collect_complete_count", "Collector")

    def __checkStat_minigames_complete_count(self):
        self.__doHardcodeAchievementProgress("minigames_complete_count", "JigsawPuzzle")

    def __checkStat_hogs_complete_no_hint_count(self):
        achievements = ["ArgusEyed", "Professional"]
        for achieve_name in achievements:
            self.__doHardcodeAchievementProgress("hogs_complete_no_hint_count", achieve_name)

    def __checkStat_scene_complete_no_hint_count(self):
        self.__doHardcodeAchievementProgress("scene_complete_no_hint_count", "Discoverer")

    # --- Achievement unlock -------------------------------------------------------------------------------------------

    def _cbAchievementExternalUnlocked(self, achievement_id):
        achievement = SystemAchievements.getExternalAchievement(achieve_id=achievement_id)
        if achievement is None:
            Trace.log("Manager", 0, "SystemAchievement has no external achievement with id: '%s'" % achievement_id)
            return False

        achievement.setComplete(True)
        if _DEVELOPMENT:
            Trace.msg("<SystemAchievements> external achieve {!r} [{}] is complete!".format(achievement_id, achievement.name))

        return False

    def _cbAchievementUnlocked(self, achievement_name):
        achievement = SystemAchievements.getAchievement(achievement_name)
        if achievement is None:
            Trace.log("Manager", 0, "SystemAchievement has no achievement with name: \"%s\"" % achievement_name)
            return False

        # check is achievement was unlocked earlier - show or not unlock notification to user
        was_unlocked = achievement.isComplete()
        # actual name (has basic name as well)
        actual_achievement_name = achievement.name

        achievement.setComplete(True)

        external_achievement = self.getExternalAchievement(achieve_name=actual_achievement_name)
        if external_achievement is not None:
            Notification.notify(Notificator.onAchievementExternalUnlocked, external_achievement.id)

        if any([was_unlocked is False,  # it is first time unlock
                DefaultManager.getDefaultBool("ShowAlreadyCompletedAchievementsNotify", False) is True]):
            Notification.notify(Notificator.onAddAchievementPlateToQueue, 'Achievements', actual_achievement_name)
        self.__sendAchievementToSteam(achievement)

        Notification.notify(Notificator.onAchievementProgress, "unlocked_achievements", 1)
        if _DEVELOPMENT:
            Trace.msg("<SystemAchievements> {} is complete!".format(actual_achievement_name))

        return False

    def __sendAchievementToSteam(self, achievement):
        if Mengine.isAvailablePlugin("Steam") is True:
            Mengine.steamSetAchievement(achievement.params.steam_value)

    # ------------------------------------------------------------------------------------------------------------------

    def _createAchievements(self):
        SystemAchievements.s_achievements = {}
        achievements_params = AchievementManager.getAchievementsParams()
        self.__createAchievements(achievements_params, Achievement, SystemAchievements.s_achievements)

        if AchievementsProvider.hasProvider() is False:
            return

        service = AchievementsProvider.getName()

        SystemAchievements.s_external_achievements = {}
        external_achievements_params = AchievementManager.getExternalAchievementsParamsByService(service)
        self.__createAchievements(external_achievements_params, ExternalAchievement,
                                  SystemAchievements.s_external_achievements)

    @staticmethod
    def __createAchievements(achievements_params, _type, _dict):
        for params in achievements_params.values():
            achievement = _type(params)
            _dict[params.name] = achievement

            task = achievement.task
            if task is not None and task not in SystemAchievements.s_stats_list:
                SystemAchievements.s_stats_list.append(task)

    @staticmethod
    def hasAchievement(name):
        return name in SystemAchievements.s_achievements

    @staticmethod
    def hasExternalAchievement(achieve_id=None, achieve_name=None):
        for achievement in SystemAchievements.s_external_achievements.values():
            if achieve_id is not None and achieve_id == achievement.id:
                return True
            elif achieve_name is not None and achieve_name == achievement.name:
                return True
        return False

    @staticmethod
    def getAchievements():
        return SystemAchievements.s_achievements

    @staticmethod
    def getExternalAchievements():
        return SystemAchievements.s_external_achievements

    @staticmethod
    def getAchievement(name):
        achievement = None
        for key in SystemAchievements.s_achievements.iterkeys():
            value = SystemAchievements.s_achievements.get(key, None)
            if value.params.basic_name == name:
                achievement = value
                break
        if achievement is None:
            achievement = SystemAchievements.s_achievements.get(name, None)
        return achievement

    @staticmethod
    def getExternalAchievement(achieve_id=None, achieve_name=None):
        for achievement in SystemAchievements.s_external_achievements.values():
            if achieve_id is not None and achieve_id == achievement.id:
                return achievement
            elif achieve_name is not None and achieve_name == achievement.name:
                return achievement

    @staticmethod
    def getAchievementsByTask(task_name, not_completed=False):
        def _filter(achieve):
            if achieve.task != task_name:
                return False
            if not_completed is True and achieve.isComplete() is True:
                return False
            return True

        external_achieves = filter(_filter, SystemAchievements.s_external_achievements.values())
        internal_achieves = filter(_filter, SystemAchievements.s_achievements.values())
        achievements = external_achieves + internal_achieves

        return achievements

    # --- observers ----------------------------------------------------------------------------------------------------

    def __cbHintClick(self, hint_demon, *_, **__):
        hint_activated_scene = SceneManager.getCurrentGameSceneName()

        hint_entity = hint_demon.getEntity()
        if hint_entity.currentHint is None:
            return False

        current_hint_action_type = hint_entity.currentHint.getType()
        if current_hint_action_type is 'HintActionDummy':
            return False

        Notification.notify(Notificator.onAchievementProgress, "hint_used_count", 1)

        if current_hint_action_type in HOGS_HINT_ACTIONS:
            if hint_activated_scene not in self.scenes_hog_hint_used:
                self.scenes_hog_hint_used.append(hint_activated_scene)

        if hint_activated_scene not in self.scenes_hint_used:
            self.scenes_hint_used.append(hint_activated_scene)
        return False

    def __cbFinishItemCollect(self, *_args, **_kwargs):  # Collector
        Notification.notify(Notificator.onAchievementProgress, "item_collect_complete_count", 1)

        return False

    def __HOGComplete(self):
        # in case if func is callback onHOGDragDropComplete some returns is False

        hog_scene_name = Mengine.getCurrentScene().getName()
        if hog_scene_name in self.scenes_hog_hint_used:
            return False

        Notification.notify(Notificator.onAchievementProgress, "hogs_complete_no_hint_count", 1)

        return False

    def __minigameComplete(self):  # PuzzleLover/JigsawPuzzle
        Notification.notify(Notificator.onAchievementProgress, "minigames_complete_count", 1)

    def __cbEnigmaComplete(self, enigma_object, *_args, **_kwargs):
        enigma_entity = enigma_object.getEntity()
        if enigma_entity.isSkipped() is True:
            if _DEVELOPMENT is False:
                return False
            else:
                Trace.msg("<SystemAchievements> enigma was skipped, but for dev ignore this")
        if enigma_entity.isMiniHOG is True:  # skip HOG2, HOG
            return False

        if enigma_entity.isHOG is True:
            self.__HOGComplete()
        else:
            self.__minigameComplete()

        return False

    def _cbLocationComplete(self, completedLocationName):  # Discoverer
        Notification.notify(Notificator.onAchievementProgress, "completed_locations", 1)

        if completedLocationName in self.scenes_hint_used:
            return False

        Notification.notify(Notificator.onAchievementProgress, "scene_complete_no_hint_count", 1)

        return False

    def _cbTaskClose(self, NoteID):
        Notification.notify(Notificator.onAchievementProgress, "completed_missions", 1)
        return False

    def _cbItemPick(self, *args):
        Notification.notify(Notificator.onAchievementProgress, "items_picked", 1)
        return False

    # --- load\save ----------------------------------------------------------------------------------------------------

    def _onSave(self):
        if self.__checkEnable() is False:
            return {}

        save_data = {
            'system_params': [  # old params, DO NOT change order - it destroys old user's saves
                self.item_collect_complete_count, self.minigames_complete_count, self.scenes_hog_hint_used,
                self.hogs_complete_no_hint_count, self.scenes_hint_used, self.scene_complete_no_hint_count, ],
            'new_params': {  # check `s_stats_list`, first 4 stats - old and saves in prev `system_params` list
                stat: self.__dict__[stat] for stat in SystemAchievements.s_stats_list[4:]
            },
            # achievements list saves only names or id to identify completed
            'achievements_params': [],
            'external_achievements_params': []
        }

        for achievement in SystemAchievements.getAchievements().itervalues():
            if achievement.isComplete():
                save_data['achievements_params'].append(achievement.name)
                self.__sendAchievementToSteam(achievement)

        for achievement in SystemAchievements.getExternalAchievements().values():
            if achievement.isComplete():
                save_data['external_achievements_params'].append(achievement.id)

        return save_data

    def __loadDeprecatedUseSomething(self, trash):
        """ deprecated load support (`trash` could be int (0) or dict {Achievement_name: value}) """

        if isinstance(trash, dict) is False:
            return

        rune_use_achieves = {
            "Lamplighter": "light_rune_use",
            "Firestarter": "fire_rune_use",
            "Artisan": "reduction_rune_use",
            "Freeze master": "ice_rune_use"
        }
        for achieve_name, value in trash.items():
            stat = rune_use_achieves[achieve_name]
            self.__dict__[stat] = value

    def _onLoad(self, save_data):
        if "system_params" not in save_data:
            # probably not CE version, but if we enable CE - prev save is empty, so we return and wait for new save
            return

        # old stats, DO NOT change order - DON'T DO SAVES WITH LIST !!!!
        self.item_collect_complete_count, \
            self.minigames_complete_count, \
            self.scenes_hog_hint_used, \
            self.hogs_complete_no_hint_count, \
            self.scenes_hint_used, \
            self.scene_complete_no_hint_count = save_data['system_params']

        new_params = save_data.get("new_params", {})
        for stat, value in new_params.items():
            if stat == "use_something":
                self.__loadDeprecatedUseSomething(value)
                continue
            self.__dict__[stat] = value

        # Achievements complete loader

        for name, achievement in SystemAchievements.getAchievements().iteritems():
            if name in save_data['achievements_params']:
                achievement.setComplete(True)
                self.__sendAchievementToSteam(achievement)
            else:
                achievement.setComplete(False)

        external_achievements_params = save_data.get('external_achievements_params', [])
        for id_, achievement in SystemAchievements.getExternalAchievements().iteritems():
            if id_ in external_achievements_params:
                achievement.setComplete(True)

    # --- DevToDebug & Cheats ------------------------------------------------------------------------------------------

    @staticmethod
    def __cheatCompleteRandomAchievement():
        not_completed = []
        for achievement in SystemAchievements.s_achievements.values():
            if not achievement.complete:
                not_completed.append(achievement)

        if len(not_completed) == 0:
            return

        achievement = not_completed[Mengine.range_rand(0, len(not_completed))]
        Notification.notify(Notificator.onAchievementUnlocked, achievement.name)

    def _runCheats(self):
        if _DEVELOPMENT is False:
            return

        def _checkEditBox():
            if SystemManager.hasSystem("SystemEditBox"):
                system_edit_box = SystemManager.getSystem("SystemEditBox")
                if system_edit_box.hasActiveEditbox():
                    return False
            return True

        with self.createTaskChain("CompleteRandAchievement", Repeat=True) as tc:
            tc.addTask('TaskKeyPress', Keys=[DefaultManager.getDefaultKey("DevDebugCompleteRandAchievement", 'VK_L')])
            with tc.addIfTask(_checkEditBox) as (tc_true, _):
                tc_true.addFunction(self.__cheatCompleteRandomAchievement)

    def _addAnalytics(self):
        SystemAnalytics.addSpecificAnalytic("unlock_achievement", "unlock_external_achievement",
                                            Notificator.onAchievementExternalUnlocked, None,
                                            lambda achieve_id: {'achievement_id': achieve_id})

    def __addDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return
        if Mengine.hasDevToDebugTab("Achievements") is True:
            return

        tab = Mengine.addDevToDebugTab("Achievements")

        # Stats:

        w_stats = Mengine.createDevToDebugWidgetText("stats")
        w_stats.setText("## Stats")
        tab.addWidget(w_stats)

        w_stats_descr = Mengine.createDevToDebugWidgetText("stats_descr")
        w_stats_descr.setText("Click to stat buttons to increase their values by 1")
        tab.addWidget(w_stats_descr)

        def _stat(key):
            count = self.__dict__.get(key)
            return "{} [{}]".format(key, count)

        _buttons = []
        for stat_key in SystemAchievements.s_stats_list:
            w_stat = Mengine.createDevToDebugWidgetButton("stat_{}".format(stat_key))
            w_stat.setTitle(_stat, stat_key)
            w_stat.setClickEvent(Notification.notify, Notificator.onAchievementProgress, stat_key, 1)
            tab.addWidget(w_stat)

        # Achievements

        details = {
            "internal": SystemAchievements.s_achievements.values(),
            "external": SystemAchievements.s_external_achievements.values(),
        }

        def _title(achievement):
            name = achievement.name
            completed = "COMPLETED" if achievement.isComplete() else "IN PROGRESS"
            external_id = achievement.__dict__.get("id", "")
            return " * `{}` ({}".format(name, completed) + (", `{}`".format(external_id) if external_id else "") + ")"

        def _complete(widget, achievement):
            if isinstance(achievement, Achievement):
                Notification.notify(Notificator.onAchievementUnlocked, achievement.name)
            elif isinstance(achievement, ExternalAchievement):
                Notification.notify(Notificator.onAchievementExternalUnlocked, achievement.id)
            widget.setHide(True)

        def _increase(widget, achievement):
            achievement.increase(1)
            if achievement.isComplete():
                widget.setHide(True)

        for key, achievements in details.items():
            if len(achievements) == 0:
                continue

            w_title = Mengine.createDevToDebugWidgetText("title_{}".format(key))
            w_title.setText("---\n## {}".format(key.title()))
            tab.addWidget(w_title)

            for achievement in achievements:
                id_name = achievement.name.replace(" ", "_")

                # achievement text name
                w_name = Mengine.createDevToDebugWidgetText("{}_{}_name".format(key, id_name))
                w_name.setText(_title, achievement)
                tab.addWidget(w_name)

                if achievement.isComplete() is True:
                    continue

                # complete achieve
                w_complete = Mengine.createDevToDebugWidgetButton("{}_{}_complete".format(key, id_name))
                w_complete.setTitle("Complete")
                w_complete.setClickEvent(_complete, w_complete, achievement)
                tab.addWidget(w_complete)

                if isinstance(achievement, ExternalAchievement) is False:
                    continue

                # increase external
                w_increase = Mengine.createDevToDebugWidgetButton("{}_{}_increase".format(key, id_name))
                w_increase.setTitle("Increase by 1")
                w_increase.setClickEvent(_increase, w_increase, achievement)
                tab.addWidget(w_increase)

    def __remDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return

        if Mengine.hasDevToDebugTab("Achievements"):
            Mengine.removeDevToDebugTab("Achievements")
