from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from HOPA.MenuHelpManager import MenuHelpManager

class MenuHelp(BaseEntity):
    def __init__(self):
        super(MenuHelp, self).__init__()
        self.Socket_Block = None
        self.Button_Left = None
        self.Button_Right = None
        self.nextPageID = []
        self.onButtonClickObserver = None
        self.LayerGroup = None
        pass

    def _onDeactivate(self):
        self.Socket_Block.setInteractive(False)

        self.Button_Left.setInteractive(False)
        self.Button_Right.setInteractive(False)
        Notification.removeObserver(self.onButtonClickObserver)

        if self.LayerGroup is not None:
            self.LayerGroup.onDisable()
            pass
        pass

    def _onActivate(self):
        self.Socket_Block = self.object.getObject("Socket_Block")
        self.Socket_Block.setInteractive(True)

        self.Button_Left = self.object.getObject("Button_Left")
        self.Button_Right = self.object.getObject("Button_Right")

        self.Button_Left.setInteractive(True)
        self.Button_Right.setInteractive(True)

        self.nextPageID = "Page1"

        self._loadPage()

        self.onButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self._changePage)
        pass

    def _loadPage(self):
        if self.LayerGroup is not None:
            self.LayerGroup.onDisable()
            pass

        Page = MenuHelpManager.getPage(self.nextPageID)

        CurrentSceneName = SceneManager.getCurrentSceneName()
        tempGroup = SceneManager.getSceneLayerGroup(CurrentSceneName, Page.groupName)
        tempGroup.onEnable()

        self.object.getGroup().getEntity().addChild(tempGroup.getEntity())
        self.LayerGroup = tempGroup

        currentGroup = GroupManager.getGroup(Page.groupName)
        for index, textID in enumerate(Page.textIDs):
            objectText = currentGroup.getObject("Text_Message%s" % (index))
            objectText.setParam("TextID", textID)
            pass

        tempIdRight = MenuHelpManager.getNextPage(self.nextPageID)
        if tempIdRight is None:
            self.Button_Right.setEnable(False)
            pass
        else:
            self.Button_Right.setEnable(True)
            pass

        tempIdLeft = MenuHelpManager.getPreviousPage(self.nextPageID)
        if tempIdLeft is None:
            self.Button_Left.setEnable(False)
            pass
        else:
            self.Button_Left.setEnable(True)
            pass

        pass

    def _changePage(self, button):
        if button is not self.Button_Left and button is not self.Button_Right:
            return False
            pass

        if button == self.Button_Left:
            tempId = MenuHelpManager.getPreviousPage(self.nextPageID)
            pass

        elif button == self.Button_Right:
            tempId = MenuHelpManager.getNextPage(self.nextPageID)
            pass

        if tempId is None:
            return False
            pass

        self.LayerGroup.getEntity().removeFromParent()

        self.nextPageID = tempId

        self._loadPage()

        return False
        pass

    pass
