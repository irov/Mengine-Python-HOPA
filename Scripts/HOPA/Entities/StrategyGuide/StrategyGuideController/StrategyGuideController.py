from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Notification import Notification

from StrategyGuideControllerManager import StrategyGuideControllerManager


class StrategyGuideController(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addActionActivate(Type, "CurrentPage", Update=StrategyGuideController.__updateCurrentPage)
        pass

    def __updateCurrentPage(self, value):
        if self.currentPage is not None:
            self.currentPage.setEnable(False)
            pass

        self.currentPage = self.pages[value]
        self.currentPage.setEnable(True)
        pass

    def __init__(self):
        super(StrategyGuideController, self).__init__()
        self.pages = {}
        self.currentPage = None
        self.ButtonMenu = None
        self.ButtonRight = None
        self.ButtonLeft = None
        self.ButtonBack = None
        self.ButtonClickObserver = None
        pass

    def _onPreparation(self):
        super(StrategyGuideController, self)._onPreparation()
        self.pages = StrategyGuideControllerManager.getPages()

        self.ButtonMenu = self.object.getObject("Button_Menu")
        self.ButtonBack = self.object.getObject("Button_Back")
        self.ButtonRight = self.object.getObject("Button_ArrowRight")
        self.ButtonLeft = self.object.getObject("Button_ArrowLeft")

        self.ButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)

        self.ButtonMenu.setInteractive(True)
        self.ButtonRight.setInteractive(True)
        self.ButtonLeft.setInteractive(True)
        self.ButtonBack.setInteractive(True)
        self.updateButtons()
        pass

    def __onButtonClick(self, button):
        if button is self.ButtonMenu:
            with TaskManager.createTaskChain() as tc:
                tc.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuidePages", Value=False)
                tc.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuideZoom", Value=False)
                pass
            return False
            pass
        if button is self.ButtonBack:
            systemStrategyGuideButton = SystemManager.getSystem("SystemStrategyGuideButton")
            systemStrategyGuideButton.setIsGuideMenu(True)
            with TaskManager.createTaskChain() as tc:
                tc.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuideMenu", Value=True)
                tc.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuidePages", Value=False)
                tc.addTask("TaskSceneLayerGroupEnable", LayerName="StrategyGuideZoom", Value=False)
                pass
            return False
            pass
        if button is self.ButtonLeft:
            self.managePages(-1)
            self.updateButtons()
            return False
            pass

        if button is self.ButtonRight:
            self.managePages(+1)
            self.updateButtons()
            return False
            pass

        return False
        pass

    def managePages(self, value):
        tmp = self.CurrentPage
        self.object.setParam("CurrentPage", tmp + value)
        return
        pass

    def updateButtons(self):
        if self.CurrentPage == 1:
            self.ButtonLeft.setEnable(False)
            pass
        else:
            self.ButtonLeft.setEnable(True)
            pass

        if self.CurrentPage == max(self.pages.keys()):
            self.ButtonRight.setEnable(False)
            pass
        else:
            self.ButtonRight.setEnable(True)
            pass
        pass

    def _onActivate(self):
        super(StrategyGuideController, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(StrategyGuideController, self)._onDeactivate()
        Notification.removeObserver(self.ButtonClickObserver)
        self.ButtonClickObserver = None

        self.ButtonMenu.setInteractive(False)
        self.ButtonRight.setInteractive(False)
        self.ButtonLeft.setInteractive(False)
        self.ButtonBack.setInteractive(False)

        self.ButtonMenu = None
        self.ButtonRight = None
        self.ButtonLeft = None
        self.ButtonBack = None

        self.pages = {}
        self.currentPage = None

        pass

    pass
