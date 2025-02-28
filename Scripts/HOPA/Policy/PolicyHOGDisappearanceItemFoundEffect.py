from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager


class PolicyHOGDisappearanceItemFoundEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHOGDisappearanceItemFoundEffect, self)._onParams(params)

        self.HOGItemName = params.get('HOGItemName')
        self.HOG = params.get('HOG')
        self.EnigmaName = params.get('EnigmaName')

    def _onGenerate(self, source):
        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        self.ItemName = hogItem.objectName

        Item = self.Group.getObject(self.ItemName)
        Item.setBlock(False)
        ItemEntity = Item.getEntity()

        node = Mengine.createNode('Interender')
        node1 = Mengine.createNode('Interender')

        pure = ItemEntity.generatePure()
        pure.enable()

        scene = SceneManager.getCurrentScene()
        Enigma = EnigmaManager.getEnigma(self.EnigmaName)
        if Enigma.ZoomFrameGroup is not None:
            AttachLayer = scene.getSlot("Zoom")
        else:
            if Mengine.hasTouchpad() is True:
                AttachLayer = scene.getMainLayer()
            else:
                AttachLayer = scene.getSlot("HOGViewport")

        AttachLayer.addChild(node)
        AttachLayer.addChild(node1)

        node.addChild(pure)

        Camera = Mengine.getRenderCamera2D()
        P0 = ItemEntity.getCameraPosition(Camera)
        P1 = ItemEntity.getSpriteCenter()
        node.setLocalPosition(P0)
        node1.setLocalPosition((P0[0] + P1[0], P0[1] + P1[1]))

        pureCenter = pure.getLocalImageCenter()
        pure.coordinate(pureCenter)

        HOGInventory = HOGManager.getInventory(self.EnigmaName)
        HOGInventoryEntity = HOGInventory.getEntity()

        slot = HOGInventoryEntity.findSlot(self.HOGItemName)
        if slot is not None:
            silhouette = slot.getItemObject()
            silhouette_node = silhouette.getEntityNode()

        checkMarkEffect = None
        if HOGInventory.hasPrototype("Movie2_CheckMark"):
            checkMarkEffect = HOGInventory.tryGenerateObjectUnique('CheckMark_{}'.format(self.HOGItemName), 'Movie2_CheckMark')
        elif HOGInventory.hasPrototype("Movie_CheckMark"):
            checkMarkEffect = HOGInventory.tryGenerateObjectUnique('CheckMark_{}'.format(self.HOGItemName), 'Movie_CheckMark')
        else:
            if _DEVELOPMENT:
                Trace.log("Policy", 0, "Not found checkMarkEffect! Please add Movie_CheckMark or Movie2_CheckMark to %s" % HOGInventory.getName())

        scale_time = DefaultManager.getDefaultFloat('HOGItemScaleTime', 500)
        alphaTo_time = DefaultManager.getDefaultFloat('HOGItemAlphaToTime', 500)

        scale_to = DefaultManager.getDefaultTuple('HOGItemScaleTo', (1.2, 1.2, 1.2))
        alphaTo_to = DefaultManager.getDefaultFloat('HOGItemAlphaToTo', 0)

        if checkMarkEffect is not None:
            checkMarkEffectEntityNode = checkMarkEffect.getEntityNode()
            node1.addChild(checkMarkEffectEntityNode)

            source.addEnable(checkMarkEffect)
            source.addTask("TaskMoviePlay", Movie=checkMarkEffect, Wait=False)

        with source.addParallelTask(4) as (lostOfItem_0, lostOfItem_1, tc_silhouette_0, tc_silhouette_1):
            lostOfItem_0.addTask('TaskNodeScaleTo', Node=pure, To=scale_to, Time=scale_time)
            lostOfItem_1.addTask('TaskNodeAlphaTo', Node=pure, To=alphaTo_to, Time=alphaTo_time)

            if slot is not None:
                # tc_silhouette_0.addTask('TaskNodeScaleTo', Node=silhouette_node, To=scale_to, Time=scale_time)
                tc_silhouette_1.addTask('TaskNodeAlphaTo', Node=silhouette_node, To=alphaTo_to, Time=alphaTo_time)

        with source.addFork() as source_fork:
            if checkMarkEffect is not None:
                source_fork.addTask("TaskMovieInterrupt", Movie=checkMarkEffect)
                source_fork.addTask("TaskObjectDestroy", Object=checkMarkEffect)
                pass

            source_fork.addTask("TaskNodeDestroy", Node=node)
            pass
