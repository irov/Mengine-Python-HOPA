from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from TraceManager import TraceManager

class StaticPopUpManager(Manager):
    s_objects = {}

    class StaticPopUp(object):
        def __init__(self, textID, ForeignKey):
            self.textID = textID
            self.ForeignKey = ForeignKey  # foreign key -> relation to another table StaticPopUpTransitionManager

        def hasForeignKey(self):
            return self.ForeignKey

    @staticmethod
    def _onFinalize():
        StaticPopUpManager.s_objects = {}
        pass

    @staticmethod
    def loadStaticPopUpObjects(module, param):
        TraceManager.addTrace("StaticPopUpManager")
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            group = record.get("Group")
            object = record.get("Object")
            sub_object = record.get("SubObject")
            text = record.get("TextId")
            ForeignKey = bool(record.get("ForeignKey"))
            StaticPopUpManager.addPopUpObject(group, object, sub_object, text, ForeignKey)
            pass
        pass

    @staticmethod
    def addPopUpObject(groupName, objectName, sub_object_name, textID, ForeignKey):
        if sub_object_name is not None:
            SubObject = GroupManager.getObject(groupName, sub_object_name)
            Object = SubObject.getObject(objectName)
            pass
        else:
            if GroupManager.hasObject(groupName, objectName) is False:
                Trace.log("StaticPopUpManager", 0, "StaticPopUpManager.addPopUpObject: : invalid objectName name %s:%s, maybe it does not exist" % (groupName, objectName))
                return
                pass
            Object = GroupManager.getObject(groupName, objectName)
            pass
        if Object in StaticPopUpManager.s_objects:
            Trace.log("Manager", 0,
                      "StaticPopUpManager.addPopUpObject: object %s:%s already exist" % (groupName, objectName))
            return
            pass

        PopUpObject = StaticPopUpManager.StaticPopUp(textID, ForeignKey)

        StaticPopUpManager.s_objects[Object] = PopUpObject
        pass

    @staticmethod
    def findTextID(object):
        if object not in StaticPopUpManager.s_objects:
            return None
            pass

        return StaticPopUpManager.s_objects[object].textID

    @staticmethod
    def hasForeignKey(object):
        if object not in StaticPopUpManager.s_objects:
            return None
            pass
        data = StaticPopUpManager.s_objects[object]
        foreign_key = data.hasForeignKey()
        return foreign_key
