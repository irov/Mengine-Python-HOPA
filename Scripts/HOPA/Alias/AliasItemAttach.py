from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.TaskAlias import TaskAlias


class AliasItemAttach(MixinItem, TaskAlias):
    def _onParams(self, params):
        super(AliasItemAttach, self)._onParams(params)
        self.AutoAttach = params.get("AutoAttach", False)
        self.MovieAttach = params.get("MovieAttach", True)
        self.Origin = params.get("Origin", True)
        self.Offset = params.get("Offset", False)
        self.OffsetValue = params.get("OffsetValue", (0, 0))
        self.AddArrowChild = params.get("AddArrowChild", True)

    def _onCheck(self):
        arrowItem = ArrowManager.getArrowAttach()

        if arrowItem is self.Item:
            return False

        return True

    def _onGenerate(self, source):
        if self.AutoAttach is False:
            source.addTask("TaskItemClick", Item=self.Item)

        source.addTask("TaskFanItemInHand", FanItem=self.Item)
        source.addTask("TaskArrowAttach", Offset=self.Offset, OffsetValue=self.OffsetValue, Origin=self.Origin,
                       Object=self.Item, MovieAttach=self.MovieAttach, AddArrowChild=self.AddArrowChild)
