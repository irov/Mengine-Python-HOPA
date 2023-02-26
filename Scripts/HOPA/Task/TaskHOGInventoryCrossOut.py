from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias

class TaskHOGInventoryCrossOut(TaskAlias):
    HOG_TEXT_COLOR_OFF = (0.3, 0.3, 0.3, 1)

    def _onParams(self, params):
        super(TaskHOGInventoryCrossOut, self)._onParams(params)
        self.HOGInventory = None

        self.HOGItemName = params.get("HOGItemName")
        self.Immediately = params.get("Immediately", False)
        pass

    def _onInitialize(self):
        super(TaskHOGInventoryCrossOut, self)._onInitialize()
        self.HOGInventory = DemonManager.getDemon("HOGInventory")

        if _DEVELOPMENT is True:
            if self.HOGInventory is None:
                self.initializeFailed("HOG inventory not found")
                pass
            pass
        pass

    def _onGenerate(self, source):
        # Trace.log("Task", 0, "TaskHOGInventoryCrossOut _onGenerate")
        if self.HOGInventory.isActive() is False:
            return
            pass

        HOGInventoryEntity = self.HOGInventory.getEntity()

        slot = HOGInventoryEntity.getSlotByName(self.HOGItemName)
        if slot is None:
            self.invalidTask("not found slot %s" % (self.HOGItemName))
            pass

        if slot.found is False:
            return
            pass

        if self.Immediately is True:
            self._crossOutLine(slot)
            return
            pass

        textField = slot.getTextField()
        textLength = textField.getTextSize()

        textLine = self._createTextLine(textField, textLength)

        time = 0.3
        time *= 1000  # speed fix

        source.addTask("TaskNodeScaleTo", Node=textLine, To=(textLength.x, 3.0, 1.0), Time=time)
        source.addTask("TaskNodeColorTo", Node=textField, To=self.HOG_TEXT_COLOR_OFF, Time=time)
        pass

    def _createTextLine(self, textField, textLength):
        WhitePixelResource = Mengine.getResourceReference("WhitePixel")
        textLine = Mengine.createSprite("textLine", WhitePixelResource)

        textLine.setLocalPosition((-textLength.x * 0.5, textLength.y * 0.5))
        textLine.setLocalColor((1, 0, 0, 1))
        textLine.enable()
        textField.addChild(textLine)
        return textLine
        pass

    def _crossOutLine(self, slot):
        textField = slot.getTextField()
        textLength = textField.getTextSize()

        textLine = self._createTextLine(textField, textLength)

        textLine.setScale((textLength.x, 3.0, 1.0))
        textField.setLocalColor(self.HOG_TEXT_COLOR_OFF)
        pass
    pass