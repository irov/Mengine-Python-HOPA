import Trace
from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class SoundObjectsManager(object):
    s_soundObjects = {}

    class SoundObject(object):
        def __init__(self, sound, object):
            self.sound = sound
            self.object = object
            pass

        def getSound(self):
            return self.sound
            pass

        def getObject(self):
            return self.object
            pass
        pass

    @staticmethod
    def loadSoundObjects(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Event = record.get("Event")
            Sound = record.get("Sound")
            ObjectName = record.get("ObjectName")
            Parents = record.get("Parents")

            if Mengine.hasSound(Sound) is False:
                Trace.log("Manager", 0, "SoundObjectsManager loadSoundObjects not found %s" % (Sound))
                continue
                pass

            GroupName = Parents[0]
            Group = GroupManager.getGroup(GroupName)
            for parentName in Parents[1:]:
                Group = Group.getObject(parentName)
                pass

            Object = Group.getObject(ObjectName)
            SoundObject = SoundObjectsManager.SoundObject(Sound, Object)

            SoundObjectsManager.s_soundObjects.setdefault(Event, []).append(SoundObject)
            pass
        pass

    @staticmethod
    def getSoundObjects():
        return SoundObjectsManager.s_soundObjects
        pass

    pass