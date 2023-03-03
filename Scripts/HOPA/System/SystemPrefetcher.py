from Foundation.System import System
from HOPA.Prefetcher.Prefetcher import Prefetcher


class SystemPrefetcher(System):
    def __init__(self):
        super(SystemPrefetcher, self).__init__()
        self.prefetcher = Prefetcher()
        pass

    def _onParams(self, params):
        super(SystemPrefetcher, self)._onParams(params)
        pass

    #########################################################

    def _onInitialize(self):
        super(SystemPrefetcher, self)._onInitialize()
        pass

    def _onRun(self):
        self.prefetcher.onInitialize()

        return True
        pass

    def _onStop(self):
        self.prefetcher.finalise()
        pass

    pass
