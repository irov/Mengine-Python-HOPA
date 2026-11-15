from Foundation.Providers.AdminPanelProvider import AdminPanelProvider
from Foundation.SceneManager import SceneManager
from Foundation.SessionManager import SessionManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager


class SystemOpButtonLanguage(System):
    def __init__(self):
        super(SystemOpButtonLanguage, self).__init__()

        self.__defaultLocale = Mengine.getLocale()
        self.__ready = False
        pass

    @staticmethod
    def _onAvailable(params):
        if _DEVELOPMENT is False:
            return False

        return AdminPanelProvider.hasProvider()

    def _onStop(self):
        self.onOpButtonStop()
        pass

    def onOpButtonReady(self):
        if self.__ready is True:
            return

        self.__ready = True

        AdminPanelProvider.addButton("Localization", "auto", "Automatic", self.__changeLocale, self.__defaultLocale, True)

        for locale in Mengine.getLocales():
            title = str(locale)
            AdminPanelProvider.addButton("Localization", title, title, self.__changeLocale, locale)
            pass
        pass

    def onOpButtonStop(self):
        if self.__ready is False:
            return

        self.__ready = False
        AdminPanelProvider.removeTab("Localization")
        pass

    def __changeLocale(self, locale, automatic=False):
        if self.__ready is False:
            return

        if SceneManager.isChangeScene() is True:
            return

        def __onSceneChanged(scene=None):
            if SystemManager.hasSystem("SystemOptions") is True:
                options = SystemManager.getSystem("SystemOptions")
                options.setLanguage(None if automatic is True else locale)

            if SystemManager.hasSystem("SystemAutoLanguage") is True:
                autoLanguage = SystemManager.getSystem("SystemAutoLanguage")
                autoLanguage.setDisabled(automatic is False)

            if Mengine.hasCurrentAccount() is False:
                return

            if SessionManager.s_currentSession is None:
                Mengine.saveAccounts()
                return

            SessionManager.saveSession()

        if Mengine.getLocale() == locale:
            __onSceneChanged()
            return

        def __onSceneRemoved():
            Mengine.setLocale(locale)

        if Mengine.getCurrentScene() is None:
            __onSceneRemoved()
            __onSceneChanged()
            return

        SceneManager.reloadCurrentScene(__onSceneChanged, cb_removed=__onSceneRemoved)
        pass
