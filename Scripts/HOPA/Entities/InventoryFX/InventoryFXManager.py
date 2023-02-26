class InventoryFXManager(object):
    s_actions = {}

    @staticmethod
    def onFinalize():
        InventoryFXManager.s_questsType = {}
        pass

    @staticmethod
    def importActions(module, names):
        for name in names:
            InventoryFXManager.importAction(module, name)
            pass
        pass

    @staticmethod
    def importAction(module, name):
        Name = "%s" % (name)
        FromName = module
        ModuleName = "%s.%s" % (FromName, Name)
        Module = __import__(ModuleName, fromlist=[FromName])
        Type = getattr(Module, Name)
        InventoryFXManager.addAction(name, Type)
        pass

    @staticmethod
    def addAction(actionType, action):
        InventoryFXManager.s_actions[actionType] = action
        pass

    @staticmethod
    def getAction(actionType):
        return InventoryFXManager.s_actions[actionType]
        pass

    @staticmethod
    def createAction(actionType, *args):
        invAction = InventoryFXManager.getAction(actionType)
        invAction = invAction()
        invAction.setType(actionType)
        invAction.onValues(*args)
        invAction.onInitialize()

        return invAction
        pass
    pass