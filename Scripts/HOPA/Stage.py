from Foundation.GroupManager import GroupManager
from Foundation.Initializer import Initializer
from Foundation.Params import Params
from Foundation.SceneManager import SceneManager
from HOPA.ChapterManager import ChapterManager
from Notification import Notification


class Stage(Params, Initializer):
    def __init__(self):
        super(Stage, self).__init__()

        self.SceneName = None
        self.ZoomName = None
        self.ScenarioChapter = None

        self.Tag = None
        pass

    def _onParams(self, params):
        super(Stage, self)._onParams(params)

        self.Name = params.get("Name")
        self.Tag = params.get("Tag")
        pass

    def getTag(self):
        return self.Tag
        pass

    def setZoomName(self, zoom):
        self.ZoomName = zoom
        pass

    def getZoomName(self):
        return self.ZoomName
        pass

    def getName(self):
        return self.Name
        pass

    def setSceneName(self, SceneName):
        self.SceneName = SceneName
        pass

    def getSceneName(self):
        return self.SceneName
        pass

    def addScenarioChapter(self, ChapterName):
        ChapterManager.setCurrentChapterName(ChapterName)
        self.ScenarioChapter = ChapterManager.generateChapterScenarios(ChapterName)
        pass

    def getScenarioChapter(self):
        return self.ScenarioChapter
        pass

    def runScenarioChapter(self):
        if self.ScenarioChapter is None:
            Trace.log("Manager", 0, "Stage.runScenarioChapter ScenarioChapter is None")

            return True
            pass

        ChapterManager.setCurrentChapter(self.ScenarioChapter)

        if self.ScenarioChapter.run() is False:
            Trace.log("Manager", 0, "Stage.runScenarioChapter invalid run ScenarioChapter")

            return False
            pass

        CurrentChapterName = ChapterManager.getCurrentChapterName()

        Notification.notify(Notificator.onSetCurrentChapter, CurrentChapterName)

        return True
        pass

    def _onInitialize(self):
        super(Stage, self)._onInitialize()
        pass

    def _onFinalize(self):
        super(Stage, self)._onFinalize()

        if self.ScenarioChapter is not None:
            self.ScenarioChapter.onFinalize()
            self.ScenarioChapter = None

            ChapterManager.setCurrentChapterName(None)
            pass
        pass

    def _onInitializeFailed(self, msg):
        Trace.log("Manager", 0, "Stage '%s' tag '%s' SceneName '%s' ZoomName '%s' invalid initialize: %s" % (
            self.Name, self.Tag, self.SceneName, self.ZoomName, msg))
        pass

    def _onFinalizeFailed(self, msg):
        Trace.log("Manager", 0, "Stage '%s' tag '%s' SceneName '%s' ZoomName '%s' invalid finalize: %s" % (
            self.Name, self.Tag, self.SceneName, self.ZoomName, msg))
        pass

    def preparation(self):
        if self.initializeGroups(self.Name) is False:
            return False
            pass

        self._onPreparation()

        return True
        pass

    def _onPreparation(self):
        pass

    def run(self):
        startScene = SceneManager.getStageStartScene(self.Name)
        if startScene is not None:
            self.setSceneName(startScene)
            pass

        Notification.notify(Notificator.onStageRun, self.Name)

        lastGameScene = SceneManager.getCurrentGameSceneName()
        if lastGameScene is not None:
            self.setSceneName(lastGameScene)
            pass

        self._onRun()

        return True
        pass

    def _onRun(self):
        # self.runScenarioChapter()
        pass

    def save(self):
        save_data = self._onSave()

        return save_data
        pass

    def stop(self):
        if self.ScenarioChapter is not None:
            self.ScenarioChapter.stop()
            pass
        pass

    def _onSave(self):
        save_macroses = None

        if self.ScenarioChapter is not None:
            save_macroses = self.ScenarioChapter.save()
            pass

        save_stage = save_macroses

        return save_stage
        pass

    def load(self, load_stage):
        Notification.notify(Notificator.onStageLoad, self.Name)

        self._onLoad(load_stage)

        return True
        pass

    def _onLoad(self, load_stage):
        load_macroses = load_stage

        if self.ScenarioChapter is not None:
            self.ScenarioChapter.load(load_macroses)
            pass
        pass

    def onResume(self, load_stage):
        self._onResume(load_stage)

        Notification.notify(Notificator.onStageResume, self.Name)

        return True
        pass

    def _onResume(self, load_stage):
        pass

    def complete(self, cb):
        SceneManager.removeCurrentScene(Functor(self.__removeCurrentSceneComplete, cb))
        pass

    def __removeCurrentSceneComplete(self, cb):
        cb()
        pass

    def _onComplete(self):
        pass

    def prefetchSprite(self):
        SpriteResources = []

        for GroupName in self.MacroGroups:
            Group = GroupManager.getGroup(GroupName)

            def __visitorSprite(obj):
                if obj.getType() != "ObjectSprite":
                    return
                    pass

                SpriteResourceName = obj.getSpriteResourceName()

                if SpriteResourceName is None:
                    return
                    pass

                if Mengine.directResourceCompile(SpriteResourceName) is False:
                    return
                    pass

                SpriteResources.append(SpriteResourceName)
                pass

            Group.visitObjects(__visitorSprite)
            pass

        return SpriteResources
        pass

    def unfetchSprite(self):
        for SpriteResourceName in self.PrefetchSpriteResources:
            Mengine.directResourceRelease(SpriteResourceName)
            pass

        self.PrefetchSpriteResources = []
        pass

    def initializeGroups(self, Tag):
        if GroupManager.initializeGroupTag(Tag) is False:
            return False
            pass

        return True
