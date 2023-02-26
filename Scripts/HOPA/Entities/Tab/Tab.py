from Foundation.Entity.BaseEntity import BaseEntity
from Notification import Notification

class Tab(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "Tabs")
        Type.addAction(Type, "CurrentTab")
        pass

    def __init__(self):
        super(Tab, self).__init__()

        self.buttons = []
        self.activeTab = None
        pass

    def _onDeactivate(self):
        for button in self.buttons:
            button.setInteractive(False)
            pass
        self.buttons = []
        Notification.removeObserver(self.onButtonClickObserver)
        pass

    def _onActivate(self):
        for tab in self.Tabs.itervalues():
            if tab == self.CurrentTab:
                tab.setEnable(True)
                continue
            tab.setEnable(False)
            pass

        for buttonName in self.Tabs.keys():
            button = self.object.getObject(buttonName)
            self.buttons.append(button)
            button.setInteractive(True)
            pass

        self.onButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self._changeTab)
        pass

    def _changeTab(self, clickButton):
        if clickButton not in self.buttons:
            return False

        for tab in self.Tabs.itervalues():
            tab.setEnable(False)
            pass

        activeTab = self.Tabs[clickButton.name]
        activeTab.setEnable(True)
        Notification.notify(Notificator.onTabClick, self.object)
        #        self.object.setParam("CurrentTab",activeTab)

        return False

    pass