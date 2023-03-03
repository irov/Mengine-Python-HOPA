from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskActiveLayerEsc(MixinObserver, Task):
    def onParams(self, params):
        super(TaskActiveLayerEsc, self).onParams(params)
        self.layerName = params.get("LayerName")
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onEscPressed, self.__onKeyEvent, self.layerName)
        return False
        pass

    def __onKeyEvent(self, layerName):
        return True
        pass

    pass
