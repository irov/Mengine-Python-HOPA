from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager


class PolicyCheckMarkNearMovieItem(TaskAlias):
    def _onParams(self, params):
        super(PolicyCheckMarkNearMovieItem, self)._onParams(params)

        self.HOGItemName = params.get('HOGItemName')
        self.HOG = params.get('HOG')
        self.EnigmaName = params.get('EnigmaName')

    def _onGenerate(self, source):
        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        ItemName = hogItem.objectName

        MovieItem = self.Group.getObject(ItemName)
        MovieItemEntity = MovieItem.getEntity()
        MovieItemEntityNode = MovieItem.getEntityNode()
        ResourceName = MovieItemEntity.getPickEffectResourceName()

        NewObjectName = "MovieItemPickEffect_{}".format(ItemName)
        scene = SceneManager.getCurrentScene()

        Enigma = EnigmaManager.getEnigma(self.EnigmaName)
        if Enigma.ZoomFrameGroup is not None:
            AttachLayer = scene.getSlot("Zoom")
            pass
        else:
            if Mengine.hasTouchpad() is True:
                AttachLayer = scene.getMainLayer()
            else:
                AttachLayer = scene.getSlot("HOGViewport")

        node = Mengine.createNode("Interender")
        AttachLayer.addChild(node)

        Offset = Mengine.vec2f(0.0, 0.0)

        # if PickEffectMovie.hasSlot('center') is True:
        #     slot = PickEffectMovie.getMovieSlot('center')
        #     Offset = slot.getLocalPosition()
        # elif PickEffectMovie.hasSocket('socket') is True:
        #     socket = PickEffectMovie.getSocket('socket')
        #     Offset = socket.getWorldPolygonCenter()

        MovieItemPosition = MovieItemEntityNode.getWorldPosition()
        node.setLocalPosition(MovieItemPosition + Offset)
        node.setOrigin(Offset)

        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        checkMarkEffect = None
        if HOGInventory.hasPrototype("Movie2_CheckMark"):
            checkMarkEffect = HOGInventory.tryGenerateObjectUnique('CheckMark_{}'.format(self.HOGItemName),
                                                                   'Movie2_CheckMark')
        elif HOGInventory.hasPrototype("Movie_CheckMark"):
            checkMarkEffect = HOGInventory.tryGenerateObjectUnique('CheckMark_{}'.format(self.HOGItemName),
                                                                   'Movie_CheckMark')
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
