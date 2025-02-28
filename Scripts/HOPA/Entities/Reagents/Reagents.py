from HOPA.CursorManager import CursorManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from Notification import Notification

from ReagentsManager import ReagentsManager


class Reagents(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "OpenReagents",
                       Append=Reagents._appendReagent,
                       Remove=Reagents._removeReagent,
                       Update=Reagents._updateReagents)
        pass

    def _appendReagent(self, id, reagentName):
        pass

    def _updateReagents(self, value):
        pass

    def _removeReagent(self):
        pass

    def __init__(self):
        super(Reagents, self).__init__()
        self.reagents = {}
        self.movieAddReagent = None
        self.currentItem = None
        self.addMovies = {}
        self.currentAdd = 0
        self.currentAddMovie = None
        self.currentReagent = None
        self.buttonRefresh = None
        self.buttonColaps = None
        self.buttonColapsActivated = None
        self.Enigma = None
        self.onEnigmaStartObserver = None
        self.onEnigmaCompleteObserver = None
        self.onCheckReagentsButtonObserever = None
        pass

    def _onPreparation(self):
        super(Reagents, self)._onPreparation()
        self.reagents = ReagentsManager.getReagents()
        self.addMovies = ReagentsManager.getAddMovies()
        self.movieAddReagent = self.object.getObject("Movie_AddReagent")
        self.buttonRefresh = self.object.getObject("Button_Refresh")
        self.buttonColaps = self.object.getObject("Button_Colaps")
        self.buttonColapsActivated = self.object.getObject("Button_ColapsActivated")

        for name, reagent in self.reagents.iteritems():
            if name not in self.OpenReagents:
                reagent.setEnable(False)
                pass
            pass

        for name in self.OpenReagents:
            self.reagents[name].setEnable(True)
            pass
        pass

    def disableAllMovies(self):
        addMovies = ReagentsManager.getAddMovies()
        for list in addMovies.values():
            for movie in list:
                movie.setEnable(False)
                movie.setPlay(False)
                pass
            pass
        pass

    def _onActivate(self):
        super(Reagents, self)._onActivate()

        self.buttonColapsActivated.setEnable(False)
        self._runButtonsChain()
        self.onCheckReagentsButtonObserever = Notification.addObserver(Notificator.onCheckReagentsButton, self._onCheckReagentsButton)

        if len(self.OpenReagents) > 0:
            self._runMixChain()
            pass

        self.disableAllMovies()

        self.onEnigmaStartObserver = Notification.addObserver(Notificator.onEnigmaStart, self.__enigmaStart)
        self.onEnigmaCompleteObserver = Notification.addObserver(Notificator.onEnigmaComplete, self.__enigmaComplete)
        pass

    def __enigmaStart(self, enigma):
        EnigmaName = EnigmaManager.getEnigmaName(enigma)
        enigmaData = EnigmaManager.getEnigma(EnigmaName)
        enigmaType = enigmaData.getType()
        if enigmaType != "ReagentsEnigma":
            return False
            pass
        self.Enigma = enigma
        return False
        pass

    def __enigmaComplete(self, enigma):
        if self.Enigma != enigma:
            return False
            pass
        self._setButtonsInteraction(1)
        return False
        pass

    def _onCheckReagentsButton(self, value):
        if value is True:
            self.buttonColaps.setEnable(False)
            self.buttonColapsActivated.setEnable(True)
            pass
        else:
            self.buttonColaps.setEnable(True)
            self.buttonColapsActivated.setEnable(False)
            pass
        return False
        pass

    def _setButtonsInteraction(self, value):
        self.buttonRefresh.setParam("Interactive", value)
        self.buttonColaps.setParam("Interactive", value)
        self.buttonColapsActivated.setParam("Interactive", value)
        pass

    def _runMixChain(self):
        count = len(self.OpenReagents)
        socket = self.object.getObject("Socket_Mix")
        with TaskManager.createTaskChain(Name="Mix", Group=self.object, Repeat=True) as tc:
            with tc.addRaceTask(count) as tc_items:
                for tc_item, openReagentName in zip(tc_items, self.OpenReagents):
                    item = self.reagents[openReagentName]
                    with tc_item.addRepeatTask() as (tc_do, tc_until):
                        tc_do.addTask("AliasItemAttach", Item=item, MovieAttach=False, Origin=False)
                        tc_do.addNotify(Notificator.onAttacheagent)
                        tc_do.addFunction(self._setButtonsInteraction, 0)
                        tc_do.addTask("TaskItemInvalidUse", Item=item)
                        tc_do.addTask("AliasRemoveItemAttach", Item=item)
                        tc_do.addTask("TaskObjectReturn", Object=item)
                        tc_do.addEnable(item)

                        def __restore(obj):
                            obj.onEntityRestore()
                            pass

                        tc_do.addFunction(__restore, item)
                        tc_do.addFunction(self._setButtonsInteraction, 1)

                        tc_until.addTask("TaskSocketUseItem", Socket=socket, Item=item, Taken=False)
                        tc_until.addFunction(self._setCurrentItem, item, openReagentName)
                        pass
                    pass
                pass
            tc.addScope(self._addReagent)
            tc.addFunction(self._setButtonsInteraction, 1)
            pass
        pass

    def __changeCursor(self, value):
        cursorChildren = CursorManager.getCursorChildren()
        if len(cursorChildren) == 0:
            return

        currentCursor = cursorChildren[0]
        currentCursor.setEnable(value)
        pass

    def _setCurrentItem(self, item, reagent):
        self.currentItem = item
        self.currentReagent = reagent
        pass

    def _addReagent(self, scope):
        itemObject = self.currentItem

        self.currentAdd += 1

        movieEntity = self.movieAddReagent.getEntity()
        slotAdd = movieEntity.getMovieSlot("add")

        scope.addTask("TaskRemoveArrowAttach")
        scope.addTask("TaskFanItemInNone", FanItem=itemObject)
        scope.addScope(self._reatachItem, slotAdd, itemObject)
        scope.addNotify(Notificator.onAddReagent, self.currentReagent)
        pass

    def _finishAction(self, scope):
        self.currentAdd = 0
        self.currentAddMovie.setEnable(False)
        self.currentAddMovie = None
        pass

    def _reatachItem(self, scope, slotAdd, itemObject):
        position = itemObject.getPosition()
        slotPosition = slotAdd.getWorldPosition()
        itemObject.setEnable(True)
        itemEntity = itemObject.getEntity()
        slotAdd.addChild(itemEntity)

        if self.currentAddMovie is not None:
            self.currentAddMovie.setEnable(False)
            self.currentAddMovie.setPlay(False)
            self.currentAddMovie.setLoop(False)
            pass

        lenAddMovies = len(self.addMovies)

        if self.currentAdd >= lenAddMovies:
            addMovies = self.addMovies[lenAddMovies]
            pass
        else:
            addMovies = self.addMovies[self.currentAdd]
            pass

        rand = Mengine.rand(len(addMovies))
        self.currentAddMovie = addMovies[rand]
        self.currentAddMovie.setEnable(True)
        self.currentAddMovie.setPlay(True)
        self.currentAddMovie.setLoop(True)

        time = 1.0
        time *= 1000  # speed fix

        scope.addTask("TaskObjectSetPosition", Object=itemObject, Value=(0, 0))
        scope.addTask("TaskSceneLayerAddEntity", Object=self.movieAddReagent, LayerName="InventoryItemEffect")
        scope.addTask("TaskMoviePlay", Movie=self.movieAddReagent, Wait=True)
        scope.addTask("TaskNodeRemoveFromParent", Node=self.movieAddReagent.getEntity())
        scope.addTask("TaskSceneLayerAddEntity", Object=itemObject, LayerName="InventoryItemEffect")
        scope.addTask("TaskObjectSetPosition", Object=itemObject, Value=slotPosition)
        scope.addTask("TaskNodeBezier2To", Node=itemEntity, Point1=position, To=position, Time=time)
        scope.addTask("TaskNodeRemoveFromParent", Node=itemEntity)
        scope.addTask("TaskObjectReturn", Object=itemObject)
        scope.addTask("TaskObjectSetPosition", Object=itemObject, Value=position)
        scope.addEnable(itemObject)

        def __restore(obj):
            obj.onEntityRestore()
            pass

        scope.addFunction(__restore, itemObject)
        pass

    def _runButtonsChain(self):
        with TaskManager.createTaskChain(Name="ReagentButtons", Group=self.object, Repeat=True) as tc:
            with tc.addRaceTask(4) as (tc_refresh, tc_colaps, tc_activated, tc_listener):
                tc_refresh.addTask("TaskButtonClick", ButtonName="Button_Refresh", AutoEnable=False)
                tc_colaps.addNotify(Notificator.onCheckReagentReaction, self, False)

                tc_colaps.addTask("TaskButtonClick", Button=self.buttonColaps, AutoEnable=False)
                tc_colaps.addNotify(Notificator.onCheckReagentReaction, self)

                tc_activated.addTask("TaskButtonClick", Button=self.buttonColapsActivated, AutoEnable=False)
                tc_activated.addNotify(Notificator.onCheckReagentReaction, self)

                tc_listener.addListener(Notificator.onReagentsCleanData)
                pass
            tc.addFunction(self._cleanData)
            pass
        pass

    def _onDeactivate(self):
        if self.onCheckReagentsButtonObserever is not None:
            Notification.removeObserver(self.onCheckReagentsButtonObserever)
            pass
        if self.onEnigmaStartObserver is not None:
            Notification.removeObserver(self.onEnigmaStartObserver)
            pass
        if self.onEnigmaCompleteObserver is not None:
            Notification.removeObserver(self.onEnigmaCompleteObserver)
            pass

        if TaskManager.existTaskChain("ReagentButtons"):
            TaskManager.cancelTaskChain("ReagentButtons")
            pass
        if TaskManager.existTaskChain("Mix"):
            TaskManager.cancelTaskChain("Mix")
            pass
        self._cleanData()

        self.disableAllMovies()
        self.reagents = {}
        self.movieAddReagent = None
        self.addMovies = {}
        self.buttonColaps = None
        self.buttonColapsActivated = None
        pass

    def _cleanData(self):
        self.buttonColaps.setEnable(True)
        self.buttonColapsActivated.setEnable(False)
        self.currentItem = None

        self.currentAdd = 0

        if self.currentAddMovie is not None:
            self.currentAddMovie.setEnable(False)
            pass

        self.currentAddMovie = None
        pass
