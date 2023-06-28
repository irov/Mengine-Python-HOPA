from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput


class About(BaseEntity):
    mov_plate = "Movie2_Plate"
    mov_open = "Movie2_Open"
    mov_close = "Movie2_Close"

    btn_quit = "Movie2Button_Quit"

    btn_weibo = "Movie2Button_Weibo"
    btn_tiktok = "Movie2Button_Tiktok"
    btn_qq = "Movie2Button_QQ"
    btn_bilibili = "Movie2Button_Bilibili"

    btn_user_agreement = "Movie2Button_User_Agreement"
    btn_privacy_policy = "Movie2Button_Privacy_Policy"

    def __init__(self):
        super(About, self).__init__()
        self.tc = None
        self.content = {}

    # ====================== BaseEntity ================================================================================
    def _onPreparation(self):
        self.initContent()

    def _onActivate(self):
        self.runTaskChain()

    def _onDeactivate(self):
        self.cleanUp()

    # ====================== Content ===================================================================================
    def initContent(self):
        if self.object.hasObject(About.btn_quit):
            self.content["quit"] = self.object.getObject(About.btn_quit)

        if self.object.hasObject(About.mov_plate):
            self.content["plate"] = self.object.getObject(About.mov_plate)

    # ====================== TaskChain =================================================================================
    def runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Name="About")
        with self.tc as tc:
            with tc.addRaceTask(2) as (tc_urls, tc_close):
                tc_urls.addBlock()
                tc_urls.addPrint("!")

                with tc_close.addRaceTask(2) as (tc_close_button, tc_close_socket):
                    tc_close_button.addTask("TaskMovie2ButtonClick", Movie2Button=self.content["quit"])
                    tc_close_socket.addTask("TaskMovie2SocketClick", Movie2=self.content["plate"], SocketName="close", isDown=True)
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

        self.content = {}

