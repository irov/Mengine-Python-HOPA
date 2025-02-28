from Foundation.TaskManager import TaskManager
from HOPA.Entities.Reagents.ReagentsManager import ReagentsManager
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")


class ReagentsEnigma(Enigma):
    def __init__(self):
        super(ReagentsEnigma, self).__init__()
        self.winItems = []
        self.currentItems = []
        self.maxAdd = None
        self.Win = False
        self.onAddReagentObserver = None
        self.onCheckReagentReactionObserver = None
        self.check = False
        pass

    def _onPreparation(self):
        super(ReagentsEnigma, self)._onPreparation()

        refreshMovieName = "Movie_Refresh"
        self.refreshMovie = self.object.getObject(refreshMovieName)
        self.refreshMovie.setEnable(False)

        self.maxAdd = ReagentsManager.getMaxAdd()
        pass

    def _playEnigma(self):
        winMix = ReagentsManager.getReagentsMix(self.EnigmaName)
        self.winItems = winMix.getItems()

        winMovieName = winMix.getWinMovieName()
        self.winMovie = self.object.getObject(winMovieName)
        self.winMovie.setEnable(False)

        looseMovieName = winMix.getLooseMovieName()
        self.looseMovie = self.object.getObject(looseMovieName)
        self.looseMovie.setEnable(False)

        self.onAddReagentObserver = Notification.addObserver(Notificator.onAddReagent, self.__onAddReagent)
        self.onCheckReagentReactionObserver = Notification.addObserver(Notificator.onCheckReagentReaction, self.__checkReaction)
        pass

    def __onAddReagent(self, reagent):
        self.currentItems.append(reagent)

        if self.currentItems == self.winItems:
            value = True
            pass
        else:
            value = False
            pass

        Notification.notify(Notificator.onCheckReagentsButton, value)

        if len(self.currentItems) >= self.maxAdd:
            self.__checkReaction()
            pass

        return False
        pass

    def __checkReaction(self, reagents, value=True):
        if self.check is True:
            return False
            pass

        # print "__checkReaction"
        # print "self.currentItems", self.currentItems
        # print "self.winItems", self.winItems

        self.check = True
        if value is False and len(self.currentItems) >= 1:
            self.refresh()
            pass
        elif self.currentItems == self.winItems:
            self.Win = True
            self.win(reagents)
            pass
        else:
            value = True
            if len(self.currentItems) <= 0:
                value = False
                pass
            self.loose(value)
            pass

        self.currentItems = []

        Notification.notify(Notificator.onReagentsCleanData)

        return False
        pass

    def refresh(self):
        with TaskManager.createTaskChain() as tc:
            tc.addEnable(self.refreshMovie)
            tc.addTask("TaskMoviePlay", Movie=self.refreshMovie, Wait=True)
            tc.addDisable(self.refreshMovie)
            tc.addFunction(self.checkFalse)
            pass
        pass

    def checkFalse(self):
        self.check = False
        pass

    def win(self, reagents):
        with TaskManager.createTaskChain() as tc:
            tc.addFunction(reagents._setButtonsInteraction, 0)
            tc.addEnable(self.winMovie)
            tc.addTask("TaskMoviePlay", Movie=self.winMovie, Wait=True)
            tc.addDisable(self.winMovie)
            tc.addFunction(self.enigmaComplete)
            tc.addFunction(self.checkFalse)
            pass
        pass

    def loose(self, value):
        with TaskManager.createTaskChain() as tc:
            if value is True:
                tc.addEnable(self.looseMovie)
                with tc.addParallelTask(2) as (tc1, tc2):
                    tc1.addTask("TaskMoviePlay", Movie=self.looseMovie, Wait=True)
                    tc2.addTask("AliasMindPlay", MindID="ID_MIND_Not_RightReagent")
                    pass
                tc.addDisable(self.looseMovie)
                pass
            else:
                tc.addTask("AliasMindPlay", MindID="ID_MIND_NoOne_Reagent")
                pass
            tc.addFunction(self.checkFalse)
            pass
        pass

    def _stopEnigma(self):
        super(ReagentsEnigma, self)._stopEnigma()
        self.Destroy()
        return False
        pass

    def onDeactivate(self):
        super(ReagentsEnigma, self).onDeactivate()
        self.Destroy()
        pass

    def Destroy(self):
        Notification.removeObserver(self.onAddReagentObserver)
        Notification.removeObserver(self.onCheckReagentReactionObserver)

        self.onCheckReagentReactionObserver = None
        self.onAddReagentObserver = None

        self.winItems = []
        self.currentItems = []
        self.maxAdd = None
        self.check = False
        pass
