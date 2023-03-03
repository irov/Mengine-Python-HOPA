from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager


class PolicyHOGRollingMovie2ItemFoundEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHOGRollingMovie2ItemFoundEffect, self)._onParams(params)

        self.HOGItemName = params.get("HOGItemName")
        self.HOG = params.get("HOG")
        self.EnigmaName = params.get("EnigmaName")

    def _onGenerate(self, source):
        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        ItemName = hogItem.objectName

        MovieItem = self.Group.getObject(ItemName)
        MovieItemEntity = MovieItem.getEntity()
        MovieItemEntityNode = MovieItem.getEntityNode()

        scene = SceneManager.getCurrentScene()

        Enigma = EnigmaManager.getEnigma(self.EnigmaName)
        if Enigma.ZoomFrameGroup is not None:
            AttachLayer = scene.getSlot("Zoom")
        else:
            if Mengine.hasTouchpad() is True:
                AttachLayer = scene.getMainLayer()
            else:
                AttachLayer = scene.getSlot("HOGViewport")

        node = Mengine.createNode("Interender")
        node1 = Mengine.createNode("Interender")
        PickEffectMovie = MovieItemEntity.getPickEffectMovie(node)

        AttachLayer.addChild(node)
        AttachLayer.addChild(node1)

        Offset = Mengine.vec2f(0.0, 0.0)

        if PickEffectMovie.hasSlot('center') is True:
            slot = PickEffectMovie.getMovieSlot('center')
            Offset = slot.getWorldPosition()
        elif PickEffectMovie.hasSocket('socket') is True:
            socket = PickEffectMovie.getSocket('socket')
            Offset = socket.getWorldPolygonCenter()
        MovieItemPosition = MovieItemEntityNode.getWorldPosition()

        node.setLocalPosition(MovieItemPosition + Offset)
        node1.setLocalPosition(MovieItemPosition + Offset)
        node.setOrigin(Offset)

        PickEffectMoveEntityNode = PickEffectMovie.getEntityNode()
        node.addChildFront(PickEffectMoveEntityNode)
        HOGInventory = HOGManager.getInventory(self.EnigmaName)
        checkMarkEffect = HOGInventory.tryGenerateObjectUnique('CheckMark_{}'.format(self.HOGItemName), 'Movie2_CheckMark')

        if checkMarkEffect is not None:
            checkMarkEffectEntityNode = checkMarkEffect.getEntityNode()
            node1.addChild(checkMarkEffectEntityNode)
            source.addTask("TaskEnable", Object=checkMarkEffect, Value=True)
            source.addTask("TaskMovie2Play", Movie2=checkMarkEffect, Wait=False)

        with source.addParallelTask(2) as (lostOfItem_0, lostOfItem_1):
            lostOfItem_0.addTask('TaskNodeScaleTo', Node=node, To=(1.2, 1.2, 1.2), Time=500)
            lostOfItem_1.addTask('TaskNodeAlphaTo', Node=node, To=0.0, Time=500)

        with source.addFork() as source_fork:
            if checkMarkEffect is not None:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=checkMarkEffect)
                source_fork.addTask("TaskObjectDestroy", Object=checkMarkEffect)
                source_fork.addTask("TaskObjectDestroy", Object=PickEffectMovie)

            source_fork.addTask("TaskNodeDestroy", Node=node)
