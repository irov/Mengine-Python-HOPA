from Foundation.Object.DemonObject import DemonObject


class ObjectSplashScreen(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("Play")
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
