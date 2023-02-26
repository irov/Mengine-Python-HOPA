from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from HOPA.ItemManager import ItemManager
from HOPA.QuestManager import QuestManager
from HOPA.SpellsManager import SpellsManager, SPELLS_UI_DEMON_NAME, SPELL_AMULET_TYPE
from HOPA.ZoomManager import ZoomManager
from Notification import Notification

ERROR_MSG_PARAM_DEMON_404 = 'SpellsManager Not founded Demon param for Spell UI button: {}'
ERROR_MSG_SPELL_AMULET_NO_ACTIVE_USE_POWER_QUEST = 'SystemSpell has not found any quest "SpellAmuletUsePower" but amulet somehow is opened'

# receive from entity SpellsUI
NOTIFICATOR_onSpellUISpellButtonClick = Notificator.onSpellUISpellButtonClick

# receive from macro MacroSpellsUnlockSpell
NOTIFICATOR_onSpellUISpellUnlock = Notificator.onSpellUISpellUnlock

# receive from macro MacroSpellsLockSpell
NOTIFICATOR_onSpellUISpellLock = Notificator.onSpellUISpellLock

# receive from macros MacroSpellAmuletAddPower, MacroSpellAmuletUnblockPower,
#                       MacroSpellAmuletRemovePower,  MacroSpellAmuletUsePower, SystemSpells.__cbSpellAmuletButtonClick
NOTIFICATOR_onSpellUISpellUpdate = Notificator.onSpellUISpellUpdate

# receive from entity SpellAmulet
NOTIFICATOR_onSpellAmuletButtonClick = Notificator.onSpellAmuletButtonClick

# receive from macro MacroSpellAmuletAddPower
NOTIFICATOR_onSpellAmuletAddPower = Notificator.onSpellAmuletAddPower

# receive from macro MacroSpellAmuletRemovePower
NOTIFICATOR_onSpellAmuletRemovePower = Notificator.onSpellAmuletRemovePower

# receive from macro MacroSpellAmuletUsePower
NOTIFICATOR_onSpellAmuletUsePower = Notificator.onSpellAmuletUsePower

# receive from macro MacroSpellAmuletBlockPower
NOTIFICATOR_onSpellAmuletBlockPower = Notificator.onSpellAmuletBlockPower

# receive from macro  MacroSpellAmuletUnblockPower
NOTIFICATOR_onSpellAmuletUnblockPower = Notificator.onSpellAmuletUnblockPower

# send from system SystemSpells to scenario macro to complete it
NOTIFICATOR_onSpellMacroComplete = Notificator.onSpellMacroComplete

# send from system SystemSpells to SystemMind etc
NOTIFICATOR_onShowMindByID = Notificator.onShowMindByID

# resolve spellUIButton update and SpellAmuletParam.hide_amulet_on_zoom_bool
NOTIFICATOR_onZoomEnter = Notificator.onZoomEnter
NOTIFICATOR_onZoomLeave = Notificator.onZoomLeave

class SpellAmuletDefaultMinds(object):
    def __init__(self, param):
        self.param = param

    def getMindCanUse(self):
        return self.param.mind_power_can_use

    def getMindBlocked(self):
        return self.param.mind_power_blocked

    def getMindUnblocked(self):
        return self.param.mind_power_unblocked

    def getMindWrongStone(self):
        return self.param.mind_power_wrong_stone

    def getMindAddStone(self):
        return self.param.mind_add_stone

class SpellAmuletPower(object):
    def __init__(self, param):
        self.param = param
        self.used = False
        self.blocked = not param.is_unblocked

        self.quest = None

    def getUsed(self):
        return self.used

    def setUsed(self, used):
        self.used = used

    def getBlocked(self):
        return self.blocked

    def setBlocked(self, blocked):
        self.blocked = blocked

    def giveMindCanUse(self):
        mind = self.param.mind_power_can_use

        if mind is not None:
            Notification.notify(NOTIFICATOR_onShowMindByID, mind)

    def giveMindBlocked(self):
        mind = self.param.mind_power_blocked

        if mind is not None:
            Notification.notify(NOTIFICATOR_onShowMindByID, mind)

    def giveMindUnblocked(self):
        mind = self.param.mind_power_unblocked
        if mind is not None:
            Notification.notify(NOTIFICATOR_onShowMindByID, mind)

    def giveMindWrongStone(self):
        mind = self.param.mind_power_wrong_stone

        if mind is not None:
            Notification.notify(NOTIFICATOR_onShowMindByID, mind)

    def setQuest(self, quest):
        self.quest = quest

    def getQuest(self):
        return self.quest

class SpellAmuletStone(object):
    def __init__(self, param):
        self.param = param
        self.locked = not param.is_unlocked

    def getLocked(self):
        return self.locked

    def setLocked(self, locked):
        self.locked = locked

    def giveMindAdd(self):
        mind = self.param.mind_add_stone

        if mind is not None:
            Notification.notify(NOTIFICATOR_onShowMindByID, mind)

class SpellUIRune(object):
    def __init__(self, is_locked, params):
        self.is_locked = is_locked
        self.params = params

    def getParams(self):
        return self.params

class SpellUIRunesSettings(object):
    def __init__(self, ready_for_add):
        self.ready_to_add_new_rune = ready_for_add
        self.found_runes = []
        self.rune_to_use = None

    def addDefaultUnlockedRunes(self):
        for rune_name, rune_obj in SystemSpells.s_spell_ui_runes.items():
            if rune_obj.is_locked is False:
                self.addFoundRune(rune_name)

    def setRuneToUse(self, rune_name):
        self.rune_to_use = rune_name

    def getRuneToUse(self):
        return self.rune_to_use

    def getReady(self):
        return self.ready_to_add_new_rune

    def setReady(self, state):
        self.ready_to_add_new_rune = state

    def getFoundRunes(self):
        return self.found_runes

    def addFoundRune(self, rune_type):
        if len(self.found_runes) is 0:
            self.found_runes.append(rune_type)
            self.setReady(True)
        elif rune_type not in self.found_runes:
            self.found_runes.append(rune_type)
            self.setReady(True)

class SpellUIComponent(object):
    SPELLS_UI_DEMON = DemonManager.getDemon(SPELLS_UI_DEMON_NAME)
    SPELLS_UI_PARAM = SpellsManager.getSpellsUIParam()

    def __init__(self, param_ui_button, param_ui_demon):
        self.param_ui_button = param_ui_button
        self.param_ui_demon = param_ui_demon

        self.locked = not param_ui_button.is_unlocked

    @classmethod
    def getSpellsUIDemon(cls):
        return cls.SPELLS_UI_DEMON

    def getSpellDemon(self):
        return DemonManager.getDemon(self.param_ui_demon.spell_demon_name)

    def getSpellUIButton(self):
        return self.SPELLS_UI_DEMON.getSpellUIButton(self.param_ui_button.spell_type)

    def getLocked(self):
        return self.locked

    def setLocked(self, locked):
        self.locked = locked

    def giveMindUseless(self):
        mind = self.param_ui_button.mind_use_less_spell

        if mind is not None:
            Notification.notify(NOTIFICATOR_onShowMindByID, mind)

    def hasSceneActiveQuest(self):
        spell_use_quest_type = self.param_ui_button.spell_use_quest

        current_scene_name = SceneManager.getCurrentSceneName()

        group_name = ZoomManager.getZoomOpenGroupName()
        item_plus_name = ItemManager.getCurrentItemPlusName()
        # if item_plus_name is not None it means that we opne item+

        if group_name is None:
            if item_plus_name is None:
                group_name = SceneManager.getSceneMainGroupName(current_scene_name)
            else:
                group_name = item_plus_name
                current_scene_name = item_plus_name
        quests = QuestManager.getSceneQuests(current_scene_name, group_name)
        for quest in quests:
            if quest.getType() != spell_use_quest_type:
                continue

            if quest.isActive():
                return True

        return False

    def getSceneActiveQuests(self, power_type_filter=None):
        spell_use_quest_type = self.param_ui_button.spell_use_quest
        item_plus_name = ItemManager.getCurrentItemPlusName()

        if item_plus_name is None:
            current_scene_name = SceneManager.getCurrentSceneName()
        else:
            current_scene_name = item_plus_name

        group_name = ZoomManager.getZoomOpenGroupName()
        if group_name is None:
            if item_plus_name is None:
                group_name = SceneManager.getSceneMainGroupName(current_scene_name)
            else:
                group_name = item_plus_name

        quests = QuestManager.getSceneQuests(current_scene_name, group_name)
        spell_use_quests = []
        for quest in quests:
            if quest.getType() != spell_use_quest_type:
                continue

            if quest.isActive():
                if power_type_filter is not None:
                    quest_power_name = quest.params["PowerName"]
                    quest_power = SystemSpells.getSpellAmuletPower(quest_power_name)
                    quest_power_type = quest_power.param.power_type
                    if power_type_filter != quest_power_type:
                        continue

                spell_use_quests.append(quest)

        return spell_use_quests

class SystemSpells(System):
    s_dev_to_debug = False

    s_spell_ui_components = dict()
    s_spell_ui_runes_settings = None
    s_spell_ui_runes = dict()

    s_spell_amulet_stones = dict()
    s_spell_amulet_powers = dict()
    s_spell_amulet_powers_by_type = dict()
    spell_amulet_powers_default_minds = None

    '''
    Spells UI Listener _________________________________________________________________________________________________
    '''

    def __cbSpellsUICloseAmulet(self, _zoom_group=None, *arg):
        spell_ui_component_amulet = SystemSpells.getSpellUIComponent(SPELL_AMULET_TYPE)

        def __amuletCurState(isSkip, cb):
            cur_state = Amulet.getCurState()

            if cur_state == Amulet.IDLE:
                cb(isSkip, 0)
                return
            elif cur_state == Amulet.HIDE:
                cb(isSkip, 1)
                return
            else:
                cb(isSkip, 2)
                return

        with self.createTaskChain(Name=self.__cbSpellsUICloseAmulet.__name__ + str(Mengine.getTimeMs())) as tc:
            # if we have spellAmulet and it's open, close it
            if spell_ui_component_amulet is not None:
                spell_amulet_demon = spell_ui_component_amulet.getSpellDemon()
                Amulet = spell_amulet_demon.getAmulet()
                spell_amulet_param = SpellsManager.getSpellAmuletParam()

                if spell_amulet_param.hide_amulet_on_zoom_bool:
                    if Amulet is not None:
                        with tc.addSwitchTask(3, __amuletCurState) as (tc_IDLE, tc_HIDE, tc_OPEN):
                            tc_IDLE.addScope(spell_amulet_demon.scopeCloseAmulet)

                            tc_OPEN.addListener(Amulet.NOTIFICATOR_AmuletStateChange, lambda state: state is Amulet.OPEN)
                            tc_OPEN.addScope(spell_amulet_demon.scopeCloseAmulet)

                            tc_HIDE.addDummy()

            # update spell_ui spell_amulet_button:
            tc.addNotify(NOTIFICATOR_onSpellUISpellUpdate, SPELL_AMULET_TYPE, updateStatePlay=False)

        return False

    def __cbSpellUISpellButtonClick(self, spell_type, _spell_state):
        # '__cbSpellUiSpellButtonClick args:', spell_type, _spell_state

        spell_ui_component = SystemSpells.getSpellUIComponent(spell_type)

        # block spell usage if spell is locked
        if spell_ui_component.getLocked() is True:
            return False

        spell_ui_button = spell_ui_component.getSpellUIButton()
        spell_demon = spell_ui_component.getSpellDemon()

        if spell_ui_component.hasSceneActiveQuest():
            # CASE: CAN USE SPELL //////////////////////////////////////////////////////////////////////////////////////
            with self.createTaskChain(Name=self.__cbSpellUISpellButtonClick.__name__ + str(Mengine.getTimeMs())) as tc:
                with tc.addParallelTask(2) as (parallel_0, parallel_1):
                    if spell_ui_button is not None:  # check
                        with parallel_0.addIfTask(lambda spell_ui_comp_: spell_ui_comp_.getSpellUIButton() is not None, spell_ui_component) as (true, _):
                            true.addFunction(spell_ui_button.changeState, spell_ui_button.USE)
                            true.addScope(spell_ui_button.scopePlayCurState)
                            true.addFunction(spell_ui_button.changeState, spell_ui_button.READY, play=True, loop=True)
                            true.addScope(self.updateSpellAmuletStoneState, spell_ui_component)

                    # HERE GENERAL METHOD FOR SPELL DEMON INTERFACE:
                    with GuardBlockInput(parallel_1) as guard_parallel_1:
                        guard_parallel_1.addScope(spell_demon.scopeSpellUIButtonValidClick)

                tc.addDummy()  # //////////////////////////////////////////////////////////////////////////////////////////////////////

        else:
            # CASE: CAN'T USE SPELL ////////////////////////////////////////////////////////////////////////////////////
            # if spell_demon.isActive():
            #     spell_ui_component.giveMindUseless()

            # Case: CANT'T OPEN AMULET IN MG //////////////////////////////////////////////////////////////////////////
            # active_enigma = EnigmaManager.getSceneActiveEnigma()
            # if active_enigma is not None:
            #     spell_ui_component.giveMindUseless()
            #     return False

            with self.createTaskChain(Name=self.__cbSpellUISpellButtonClick.__name__ + str(Mengine.getTimeMs())) as tc:
                with tc.addParallelTask(2) as (parallel_0, parallel_1):
                    if spell_ui_button is not None:  # check
                        with parallel_0.addIfTask(lambda spell_ui_comp_: spell_ui_comp_.getSpellUIButton() is not None, spell_ui_component) as (true, _):
                            true.addFunction(spell_ui_button.changeState, spell_ui_button.USE)
                            true.addScope(spell_ui_button.scopePlayCurState)
                            true.addFunction(spell_ui_button.changeState, spell_ui_button.IDLE, play=True, loop=True)

                    # HERE GENERAL METHOD FOR SPELL DEMON INTERFACE:
                    with GuardBlockInput(parallel_1) as guard_parallel_1:
                        guard_parallel_1.addScope(spell_demon.scopeSpellUIButtonValidClick)

            # //////////////////////////////////////////////////////////////////////////////////////////////////////////

        return False

    def __cbSpellUISpellUnlock(self, spell_type, notificator_caller):
        # print '__cbSpellUISpellUnlock args:', spell_type

        spell_ui_component = SystemSpells.getSpellUIComponent(spell_type)
        spell_ui_button = spell_ui_component.getSpellUIButton()

        spell_ui_component.setLocked(False)  # main action

        def cb(*_, **__):
            # COMPLETE MACRO COMMAND MacroSpellsUnlockSpell
            Notification.notify(NOTIFICATOR_onSpellMacroComplete, notificator_caller, spell_type)  # main action

        with self.createTaskChain(Name=self.__cbSpellUISpellUnlock.__name__ + str(Mengine.getTimeMs()), Cb=cb) as tc:
            # visual
            if spell_ui_button is not None:  # check
                with tc.addIfTask(lambda spell_ui_comp_: spell_ui_comp_.getSpellUIButton() is not None, spell_ui_component) as (true, _):
                    true.addFunction(spell_ui_button.changeState, spell_ui_button.LOCKED)
                    true.addScope(spell_ui_button.scopePlayCurState)
                    true.addFunction(spell_ui_button.changeState, spell_ui_button.IDLE)
            #
            tc.addDummy()
        return False

    def __cbSpellUISpellLock(self, spell_type, notificator_caller):
        # print '__cbSpellUISpellLock args:', spell_type

        spell_ui_component = SystemSpells.getSpellUIComponent(spell_type)
        spell_ui_button = spell_ui_component.getSpellUIButton()

        spell_ui_component.setLocked(True)  # main action

        def cb(*_, **__):
            # COMPLETE MACRO COMMAND MacroSpellsLockSpell
            Notification.notify(NOTIFICATOR_onSpellMacroComplete, notificator_caller, spell_type)  # main action

        with self.createTaskChain(Name=self.__cbSpellUISpellLock.__name__ + str(Mengine.getTimeMs()), Cb=cb) as tc:
            # visual
            if spell_ui_button is not None:  # check
                with tc.addIfTask(lambda spell_ui_comp_: spell_ui_comp_.getSpellUIButton() is not None, spell_ui_component) as (true, _):
                    true.addFunction(spell_ui_button.changeState, spell_ui_button.LOCKED, play=False, last_frame=False)
            #
            tc.addDummy()
        return False

    def __cbSpellUISpellUpdate(self, spell_type, notificator_caller, updateStatePlay=True):
        # print '__cbSpellUISpellUpdate args:', spell_type

        spell_ui_component = SystemSpells.getSpellUIComponent(spell_type)
        spell_amulet_demon = spell_ui_component.getSpellDemon()
        spell_amulet = spell_amulet_demon.getAmulet()
        spell_ui_button = spell_ui_component.getSpellUIButton()

        def cb(*_, **__):
            # COMPLETE MACRO COMMAND where we use Notificator.onSpellUISpellUpdate
            Notification.notify(NOTIFICATOR_onSpellMacroComplete, notificator_caller, spell_type)  # main action

        with self.createTaskChain(Name=self.__cbSpellUISpellUpdate.__name__ + str(Mengine.getTimeMs()), Cb=cb) as tc:
            # visual
            with tc.addRaceTask(2) as (interrupt, source):
                # if we have new update event on same spell_type, shut down previous tc
                interrupt.addListener(notificator_caller, Filter=lambda _spell_type, *_: _spell_type == spell_type)

                # update anim if spell is unlocked
                if spell_ui_component.getLocked() is False:
                    if spell_ui_button is not None:  # check
                        with source.addIfTask(lambda spell_ui_comp_: spell_ui_comp_.getSpellUIButton() is not None, spell_ui_component) as (true, _):
                            if spell_ui_component.hasSceneActiveQuest():
                                if spell_amulet.isOpen() is False:
                                    # change state only if amulet is close
                                    true.addFunction(spell_ui_button.disableAllStatesMovies)
                                    true.addFunction(spell_ui_button.changeState, spell_ui_button.READY, play=True, loop=True)
                                else:
                                    if spell_ui_button.cur_state is spell_ui_button.READY:
                                        true.addDelay(1000)  # Macro spellAmuletUsePower send notify 2 times

                                    true.addFunction(spell_ui_button.disableAllStatesMovies)
                                    true.addFunction(spell_ui_button.changeState, spell_ui_button.READY, play=True, loop=True)
                            else:
                                if spell_ui_button.cur_movie.getName() != "Movie2_SpellAmulet_idle":
                                    true.addFunction(spell_ui_button.disableAllStatesMovies)

                                if updateStatePlay:
                                    true.addFunction(spell_ui_button.changeState, spell_ui_button.UPDATE)
                                    true.addScope(spell_ui_button.scopePlayCurState)
                                if spell_ui_button.cur_movie.getName() != "Movie2_SpellAmulet_idle":
                                    true.addFunction(spell_ui_button.changeState, spell_ui_button.IDLE, play=True, loop=True)  # ----------------------IDLE socket click
            tc.addDummy()
        return False

    '''
    Spell Amulet Listeners  ____________________________________________________________________________________________
    '''

    def __cbSpellAmuletButtonClick(self, button_power_type, _button_power_state):
        # print('__cbSpellAmuletButtonClick type {}, state {}'.format(button_power_type, _button_power_state))
        item_plus_name = ItemManager.getCurrentItemPlusName()

        if item_plus_name is None:
            spell_amulet_power = SystemSpells.getSpellAmuletPowerWithActiveQuest(power_type_filter=button_power_type, scene_filter=SceneManager.getCurrentSceneName(), group_filter=ZoomManager.getZoomOpenGroupName())
        else:
            spell_amulet_power = SystemSpells.getSpellAmuletPowerWithActiveQuest(power_type_filter=button_power_type, scene_filter=item_plus_name, group_filter=item_plus_name)

        spell_ui_component = SystemSpells.getSpellUIComponent(SPELL_AMULET_TYPE)
        spell_amulet_demon = spell_ui_component.getSpellDemon()
        spell_amulet_button = spell_amulet_demon.getSpellAmuletButton(button_power_type)
        spell_amulet_stone = SystemSpells.getSpellAmuletStone(button_power_type)

        rune_submovies = spell_amulet_button.getSubmovies()
        found_runes = SystemSpells.s_spell_ui_runes_settings.getFoundRunes()

        for submovie_name, submovie in rune_submovies.items():
            if submovie_name in found_runes:
                spell_amulet_button.changeSubmovieState(True, submovie_name)
            else:
                spell_amulet_button.changeSubmovieState(False, submovie_name)

        spell_amulet_param = SpellsManager.getSpellAmuletParam()
        play_hide_amulet_after_use = spell_amulet_param.play_hide_amulet_after_use_bool

        # CASE: WRONG SPELL POWER USED /////////////////////////////////////////////////////////////////////////////////
        if len(spell_amulet_power) == 0:
            # no found quest for power use of current type, wrong power button pressed
            # find amulet power with active quest and show it's "wrong spell mind"
            # if no such, then it's bug, if active quests for amulet power use not exists we couldn't even open amulet

            spell_amulet_power = SystemSpells.getSpellAmuletPowerWithActiveQuest()

            if len(spell_amulet_power) == 0:
                if spell_amulet_button is not None and spell_amulet_demon.isActive():
                    if spell_amulet_stone.getLocked() is False:
                        default_minds = SystemSpells.getSpellAmuletPowersDefaultMinds()
                        mind = default_minds.getMindBlocked()
                        Notification.notify(NOTIFICATOR_onShowMindByID, mind)
                # Trace.log("System", 0, ERROR_MSG_SPELL_AMULET_NO_ACTIVE_USE_POWER_QUEST)
                return False

            else:
                if spell_amulet_button is not None and spell_amulet_demon.isActive():
                    if spell_amulet_stone.getLocked() is False:
                        spell_amulet_power[0].giveMindWrongStone()

            # update spell_ui spell_amulet_button
            Notification.notify(NOTIFICATOR_onSpellUISpellUpdate, SPELL_AMULET_TYPE)

        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////

        # CASE: SPELL STONE IS LOCKED //////////////////////////////////////////////////////////////////////////////////
        elif spell_amulet_stone.getLocked() is True:
            if spell_amulet_button is not None and spell_amulet_demon.isActive():
                # update spell_ui spell_amulet_button
                Notification.notify(NOTIFICATOR_onSpellUISpellUpdate, SPELL_AMULET_TYPE)

        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////

        else:
            power_use_movie_type = None
            spell_amulet_power = spell_amulet_power[0]

            # CASE: SPELL POWER IS BLOCKED /////////////////////////////////////////////////////////////////////////////
            if spell_amulet_power.getBlocked() is True:
                if spell_amulet_button is not None and spell_amulet_demon.isActive():
                    power_use_movie_type = spell_amulet_button.FAIL

            # //////////////////////////////////////////////////////////////////////////////////////////////////////////

            # CASE: USE POWER //////////////////////////////////////////////////////////////////////////////////////////
            else:
                if spell_amulet_button is not None and spell_amulet_demon.isActive():
                    power_use_movie_type = spell_amulet_button.AIM

            # //////////////////////////////////////////////////////////////////////////////////////////////////////////

            if spell_amulet_button is None:
                return False
            elif spell_amulet_button.cur_button_state in ['aim', 'select']:
                return False
            with self.createTaskChain(Name=self.__cbSpellAmuletButtonClick.__name__ + str(Mengine.getTimeMs())) as tc:
                with GuardBlockInput(tc) as guard_source:
                    with guard_source.addIfTask(lambda amulet_demon_, power_: amulet_demon_.getSpellAmuletButton(power_) is not None, spell_amulet_demon, button_power_type) as (true, _):
                        true.addFunction(spell_amulet_button.changeState, spell_amulet_button.SELECT)
                        true.addScope(spell_amulet_button.scopePlayCurState)
                        true.addFunction(spell_amulet_button.changeState, spell_amulet_button.IDLE, play=True, loop=True)

                        # play stone use
                        if power_use_movie_type is not None:
                            true.addScope(spell_amulet_button.scopePlayAmuletUse, power_use_movie_type, play_hide_amulet_after_use=play_hide_amulet_after_use)

                        if spell_amulet_power.getBlocked() is True:
                            true.addFunction(spell_amulet_power.giveMindBlocked)

                        else:
                            true.addFunction(spell_amulet_power.setUsed, True)  # main action

                            # main action
                            # COMPLETE MACRO COMMAND MacroSpellAmuletUsePower
                            true.addNotify(NOTIFICATOR_onSpellMacroComplete, NOTIFICATOR_onSpellAmuletUsePower, spell_amulet_power.param.power_name)

                            # for achievements
                            stat_name = "{}_rune_use".format(button_power_type)
                            true.addNotify(Notificator.onAchievementProgress, stat_name, 1)

                        # update spell_ui spell_amulet_button:
                        true.addNotify(NOTIFICATOR_onSpellUISpellUpdate, SPELL_AMULET_TYPE)

        return False

    def __cbSpellAmuletAddPower(self, power_type, open_amulet, close_after_open, notificator_caller):
        # print '__cbSpellAmuletAddPower args:', power_type, open_amulet
        SystemSpells.s_spell_ui_runes_settings.addFoundRune(power_type)

        spell_amulet_stone = SystemSpells.getSpellAmuletStone(power_type)

        spell_ui_component = SystemSpells.getSpellUIComponent(SPELL_AMULET_TYPE)
        spell_amulet_demon = spell_ui_component.getSpellDemon()

        amulet = spell_amulet_demon.getAmulet()
        spell_amulet_button = spell_amulet_demon.getSpellAmuletButton(power_type)

        spell_amulet_stone.setLocked(False)  # main action

        def cb(*_, **__):
            # COMPLETE MACRO COMMAND MacroSpellAmuletAddPower
            Notification.notify(NOTIFICATOR_onSpellMacroComplete, notificator_caller, power_type)  # main action

        with self.createTaskChain(Name=self.__cbSpellAmuletAddPower.__name__ + str(Mengine.getTimeMs()), Cb=cb) as tc:
            # visual
            if amulet is not None and spell_amulet_button is not None:
                with tc.addIfTask(lambda amulet_demon_, power_: amulet_demon_.getSpellAmuletButton(power_) is not None, spell_amulet_demon, power_type) as (true, _):
                    true.addFunction(spell_amulet_stone.giveMindAdd)

                    if open_amulet is True:
                        # open amulet
                        with GuardBlockInput(true) as guard_tc:
                            guard_tc.addScope(amulet.scopeOpenAmulet)

                            # update stone after amulet open

                            guard_tc.addFunction(spell_amulet_button.changeState, spell_amulet_button.APPEAR, play=False, loop=False, last_frame=False)

                            guard_tc.addScope(spell_amulet_button.scopePlayCurState)

                        true.addFunction(spell_amulet_button.changeState, spell_amulet_button.IDLE, play=True, loop=True)

                        if close_after_open is True:
                            with GuardBlockInput(true) as guard_tc:
                                guard_tc.addScope(amulet.scopeCloseAmulet)

                    else:
                        if amulet.getCurState() != amulet.HIDE:
                            true.addFunction(spell_amulet_button.changeState, spell_amulet_button.APPEAR, play=False, loop=False, last_frame=False)

                            true.addScope(spell_amulet_button.scopePlayCurState)

                            true.addFunction(spell_amulet_button.changeState, spell_amulet_button.IDLE, play=True, loop=True)

                        else:
                            true.addFunction(spell_amulet_button.changeState, spell_amulet_button.IDLE, play=True, loop=True)

            #
            tc.addDummy()
        return False

    def __cbSpellAmuletRemovePower(self, power_type, notificator_caller):
        # print '__cbSpellAmuletRemovePower args:', power_type

        spell_amulet_stone = SystemSpells.getSpellAmuletStone(power_type)

        spell_ui_component = SystemSpells.getSpellUIComponent(SPELL_AMULET_TYPE)
        spell_amulet_demon = spell_ui_component.getSpellDemon()
        spell_amulet_button = spell_amulet_demon.getSpellAmuletButton(power_type)

        spell_amulet_stone.setLocked(True)  # main action

        def cb(*_, **__):
            # COMPLETE MACRO COMMAND MacroSpellAmuletRemovePower
            Notification.notify(NOTIFICATOR_onSpellMacroComplete, notificator_caller, power_type)  # main action

        with self.createTaskChain(Name=self.__cbSpellAmuletRemovePower.__name__ + str(Mengine.getTimeMs()), Cb=cb) as tc:
            # visual
            if spell_amulet_button is not None:
                with tc.addIfTask(lambda amulet_demon_, power_: amulet_demon_.getSpellAmuletButton(power_) is not None, spell_amulet_demon, power_type) as (true, _):
                    true.addFunction(spell_amulet_button.changeState, spell_amulet_button.APPEAR, play=False, last_frame=False)
            #
            tc.addDummy()
        return False

    def __cbSpellAmuletUsePower(self, power_name, open_amulet, quest):
        spell_amulet_power = SystemSpells.getSpellAmuletPower(power_name)
        spell_ui_component = SystemSpells.getSpellUIComponent(SPELL_AMULET_TYPE)
        spell_amulet_demon = spell_ui_component.getSpellDemon()
        power_type = SystemSpells.getSpellAmuletPower(power_name).param.power_type
        # print '__cbSpellAmuletUsePower', power_name, "spell amulet power ", power_type
        SystemSpells.s_spell_ui_runes_settings.setRuneToUse(power_type)
        spell_amulet_button = spell_amulet_demon.getSpellAmuletButton(power_type)

        # main action
        spell_amulet_power.setQuest(quest)
        spell_amulet_power.setUsed(False)

        with self.createTaskChain(Name=self.__cbSpellAmuletUsePower.__name__ + str(Mengine.getTimeMs())) as tc:
            # visual
            if open_amulet is True:
                if spell_amulet_demon.isActive():
                    with tc.addIfTask(lambda demon_: demon_.isActive(), spell_amulet_demon) as (true, _):
                        true.addFunction(spell_amulet_power.giveMindCanUse)

                        # open amulet
                        with GuardBlockInput(true) as guard_tc:
                            guard_tc.addScope(spell_amulet_demon.scopeOpenAmulet)

            # play READY hint
            if spell_amulet_button.getLocked() is False:
                if spell_amulet_button.cur_button_state is spell_amulet_button.APPEAR:
                    cur_button_movie_duration = spell_amulet_button.cur_button_movie.getDuration()
                    tc.addDelay(cur_button_movie_duration + 500)
                tc.addFunction(spell_amulet_button.changeState, spell_amulet_button.READY)
                tc.addScope(spell_amulet_button.scopePlayCurState, Loop=True)

            # COMPLETE MACRO COMMAND FOR THIS CALLBACK IS RESOLVED IN __cbSpellAmuletButtonClick
            tc.addDummy()
        return False

    def __cbSpellAmuletBlockPower(self, power_name, notificator_caller):
        # print '__cbSpellAmuletBlockPower args:', power_name

        spell_amulet_power = SystemSpells.getSpellAmuletPower(power_name)
        spell_amulet_power.setBlocked(True)  # main action

        # COMPLETE MACRO COMMAND MacroSpellAmuletBlockPower
        Notification.notify(NOTIFICATOR_onSpellMacroComplete, notificator_caller, power_name)  # main action

        return False

    def __cbSpellAmuletUnblockPower(self, power_name, open_amulet, notificator_caller):
        # print '__cbSpellAmuletUnblockPower args:', power_name, open_amulet

        spell_amulet_power = SystemSpells.getSpellAmuletPower(power_name)

        spell_amulet_power.setBlocked(False)  # main action

        def cb(*_, **__):
            # COMPLETE MACRO COMMAND MacroSpellAmuletUnblockPower
            Notification.notify(NOTIFICATOR_onSpellMacroComplete, notificator_caller, power_name)  # main action

        with self.createTaskChain(Name=self.__cbSpellAmuletUnblockPower.__name__ + str(Mengine.getTimeMs()), Cb=cb) as tc:
            # visual
            if open_amulet is True:
                spell_ui_component = SystemSpells.getSpellUIComponent(SPELL_AMULET_TYPE)
                spell_amulet_demon = spell_ui_component.getSpellDemon()

                if spell_amulet_demon.isActive():
                    with tc.addIfTask(lambda demon_: demon_.isActive(), spell_amulet_demon) as (true, _):
                        true.addFunction(spell_amulet_power.giveMindUnblocked)

                        # open amulet
                        with GuardBlockInput(true) as guard_tc:
                            guard_tc.addScope(spell_amulet_demon.scopeOpenAmulet)
            #
            tc.addDummy()
        return False

    '''
    Instances Creators _________________________________________________________________________________________________
    '''

    @staticmethod
    def __createSpellAmuletPowers():
        amulet_powers = dict()
        amulet_powers_by_type = dict()

        params = SpellsManager.getSpellAmuletPowersParams()
        for power_name, param in params.items():
            spell_amulet_power = SpellAmuletPower(param)

            amulet_powers[power_name] = spell_amulet_power

            power_type = param.power_type

            if power_type not in amulet_powers_by_type:
                amulet_powers_by_type[power_type] = dict()

            amulet_powers_by_type[power_type][power_name] = spell_amulet_power

        return amulet_powers, amulet_powers_by_type

    @staticmethod
    def __createSpellAmuletPowersDefaultMinds():
        params = SpellsManager.getSpellAmuletPowerDefaultMinds()
        minds = SpellAmuletDefaultMinds(params)
        return minds

    @staticmethod
    def __createSpellAmuletStones():
        amulet_stones = dict()
        params = SpellsManager.getSpellAmuletStonesParams()
        for power_type, param in params.items():
            amulet_stones[power_type] = SpellAmuletStone(param)
        return amulet_stones

    @staticmethod
    def __createSpellUIComponents():
        ui_components = dict()

        params_ui_buttons = SpellsManager.getSpellsUIButtonsParams()

        for spell_type, param_ui_button in params_ui_buttons.items():
            params_demon = SpellsManager.getSpellsDemonParam(spell_type)

            if params_demon is None:
                Trace.log("Manager", 0, ERROR_MSG_PARAM_DEMON_404.format(spell_type))
                continue

            ui_components[spell_type] = SpellUIComponent(param_ui_button, params_demon)

        return ui_components

    @staticmethod
    def __createSpellUIRunes():
        ui_runes = dict()

        params_ui_runes = SpellsManager.getSpellsUIRunesParams()

        for rune_type, params_ui_rune in params_ui_runes.items():
            ui_runes[rune_type] = SpellUIRune(SystemSpells.s_spell_amulet_stones[rune_type].locked, params_ui_rune)

        return ui_runes
    '''
    Getters ____________________________________________________________________________________________________________
    '''
    @staticmethod
    def getSpellUIRunes():
        return SystemSpells.s_spell_ui_runes

    @staticmethod
    def getSpellUIRune(rune_type):
        return SystemSpells.s_spell_ui_runes.get(rune_type)

    @staticmethod
    def getSpellAmuletStones():
        return SystemSpells.s_spell_amulet_stones

    @staticmethod
    def getSpellAmuletStone(power_type):
        return SystemSpells.s_spell_amulet_stones.get(power_type)

    @staticmethod
    def getSpellAmuletStoneByPower(power_name):
        power = SystemSpells.getSpellAmuletPower(power_name)
        power_type = power.param.power_type
        stone = SystemSpells.getSpellAmuletStone(power_type)
        return stone

    @staticmethod
    def getSpellAmuletPowers():
        return SystemSpells.s_spell_amulet_powers

    @staticmethod
    def getSpellAmuletPower(power_name):
        return SystemSpells.s_spell_amulet_powers.get(power_name)

    @staticmethod
    def getSpellUIComponents():
        return SystemSpells.s_spell_ui_components

    @staticmethod
    def getSpellUIComponent(spell_type):
        return SystemSpells.s_spell_ui_components.get(spell_type)

    @staticmethod
    def getSpellAmuletPowersByTypes():
        return SystemSpells.s_spell_amulet_powers_by_type

    @staticmethod
    def getSpellAmuletPowerByType(power_type):
        return SystemSpells.s_spell_amulet_powers_by_type.get(power_type, {})

    @staticmethod
    def getSpellAmuletPowersDefaultMinds():
        return SystemSpells.spell_amulet_powers_default_minds

    @staticmethod
    def getSpellAmuletPowerWithActiveQuest(power_type_filter=None, scene_filter=None, group_filter=None):
        if power_type_filter is None:
            spell_amulet_powers = SystemSpells.getSpellAmuletPowers()
        else:
            spell_amulet_powers = SystemSpells.getSpellAmuletPowerByType(power_type_filter)

        if group_filter is None and scene_filter is not None:
            group_filter = SceneManager.getSceneMainGroupName(scene_filter)

        powers_with_quest = []
        for spell_amulet_power in spell_amulet_powers.values():
            quest = spell_amulet_power.getQuest()

            if quest is None:
                continue

            # probably need debug:
            if isinstance(quest, tuple):
                for q in quest:
                    if q.isActive() and not q.isComplete():
                        if scene_filter is not None and scene_filter != q.params["SceneName"]:
                            continue
                        if group_filter != q.params["GroupName"]:
                            continue
                        powers_with_quest.append(spell_amulet_power)
            else:
                if quest.isActive() and not quest.isComplete():
                    if scene_filter is not None:
                        if scene_filter == quest.params["SceneName"] and group_filter == quest.params["GroupName"]:
                            powers_with_quest.append(spell_amulet_power)
                    else:
                        powers_with_quest.append(spell_amulet_power)
        return powers_with_quest

    '''
    System _____________________________________________________________________________________________________________
    '''
    def __init__(self):
        super(SystemSpells, self).__init__()

        self.active_tcs = []

    def _onRun(self):
        SystemSpells.s_spell_ui_components = SystemSpells.__createSpellUIComponents()
        SystemSpells.s_spell_amulet_stones = SystemSpells.__createSpellAmuletStones()
        SystemSpells.s_spell_ui_runes = SystemSpells.__createSpellUIRunes()
        SystemSpells.s_spell_ui_runes_settings = SpellUIRunesSettings(False)
        SystemSpells.s_spell_ui_runes_settings.addDefaultUnlockedRunes()

        SystemSpells.s_spell_amulet_powers, SystemSpells.s_spell_amulet_powers_by_type = SystemSpells.__createSpellAmuletPowers()
        SystemSpells.spell_amulet_powers_default_minds = SystemSpells.__createSpellAmuletPowersDefaultMinds()

        '''
        observers with arg 'Notificator' has to report back for macros SpellsUI, SpellAmulet to complete macro command
        '''

        self.addObserver(NOTIFICATOR_onSpellUISpellButtonClick, self.__cbSpellUISpellButtonClick)

        self.addObserver(NOTIFICATOR_onSpellUISpellUnlock, self.__cbSpellUISpellUnlock, NOTIFICATOR_onSpellUISpellUnlock)
        self.addObserver(NOTIFICATOR_onSpellUISpellLock, self.__cbSpellUISpellLock, NOTIFICATOR_onSpellUISpellLock)
        self.addObserver(NOTIFICATOR_onSpellUISpellUpdate, self.__cbSpellUISpellUpdate, NOTIFICATOR_onSpellUISpellUpdate)

        self.addObserver(NOTIFICATOR_onSpellAmuletButtonClick, self.__cbSpellAmuletButtonClick)

        self.addObserver(NOTIFICATOR_onSpellAmuletAddPower, self.__cbSpellAmuletAddPower, NOTIFICATOR_onSpellAmuletAddPower)
        self.addObserver(NOTIFICATOR_onSpellAmuletRemovePower, self.__cbSpellAmuletRemovePower, NOTIFICATOR_onSpellAmuletRemovePower)
        self.addObserver(NOTIFICATOR_onSpellAmuletBlockPower, self.__cbSpellAmuletBlockPower, NOTIFICATOR_onSpellAmuletBlockPower)
        self.addObserver(NOTIFICATOR_onSpellAmuletUnblockPower, self.__cbSpellAmuletUnblockPower, NOTIFICATOR_onSpellAmuletUnblockPower)
        # report 'back' resolved in __cbSpellAmuletButtonClick
        self.addObserver(NOTIFICATOR_onSpellAmuletUsePower, self.__cbSpellAmuletUsePower)

        self.addObserver(NOTIFICATOR_onZoomEnter, self.__cbSpellsUICloseAmulet)
        self.addObserver(NOTIFICATOR_onZoomLeave, self.__cbSpellsUICloseAmulet)
        self.addObserver(Notificator.onInventoryPickInventoryItem, self.__cbSpellsUICloseAmulet)
        self.addObserver(Notificator.onMacroClick, self.__cbSpellsUICloseAmulet)
        self.addObserver(Notificator.onItemZoomLeaveOpenZoom, self.__cbSpellsUICloseAmulet)
        self.addObserver(Notificator.onItemZoomEnter, self.__cbSpellsUICloseAmulet)

        self.addObserver(Notificator.onSceneLeave, self.__cbOnSceneLeave)  # cancel active tcs

        if _DEVELOPMENT is True and Mengine.hasOption("cheats") is True:
            def checkEditBox():
                if SystemManager.hasSystem("SystemEditBox"):
                    system_edit_box = SystemManager.getSystem("SystemEditBox")
                    if system_edit_box.hasActiveEditbox():
                        return False
                return True

            with super(SystemSpells, self).createTaskChain("CheatsGetSpellStone", Repeat=True) as tc:
                tc.addTask('TaskKeyPress', Keys=[DefaultManager.getDefaultKey("CheatsGetSpellStone", 'VK_1')])
                with tc.addIfTask(checkEditBox) as (tc_true, _):
                    tc_true.addFunction(self.__cheatGetSpellStone)

        self.__addDevToDebug()

        return True

    def __addDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return
        if SystemSpells.s_dev_to_debug is True:
            return
        SystemSpells.s_dev_to_debug = True

        stones = SystemSpells.getSpellAmuletStones()
        has_locked_stone = True in [stone.getLocked() is True for stone in stones.values() if stone is not None]
        if has_locked_stone is False:
            return

        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")

        widget = Mengine.createDevToDebugWidgetButton("get_spellamulet_stone")
        widget.setTitle("SpellAmulet: get random rune")
        widget.setClickEvent(self.__cheatGetSpellStone)

        tab.addWidget(widget)

    def createTaskChain(self, Name, Cb=None, CbArgs=(), **Params):
        tc = super(SystemSpells, self).createTaskChain(Name, Cb, CbArgs, **Params)

        if "__cbSpellsUICloseAmulet" in Name and Mengine.hasOption("eva"):
            Trace.log("System", 0, "create tc {}".format(Name))

        # fixme: find where and why tc creates with same name and fix it
        #   https://wonderland-games.atlassian.net/browse/CAME2-1447
        if tc is None:
            msg_err = "SystemSpells createTaskChain [Name={} Cb={} CbArgs={} Params={}]".format(Name, Cb, CbArgs, Params)
            msg_err += " failed! Scene={} Zoom={} - ALREADY HAS THIS NAME".format(SceneManager.getCurrentSceneName(), ZoomManager.getZoomOpenGroupName())
            Trace.log("System", 0, msg_err)
            Name += str(Mengine.getTime())
            tc = super(SystemSpells, self).createTaskChain(Name, Cb, CbArgs, **Params)

        self.active_tcs.append(tc)

        return tc

    def __cbOnSceneLeave(self, _scene_name):
        for tc in self.active_tcs:
            tc.cancel()

        self.active_tcs = []

        return False

    def _onSave(self):
        spells_data = {'spell_amulet': {'amulet_powers_used_save': [], 'amulet_powers_blocked_save': [], 'amulet_stones_save': []},

            'spell_ui_component': {'spell_ui_button_save': []},

            's_spell_ui_runes_settings': {'ready_for_add_save': [], 'found_runes_save': [], 'rune_to_use': []}}

        amulet_powers_used_save = spells_data['spell_amulet']['amulet_powers_used_save']
        amulet_powers_blocked_save = spells_data['spell_amulet']['amulet_powers_blocked_save']
        for power_name, spell_amulet_power in SystemSpells.s_spell_amulet_powers.items():
            if spell_amulet_power.used:
                amulet_powers_used_save.append(power_name)

            if spell_amulet_power.blocked:
                amulet_powers_blocked_save.append(power_name)

        amulet_stones_save = spells_data['spell_amulet']['amulet_stones_save']
        for power_type, spell_amulet_stone in SystemSpells.s_spell_amulet_stones.items():
            if not spell_amulet_stone.locked:
                amulet_stones_save.append(power_type)

        spell_ui_button_save = spells_data['spell_ui_component']['spell_ui_button_save']
        for spell_type, spell_ui_component in SystemSpells.s_spell_ui_components.items():
            if not spell_ui_component.locked:
                spell_ui_button_save.append(spell_type)

        s_spell_ui_runes_settings_found_runes_save = spells_data['s_spell_ui_runes_settings']['found_runes_save']
        s_spell_ui_runes_settings_ready_for_add_save = spells_data['s_spell_ui_runes_settings']['ready_for_add_save']
        s_spell_ui_runes_settings_rune_to_use_save = spells_data['s_spell_ui_runes_settings']['rune_to_use']
        for rune_name in SystemSpells.s_spell_ui_runes_settings.found_runes:
            s_spell_ui_runes_settings_found_runes_save.append(rune_name)
        s_spell_ui_runes_settings_ready_for_add_save.append(SystemSpells.s_spell_ui_runes_settings.ready_to_add_new_rune)
        s_spell_ui_runes_settings_rune_to_use_save.append(SystemSpells.s_spell_ui_runes_settings.rune_to_use)

        return spells_data

    def _onLoad(self, save_data):
        amulet_powers_used_save = save_data['spell_amulet']['amulet_powers_used_save']
        amulet_powers_blocked_save = save_data['spell_amulet']['amulet_powers_blocked_save']
        sys_param_spell_amulet_powers = SystemSpells.s_spell_amulet_powers
        for power_type in amulet_powers_used_save:
            if power_type in sys_param_spell_amulet_powers:
                sys_param_spell_amulet_powers[power_type].used = True

            if power_type in amulet_powers_blocked_save:
                sys_param_spell_amulet_powers[power_type].blocked = True

        amulet_stones_save = save_data['spell_amulet']['amulet_stones_save']
        sys_param_spell_amulet_stones = SystemSpells.s_spell_amulet_stones
        for power_name in amulet_stones_save:
            if power_name in sys_param_spell_amulet_stones:
                sys_param_spell_amulet_stones[power_name].locked = False

        spell_ui_button_save = save_data['spell_ui_component']['spell_ui_button_save']
        sys_param_spell_ui_components = SystemSpells.s_spell_ui_components
        for spell_type in spell_ui_button_save:
            if spell_type in sys_param_spell_ui_components:
                sys_param_spell_ui_components[spell_type].locked = False

        s_spell_ui_runes_settings_found_runes_save = save_data['s_spell_ui_runes_settings']['found_runes_save']
        s_spell_ui_runes_settings_ready_for_add_save = save_data['s_spell_ui_runes_settings']['ready_for_add_save']
        s_spell_ui_runes_settings_rune_to_use_save = save_data['s_spell_ui_runes_settings']['rune_to_use']
        sys_param_spell_ui_settings = SystemSpells.s_spell_ui_runes_settings
        sys_param_spell_ui_settings.found_runes = s_spell_ui_runes_settings_found_runes_save
        sys_param_spell_ui_settings.ready_to_add_new_rune = s_spell_ui_runes_settings_ready_for_add_save[0]
        sys_param_spell_ui_settings.rune_to_use = s_spell_ui_runes_settings_rune_to_use_save[0]

    def updateSpellAmuletStoneState(self, source, spell_ui_component):
        spell_amulet_demon = spell_ui_component.getSpellDemon()

        quests = spell_ui_component.getSceneActiveQuests()
        for quest in quests:
            power_name = quest.params["PowerName"]
            spell_amulet_power = SystemSpells.getSpellAmuletStoneByPower(power_name)
            power_type = spell_amulet_power.param.power_type
            spell_amulet_button = spell_amulet_demon.getSpellAmuletButton(power_type)

            if spell_amulet_button.getLocked() is False:
                source.addFunction(spell_amulet_button.changeState, spell_amulet_button.READY)
                source.addScope(spell_amulet_button.scopePlayCurState, Loop=True)

    def __cheatGetSpellStone(self):
        def _hideDTD():
            if Mengine.isAvailablePlugin("DevToDebug") is False:
                return
            tab = Mengine.getDevToDebugTab("Cheats")
            widget = tab.findWidget("get_spellamulet_stone")
            widget.setHide(True)

        stones = SystemSpells.getSpellAmuletStones()

        for stone in stones.values():
            if stone is None or stone.getLocked() is False:
                continue

            power_type = stone.param.power_type
            Notification.notify(NOTIFICATOR_onSpellAmuletAddPower, power_type, False, False)
            Notification.notify(NOTIFICATOR_onSpellUISpellUpdate, SPELL_AMULET_TYPE)
            Trace.msg("<SystemSpells> unlocked stone {!r}".format(power_type))

            has_locked_stone = True in [stone.getLocked() is True for stone in stones.values() if stone is not None]
            if has_locked_stone is False:
                _hideDTD()
            return

        Trace.msg("<SystemSpells> all stones are already unlocked")