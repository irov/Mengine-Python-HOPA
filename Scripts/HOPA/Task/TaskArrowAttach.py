from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.Task import Task
from HOPA.CursorManager import CursorManager


class TaskArrowAttach(MixinObject, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskArrowAttach, self)._onParams(params)
        self.Offset = params.get("Offset", False)
        self.OffsetValue = params.get("OffsetValue", (0, 0))
        self.Origin = params.get("Origin", False)
        self.MovieAttach = params.get("MovieAttach", True)
        self.AddArrowChild = params.get("AddArrowChild", True)

    def _onRun(self):
        if ArrowManager.emptyArrowAttach() is False:
            attach = ArrowManager.getArrowAttach()
            attach.setParam("Enable", False)
            attachEntity = attach.getEntity()
            attachEntity.disable()

        ArrowManager.attachArrow(self.Object, self.MovieAttach)

        if self.AddArrowChild is False:
            return True

        ItemEntity = self.Object.getEntity()
        Image = ItemEntity.getSprite()

        position = (0, 0)
        if self.Offset is True:
            ArrowPosition = Mengine.getCursorPosition()
            ItemPosition = Image.getWorldPosition()
            position = (ArrowPosition.x - ItemPosition.x, ArrowPosition.y - ItemPosition.y)

        position = (position[0] + self.OffsetValue[0], position[1] + self.OffsetValue[1])

        if CursorManager.hasSlotItem() is False or self.MovieAttach is False:
            arrow = Mengine.getArrow()
            arrow_node = arrow.getNode()

            if self.Origin is True:
                origin = Image.getLocalImageCenter()
                Image.setOrigin(origin)

            Image.setLocalPosition(position)
            arrow_node.addChildFront(Image)

        return True
