from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager


class PolicyCheckMarkNearItem(TaskAlias):
    def _onParams(self, params):
        super(PolicyCheckMarkNearItem, self)._onParams(params)

        self.HOGItemName = params.get('HOGItemName')
        self.HOG = params.get('HOG')
        self.EnigmaName = params.get('EnigmaName')

    def _onGenerate(self, source):
        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        self.ItemName = hogItem.objectName

        Item = self.Group.getObject(self.ItemName)
        Item.setBlock(False)
        ItemEntity = Item.getEntity()

        Camera = Mengine.getRenderCamera2D()

        node = Mengine.createNode("Interender")
        scene = SceneManager.getCurrentScene()
        # layer_InventoryItemEffect = scene.getSlot("HOGViewport")

        Enigma = EnigmaManager.getEnigma(self.EnigmaName)
        if Enigma.ZoomFrameGroup is not None:
            AttachLayer = scene.getSlot("Zoom")
        else:
            if Mengine.hasTouchpad() is True:
                AttachLayer = scene.getMainLayer()
            else:
                AttachLayer = scene.getSlot("HOGViewport")

        AttachLayer.addChildFront(node)

        P0 = ItemEntity.getCameraPosition(Camera)
        P1 = ItemEntity.getSpriteCenter()
        node.setLocalPosition((P0[0] + P1[0], P0[1] + P1[1]))

        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        checkMarkEffect = None
        if HOGInventory.hasPrototype("Movie2_CheckMark"):
            checkMarkEffect = HOGInventory.tryGenerateObjectUnique('CheckMark_{}'.format(self.HOGItemName), 'Movie2_CheckMark')
        elif HOGInventory.hasPrototype("Movie_CheckMark"):
            checkMarkEffect = HOGInventory.tryGenerateObjectUnique('CheckMark_{}'.format(self.HOGItemName), 'Movie_CheckMark')
        else:
            if _DEVELOPMENT is True:
                Trace.log("Policy", 0, "Not found checkMarkEffect! Please add Movie_CheckMark or Movie2_CheckMark to %s" % HOGInventory.getName())

        if checkMarkEffect is not None:
            effectEntityNode = checkMarkEffect.getEntityNode()

            node.addChildFront(effectEntityNode)

            source.addEnable(checkMarkEffect)
            source.addTask("TaskMoviePlay", Movie=checkMarkEffect, Wait=False)

        with source.addFork() as source_fork:
            if checkMarkEffect is not None:
                source_fork.addTask("TaskMovieInterrupt", Movie=checkMarkEffect)
                source_fork.addTask("TaskObjectDestroy", Object=checkMarkEffect)
                pass

            source_fork.addTask("TaskNodeDestroy", Node=node)
            pass
