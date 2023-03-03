from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasFadeOut(TaskAlias):
    def __init__(self):
        super(AliasFadeOut, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasFadeOut, self)._onParams(params)

        self.FadeGroupName = params.get("FadeGroupName", "Fade")
        self.From = params.get("From", 1)
        self.Time = params.get("Time", 1000.0)
        self.Unblock = params.get("Unblock", True)
        self.DemonNameSuffix = params.get("DemonNameSuffix", None)
        self.FromIdle = params.get("FromIdle", False)
        self.easing = params.get("Easing", "easyLinear")
        self.reset_fade_count = params.get("ResetFadeCount", False)
        pass

    def _onInitialize(self):
        super(AliasFadeOut, self)._onInitialize()

        if _DEVELOPMENT is True:
            if GroupManager.hasGroup(self.FadeGroupName) is False:
                self.initializeFailed("GroupManager not found fade group '%s'" % (self.FadeGroupName,))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskFadeOut", GroupName=self.FadeGroupName, From=self.From, Time=self.Time,
                       DemonNameSuffix=self.DemonNameSuffix, FromIdle=self.FromIdle, Easing=self.easing,
                       ResetFadeCount=self.reset_fade_count)
