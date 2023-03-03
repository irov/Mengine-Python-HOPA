from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class ExtrasMusicManager(object):
    s_objects = {}

    class Data(object):
        def __init__(self, play, pause, save, resource):
            self.play = play
            self.pause = pause
            self.save = save
            self.resource = resource
            pass

        def getPlayButtons(self):
            return self.play
            pass

        def getSaveButtons(self):
            return self.save
            pass

        def getPauseButtons(self):
            return self.pause
            pass

        def getResource(self):
            return self.resource
            pass

        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            GroupName = record.get("GroupName")
            DemonName = record.get("DemonName")
            Collection = record.get("Collection")

            DemonObject = GroupManager.getObject(GroupName, DemonName)

            data = ExtrasMusicManager.loadCollection(DemonObject, module, Collection)

            ExtrasMusicManager.s_objects[DemonObject] = data
            pass
        pass

    @staticmethod
    def loadCollection(demon, module, param):
        play = {}
        save = {}
        pause = {}
        resources = {}
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            Track = record.get("TrackResourceName")
            PlayButtonName = record.get("PlayButton")
            PauseButtonName = record.get("PauseButton")
            SaveButtonName = record.get("SaveButton")
            SaveResource = record.get("SaveResource")
            FileName = record.get("FileName")

            playButton = demon.getObject(PlayButtonName)
            play[playButton] = Track

            pauseButton = demon.getObject(PauseButtonName)
            pause[pauseButton] = Track

            saveButton = demon.getObject(SaveButtonName)
            save[saveButton] = Track

            resources[Track] = (SaveResource, FileName)
            pass

        data = ExtrasMusicManager.Data(play, pause, save, resources)
        return data
        pass

    @staticmethod
    def getData(object):
        return ExtrasMusicManager.s_objects[object]
        pass

    pass
