from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasMessageOKShow(TaskAlias):
    def __init__(self):
        super(AliasMessageOKShow, self).__init__()

        self.TextID = None
        self.TextArgs = None
        self.OkID = None

    def _onParams(self, params):
        super(AliasMessageOKShow, self)._onParams(params)

        self.TextID = params.get("TextID")
        self.TextArgs = params.get("TextArgs", None)
        self.OkID = params.get("OkID", "ID_OK")

    def _onInitialize(self):
        super(AliasMessageOKShow, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.TextID is not None:
                if Mengine.existText(self.TextID) is False:
                    self.initializeFailed("AliasMessageOKShow invalid ID_TEXT %s" % (self.TextID))

            if self.OkID is not None:
                if Mengine.existText(self.OkID) is False:
                    self.initializeFailed("AliasMessageOKShow invalid OkID %s" % (self.OkID))

            if GroupManager.hasGroup("MessageOK") is False:
                self.initializeFailed("AliasMessageOKShow invalid group MessageOK")

    def _onGenerate(self, source):
        source.addTask("TaskSceneLayerGroupEnable", LayerName="MessageOK", Value=True)
        source.addTask("TaskInteractive", GroupName="MessageOK", ObjectName="Socket_Block", Value=True)
        source.addTask("TaskSetParam", GroupName="MessageOK", ObjectName="Text_Message", Param="TextID", Value=self.TextID)
        if self.TextArgs is not None:
            source.addTask("TaskSetParam", GroupName="MessageOK", ObjectName="Text_Message", Param="TextArgs", Value=self.TextArgs)

        if self.OkID is not None:
            source.addTask("TaskSetParam", GroupName="MessageOK", ObjectName="Button_OK", Param="TextID", Value=self.OkID)
        else:
            source.addTask("TaskSetParam", GroupName="MessageOK", ObjectName="Button_OK", Param="TextID", Value=None)
