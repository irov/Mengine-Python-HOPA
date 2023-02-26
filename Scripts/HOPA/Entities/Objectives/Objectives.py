from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.ObjectiveManager import ObjectiveManager
from Notification import Notification

class Objectives(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "ObjectivesList", Append=Objectives._appendObjectives, Remove=Objectives._removeObjectives)
        pass

    def __init__(self):
        super(Objectives, self).__init__()

        self.textObjects = []

        self.movieShow = None
        self.movieIdle = None
        self.movieHide = None

        self.state = "close"
        pass

    def getObjectivesList(self):
        return self.object.getObjectivesList()
        pass

    def _onActivate(self):
        socketObjective = GroupManager.getObject("Objectives", "Socket_Objective")
        socketObjective.setInteractive(True)

        self.state = "close"

        self.movieShow = self.object.getObject("Movie_Show")
        self.movieIdle = self.object.getObject("Movie_Idle")
        self.movieHide = self.object.getObject("Movie_Hide")

        self.movieShow.setEnable(False)
        self.movieIdle.setEnable(False)
        self.movieHide.setEnable(False)

        self.onShowObjectiveObserver = Notification.addObserver(Notificator.onObjectiveShow, self.__onObjectiveShow)
        self.onHideObjectiveObserver = Notification.addObserver(Notificator.onObjectiveHide, self.__onObjectiveHide)
        pass

    def _onDeactivate(self):
        Notification.removeObserver(self.onShowObjectiveObserver)
        Notification.removeObserver(self.onHideObjectiveObserver)
        self._removeObjectiveFromSlot()
        pass

    def __onObjectiveShow(self):
        if self.state == "close":
            self.state = "show"
            with TaskManager.createTaskChain(Name="Objective_Show", Group=self.object) as tc_show:
                tc_show.addTask("TaskEnable", Object=self.movieShow, Value=True)
                tc_show.addTask("TaskFunction", Fn=self._setObjectiveToSlot, Args=(self.movieShow,))

                tc_show.addTask("TaskMoviePlay", Movie=self.movieShow)
                tc_show.addTask("TaskFunction", Fn=self._setState, Args=("idle",))

                tc_show.addTask("TaskFunction", Fn=self._removeObjectiveFromSlot)
                tc_show.addTask("TaskEnable", Object=self.movieIdle, Value=True)
                tc_show.addTask("TaskEnable", Object=self.movieShow, Value=False)
                tc_show.addTask("TaskFunction", Fn=self._setObjectiveToSlot, Args=(self.movieIdle,))

                tc_show.addTask("TaskMoviePlay", Movie=self.movieIdle)
                pass
        return False
        pass

    def __onObjectiveHide(self):
        if self.state == "idle":
            self.state = "hide"

            if TaskManager.existTaskChain("Objective_Show"):
                TaskManager.cancelTaskChain("Objective_Show")
                pass

            with TaskManager.createTaskChain(Name="Objective_Hide", Group=self.object) as tc_show:
                tc_show.addTask("TaskFunction", Fn=self._removeObjectiveFromSlot, Args=())
                tc_show.addTask("TaskEnable", Object=self.movieIdle, Value=False)
                tc_show.addTask("TaskEnable", Object=self.movieHide, Value=True)
                tc_show.addTask("TaskFunction", Fn=self._setObjectiveToSlot, Args=(self.movieHide,))

                tc_show.addTask("TaskMoviePlay", Movie=self.movieHide)
                tc_show.addTask("TaskFunction", Fn=self._setState, Args=("close",))
                tc_show.addTask("TaskFunction", Fn=self._removeObjectiveFromSlot, Args=())
                tc_show.addTask("TaskEnable", Object=self.movieHide, Value=False)

                pass
            pass
        return False
        pass

    def _setState(self, state):
        self.state = state
        pass

    def _appendObjectives(self, value, params):
        if self.state == "idle":
            self._removeObjectiveFromSlot()
            self._setObjectiveToSlot(self.movieIdle)
            pass
        pass

    def _removeObjectives(self, elementName, params, elements):
        if self.state == "idle":
            self._removeObjectiveFromSlot()
            self._setObjectiveToSlot(self.movieIdle)
            pass
        pass

    def _setObjectiveToSlot(self, movieObject):
        for i, values in enumerate(self.ObjectivesList):
            objectiveID = values[0]
            objectiveTextID = ObjectiveManager.getObjectiveTextID(objectiveID)
            objectText = self.object.generateObject("Text_%d" % (i), "Text_Message")

            self.textObjects.append(objectText)

            objectText.setTextID(objectiveTextID)
            textEntity = objectText.getEntity()

            id = "slot_%d" % (i)
            movieEntity = movieObject.getEntity()
            slot = movieEntity.getMovieSlot(id)
            slot.addChild(textEntity)
            pass
        pass

    def _removeObjectiveFromSlot(self):
        for text in self.textObjects:
            text.removeFromParent()
            pass

        self.textObjects = []
        pass