from Foundation.DefaultManager import DefaultManager
from Foundation.ObjectManager import ObjectManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager


class AliasHOGFXPartsGatheringItemFoundEffect(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGFXPartsGatheringItemFoundEffect, self)._onParams(params)
        self.HOGItemName = params.get("HOGItemName")
        self.HOG = params.get("HOG")
        self.EnigmaName = params.get("EnigmaName")
        pass

    def _onGenerate(self, source):
        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        if HOGInventory.isActive() is False:
            self.log("HOGInventory.isActive() is False  return")
            return
            pass

        effect = HOGInventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        self.ItemName = hogItem.objectName

        InventoryEntity = HOGInventory.getEntity()
        slot = InventoryEntity.getSlotByName(self.HOGItemName)

        if slot is None:
            self.invalidTask("not found slot %s" % (self.HOGItemName))
            pass

        P2 = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()

        Item = self.Group.getObject(self.ItemName)
        ItemEntity = Item.getEntity()
        node = Mengine.createNode("Interender")
        P0 = ItemEntity.getCameraPosition(Camera)

        scene = SceneManager.getCurrentScene()
        if Mengine.hasTouchpad() is True:
            layer = scene.getMainLayer()
        else:
            layer = scene.getSlot("HOGInventoryFXPartsGathering")  # InventoryItemEffect

        ObjectType = Item.getType()

        HOGItemHideEffectSpeed = DefaultManager.getDefaultFloat("HOGItemHideEffectSpeed", 1000)
        HOGItemHideEffectSpeed *= 0.001  # speed fix
        HOGItemIncreaseTime = DefaultManager.getDefaultFloat("HOGItemIncreaseTime", 1)
        HOGItemIncreaseTime *= 1000  # speed fix

        if ObjectType == "ObjectItem":
            Item.setBlock(False)
            pure = ItemEntity.generatePure()
            pure.enable()
            pureCenter = pure.getLocalImageCenter()
            pure.coordinate(pureCenter)
            itemSpriteSize = pure.getLocalImageCenter()
            scale1 = (1.5, 1.5, 1.0)
            scale2 = (0.4, 0.4, 1.0)
            P1 = (P2.x, P0[1])
            node.setLocalPosition(P0)
            node.addChild(pure)
            layer.addChild(node)

        else:
            NewObjectName = "Movie2ItemPickEffect_{}".format(self.ItemName)
            ResourceMovie, CompositionName = ItemEntity.getPickEffectResourceName()
            movie = self.createMovie2FromResource(ResourceMovie, CompositionName, NewObjectName, node)
            movie.setPlay(False)
            pure = movie.getEntityNode()
            node.setLocalPosition(P0)
            node.addChild(pure)
            layer.addChild(node)

            if movie.hasSlot('center') is True:
                slot = movie.getMovieSlot('center')
                Offset = slot.getWorldPosition()
            elif movie.hasSocket('socket') is True:
                socket = movie.getSocket('socket')
                Offset = socket.getWorldPolygonCenter()
            else:
                Offset = Mengine.vec2f(0.0, 0.0)

            P2 = (P2.x - Offset.x, P2.y - Offset.y)
            P1 = (P2[0], P0[1])

            scale1 = (1.0, 1.0, 1.0)
            scale2 = (1.0, 1.0, 1.0)
            HOGItemIncreaseTime = 100.0
            itemSpriteSize = (0.0, 0.0)

        length = Mengine.length_v2_v2(P1, P2)

        time = length / HOGItemHideEffectSpeed
        source.addTask("TaskNodeScaleTo", Node=pure, To=scale1, Time=HOGItemIncreaseTime)

        if effect is not None:
            effectEntityNode = effect.getEntityNode()

            effectEntityNode.setLocalPosition(itemSpriteSize)

            node.addChildFront(effectEntityNode)
            source.addEnable(effect)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addTask("TaskNodeBezier2To", Node=node, Point1=P1, To=P2, Speed=HOGItemHideEffectSpeed)

            tcp1.addTask("TaskNodeScaleTo", Node=node, To=scale2, Time=time)
            pass

        source.addTask("TaskNodeEnable", Node=pure, Value=False)

        with source.addFork() as source_fork:
            if effect is not None:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                source_fork.addTask("TaskObjectDestroy", Object=effect)
                pass

            source_fork.addTask("TaskNodeDestroy", Node=node)
            pass

        def __playMovie(scope):
            HOGInventory = HOGManager.getInventory(self.EnigmaName)
            InventoryEntity = HOGInventory.getEntity()
            slot = InventoryEntity.getSlotByName(self.HOGItemName)
            slotGroup = slot.getGroup()
            part_movie = slot.getPart_Movie()
            enigma = EnigmaManager.getEnigma(self.EnigmaName)
            enigma_Object = enigma.getObject()
            enigma_Object.appendParam("FoundItems", self.HOGItemName)

            scope.addTask("TaskMovie2Play", Movie2=part_movie, Wait=True)

            with scope.addIfTask(slot.isGathered) as (gathered, _):
                gathered.lockSemaphore(slot.getSemaphore())

                movie = slot.getMovie()
                gathered.addEnable(movie)
                gathered.addFunction(slot.disableItemMovies, slotGroup)
                gathered.addTask("TaskMovie2Play", Movie2=movie, Wait=True)

                gathered.unlockSemaphore(slot.getSemaphore())
            with scope.addIfTask(slot.isAllGathered) as (all_gathered, _):
                def prepare():
                    slot.disableGroupsMovies()
                    Movie_Gathering = InventoryEntity.getMovieGathering()
                    Movie_Gathering.setEnable(True)

                for semaphore in slot.getSemaphores():
                    all_gathered.trySemaphore(semaphore)

                all_gathered.addFunction(prepare)

                all_gathered.addTask('TaskMovie2Play', Movie2=InventoryEntity.getMovieGathering(), Wait=True)

                def enigmaComplete():
                    EnigmaManager.getEnigma(self.EnigmaName).getEntity().enigmaComplete()

                all_gathered.addFunction(enigmaComplete)

        source.addScope(__playMovie)

    def createMovie2FromResource(self, ResourceMovie, CompositionName, MovieName, AttachNode):
        if ResourceMovie is None:
            return None
            pass

        if CompositionName is None:
            return None
            pass

        Movie = ObjectManager.createObjectUnique("Movie2", MovieName, None, ResourceMovie=ResourceMovie,
                                                 CompositionName=CompositionName)

        Movie.setEnable(True)
        Movie.setPlay(False)
        Movie.setLoop(False)
        Movie.setLastFrame(True)
        MovieEntityNode = Movie.getEntityNode()
        AttachNode.addChild(MovieEntityNode)

        return Movie
