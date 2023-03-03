from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.TaskAlias import TaskAlias


class TaskHOGItemTakeEffect(MixinItem, TaskAlias):

    def _onParams(self, params):
        super(TaskHOGItemTakeEffect, self)._onParams(params)
        pass

    def _onInitialize(self):
        super(TaskHOGItemTakeEffect, self)._onInitialize()
        pass

    def _onFinalize(self):
        super(TaskHOGItemTakeEffect, self)._onFinalize()
        pass

    def _onGenerate(self, source):
        ImageEntity = self.Item.getEntity()
        #        Camera = Mengine.getRenderCamera2D()

        sprite = ImageEntity.getSprite()
        #        sprite.disable()

        pure = ImageEntity.generatePure()
        pure.enable()

        pureCenter = pure.getLocalImageCenter()

        # tempPos = ImageEntity.getCameraPosition(Camera)
        # offset = pure.getWorldPosition()
        # offsetPos = (tempPos[0] + offset.x, tempPos[1] + offset.y)
        # itemPos = (offsetPos[0] + pureCenter.x, offsetPos[1] + pureCenter.y)

        scene = SceneManager.getCurrentScene()

        layer_HogUpEffect = scene.getSlot("HintEffect")
        layer_HogUpEffect.addChild(pure)

        pure_imageResource = pure.getResourceImage()
        pure_white = Mengine.createSprite("pure_white", pure_imageResource)

        pure_white.disableTextureColor(True)
        pure_white.setLocalAlpha(0.0)
        pure_white.enable()

        pure.setRelationTransformation(sprite)

        pure.addChild(pure_white)
        # pure.setLocalPosition(itemPos)
        pure.setCoordinate(pureCenter)

        timeScaleTo = 0.2
        timeScaleTo *= 1000  # speed fix

        timeAphaTo1 = 0.3
        timeAphaTo1 *= 1000  # speed fix

        timeAphaTo2 = 0.4
        timeAphaTo2 *= 1000  # speed fix

        source.addTask("TaskEnable", Object=self.Item, Value=False)
        source.addTask("TaskNodeScaleTo", Node=pure, To=(1.1, 1.1, 1.0), Time=timeScaleTo)
        source.addTask("TaskNodeAlphaTo", Node=pure_white, To=0.3, Time=timeAphaTo1)
        source.addTask("TaskNodeScaleTo", Node=pure, To=(1.0, 1.0, 1.0), Time=timeScaleTo)
        source.addTask("TaskNodeAlphaTo", Node=pure, To=(0.0), Time=timeAphaTo2)

        source.addTask("TaskNodeRemoveFromParent", Node=pure_white)
        source.addTask("TaskNodeDestroy", Node=pure_white)

        source.addTask("TaskNodeRemoveFromParent", Node=pure)
        source.addTask("TaskNodeDestroy", Node=pure)
        pass

    pass
