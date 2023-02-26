from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.TaskAlias import TaskAlias

class AliasEnableMagicVision(MixinObserver, TaskAlias):
    def _onParams(self, params):
        super(AliasEnableMagicVision, self)._onParams(params)

        self.Value = params.get("Value")
        pass

    def _onGenerate(self, source):
        MagicVision = DemonManager.getDemon("MagicVision")
        Movies_Names = ["Movie_Ready", "Movie_Activate", "Movie_Recharge", "Movie_ChargingComplete"]

        source.addTask("TaskEnable", Object=MagicVision, Value=self.Value)

        if self.Value is False:
            for movieName in Movies_Names:
                movie = MagicVision.getObject(movieName)
                movie.setEnable(False)
                pass
            pass
        pass
    pass