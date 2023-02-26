from Foundation.Entities.Movie2Button.ObjectMovie2Button import ObjectMovie2Button
from Foundation.Entities.MovieButton.ObjectMovieButton import ObjectMovieButton
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

class ResetPuzzle(BaseEntity):
    def __init__(self):
        super(ResetPuzzle, self).__init__()

        self.reset_button = None

    def _onPreparation(self):
        super(ResetPuzzle, self)._onPreparation()

        if self.object.hasObject("Movie2Button_Reset"):
            self.reset_button = self.object.getObject("Movie2Button_Reset")

        elif self.object.hasObject("MovieButton_Reset"):
            self.reset_button = self.object.getObject("MovieButton_Reset")
            if _DEVELOPMENT:
                Trace.msg("<ResetPuzzle> You are using old version of Movie T_T. Pls, update button 'Reset'")

        else:
            msg = "ResetPuzzle Demon should have \"Movie2Button_Reset\" or \"MovieButton_Reset\" object. Please add one"
            Trace.log("Entity", 0, msg)

    def _onActivate(self):
        super(ResetPuzzle, self)._onActivate()

        with TaskManager.createTaskChain(Name='ResetPuzzle', Repeat=True) as tc:
            if isinstance(self.reset_button, ObjectMovie2Button):
                tc.addTask('TaskMovie2ButtonClick', Movie2Button=self.reset_button)

            elif isinstance(self.reset_button, ObjectMovieButton):
                tc.addTask('TaskMovieButtonClick', MovieButton=self.reset_button)

            else:
                msg = "ResetPuzzle Demon should have \"Movie2Button_Reset\" " \
                      "or \"MovieButton_Reset\" object. Please add one"
                Trace.log("Entity", 0, msg)
                return

            tc.addTask('TaskNotify', ID=Notificator.onEnigmaReset)  # tc.addScope(self.__scopeButtonDelay)

    def __scopeButtonDelay(self, source):
        DELAY = 1 * 1000  # delay in ms after pressing button
        button = self.reset_button

        source.addFunction(button.setBlock, True)
        source.addDelay(DELAY)
        source.addFunction(button.setBlock, False)

    def _onDeactivate(self):
        super(ResetPuzzle, self)._onDeactivate()

        self.reset_button = None

        if TaskManager.existTaskChain('ResetPuzzle'):
            TaskManager.cancelTaskChain('ResetPuzzle')