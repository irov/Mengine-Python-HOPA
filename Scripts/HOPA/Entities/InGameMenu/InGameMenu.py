from Event import Event
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.Systems.SystemGoogleServices import SystemGoogleServices
from Foundation.Providers.AchievementsProvider import AchievementsProvider
from Foundation.TaskManager import TaskManager


class InGameMenu(BaseEntity):
    def __init__(self):
        super(InGameMenu, self).__init__()
        self.auth_buttons = {}
        self.achievements_button = None

    def _onActivate(self):
        socket_block = self.object.getObject("Socket_Block")
        socket_block.setInteractive(True)

    # Google Auth

    def _onPreparation(self):
        if self._initGoogleAuthButtons() is True:
            self._runAuthTaskChain()

        if self._initGoogleAchievements() is True:
            self._runAchievementsTaskChain()

    def _initGoogleAuthButtons(self):
        if Mengine.hasTouchpad() is False:
            return False
        if Mengine.getConfigBool("GoogleService", "EnableInGameMenuSignOut", False) is False:
            return False

        _plugin = SystemGoogleServices.b_plugins["GoogleGameSocial"] is True
        if _plugin is False:
            if _DEVELOPMENT is False:
                return False

        buttons_names = {"login": "Movie2_Google", "logout": "Movie2_Logout"}
        for id_, movie_name in buttons_names.items():
            if GroupManager.hasObject("InGameMenu", movie_name) is False:
                continue
            movie = GroupManager.getObject("InGameMenu", movie_name)
            movie.setInteractive(True)
            self.auth_buttons[id_] = movie

        if len(self.auth_buttons) != len(buttons_names):
            if _DEVELOPMENT is True and _plugin is True:
                Trace.log("Entity", 0, "InGameMenu fail to setup Google Auth buttons: {} != {}".format(self.auth_buttons, buttons_names))

            for movie in self.auth_buttons.values():
                movie.setEnable(False)

            return False

        self._cbManageAuthButtons()
        return True

    def _cbManageAuthButtons(self):
        is_logged_in = SystemGoogleServices.isLoggedIn() is True
        self.auth_buttons["logout"].setEnable(is_logged_in)
        self.auth_buttons["login"].setEnable(not is_logged_in)

    def _runAuthTaskChain(self):
        if TaskManager.existTaskChain("InGameMenuAuth") is True:
            TaskManager.cancelTaskChain("InGameMenuAuth")
        if TaskManager.existTaskChain("InGameMenuAuthUpdater") is True:
            TaskManager.cancelTaskChain("InGameMenuAuthUpdater")

        done_event = Event("onDoneGoogleAuth")

        # def _login():
        #     SystemGoogleServices.login_data = 1
        #
        # def _logout():
        #     SystemGoogleServices.login_data = None

        with TaskManager.createTaskChain(Name="InGameMenuAuth", Repeat=True) as tc:
            with tc.addIfTask(SystemGoogleServices.isLoggedIn) as (tc_logout, tc_login):
                tc_logout.addTask("TaskMovie2SocketClick", Movie2=self.auth_buttons["logout"], SocketName="socket")
                tc_logout.addFunction(SystemGoogleServices.signOut)
                # tc_logout.addFunction(_logout)
                # tc_logout.addFunction(SystemGoogleServices.logout_event)

                tc_login.addTask("TaskMovie2SocketClick", Movie2=self.auth_buttons["login"], SocketName="socket")
                tc_login.addFunction(SystemGoogleServices.signIn)
                # tc_login.addFunction(_login)
                # tc_login.addFunction(SystemGoogleServices.login_event, True)
            tc.addEvent(done_event)

        with TaskManager.createTaskChain(Name="InGameMenuAuthUpdater", Repeat=True) as tc:
            with tc.addRaceTask(2) as (tc_login, tc_logout):
                tc_login.addEvent(SystemGoogleServices.login_event)
                tc_logout.addEvent(SystemGoogleServices.logout_event)
            tc.addFunction(self._cbManageAuthButtons)
            tc.addDelay(1.0)
            tc.addFunction(done_event)

    def _initGoogleAchievements(self):
        if Mengine.getGameParamBool("Achievements", False) is False:
            return False
        if Mengine.hasTouchpad() is False:
            return False
        if Utils.getCurrentPlatform() != "Android":
            return False
        if GroupManager.hasObject("InGameMenu", "Movie2Button_GoogleAchievements") is False:
            return False

        achieve_btn = GroupManager.getObject("InGameMenu", "Movie2Button_GoogleAchievements")
        achieve_btn.setInteractive(True)
        achieve_btn.setEnable(True)
        self.achievements_button = achieve_btn
        return True

    def _runAchievementsTaskChain(self):
        if TaskManager.existTaskChain("InGameMenuGoogleAchievements") is True:
            TaskManager.cancelTaskChain("InGameMenuGoogleAchievements")

        with TaskManager.createTaskChain(Name="InGameMenuGoogleAchievements", Repeat=True) as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.achievements_button, SocketName="socket")
            tc.addScope(self._scopeOpenAchievements)

    def _scopeOpenAchievements(self, source):
        if AchievementsProvider.hasMethod("showAchievements") is False:
            Trace.msg_err("[!] showAchievements impossible to show - provider failed")

        source.addDelay(300)  # fix for part services spamming
        source.addFunction(AchievementsProvider.showAchievements)
