from Foundation.SceneManager import SceneManager
from Foundation.System import System


class SystemCommandLayerGroupEnableSave(System):
    def __init__(self):
        super(SystemCommandLayerGroupEnableSave, self).__init__()
        self.enableLayers = []
        pass

    def _onSave(self):
        save_data = self.enableLayers
        # print "_onSave", self.enableLayers
        return save_data
        pass

    def _onLoad(self, data_save):
        self.enableLayers = data_save
        # print "_onLoad", self.enableLayers
        pass

    def _onRun(self):
        # print "SystemCommandLayerGroupEnableSave _onRun"
        self.addObserver(Notificator.onCommandLayerEnable, self.__onCommandLayerEnable)
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)

        return True
        pass

    def __onSceneInit(self, sceneName):
        isGameScene = SceneManager.isGameScene(sceneName)
        if isGameScene is True:
            for layerName in self.enableLayers:
                if SceneManager.hasLayerScene(layerName) is False:
                    continue
                    pass
                LayerGroup = SceneManager.getSceneLayerGroup(sceneName, layerName)
                if LayerGroup is None:
                    continue
                    pass
                Enable = LayerGroup.getEnable()
                if Enable is True:
                    continue
                    pass
                LayerGroup.onEnable()
                pass
            pass
        return False
        pass

    def __onCommandLayerEnable(self, layerName, value):
        CurrentSceneName = SceneManager.getCurrentSceneName()

        if value is False and layerName in self.enableLayers:
            self.enableLayers.remove(layerName)
            pass
        elif value is True and layerName not in self.enableLayers:
            self.enableLayers.append(layerName)
            pass

        # print "self.enableLayers", self.enableLayers

        if CurrentSceneName is not None:
            if SceneManager.hasLayerScene(layerName) is False:
                return False
                pass
            LayerGroup = SceneManager.getSceneLayerGroup(CurrentSceneName, layerName)
            if LayerGroup is None:
                return False
                pass
            Enable = LayerGroup.getEnable()
            if Enable is value:
                return False
                pass

            if value is True:
                LayerGroup.onEnable()
            else:
                LayerGroup.onDisable()
                pass
            pass

        return False
        pass

    def _onStop(self):
        # print "SystemCommandLayerGroupEnableSave _onStop"
        pass

    pass
