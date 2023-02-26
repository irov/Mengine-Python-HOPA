from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Notification import Notification

from SplashScreenManager import SplashScreenManager

class Splash(object):
    def __init__(self, resource, type, resource_name):
        self.resource = resource
        self.type = type
        self.name = resource_name
        self.shape = None
        pass

    def create(self):
        if self.type == "Sprite":
            shape = Mengine.createSprite("splash", self.resource)
        elif self.type == "Video":
            shape = Mengine.createVideo("splash", "ShapeQuadSize", self.resource)

            contentResolution = Mengine.getContentResolution()
            width = contentResolution.getWidthF()
            height = contentResolution.getHeightF()
            shape.setSize((width, height))
        else:
            Trace.log("Entity", 0, "SplashScreen: can't create splash for unknown {!r} [{!r}]".format(self.type, self.name))
            return False
            pass

        self.shape = shape

        return True

    def scopeShow(self, source, Time):
        if self.type == "Sprite":
            source.addDelay(Time)
        elif self.type == "Video":
            surface = self.shape.getSurface()

            source.addTask("TaskSurfaceAnimationPlay", Surface=surface)
            pass
        pass

class SplashScreen(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addActionActivate(Type, "Play", Update=SplashScreen._updatePlay)

    def __init__(self):
        super(SplashScreen, self).__init__()

        self.SplashScreens = []

    def _updatePlay(self, value):
        if value is False:
            return

        self.playSplashScreens()

    def playSplashScreens(self):
        SplashScreenData = SplashScreenManager.getSplashScreenData()

        SplashScreens = []

        for Data in SplashScreenData:
            if Mengine.hasResource(Data.ResourceName) is False:
                continue

            resource = Mengine.getResourceReference(Data.ResourceName)

            content = resource.getContent()

            FileGroup = content.getFileGroup()
            FileGroupName = FileGroup.getName()
            FilePath = content.getFilePath()

            if Mengine.existFile(FileGroupName, FilePath) is False:
                continue

            splash = Splash(resource, Data.Type, Data.ResourceName)

            if splash.create() is False:
                continue

            splash.shape.disable()

            self.addChild(splash.shape)

            SplashScreens.append(splash)

        if len(SplashScreens) == 0:
            self.__onPlaySplashScreens(False, [])
            return

        with TaskManager.createTaskChain(Group=self.object, Cb=self.__onPlaySplashScreens, CbArgs=(SplashScreens,)) as tc:
            SplashScreenFadeTime = DefaultManager.getDefaultFloat("SplashScreenFadeTime", 1.0)
            SplashScreenFadeTime *= 1000.0  # speed fix
            SplashScreenTime = DefaultManager.getDefaultFloat("SplashScreenTime", 1.0)
            SplashScreenTime *= 1000.0  # speed fix

            if SplashScreenFadeTime > 0:
                tc.addTask("AliasFadeIn", To=1.0, Time=SplashScreenFadeTime)

            for splash in SplashScreens:
                tc.addTask("TaskNodeEnable", Node=splash.shape, Value=True)

                with tc.addParallelTask(2) as (tc_fade, tc_skip):
                    if SplashScreenFadeTime > 0:
                        tc_fade.addTask("AliasFadeOut", From=1.0, Time=SplashScreenFadeTime)

                    with tc_skip.addRaceTask(2) as (tc_show, tc_skip):
                        tc_show.addScope(splash.scopeShow, Time=SplashScreenFadeTime + SplashScreenTime)
                        tc_skip.addTask("TaskMouseButtonClickEnd")

                if SplashScreenFadeTime > 0:
                    tc.addTask("AliasFadeIn", To=1.0, Time=SplashScreenFadeTime)

                tc.addTask("TaskNodeEnable", Node=splash.shape, Value=False)

            tc.addFunction(Mengine.moduleMessage, "ModuleGoogleAdMob", "Show", dict())
            pass
        pass

    def __onPlaySplashScreens(self, isSkip, SplashScreens):
        for splash in SplashScreens:
            Mengine.destroyNode(splash.shape)

        Notification.notify(Notificator.onPlaySplashScreens)
        pass