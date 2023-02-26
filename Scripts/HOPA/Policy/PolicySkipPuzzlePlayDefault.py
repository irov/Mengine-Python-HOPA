from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicySkipPuzzlePlayDefault(TaskAlias):

    def _onGenerate(self, source):
        DemonSkipPuzzle = DemonManager.getDemon("SkipPuzzle")

        if DemonSkipPuzzle.hasObject("Movie2_Activate") is True:
            source.addTask("TaskEnable", ObjectName="Movie2_Activate", Value=True)
            source.addTask("TaskMovie2Play", Movie2Name="Movie2_Activate", Wait=False)
        source.addTask("TaskNotify", ID=Notificator.onShiftCollectSkip)
        source.addTask("TaskNotify", ID=Notificator.onEnigmaSkip)