from Foundation.DemonManager import DemonManager
from Foundation.System import System

class SystemBoneBoard(System):

    def __init__(self):
        super(SystemBoneBoard, self).__init__()

        self.scenes = {}
        self.HelperState = None
        self.BoneActivities = None
        self.ButtonAvailable = None
        self.UseAvailable = None

        pass

    def _onParams(self, params):
        super(SystemBoneBoard, self)._onParams(params)
        pass

    def _onSave(self):
        HelperState = self.boneDemonObject.getParam("HelperState")
        BoneActivities = self.boneDemonObject.getParam("BoneActivities")
        ButtonAvailable = self.boneDemonObject.getParam("ButtonAvailable")
        UseAvailable = self.boneDemonObject.getParam("UseAvailable")

        saveDocument = (HelperState, BoneActivities, ButtonAvailable, UseAvailable)

        return saveDocument
        pass

    def _onLoad(self, data_save):
        self.HelperState, self.BoneActivities, self.ButtonAvailable, self.UseAvailable = data_save
        pass

    def _onRun(self):
        self.boneDemonObject = DemonManager.getDemon("BoneBoard")

        if self.HelperState is not None:
            self.boneDemonObject.setParam("HelperState", self.HelperState)
            self.boneDemonObject.setParam("BoneActivities", self.BoneActivities)
            self.boneDemonObject.setParam("ButtonAvailable", self.ButtonAvailable)
            self.boneDemonObject.setParam("UseAvailable", self.UseAvailable)
            pass

        self.addObserver(Notificator.onButtonClick, self.on_show_bones)
        self.addObserver(Notificator.onSocketClick, self.on_socket_click)
        self.addObserver(Notificator.onBoneAdd, self.on_bone_come)
        self.addObserver(Notificator.onItemClick, self.on_item_click)
        self.addObserver(Notificator.onBoneUse, self.on_bone_usage)
        self.addObserver(Notificator.onItemMouseEnter, self.onItemEntered)
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        self.addObserver(Notificator.onSceneLeave, self.__onSceneLeave)

        return True
        pass

    def _onStop(self):
        self.boneDemonObject.removeAllData()
        self.boneDemonObject = None
        self.boneInstance = None
        self.scenes = {}
        pass

    def __onSceneInit(self, sceneName):
        if self.boneDemonObject is None:
            return False
            pass

        if self.boneDemonObject.isActive() is False:
            return False
            pass

        self.boneInstance = self.boneDemonObject.getEntity()

        if self.boneInstance is None:
            return False
            pass

        if sceneName not in self.scenes.values():
            return False
            pass

        self.boneInstance.onCasualShowHelp()

        return False
        pass

    def __onSceneLeave(self, sceneName):
        if self.boneDemonObject is None:
            return False
            pass
        if self.boneDemonObject.isActive() is False:
            return False
            pass
        self.boneInstance = self.boneDemonObject.getEntity()
        if self.boneInstance is None:
            return False
            pass
        #
        if sceneName not in self.scenes.values():
            return False
            pass

        self.boneInstance.onCasualHideHelp()
        return False
        pass

    def on_show_bones(self, *args):
        if self.boneDemonObject.isActive() is False:
            return False
            pass
        self.boneInstance = self.boneDemonObject.getEntity()
        if self.boneInstance.isActivate() is False:
            return False
            pass
        self.boneInstance.on_show_bones(*args)
        return False
        pass

    def on_socket_click(self, *args):
        if self.boneDemonObject.isActive() is False:
            return False
            pass
        self.boneInstance = self.boneDemonObject.getEntity()
        if self.boneInstance.isActivate() is False:
            return False
            pass
        self.boneInstance.on_socket_click(*args)
        return False
        pass

    def on_bone_come(self, invItem, relatedItem):
        if self.boneDemonObject.isActive() is False:
            return False
            pass

        self.boneInstance = self.boneDemonObject.getEntity()

        if self.boneInstance.isActivate() is False:
            return False
            pass

        if relatedItem.startswith("done"):
            self.boneInstance.onCasualHideHelp()
            if relatedItem[5:] not in self.scenes.keys():
                return False
                pass
            del self.scenes[relatedItem[5:]]
            return False
            pass

        self.boneInstance.on_bone_come(invItem, relatedItem)

        return False
        pass

    def on_item_click(self, *args):
        if self.boneDemonObject.isActive() is False:
            return False
            pass
        self.boneInstance = self.boneDemonObject.getEntity()
        if self.boneInstance.isActivate() is False:
            return False
            pass
        self.boneInstance.on_item_click(*args)
        return False
        pass

    def on_bone_usage(self, itemName, groupName=None):
        if self.boneDemonObject.isActive() is False:
            return False
            pass
        self.boneInstance = self.boneDemonObject.getEntity()
        if self.boneInstance.isActivate() is False:
            return False
            pass

        if itemName.startswith("done"):
            self.boneInstance.onCasualHideHelp()
            del self.scenes[itemName[5:]]
            pass
        else:
            self.scenes[itemName] = groupName
            self.boneInstance.onCasualShowHelp()
            pass

        self.boneInstance.on_bone_usage(itemName, groupName)
        return False
        pass

    def onItemEntered(self, itemObject):
        if self.boneDemonObject.isActive() is False:
            return False
            pass
        self.boneInstance = self.boneDemonObject.getEntity()
        self.boneInstance.onItemEntered(itemObject)
        return False
        pass

    pass