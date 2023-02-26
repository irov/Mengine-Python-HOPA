from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class SoundEffectOnObjectManager(object):
    s_soundEffects = {}
    s_soundEffectsOnce = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            GroupName = record.get("GroupName", None)
            DemonName = record.get("DemonName", None)
            ObjectName = record.get("ObjectName", None)
            Tag = record.get("Tag")
            Sound = record.get("Sound")
            Once = bool(record.get("Once", 1))

            if Mengine.hasSound(Sound) is False:
                Trace.log("Manager", 0, "SoundEffectOnObjectManager.loadSoundEffect '%s' not found sound '%s' for object '%s' group '%s'" % (param, Sound, ObjectName, GroupName))
                continue
                pass

            if GroupName is None and ObjectName is None and DemonName is None:
                Object = None
                pass
            elif isinstance(GroupManager.getGroup(GroupName), GroupManager.EmptyGroup):
                continue
                pass
            elif DemonName is None:
                Object = GroupManager.getObject(GroupName, ObjectName)
                pass
            else:
                Demon = GroupManager.getObject(GroupName, DemonName)
                Object = Demon.getObject(ObjectName)
                pass

            SoundEffectOnObjectManager.s_soundEffects[(Object, Tag)] = Sound
            SoundEffectOnObjectManager.s_soundEffectsOnce[(Object, Tag)] = Once
            pass

        return True
        pass

    @staticmethod
    def getObjectSounds():
        return SoundEffectOnObjectManager.s_soundEffects
        pass

    @staticmethod
    def getSound(Object, Tag):
        if (Object, Tag) in SoundEffectOnObjectManager.s_soundEffects:
            return SoundEffectOnObjectManager.s_soundEffects[(Object, Tag)]
            pass

        return None
        pass

    @staticmethod
    def getObjectsByTag(Tag):
        objects = []
        for object, tag in SoundEffectOnObjectManager.s_soundEffects.iterkeys():
            if tag == Tag and object is not None:
                objects.append(object)
                pass
            pass

        return objects
        pass

    @staticmethod
    def getOnce(Object, Tag):
        if (Object, Tag) in SoundEffectOnObjectManager.s_soundEffectsOnce:
            return SoundEffectOnObjectManager.s_soundEffectsOnce[(Object, Tag)]
            pass

        return None
        pass

    @staticmethod
    def onDeactivate():
        pass
    pass