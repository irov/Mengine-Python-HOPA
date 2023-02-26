from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias

class AliasFadeIn(TaskAlias):
    def _onParams(self, params):
        super(AliasFadeIn, self)._onParams(params)
        self.FadeGroupName = params.get("FadeGroupName", "Fade")
        self.To = params.get("To", 1)
        self.Time = params.get("Time", 500.0)
        self.Block = params.get("Block", True)
        self.ReturnItem = params.get("ReturnItem", True)
        self.DemonNameSuffix = params.get("DemonNameSuffix", None)
        self.easing = params.get("Easing", "easyLinear")
        pass

    def _onGenerate(self, source):
        with GuardBlockInput(source, self.Block) as guard_source:
            if self.ReturnItem is True:
                guard_source.addTask("AliasFadeInBefore")
                pass

            guard_source.addTask("TaskFadeIn", GroupName=self.FadeGroupName, To=self.To, Time=self.Time, DemonNameSuffix=self.DemonNameSuffix, Easing=self.easing)
            pass
        pass
    pass