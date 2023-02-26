from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias

class AliasMessageOKClick(TaskAlias):
    def __init__(self):
        super(AliasMessageOKClick, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasMessageOKClick, self)._onParams(params)
        pass

    def _onInitialize(self):
        super(AliasMessageOKClick, self)._onInitialize()

        if _DEVELOPMENT is True:
            if GroupManager.hasGroup("MessageOK") is False:
                self.initializeFailed("AliasMessageOKShow invalid group MessageOK")
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskButtonClick", GroupName="MessageOK", ButtonName="Button_OK")
        pass
    pass