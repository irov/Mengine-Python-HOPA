from Foundation.ArrowManager import ArrowManager
from Foundation.StateManager import StateManager
from Foundation.System import System
from Notification import Notification

from SpellManager import SpellManager

class __SystemSpell(System):
    """
    deprecated
    """
    s_currentSpell = None
    noficators = {'ObjectSocket': (Notificator.onSocketMouseEnter, Notificator.onSocketMouseLeave), 'ObjectTransition': (Notificator.onTransitionMouseEnter, Notificator.onTransitionMouseLeave), 'ObjectZoom': (Notificator.onZoomMouseEnter, Notificator.onZoomMouseLeave), 'ObjectItem': (Notificator.onItemMouseEnter, Notificator.onItemMouseLeave)}

    # onQuestObjectsNotificators = {
    #        'SpellOne': (Notificator.onSpellOneMouseEnter,	Notificator.onSpellOneMouseLeave)
    #     ,  'SpellTwo': (Notificator.onSpellTwoMouseEnter,	Notificator.onSpellTwoMouseLeave)
    #     ,'SpellThree': (Notificator.onSpellThreeMouseEnter,	Notificator.onSpellThreeMouseLeave)
    #     , 'SpellFour': (Notificator.onSpellFourMouseEnter,	Notificator.onSpellFourMouseLeave)
    # }
    def __init__(self):
        super(SystemSpell, self).__init__()
        self.macroObjects = {}

        self.onSpellPreparedObserver = None
        self.onSpellReadyObserver = None
        self.onSpellLockObserver = None
        self.onSpellBeginUseObserver = None
        self.onSpellEndUseObserver = None
        self.onSpellHideObserver = None
        self.onSpellShowObserver = None
        self.onSpellUseMacroBeginObserver = None
        self.onSpellUseMacroEndObserver = None

        self.MouseEnterObservers = []
        self.onQuestObjectsNotificators = {}
        pass

    def _onSave(self):
        return self.macroObjects
        pass

    def _onLoad(self, data_save):
        self.macroObjects = data_save
        pass

    def __onInventoryUp(self):
        spells = SpellManager.getAllSpellObjects()
        for spell in spells.itervalues():
            spell.setParam("HideState", "Idle")
            pass
        return False
        pass

    def _onRun(self):
        inventoryState = StateManager.getState("StateInventory")
        if inventoryState == "INVENTORY_UP":
            self.__onInventoryUp()
            pass

        self.onQuestObjectsNotificators = {'SpellOne': (Notificator.onSpellOneMouseEnter, Notificator.onSpellOneMouseLeave), 'SpellTwo': (Notificator.onSpellTwoMouseEnter, Notificator.onSpellTwoMouseLeave), 'SpellThree': (Notificator.onSpellThreeMouseEnter, Notificator.onSpellThreeMouseLeave), 'SpellFour': (Notificator.onSpellFourMouseEnter, Notificator.onSpellFourMouseLeave)}

        self.onSpellPreparedObserver = Notification.addObserver(Notificator.onSpellPrepared, self.__onSpellPrepared)
        self.onSpellReadyObserver = Notification.addObserver(Notificator.onSpellReady, self.__onSpellReady)
        self.onSpellLockObserver = Notification.addObserver(Notificator.onSpellLock, self.__onSpellLock)
        self.onSpellBeginUseObserver = Notification.addObserver(Notificator.onSpellBeginUse, self.__onSpellBeginUse)
        self.onSpellEndUseObserver = Notification.addObserver(Notificator.onSpellEndUse, self.__onSpellEndUse)
        self.onSpellHideObserver = Notification.addObserver(Notificator.onInventoryHide, self.__onSpellHide)
        self.onSpellShowObserver = Notification.addObserver(Notificator.onInventoryShow, self.__onSpellShow)
        self.onInventoryUpObserver = Notification.addObserver(Notificator.onInventoryUp, self.__onInventoryUp)
        self.onSpellUseMacroBeginObserver = Notification.addObserver(Notificator.onSpellUseMacroBegin, self.__onSpellMacroBegin)
        self.onSpellUseMacroEndObserver = Notification.addObserver(Notificator.onSpellUseMacroEnd, self.__onSpellMacroEnd)

        for pair in SystemSpell.noficators.values():
            NotifyEnter, NotifyLeave = pair
            Enter = Notification.addObserver(NotifyEnter, self.__ObjectEnterFilter)
            Leave = Notification.addObserver(NotifyLeave, self.__ObjectLeaveFilter)
            self.MouseEnterObservers.append(Enter)
            self.MouseEnterObservers.append(Leave)
            pass

        return True
        pass

    def _onStop(self):
        Notification.removeObserver(self.onSpellPreparedObserver)
        Notification.removeObserver(self.onSpellReadyObserver)
        Notification.removeObserver(self.onSpellBeginUseObserver)
        Notification.removeObserver(self.onSpellEndUseObserver)
        Notification.removeObserver(self.onSpellHideObserver)
        Notification.removeObserver(self.onSpellShowObserver)
        Notification.removeObserver(self.onInventoryUpObserver)
        Notification.removeObserver(self.onSpellLockObserver)
        Notification.removeObserver(self.onSpellUseMacroBeginObserver)
        Notification.removeObserver(self.onSpellUseMacroEndObserver)
        for observer in self.MouseEnterObservers:
            Notification.removeObserver(observer)
            pass
        self.MouseEnterObservers = []
        self.onQuestObjectsNotificators = {}
        pass

    def __ObjectEnterFilter(self, object):
        if ArrowManager.emptyArrowAttach() is False:
            return False
            pass
        if object not in self.macroObjects:
            return False
            pass
        spells = self.macroObjects[object]

        for spell in spells:
            spellID = SpellManager.getSpellID(spell)
            if spellID in self.onQuestObjectsNotificators:
                enterNotify = self.onQuestObjectsNotificators[spellID][0]
                Notification.notify(enterNotify, object)
                pass
            entity = spell.getEntity()
            entity.StartOverview()
            pass
        return False
        pass

    def __ObjectLeaveFilter(self, object):
        if object not in self.macroObjects:
            return False
            pass
        spells = self.macroObjects[object]
        for spell in spells:
            spellID = SpellManager.getSpellID(spell)
            if spellID in self.onQuestObjectsNotificators:
                leaveNotify = self.onQuestObjectsNotificators[spellID][1]
                Notification.notify(leaveNotify, object)
                pass
            entity = spell.getEntity()
            entity.FinishOverview()
            pass
        return False
        pass

    def __onSpellMacroBegin(self, object, spellObject):
        if object not in self.macroObjects:
            self.macroObjects[object] = [spellObject]
            pass
        elif object in self.macroObjects:
            innerList = self.macroObjects[object]
            innerList.append(spellObject)
            pass
        return False
        pass

    def __onSpellMacroEnd(self, object, spellObject):
        if object not in self.macroObjects:
            return False
            pass
        innerList = self.macroObjects[object]
        innerList.remove(spellObject)
        if len(innerList) == 0:
            del self.macroObjects[object]
            pass
        return False
        pass

    def __onSpellPrepared(self, spellId):
        spellObject = SpellManager.getSpellObject(spellId)

        if spellObject is None:
            return False
            pass

        spellObject.setParam("CurrentState", "Prepared")
        return False
        pass

    def __onSpellReady(self, spellId):
        spellObject = SpellManager.getSpellObject(spellId)

        if spellObject is None:
            return False
            pass

        spellObject.setParam("CurrentState", "Charge")
        return False
        pass

    def __onSpellLock(self, spellId):
        spellObject = SpellManager.getSpellObject(spellId)

        if spellObject is None:
            return False
            pass

        spellObject.setParam("CurrentState", "Locked")
        return False
        pass

    def __onSpellBeginUse(self, spellObject):
        SystemSpell.s_currentSpell = spellObject
        return False
        pass

    def __onSpellEndUse(self, spellObject):
        SystemSpell.s_currentSpell = None
        return False
        pass

    def __onSpellHide(self):
        spells = SpellManager.getAllSpellObjects()
        for spell in spells.itervalues():
            spell.setParam("HideState", "Hide")
            pass
        return False
        pass

    def __onSpellShow(self):
        spells = SpellManager.getAllSpellObjects()
        for spell in spells.itervalues():
            spell.setParam("HideState", "Show")
            pass
        return False
        pass

    @staticmethod
    def getCurrentSpell():
        return SystemSpell.s_currentSpell
        pass

    pass