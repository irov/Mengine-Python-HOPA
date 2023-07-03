from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput


class About(BaseEntity):
    MOVIE_PLATE_NAME = "Movie2_Plate"
    MOVIE_OPEN_NAME = "Movie2_Open"
    MOVIE_CLOSE_NAME = "Movie2_Close"
    BUTTON_QUIT_NAME = "Movie2Button_Quit"
    SOCKET_CLOSE_NAME = "close"

    BUTTON_PRIVACY_POLICY_NAME = "Movie2Button_Privacy_Policy"
    BUTTON_USER_AGREEMENT_NAME = "Movie2Button_User_Agreement"
    BUTTON_SOCIAL_WEIBO_NAME = "Movie2Button_Weibo"
    BUTTON_SOCIAL_TIKTOK_NAME = "Movie2Button_Tiktok"
    BUTTON_SOCIAL_QQ_NAME = "Movie2Button_QQ"
    BUTTON_SOCIAL_BILIBILI_NAME = "Movie2Button_Bilibili"

    def __init__(self):
        super(About, self).__init__()
        self.close_buttons = {}
        self.url_buttons = {}

    # ====================== BaseEntity ================================================================================
    def _onPreparation(self):
        self._initContent()
        self._validateURLButtons()

    def _onActivate(self):
        self.runTaskChain()

    def _onDeactivate(self):
        self.cleanUp()

    # ====================== Content ===================================================================================
    def _initContent(self):
        if self.object.hasObject(About.MOVIE_PLATE_NAME):
            self.close_buttons["plate"] = self.object.getObject(About.MOVIE_PLATE_NAME)
        if self.object.hasObject(About.BUTTON_QUIT_NAME):
            self.close_buttons["quit"] = self.object.getObject(About.BUTTON_QUIT_NAME)

        if self.object.hasObject(About.BUTTON_PRIVACY_POLICY_NAME):
            self.url_buttons["privacy_policy"] = self.object.getObject(About.BUTTON_PRIVACY_POLICY_NAME)

        if self.object.hasObject(About.BUTTON_USER_AGREEMENT_NAME):
            self.url_buttons["user_agreement"] = self.object.getObject(About.BUTTON_USER_AGREEMENT_NAME)

        if self.object.hasObject(About.BUTTON_SOCIAL_BILIBILI_NAME):
            self.url_buttons["social_bilibili"] = self.object.getObject(About.BUTTON_SOCIAL_BILIBILI_NAME)

        if self.object.hasObject(About.BUTTON_SOCIAL_QQ_NAME):
            self.url_buttons["social_qq"] = self.object.getObject(About.BUTTON_SOCIAL_QQ_NAME)

        if self.object.hasObject(About.BUTTON_SOCIAL_TIKTOK_NAME):
            self.url_buttons["social_tiktok"] = self.object.getObject(About.BUTTON_SOCIAL_TIKTOK_NAME)

        if self.object.hasObject(About.BUTTON_SOCIAL_WEIBO_NAME):
            self.url_buttons["social_weibo"] = self.object.getObject(About.BUTTON_SOCIAL_WEIBO_NAME)

    def _validateURLButtons(self):
        for (name, button) in self.url_buttons.items():
            url = self._getURLByName(name)
            if url is None:
                button.setEnable(False)

    def _getURLByName(self, name):
        url_value = Mengine.getConfigString("About", name+"_url", "")
        if url_value == "":
            return None
        url = unicode(url_value, "utf-8")
        return url

    # ====================== TaskChain =================================================================================
    def runTaskChain(self):
        if TaskManager.existTaskChain("About_URLs") is True:
            TaskManager.cancelTaskChain("About_URLs")

        with TaskManager.createTaskChain(Name="About_URLs", Repeat=True) as tc:
            with tc.addRaceTask(2) as (tc_urls, tc_close):
                for (name, button), race in tc_urls.addRaceTaskList(self.url_buttons.items()):
                    url = self._getURLByName(name)
                    if url is not None:
                        race.addTask("TaskMovie2ButtonClick", Movie2Button=button)
                        race.addFunction(Mengine.openUrlInDefaultBrowser, url)
                    else:
                        race.addBlock()

                with tc_close.addRaceTask(2) as (tc_close_button, tc_close_socket):
                    tc_close_button.addTask("TaskMovie2ButtonClick", Movie2Button=self.close_buttons["quit"])
                    tc_close_socket.addTask("TaskMovie2SocketClick", Movie2=self.close_buttons["plate"],
                                            SocketName=About.SOCKET_CLOSE_NAME, isDown=True)

                tc_close.addScope(self.sceneEffect, "About", About.MOVIE_CLOSE_NAME)
                tc_close.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
                tc_close.addScope(self.sceneEffect, "Options", About.MOVIE_OPEN_NAME)
                tc_close.addTask("TaskSceneLayerGroupEnable", LayerName="About", Value=False)

    def sceneEffect(self, source, group_name, movie_name):
        if GroupManager.hasObject(group_name, movie_name) is False:
            return
        movie = GroupManager.getObject(group_name, movie_name)
        with GuardBlockInput(source) as guard_source:
            guard_source.addTask("TaskEnable", Object=movie, Value=True)
            guard_source.addTask("TaskMovie2Play", Movie2=movie, Wait=True)
            guard_source.addTask("TaskEnable", Object=movie, Value=False)

    # ====================== CleanUp ===================================================================================
    def cleanUp(self):
        if TaskManager.existTaskChain("About_URLs") is True:
            TaskManager.cancelTaskChain("About_URLs")

        self.close_buttons = {}
        self.url_buttons = {}
