from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias


class AliasSystemMessage(TaskAlias):

    def _onParams(self, params):
        super(AliasSystemMessage, self)._onParams(params)

        self.TextID = params.get("TextID", None)
        self.TextArgs = params.get("TextArgs", None)
        self.OkID = params.get("OkID", "ID_OK")
        self.CloseOnBtnUp = params.get("CloseOnBtnUp", False)

        self.AlphaFadeIn = params.get("AlphaFadeIn", 1)
        self.AlphaFadeOut = params.get("AlphaFadeOut", 1)
        self.TimeFadeIn = params.get("TimeFadeIn", 0.5)
        self.TimeFadeOut = params.get("TimeFadeOut", 0.2)

        self.FadeGroupName = params.get("FadeGroupName", "Fade")

        self.Callback = params.get("Callback", None)
        self.Scope = params.get("Scope", None)

    def _onInitialize(self):
        super(AliasSystemMessage, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.TextID is not None:
                if Mengine.existText(self.TextID) is False:
                    self.initializeFailed("AliasSystemMessage invalid ID_TEXT %s" % self.TextID)
            if self.TextArgs is not None:
                if isinstance(self.TextArgs, (tuple, list)) is False:
                    self.initializeFailed("AliasSystemMessage invalid text args %s - must be tuple or list" % self.TextArgs)
                elif len(self.TextArgs) == 0:
                    self.initializeFailed("AliasSystemMessage invalid text args %s - insert at least one arg" % self.TextArgs)

            if GroupManager.hasGroup("SystemMessage") is False:
                self.initializeFailed("AliasSystemMessage invalid group SystemMessage")

    def scopeOpen(self, source, GroupName):
        MovieName = "Movie2_Open"
        source.addScope(self.sceneEffect, GroupName, MovieName)
        source.addNotify(Notificator.onPopupMessageShow, self.TextID)

    def scopeClose(self, source, GropName):
        MovieName = "Movie2_Close"
        source.addScope(self.sceneEffect, GropName, MovieName)

    def sceneEffect(self, source, GropName, MovieName):
        if GroupManager.hasObject(GropName, MovieName) is False:
            return

        Movie = GroupManager.getObject(GropName, MovieName)
        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addTask("TaskEnable", Object=Movie, Value=True)
                guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
                guard_source_movie.addTask("TaskEnable", Object=Movie, Value=False)

    def _setTexts(self):
        if self.OkID is not None:
            Mengine.removeTextAliasArguments("", "$SystemMessage_OK")
            Mengine.setTextAlias("", "$SystemMessage_OK", self.OkID)

        if self.TextID is not None:
            Mengine.removeTextAliasArguments("", "$SystemMessage")
            Mengine.setTextAlias("", "$SystemMessage", self.TextID)
            if self.TextArgs is not None:
                Mengine.setTextAliasArguments("", "$SystemMessage", *self.TextArgs)

    def _onGenerate(self, source):
        source.addFunction(self._setTexts)

        source.addTask("TaskSceneLayerGroupEnable", LayerName="SystemMessage", Value=True)
        source.addScope(self.scopeOpen, "SystemMessage")

        source.addTask("TaskInteractive", GroupName="SystemMessage", ObjectName="Socket_Block", Value=True)

        with source.addRaceTask(2) as (tc_button, tc_socket):
            tc_button.addTask('TaskMovie2ButtonClick', GroupName='SystemMessage', Movie2ButtonName='Movie2Button_Ok')
            tc_socket.addTask("TaskMovie2SocketClick", GroupName="SystemMessage", Movie2Name="Movie2_BG", SocketName="close")

        source.addScope(self.scopeClose, "SystemMessage")
        source.addTask("TaskSceneLayerGroupEnable", LayerName="SystemMessage", Value=False)

        if self.Callback:
            source.addTask("TaskFunction", Fn=self.Callback)

        if self.Scope:
            source.addScope(self.Scope)
