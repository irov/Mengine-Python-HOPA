from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

from ExtrasWallpaperManager import ExtrasWallpaperManager

class ExtrasWallpaper(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        pass

    def _updateConcept(self, value):
        if value is None:
            pass
        pass

    def __init__(self):
        super(ExtrasWallpaper, self).__init__()
        self.ButtonLeft = None
        self.ButtonRight = None
        self.ButtonSave = None
        self.ButtonClickObserver = None
        self.concepts = []
        self.resources = {}
        self.currentIndex = 0
        pass

    def _onPreparation(self):
        super(ExtrasWallpaper, self)._onPreparation()
        Data = ExtrasWallpaperManager.getData()

        for spriteName, resource in Data.iteritems():
            sprite = self.object.getObject(spriteName)
            sprite.setEnable(False)
            self.resources[sprite] = resource
            self.concepts.append(sprite)
            pass

        self.ButtonLeft = self.object.getObject("Button_Left")
        self.ButtonLeft.setInteractive(True)

        self.ButtonRight = self.object.getObject("Button_Right")
        self.ButtonRight.setInteractive(True)

        self.ButtonSave = self.object.getObject("Button_Save")
        self.ButtonSave.setInteractive(True)
        self.concepts[self.currentIndex].setEnable(True)
        pass

    def __update(self, value):
        self.concepts[self.currentIndex].setEnable(False)

        tmpValue = self.currentIndex + value
        if tmpValue >= len(self.concepts):
            tmpValue = 0
            pass
        elif tmpValue < 0:
            tmpValue = len(self.concepts) - 1
            pass

        self.currentIndex = tmpValue
        self.concepts[self.currentIndex].setEnable(True)
        pass

    def _onActivate(self):
        super(ExtrasWallpaper, self)._onActivate()
        self.ButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)
        pass

    def __onButtonClick(self, button):
        if button is self.ButtonRight:
            self.__update(1)
            return False
            pass
        if button is self.ButtonLeft:
            self.__update(-1)
            return False
            pass

        if button is self.ButtonSave:
            self.saveWallpaper()
            return False
            pass
        return False
        pass

    def saveWallpaper(self):
        wallpaperResourceName = self.resources[self.concepts[self.currentIndex]][0]
        fileName = self.resources[self.concepts[self.currentIndex]][1]
        validResource = Mengine.validResource(wallpaperResourceName)
        if validResource is True:
            Mengine.copyUserPicture(wallpaperResourceName, fileName)
            pass
        else:
            Trace.log("Entity", 0, "Resource not valid, copying not proceed...")
            pass

        with TaskManager.createTaskChain() as tc:
            tc.addTask("AliasFadeIn", FadeGroupName="Fade", To=0.5, Time=0.25 * 1000)  # speed fix
            tc.addTask("AliasMessageOKShow", TextID="ID_WALLPAPERSAVE")
            tc.addTask("TaskButtonClick", GroupName="MessageOK", ButtonName="Button_OK")
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="MessageOK", Value=False)
            tc.addTask("AliasFadeOut", FadeGroupName="Fade", Time=0.25 * 1000, From=0.5)  # speed fix
            pass
        pass

    def _onDeactivate(self):
        super(ExtrasWallpaper, self)._onDeactivate()

        Notification.removeObserver(self.ButtonClickObserver)
        self.ButtonClickObserver = None

        self.ButtonLeft.setInteractive(False)
        self.ButtonRight.setInteractive(False)
        self.ButtonSave.setInteractive(False)
        pass

    pass
