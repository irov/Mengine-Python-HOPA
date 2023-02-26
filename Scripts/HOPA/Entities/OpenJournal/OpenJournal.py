from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager

from OpenJournalManager import OpenJournalManager

class OpenJournal(BaseEntity):
    STATIC = "Static"
    IDLE = "Idle"
    ACTIVATE = "Activate"
    ENTER = "Enter"
    LEAVE = "Leave"
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "State", Update=OpenJournal.__updateState)
        pass

    def __init__(self):
        super(OpenJournal, self).__init__()
        self.Data = None
        self.isClicked = False
        pass

    def __updateState(self, value):
        if self.isClicked is True:  # ---for return to gameScene after click on Socket_Open
            self.isClicked = False
            self.object.setState(OpenJournal.STATIC)
            return
            pass

        if value == OpenJournal.STATIC:
            self.staticChain()
            return
            pass
        if value == OpenJournal.ENTER:
            self.enterChain()
            return
            pass

        if value == OpenJournal.IDLE:
            self.idleChain()
            return
            pass

        if value == OpenJournal.LEAVE:
            self.leaveChain()
            return
            pass

        if value == OpenJournal.ACTIVATE:
            self.activateChain()
            return
            pass
        return
        pass

    def changeState(self, isSkip):
        if self.State == OpenJournal.STATIC:
            newState = OpenJournal.ENTER
            pass

        if self.State == OpenJournal.ENTER:
            newState = OpenJournal.IDLE
            pass

        if self.State == OpenJournal.LEAVE:
            newState = OpenJournal.STATIC
            pass

        self.object.setState(newState)
        pass

    def staticChain(self):
        self.disableMovies(self.Data)
        self.cancelTaskChains()
        movie = self.Data[self.State]

        with TaskManager.createTaskChain(Name="OpenJournal_Static", Cb=self.changeState) as tc:
            tc.addTask("TaskEnable", Object=movie)
            tc.addTask("TaskMoviePlay", Movie=movie, Loop=True, Wait=False)
            tc.addTask("TaskSocketEnter", SocketName="Socket_Open", GroupName="Open_Journal")
            pass
        pass

    def enterChain(self):
        self.disableMovies(self.Data)
        self.cancelTaskChains()
        movie = self.Data[self.State]

        with TaskManager.createTaskChain(Name="OpenJournal_Enter", Cb=self.changeState) as tc:
            tc.addTask("TaskEnable", Object=movie)
            tc.addTask("TaskMoviePlay", Movie=movie, Loop=False, Wait=True)
            pass
        pass

    def idleChain(self):
        self.disableMovies(self.Data)
        self.cancelTaskChains()
        movie = self.Data[self.State]

        with TaskManager.createTaskChain(Name="OpenJournal_Idle") as tc:
            tc.addTask("TaskEnable", Object=movie)
            tc.addTask("TaskMoviePlay", Movie=movie, Loop=True, Wait=False)
            with tc.addRaceTask(2) as (tc_leave, tc_click):
                tc_leave.addTask("TaskSocketLeave", SocketName="Socket_Open", GroupName="Open_Journal")
                tc_leave.addTask("TaskSetParam", Object=self.object, Param="State", Value=OpenJournal.LEAVE)

                tc_click.addTask("TaskSocketClick", SocketName="Socket_Open", GroupName="Open_Journal")
                tc_click.addTask("TaskSetParam", Object=self.object, Param="State", Value=OpenJournal.ACTIVATE)
                pass
            pass
        pass

    def leaveChain(self):
        self.disableMovies(self.Data)
        self.cancelTaskChains()
        movie = self.Data[self.State]

        with TaskManager.createTaskChain(Name="OpenJournal_Leave", Cb=self.changeState) as tc:
            tc.addTask("TaskEnable", Object=movie)
            tc.addTask("TaskMoviePlay", Movie=movie, Loop=False, Wait=True)
            pass
        pass

    def activateChain(self):
        self.disableMovies(self.Data)
        self.cancelTaskChains()
        movie = self.Data[self.State]

        def setClicked():
            self.isClicked = True
            pass

        with TaskManager.createTaskChain(Name="OpenJournal_Activate") as tc:
            tc.addTask("TaskFunction", Fn=setClicked)
            tc.addTask("TaskEnable", Object=movie)

            with GuardBlockInput(tc) as guard_tc:
                guard_tc.addTask("TaskMoviePlay", Movie=movie, Loop=False, Wait=True)
                pass

            tc.addTask("TaskNotify", ID=Notificator.onJournalOpen)
            pass
        pass

    def disableMovies(self, Data):
        for state, movie in Data.iteritems():
            if movie is None:
                continue
                pass
            movie.setEnable(False)
            pass
        pass

    def _onPreparation(self):
        super(OpenJournal, self)._onPreparation()
        self.Data = OpenJournalManager.getData(self.object)
        self.disableMovies(self.Data)
        pass

    def _onActivate(self):
        super(OpenJournal, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(OpenJournal, self)._onDeactivate()
        self.cancelTaskChains()
        pass

    def cancelTaskChains(self):
        if TaskManager.existTaskChain("OpenJournal_Static") is True:
            TaskManager.cancelTaskChain("OpenJournal_Static")
            pass

        if TaskManager.existTaskChain("OpenJournal_Enter") is True:
            TaskManager.cancelTaskChain("OpenJournal_Enter")
            pass

        if TaskManager.existTaskChain("OpenJournal_Idle") is True:
            TaskManager.cancelTaskChain("OpenJournal_Idle")
            pass

        if TaskManager.existTaskChain("OpenJournal_Leave") is True:
            TaskManager.cancelTaskChain("OpenJournal_Leave")
            pass

        if TaskManager.existTaskChain("OpenJournal_Activate") is True:
            TaskManager.cancelTaskChain("OpenJournal_Activate")
            pass
        pass

    pass