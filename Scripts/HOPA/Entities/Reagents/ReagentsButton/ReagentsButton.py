from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager


class ReagentsButton(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "EnablePaper", Update=ReagentsButton._updateButton)
        pass

    def _updateButton(self, value):
        self.checkPaper(value)
        pass

    def __init__(self):
        super(ReagentsButton, self).__init__()
        self.moviePaper = None
        pass

    def _onPreparation(self):
        super(ReagentsButton, self)._onPreparation()
        self.moviePaper = self.object.getObject("Movie_Paper")
        pass

    def _onActivate(self):
        self.checkPaper(self.EnablePaper)

        with TaskManager.createTaskChain(Name="onOver", Group=self.object, Repeat=True) as tc:
            tc.addTask("TaskSocketEnter", SocketName="Socket_Reagents")
            with tc.addRepeatTask() as (tc_r, tc_u):
                tc_r.addTask("TaskMoviePlay", MovieName="Movie_ReagentsOnOver", Wait=True)

                tc_u.addTask("TaskSocketLeave", SocketName="Socket_Reagents")
                tc_u.addTask("TaskMovieStop", MovieName="Movie_ReagentsOnOver")
                tc_u.addTask("TaskMovieLastFrame", MovieName="Movie_ReagentsOnOver", Value=False)
                pass
            pass
        pass

    def _onDeactivate(self):
        if TaskManager.existTaskChain("onOver"):
            TaskManager.cancelTaskChain("onOver")
            pass
        pass

    def checkPaper(self, value):
        if value is True:
            self.moviePaper.setEnable(True)
            pass
        elif value is False:
            self.moviePaper.setEnable(False)
            pass
        pass
