from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from MARSDK.MarParamsManager import MarParamsManager


class About(BaseEntity):
    mov_open = "Movie2_Open"
    mov_close = "Movie2_Close"

    mov_plate = "Movie2_Plate"
    soc_close = "close"

    btn_quit = "Movie2Button_Quit"

    btn_privacy_policy = "Movie2Button_Privacy_Policy"
    btn_user_agreement = "Movie2Button_User_Agreement"

    btn_social_weibo = "Movie2Button_Weibo"
    btn_social_tiktok = "Movie2Button_Tiktok"
    btn_social_qq = "Movie2Button_QQ"
    btn_social_bilibili = "Movie2Button_Bilibili"

    def __init__(self):
        super(About, self).__init__()
        self.tc = None
        self.close_buttons = {}
        self.urls_buttons = {}

    # ====================== BaseEntity ================================================================================
    def _onPreparation(self):
        self.initContent()

    def _onActivate(self):
        self.runTaskChain()

    def _onDeactivate(self):
        self.cleanUp()

    # ====================== Content ===================================================================================
    def initContent(self):
        if self.object.hasObject(About.mov_plate):
            self.close_buttons["plate"] = self.object.getObject(About.mov_plate)

        if self.object.hasObject(About.btn_quit):
            self.close_buttons["quit"] = self.object.getObject(About.btn_quit)

        if self.object.hasObject(About.btn_privacy_policy):
            self.urls_buttons["privacy_policy"] = self.object.getObject(About.btn_privacy_policy)

        if self.object.hasObject(About.btn_user_agreement):
            self.urls_buttons["user_agreement"] = self.object.getObject(About.btn_user_agreement)

        if self.object.hasObject(About.btn_social_bilibili):
            self.urls_buttons["social_bilibili"] = self.object.getObject(About.btn_social_bilibili)

        if self.object.hasObject(About.btn_social_qq):
            self.urls_buttons["social_qq"] = self.object.getObject(About.btn_social_qq)

        if self.object.hasObject(About.btn_social_tiktok):
            self.urls_buttons["social_tiktok"] = self.object.getObject(About.btn_social_tiktok)

        if self.object.hasObject(About.btn_social_weibo):
            self.urls_buttons["social_weibo"] = self.object.getObject(About.btn_social_weibo)

    # ====================== TaskChain =================================================================================
    def runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Name="About", Repeat=True)
        with self.tc as tc:
            with tc.addRaceTask(2) as (tc_urls, tc_close):
                for (name, button), race in tc_urls.addRaceTaskList(self.urls_buttons.items()):
                    race.addTask("TaskMovie2ButtonClick", Movie2Button=button)
                    race.addFunction(Mengine.openUrlInDefaultBrowser, unicode(MarParamsManager.getData(name), "utf-8"))

                with tc_close.addRaceTask(2) as (tc_close_button, tc_close_socket):
                    tc_close_button.addTask("TaskMovie2ButtonClick", Movie2Button=self.close_buttons["quit"])
                    tc_close_socket.addTask("TaskMovie2SocketClick", Movie2=self.close_buttons["plate"],
                                            SocketName=About.soc_close, isDown=True)
                tc_close.addScope(self.sceneEffect, "About", About.mov_close)
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
        self.urls_buttons = {}
