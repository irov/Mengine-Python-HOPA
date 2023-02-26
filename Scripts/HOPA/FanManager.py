from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from Notification import Notification

class FanManager(object):
    onTransition = None
    s_fans = {}

    class FanParam(object):
        def __init__(self, FanItems, FanObject):
            self.FanItems = FanItems
            self.FanObject = FanObject
            pass
        pass

    pass

    @staticmethod
    def onInitialize():
        Sprite_Black = GroupManager.getObject("Fan", "Sprite_Black")
        Sprite_Black.setEnable(False)
        pass

    @staticmethod
    def onFinalize():
        pass

    @staticmethod
    def loadFans(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            name = record.get("Name")
            param = record.get("Param")

            FanManager.loadFan(module, name, param)
            pass
        pass

    @staticmethod
    def loadFan(module, name, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        FanObject = EnigmaManager.getEnigmaObject(name)

        if FanObject is None:
            Trace.log("FanManager", 0, "FanManager.loadFan: can't get Fan Object %s:" % (name))
            return
            pass

        FanItems = []

        for record in records:
            FanItemName = record.get("Key")
            if FanItemName is None:
                continue

            FanItems.append(FanItemName)
            pass

        FanObject.onEnigmaInit(name)
        FanObject.setFindItems(FanItems)

        fanParam = FanManager.FanParam(FanItems, FanObject)
        FanManager.s_fans[name] = fanParam

        return fanParam
        pass

    @staticmethod
    def hasFan(name):
        return name in FanManager.s_fans
        pass

    @staticmethod
    def getFan(name):
        if name not in FanManager.s_fans:
            Trace.log("FanManager", 0, "FanManager.getFan: not found fan %s" % (name))
            return None
            pass

        fanParams = FanManager.s_fans[name]

        return fanParams
        pass

    @staticmethod
    def getFanItems(name):
        if FanManager.hasFan(name) is False:
            Trace.log("FanManager", 0, "FanManager.getFanItems: not found hog %s" % (name))
            return None

        fanParams = FanManager.getFan(name)

        return fanParams.FanItems
        pass

    @staticmethod
    def getFanObject(name):
        if FanManager.hasFan(name) is False:
            Trace.log("FanManager", 0, "FanManager.getFanObject: not found fan %s" % (name))
            return None

        fanParams = FanManager.getFan(name)

        return fanParams.FanObject
        pass

    @staticmethod
    def openFan(Fan):
        if TaskManager.existTaskChain("CloseFan") is True:
            TaskManager.cancelTaskChain("CloseFan")

        Notification.notify(Notificator.onFanOpen, Fan)
        pass

    @staticmethod
    def closeFan(Fan):
        Notification.notify(Notificator.onFanClose, Fan)
        pass