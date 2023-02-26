from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.TaskAlias import TaskAlias

class AliasSpinCircles(MixinObject, TaskAlias):
    def _onParams(self, params):
        super(AliasSpinCircles, self)._onParams(params)

        self.Sockets = params.get("Sockets")
        pass

    def _onGenerate(self, source):
        countSockets = len(self.Sockets)
        with source.addRaceTask(countSockets) as tcs:
            for tci, socket in zip(tcs, self.Sockets):
                tci.addTask("TaskSocketClick", SocketName=socket, AutoEnable=True)
                tci.addTask("TaskNotify", ID=Notificator.onSpin, Args=(socket,))
                pass
            pass
        pass

    pass