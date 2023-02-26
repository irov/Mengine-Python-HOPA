# from Foundation.Task.TaskAlias import TaskAlias
#
# from Foundation.Task.MixinObjectTemplate import MixinItem
##from Foundation.Task.MixinObjectTemplate import MixinEffect
#
# from Foundation.SceneManager import SceneManager
# from HOPA.ItemManager import ItemManager
# from Foundation.TaskManager import TaskManager
# from Foundation.DefaultManager import DefaultManager
#
#
#
#
# class AliasEffectBeforeInventoryAddItem(MixinItem, TaskAlias):
#    Skiped = False
#
#    def _onParams(self, params):
#        super(AliasEffectBeforeInventoryAddItem, self)._onParams(params)
#        self.front = params.get("Front", True)
#        self.itemEntity = None
#        self.time = params.get("Time")
#        self.Inventory = params.get("Inventory")
#        pass
#
#    def _onInitialize(self):
#        super(AliasEffectBeforeInventoryAddItem, self)._onInitialize()
#        pass
#
#    def _onGenerate(self, source):
#        self.itemEntity = self.Item.getEntity()
#
##        Camera = Mengine.getRenderCamera2D()
##        P0 = self.itemEntity.getCameraPosition(Camera)
#
##        scene = SceneManager.getCurrentScene()
##        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
##        layer_InventoryItemEffect.addChild(self.itemEntity)
#
##        self.itemEntity.setLocalPosition(P0)
##        self.itemEntity.enable()
#
#        spriteFull = self.itemEntity.getSprite()
#        spriteFull.disable()
#        spritePure = self.itemEntity.getPure()
#        spritePure.enable()
#        size = spritePure.getImageSize()
#
#        self.itemEntity.setCoordinate((size.x/2, size.y/2))
#
#        source.addTask("TaskSceneLayerAddEntity", LayerName = "InventoryItemEffect", Object = self.Item, AdaptScreen = True)
#        source.addTask("TaskNodeScaleTo", Node = self.itemEntity, To = (1.2, 1.2, 1.0), Time = self.time)
#        pass
#
#    pass