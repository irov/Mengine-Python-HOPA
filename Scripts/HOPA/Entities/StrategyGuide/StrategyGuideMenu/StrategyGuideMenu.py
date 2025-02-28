from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Notification import Notification

from StrategyGuideMenuManager import StrategyGuideMenuManager


class StrategyGuideMenu(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        pass

    def __init__(self):
        super(StrategyGuideMenu, self).__init__()
        self.buttons = None
        self.ButtonClickObserver = None
        self.ButtonMenu = None
        pass

    def _onPreparation(self):
        super(StrategyGuideMenu, self)._onPreparation()
        self.ButtonMenu = self.object.getObject("Button_Menu")
        self.ButtonMenu.setInteractive(True)

        self.buttons = StrategyGuideMenuManager.getButtons()

        for button in self.buttons.keys():
            button.setInteractive(True)
            pass
        pass

    def _onActivate(self):
        super(StrategyGuideMenu, self)._onActivate()
        self.ButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)
        pass

    def __onButtonClick(self, button):
        if button is self.ButtonMenu:
            TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName="StrategyGuideMenu", Value=False)
            return False
            pass
        if button in self.buttons.keys():
            pageId = self.buttons[button]
            self.openPage(pageId)
            return False
            pass
        return False
        pass

    def openPage(self, pageId):
        systemStrategyGuideButton = SystemManager.getSystem("SystemStrategyGuideButton")
        systemStrategyGuideButton.setIsGuideMenu(False)

        guideController = DemonManager.getDemon("StrategyGuideController")
        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuideMenu", Value=False)
            tc.addParam(guideController, "CurrentPage", pageId)
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuidePages", Value=True)
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuideZoom", Value=True)
            pass
        pass

    def _onDeactivate(self):
        super(StrategyGuideMenu, self)._onDeactivate()
        self.ButtonMenu.setInteractive(False)
        self.ButtonMenu = None

        for button in self.buttons.keys():
            button.setInteractive(False)
            pass

        self.buttons = None

        Notification.removeObserver(self.ButtonClickObserver)
        self.ButtonClickObserver = None
        pass

    pass
