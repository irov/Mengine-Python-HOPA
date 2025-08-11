from Foundation.DemonManager import DemonManager
from Foundation.System import System

class SystemMenuGreeting(System):
    def __init__(self):
        super(SystemMenuGreeting, self).__init__()
        self.onAccountChangeNameObserver = None
        self.Greeting = None
        pass

    def _onInitialize(self):
        super(SystemMenuGreeting, self)._onInitialize()

        if _DEVELOPMENT is True:
            if DemonManager.hasDemon("MenuGreeting") is False:
                self.initializeFailed("SystemMenuGreeting not found MenuGreeting demon!")

        self.Greeting = DemonManager.getDemon("MenuGreeting")

        return True

    def _onRun(self):
        if Mengine.hasCurrentAccount() is True:
            AccountName = Mengine.getCurrentAccountName()
            Name = Mengine.getAccountSetting(AccountName, "Name")
            self.__onAccountChangeName(Name)
            pass

        self.onAccountChangeNameObserver = Notification.addObserver(Notificator.onAccountChangeName, self.__onAccountChangeName)
        return True
        pass

    def __onAccountChangeName(self, newName):
        if newName == "Default" or newName == "" or newName is None or newName == u"Default":
            self.Greeting.setEnable(False)
            return False
            pass

        self.Greeting.setEnable(True)

        if self.Greeting.isActive() is True:
            self.Greeting.getEntity().updateText()
            pass

        return False
        pass

    def _onStop(self):
        Notification.removeObserver(self.onAccountChangeNameObserver)
