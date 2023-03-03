from Foundation.System import System


class SystemMap2Switch(System):
    def __init__(self):
        super(SystemMap2Switch, self).__init__()
        self.onSceneEnterObserver = None
        self.onMapPointBlockObserver = None
        self.onMapPointUnblockObserver = None

    def _onParams(self, params):
        super(SystemMap2Switch, self)._onParams(params)

    def _onRun(self):
        pass

    def _onStop(self):
        pass
