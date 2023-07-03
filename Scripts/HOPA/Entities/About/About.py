from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput


class About(BaseEntity):
    MOV_OPEN = "Movie2_Open"
    MOV_CLOSE = "Movie2_Close"

    MOV_PLATE = "Movie2_Plate"
    SOC_CLOSE = "close"

    BTN_QUIT = "Movie2Button_Quit"

    BTN_PRIVACY_POLICY = "Movie2Button_Privacy_Policy"
    BTN_USER_AGREEMENT = "Movie2Button_User_Agreement"

    BTN_SOCIAL_WEIBO = "Movie2Button_Weibo"
    BTN_SOCIAL_TIKTOK = "Movie2Button_Tiktok"
    BTN_SOCIAL_QQ = "Movie2Button_QQ"
    BTN_SOCIAL_BILIBILI = "Movie2Button_Bilibili"

    def __init__(self):
        super(About, self).__init__()
        self.tc = None
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
        if self.object.hasObject(About.MOV_PLATE):
            self.close_buttons["plate"] = self.object.getObject(About.MOV_PLATE)

        if self.object.hasObject(About.BTN_QUIT):
            self.close_buttons["quit"] = self.object.getObject(About.BTN_QUIT)

        if self.object.hasObject(About.BTN_PRIVACY_POLICY):
            self.url_buttons["privacy_policy"] = self.object.getObject(About.BTN_PRIVACY_POLICY)

        if self.object.hasObject(About.BTN_USER_AGREEMENT):
            self.url_buttons["user_agreement"] = self.object.getObject(About.BTN_USER_AGREEMENT)

        if self.object.hasObject(About.BTN_SOCIAL_BILIBILI):
            self.url_buttons["social_bilibili"] = self.object.getObject(About.BTN_SOCIAL_BILIBILI)

        if self.object.hasObject(About.BTN_SOCIAL_QQ):
            self.url_buttons["social_qq"] = self.object.getObject(About.BTN_SOCIAL_QQ)

        if self.object.hasObject(About.BTN_SOCIAL_TIKTOK):
            self.url_buttons["social_tiktok"] = self.object.getObject(About.BTN_SOCIAL_TIKTOK)

        if self.object.hasObject(About.BTN_SOCIAL_WEIBO):
            self.url_buttons["social_weibo"] = self.object.getObject(About.BTN_SOCIAL_WEIBO)

    def _validateURLButtons(self):
        for (name, button) in self.url_buttons.items():
            url = self._getURLByName(name)
            if url is None:
                button.setEnable(False)
                button.onDestroy()
                del self.url_buttons[name]

    def _getURLByName(self, name):
        url_value = Mengine.getConfigString("About", name+"_url", "None")
        if url_value == "None":
            return None
        url = unicode(url_value, "utf-8")
        return url

    # ====================== TaskChain =================================================================================
    def runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Name="About", Repeat=True)
        with self.tc as tc:
            with tc.addRaceTask(2) as (tc_urls, tc_close):
                for (name, button), race in tc_urls.addRaceTaskList(self.url_buttons.items()):
                    race.addTask("TaskMovie2ButtonClick", Movie2Button=button)
                    race.addFunction(Mengine.openUrlInDefaultBrowser, self._getURLByName(name))

                with tc_close.addRaceTask(2) as (tc_close_button, tc_close_socket):
                    tc_close_button.addTask("TaskMovie2ButtonClick", Movie2Button=self.close_buttons["quit"])
                    tc_close_socket.addTask("TaskMovie2SocketClick", Movie2=self.close_buttons["plate"],
                                            SocketName=About.SOC_CLOSE, isDown=True)
                tc_close.addScope(self.sceneEffect, "About", About.MOV_CLOSE)
                tc_close.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
                tc_close.addScope(self.sceneEffect, "Options", "Movie2_Open")
                tc_close.addTask("TaskSceneLayerGroupEnable", LayerName="About", Value=False)

    def sceneEffect(self, source, group_name, movie_name):
        if GroupManager.hasObject(group_name, movie_name) is True:
            movie = GroupManager.getObject(group_name, movie_name)
            with GuardBlockInput(source) as guard_source:
                guard_source.addTask("TaskEnable", Object=movie, Value=True)
                guard_source.addTask("TaskMovie2Play", Movie2=movie, Wait=True)
                guard_source.addTask("TaskEnable", Object=movie, Value=False)

    # ====================== CleanUp ===================================================================================
    def cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        self.close_buttons = {}
        self.url_buttons = {}
