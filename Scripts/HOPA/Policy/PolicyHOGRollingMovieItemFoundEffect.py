from Foundation.ObjectManager import ObjectManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager


class PolicyHOGRollingMovieItemFoundEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHOGRollingMovieItemFoundEffect, self)._onParams(params)

        self.HOGItemName = params.get("HOGItemName")
        self.HOG = params.get("HOG")
        self.EnigmaName = params.get("EnigmaName")

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
        else:
            if Mengine.hasTouchpad() is True:
                AttachLayer = scene.getMainLayer()
            else:
                AttachLayer = scene.getSlot("HOGViewport")

        node = Mengine.createNode("Interender")
        node1 = Mengine.createNode("Interender")
        PickEffectMovie = self.createMovieFromResource(ResourceName, NewObjectName, node)

        AttachLayer.addChild(node)
        AttachLayer.addChild(node1)

        Offset = Mengine.vec2f(0.0, 0.0)

        if PickEffectMovie.hasSlot('center') is True:
            slot = PickEffectMovie.getMovieSlot('center')
            Offset = slot.getLocalPosition()
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

        checkMarkEffect = None
        if HOGInventory.hasPrototype("Movie2_CheckMark"):
            checkMarkEffect = HOGInventory.tryGenerateObjectUnique('CheckMark_{}'.format(self.HOGItemName), 'Movie2_CheckMark')
        elif HOGInventory.hasPrototype("Movie_CheckMark"):
            checkMarkEffect = HOGInventory.tryGenerateObjectUnique('CheckMark_{}'.format(self.HOGItemName), 'Movie_CheckMark')
        else:
            if _DEVELOPMENT:
                Trace.log("Policy", 0, "Not found checkMarkEffect! Please add Movie_CheckMark or Movie2_CheckMark to %s" % HOGInventory.getName())

        if checkMarkEffect is not None:
            checkMarkEffectEntityNode = checkMarkEffect.getEntityNode()
            node1.addChild(checkMarkEffectEntityNode)
            source.addEnable(checkMarkEffect)
            source.addTask("TaskMoviePlay", Movie=checkMarkEffect, Wait=False)

        with source.addParallelTask(2) as (lostOfItem_0, lostOfItem_1):
            lostOfItem_0.addTask('TaskNodeScaleTo', Node=node, To=(1.2, 1.2, 1.2), Time=500)
            lostOfItem_1.addTask('TaskNodeAlphaTo', Node=node, To=0, Time=500)

        with source.addFork() as source_fork:
            if checkMarkEffect is not None:
                source_fork.addTask("TaskMovieInterrupt", Movie=checkMarkEffect)
                source_fork.addTask("TaskObjectDestroy", Object=checkMarkEffect)
                source_fork.addTask("TaskObjectDestroy", Object=PickEffectMovie)

            source_fork.addTask("TaskNodeDestroy", Node=node)

    def createMovieFromResource(self, ResourceName, MovieName, AttachNode):
        if ResourceName is None:
            return None
        if Mengine.hasResource(ResourceName) is False:
            return None

        resource = Mengine.getResourceReference(ResourceName)
        if resource is None:
            return None

        Movie = ObjectManager.createObjectUnique("Movie", MovieName, None, ResourceMovie=resource)

        Movie.setEnable(True)
        Movie.setPlay(False)
        Movie.setLoop(False)
        Movie.setLastFrame(True)

        MovieEntityNode = Movie.getEntityNode()

        AttachNode.addChild(MovieEntityNode)

        return Movie
