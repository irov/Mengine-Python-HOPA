from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager
from Foundation.SceneManager import SceneManager
from Notification import Notification

class StageManager(Manager):
    s_stages = {}
    s_stageLabels = {}
    s_currentStage = None

    @staticmethod
    def _onInitialize():
        StageManager.addObserver(Notificator.onSessionLoadComplete, StageManager.__onSessionLoadComplete)
        StageManager.addObserver(Notificator.onSessionRemove, StageManager.__onSessionRemove)
        StageManager.addObserver(Notificator.onSessionRemoveComplete, StageManager.__onSessionRemoveComplete)
        pass

    @staticmethod
    def _onFinalize():
        StageManager.s_stages = {}

        if StageManager.s_currentStage is not None:
            StageManager.s_currentStage.onFinalize()
            StageManager.s_currentStage = None
            pass
        pass

    @staticmethod
    def _onSave():
        dict_save = {}

        hasCurrentStage = StageManager.hasCurrentStage()

        dict_save["hasCurrentStage"] = hasCurrentStage

        if hasCurrentStage is False:
            return dict_save
            pass

        stage = StageManager.s_currentStage
        stage_name = stage.getName()
        save_stage = stage.save()
        save_data = (stage_name, save_stage)

        dict_save["Data"] = save_data

        return dict_save
        pass

    @staticmethod
    def _onLoad(dict_save):
        hasCurrentStage = dict_save["hasCurrentStage"]

        if hasCurrentStage is False:
            return False
            pass

        load_data = dict_save["Data"]

        if load_data is None:
            Trace.log("Manager", 0, "StageManager.loadStage load_account is None")

            Notification.notify(Notificator.onStageInvalidLoad)
            return False
            pass

        name, load_stage = load_data

        stageType, tag = StageManager.s_stages.get(name)

        stage = stageType()

        params = dict(Name=name, Tag=tag)
        stage.onParams(params)

        if stage.onInitialize() is False:
            return False
            pass

        StageManager.s_currentStage = stage

        stage.preparation()
        stage.load(load_stage)

        return True
        pass

    @staticmethod
    def __onSessionLoadComplete():
        if StageManager.hasCurrentStage() is False:
            return False
            pass

        stage = StageManager.getCurrentStage()

        if stage.runScenarioChapter() is False:
            return False
            pass

        Notification.notify(Notificator.onStageInit, stage.Name)

        return False
        pass

    @staticmethod
    def __onSessionRemove():
        StageManager.stopStage()

        return False
        pass

    @staticmethod
    def __onSessionRemoveComplete():
        StageManager.removeCurrentStage()

        return False
        pass

    @staticmethod
    def importStages(module, param):
        StageParam = Mengine.getParam(param)
        for values in StageParam:
            stageName = values[0].strip()
            if stageName == "":
                return
                pass

            StageManager.importStage(module, stageName)
            pass
        pass

    @staticmethod
    def importStage(module, name, tag):
        Name = "%s" % (name)
        FromName = module
        ModuleName = "%s.%s" % (FromName, Name)
        Module = __import__(ModuleName, fromlist=[FromName])
        Type = getattr(Module, Name)

        StageManager.addStage(name, Type, tag)
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Module = record.get("Module")
            Name = record.get("Name")
            Tag = record.get("Tag")
            StartScene = record.get("StartScene")
            Label = record.get("Label")

            StageManager.s_stageLabels[Name] = Label

            StageManager.importStage(Module, Name, Tag)
            SceneManager.addStageStartScenes(Name, StartScene)
            pass

        return True
        pass

    @staticmethod
    def getStageLabels():
        return StageManager.s_stageLabels
        pass

    @staticmethod
    def hasStage(name):
        return name in StageManager.s_stages
        pass

    @staticmethod
    def addStage(name, groupType, tag):
        StageManager.s_stages[name] = (groupType, tag)
        pass

    @staticmethod
    def getStage(name):
        stageType, tag = StageManager.s_stages.get(name)
        return stageType
        pass

    @staticmethod
    def removeCurrentStage():
        if StageManager.s_currentStage is not None:
            StageManager.s_currentStage.onFinalize()
            StageManager.s_currentStage = None
            pass
        pass

    @staticmethod
    def getCurrentStage():
        if StageManager.s_currentStage is None:
            return None
            pass

        return StageManager.s_currentStage
        pass

    @staticmethod
    def hasCurrentStage():
        if StageManager.s_currentStage is None:
            return False
            pass

        return True
        pass

    @staticmethod
    def stopStage():
        if StageManager.s_currentStage is None:
            return False
            pass

        stage = StageManager.s_currentStage

        stage.stop()
        pass

    @staticmethod
    def runStage(name):
        SceneManager.setCurrentGameSceneName(None)

        if StageManager.s_currentStage is not None:
            StageManager.s_currentStage.onFinalize()
            StageManager.s_currentStage = None
            pass

        if name not in StageManager.s_stages:
            Trace.log("Manager", 0, "StageManager.runStage no have stage with this name '%s'" % (name))
            return False
            pass

        stageType, tag = StageManager.s_stages.get(name)

        stage = stageType()

        params = dict(Name=name, Tag=tag)
        stage.onParams(params)

        StageManager.s_currentStage = stage

        if stage.onInitialize() is False:
            Trace.log("Manager", 0, "StageManager.runStage invalid stage '%s' initialize" % (name))

            return False
            pass

        if _DEVELOPMENT is True:
            Mengine.watchdog("StageManager preparation")
            pass

        stage.preparation()

        if _DEVELOPMENT is True:
            print("StageManager stage preparation %s %f" % (name, Mengine.watchdog("StageManager preparation")))
            pass

        if _DEVELOPMENT is True:
            Mengine.watchdog("StageManager run")
            pass

        if stage.runScenarioChapter() is False:
            Trace.log("Manager", 0, "StageManager.runStage invalid run ScenarioChapter")

            return False
            pass

        stage.run()

        if _DEVELOPMENT is True:
            print("StageManager stage run %s %f" % (name, Mengine.watchdog("StageManager run")))
            pass

        if _DEVELOPMENT is True:
            Mengine.watchdog("StageManager init")
            pass

        Notification.notify(Notificator.onStageInit, name)

        if _DEVELOPMENT is True:
            print("StageManager stage init %s %f" % (name, Mengine.watchdog("StageManager init")))
            pass

        return True
        pass
    pass