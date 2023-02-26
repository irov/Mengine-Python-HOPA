from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class ParallaxEffectManager(Manager):
    s_data = {}

    class ParallaxEffect(object):
        def __init__(self, obj, group, ParallaxEffect, ArtResolution, Time):
            self.obj = obj
            self.group = group
            self.parallaxEffect = ParallaxEffect
            self.ArtResolution = ArtResolution
            self.Time = Time
            pass

        def getObjectName(self):
            return self.obj

        def getGroupName(self):
            return self.group

        def getParallaxEffect(self):
            return self.parallaxEffect

    class Param(object):
        def __init__(self, SceneName, ScreenResolution, CameraSpeed, Objects):
            self.SceneName = SceneName
            self.ScreenResolution = ScreenResolution
            self.CameraSpeed = CameraSpeed
            self.Objects = Objects
            pass

        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            SceneName = record.get("SceneName")
            ScreenResolution = float(record.get("ScreenResolution", 1280))
            CameraSpeed = float(record.get("CameraSpeed", 10))
            result = ParallaxEffectManager.addParam(module, SceneName, ScreenResolution, CameraSpeed)

            if result is False:
                error_msg = "ParallaxEffectManager invalid addParam {}".format(SceneName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True
        pass

    @staticmethod
    def addParam(module, SceneName, ScreenResolution, CameraSpeed):
        param = SceneName
        records = DatabaseManager.getDatabaseRecords(module, param)
        objects = {}
        for record in records:
            ObjectName = record.get("ObjectName")
            GroupName = record.get("GroupName")
            ParallaxEffect = record.get("ParallaxEffect", 0)
            ArtResolution = float(record.get("ArtResolution", 1280))
            Time = float(record.get("Time", 500.0))

            paralax = ParallaxEffectManager.ParallaxEffect(ObjectName, GroupName, ParallaxEffect, ArtResolution, Time)
            objects[ObjectName] = (paralax)
        NewParam = ParallaxEffectManager.Param(SceneName, ScreenResolution, CameraSpeed, objects)
        ParallaxEffectManager.s_data[SceneName] = NewParam
        pass

    @staticmethod
    def getData(SceneName):
        return ParallaxEffectManager.s_data[SceneName]

    @staticmethod
    def getScenes():
        return ParallaxEffectManager.s_data.keys()

    @staticmethod
    def hasScene(scene_name):
        return scene_name in ParallaxEffectManager.s_data