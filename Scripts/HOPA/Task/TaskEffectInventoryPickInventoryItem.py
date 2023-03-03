from Foundation.DefaultManager import DefaultManager
from Foundation.Task.TaskAlias import TaskAlias


class TaskEffectInventoryPickInventoryItem(TaskAlias):
    Skiped = True

    def _onParams(self, params):
        super(TaskEffectInventoryPickInventoryItem, self)._onParams(params)

        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onInitialize(self):
        super(TaskEffectInventoryPickInventoryItem, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        InventoryItemEntity = self.InventoryItem.getEntity()
        InventoryItemEntity.setScale((1.0, 1.0, 1.0))

        sprite = InventoryItemEntity.getSprite()
        imageSize = sprite.getSurfaceSize()

        dx = -imageSize.x / 2
        dy = -imageSize.y / 2

        InventoryItemEntity.setLocalPosition((dx, dy))
        InvItemCursorScaleIn = DefaultManager.getDefaultFloat("InvItemCursorScaleIn", 0.2)
        InvItemCursorScaleIn *= 1000  # speed fix

        source.addTask("TaskNodeScaleTo", Node=InventoryItemEntity, To=(1.0, 1.0, 1.0), Time=InvItemCursorScaleIn)
        pass

    pass
