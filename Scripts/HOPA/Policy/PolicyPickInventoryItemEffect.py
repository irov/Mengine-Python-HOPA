from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.CursorManager import CursorManager

class PolicyPickInventoryItemEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyPickInventoryItemEffect, self)._onParams(params)

        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onGenerate(self, source):
        scene = SceneManager.getCurrentScene()

        if scene is None:
            return
            pass

        Inventory = DemonManager.getDemon("Inventory")

        effect = Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        InventoryItemEntity = self.InventoryItem.getEntity()

        # - old functionality -----------------------------------
        # itemSprite = InventoryItemEntity.getSprite()
        # itemSpriteSize = itemSprite.getLocalImageCenter()
        # - new -------------------------------------------------
        # * issue for CountItemFX:
        # - hold movie, not sprite
        # - but support entity.getSpriteCenter interface
        itemSpriteSize = InventoryItemEntity.getSpriteCenter()
        # -------------------------------------------------------

        if effect is not None:
            effectEntityNode = effect.getEntityNode()
            InventoryItemEntity.addChildFront(effectEntityNode)
            InventoryItemEntity.effect = effect

            effect.setPosition((itemSpriteSize.x, itemSpriteSize.y))
            pass

        InvItemCursorScaleIn = DefaultManager.getDefaultFloat("InvItemCursorScaleIn", 0.2)
        InvItemCursorScaleIn *= 1000  # speed fix

        source.addTask("TaskFunction", Fn=CursorManager.attachSlotItem, Args=(self.InventoryItem,))

        if effect is not None:
            source.addTask("TaskEnable", Object=effect, Value=True)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        source.addEnable(self.InventoryItem)
        source.addTask("TaskNodeScaleTo", Node=InventoryItemEntity.node, To=(1.0, 1.0, 1.0), Time=InvItemCursorScaleIn)
        source.addNotify(Notificator.onSoundEffectOnObject, self.InventoryItem, "PickInventoryItemEffect")

        pass