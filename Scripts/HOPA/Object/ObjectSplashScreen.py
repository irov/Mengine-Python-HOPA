from Foundation.Object.DemonObject import DemonObject

class ObjectSplashScreen(DemonObject):
    def __init__(self):
        super(ObjectSplashScreen, self).__init__()
        pass

    def _onParams(self, params):
        super(ObjectSplashScreen, self)._onParams(params)

        self.initParam("Play", params, False)
        pass

    def _onLoader(self):
        super(ObjectSplashScreen, self)._onLoader()

        Splashes = self.getObjects()

        for object in Splashes:
            object.superParam("Enable", False)
            pass
        pass
    pass