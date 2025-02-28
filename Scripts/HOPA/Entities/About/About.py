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

        url_buttons = {
            "privacy_policy": About.BUTTON_PRIVACY_POLICY_NAME,
            "user_agreement": About.BUTTON_USER_AGREEMENT_NAME,
            "social_bilibili": About.BUTTON_SOCIAL_BILIBILI_NAME,
            "social_qq": About.BUTTON_SOCIAL_QQ_NAME,
            "social_tiktok": About.BUTTON_SOCIAL_TIKTOK_NAME,
            "social_weibo": About.BUTTON_SOCIAL_WEIBO_NAME,
        }
        for key, name in url_buttons.items():
            if self.object.hasObject(name) is False:
                continue
            url = self._getURLByName(key)
            if url is None:
                continue
            self.url_buttons[key] = self.object.getObject(name)

    def _getURLByName(self, name):
        url = Mengine.getConfigString("About", name+"_url", "")
        if url == "":
            return None
        url = unicode(url, "utf-8")
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
            guard_source.addTask("TaskMovie2Play", Movie2=movie, Wait=True, AutoEnable=True)

    # ====================== CleanUp ===================================================================================
    def cleanUp(self):
        if TaskManager.existTaskChain("About_URLs") is True:
            TaskManager.cancelTaskChain("About_URLs")

        self.close_buttons = {}
        self.url_buttons = {}
