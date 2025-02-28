from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias


class AliasMessageShow(TaskAlias):
    def __init__(self):
        super(AliasMessageShow, self).__init__()

        self.TextID = None
        self.TextArgs = None
        self.YesID = None
        self.NoID = None

    def _onParams(self, params):
        super(AliasMessageShow, self)._onParams(params)

        self.TextID = params.get("TextID")
        self.TextArgs = params.get("TextArgs", None)
        self.YesID = params.get("YesID", "ID_YES")
        self.NoID = params.get("NoID", "ID_NO")

    def _onInitialize(self):
        super(AliasMessageShow, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.TextID is not None:
                if Mengine.existText(self.TextID) is False:
                    self.initializeFailed("AliasMessageShow invalid ID_TEXT %s" % self.TextID)

            if self.YesID is not None:
                if Mengine.existText(self.YesID) is False:
                    self.initializeFailed("AliasMessageShow invalid ID_YES %s" % self.YesID)

            if self.NoID is not None:
                if Mengine.existText(self.NoID) is False:
                    self.initializeFailed("AliasMessageShow invalid ID_NO %s" % self.NoID)

            if GroupManager.hasGroup("Message") is False:
                self.initializeFailed("AliasMessageShow invalid group Message")

    def SceneEffect(self, source, GroupName, MovieName):
        if GroupManager.hasObject(GroupName, MovieName) is False:
            return
        Movie = GroupManager.getObject(GroupName, MovieName)

        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True, AutoEnable=True)

    def _onGenerate(self, source):
        source.addTask("TaskSceneLayerGroupEnable", LayerName="Message", Value=True)
        source.addTask("TaskSetParam", GroupName="Message", ObjectName="Text_Message", Param="TextID", Value=self.TextID)
        source.addScope(self.SceneEffect, "Message", 'Movie2_Open')

        source.addTask("TaskInteractive", GroupName="Message", ObjectName="Socket_Block", Value=True)

        if self.TextArgs is not None:
            source.addTask("TaskSetParam", GroupName="Message", ObjectName="Text_Message", Param="TextArgs", Value=self.TextArgs)

        if GroupManager.hasObject('SystemMessage', 'Button_Yes'):
            if self.YesID is not None:
                source.addTask("TaskSetParam", GroupName="Message", ObjectName="Button_Yes", Param="TextID", Value=self.YesID)
            else:
                source.addTask("TaskSetParam", GroupName="Message", ObjectName="Button_Yes", Param="TextID", Value=None)

        if GroupManager.hasObject('SystemMessage', 'Button_No'):
            if self.NoID is not None:
                source.addTask('TaskSetParam', GroupName='Message', ObjectName='Button_No', Param='TextID', Value=self.NoID)
            else:
                source.addTask('TaskSetParam', GroupName='Message', ObjectName='Button_No', Param='TextID', Value=None)

        source.addNotify(Notificator.onPopupMessageShow, self.TextID)
