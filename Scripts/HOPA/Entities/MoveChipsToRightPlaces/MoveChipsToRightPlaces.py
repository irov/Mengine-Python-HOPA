from Foundation.ArrowManager import ArrowManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager
from HOPA.MoveChipsToRightPlacesManager import MoveChipsToRightPlacesManager


Enigma = Mengine.importEntity("Enigma")


class MoveChipsToRightPlaces(Enigma):
    class Chip(object):
        def __init__(self, movie, place):
            self.movie = movie
            self.node = self.movie.getEntityNode()
            self.preAttachPosition = (0, 0)
            self.placeToMove = place
            self.onPlace = False

        def scopeClickDown(self, source):
            source.addTask("TaskMovieSocketClick", Movie=self.movie, SocketName='chip', isDown=True)

        def scopeClickUp(self, source):
            source.addTask("TaskMouseButtonClick", isDown=False)

        def attach(self):
            arrow = ArrowManager.getArrow()
            arrowPos = arrow.node.getLocalPosition()

            entity_node = self.movie.getEntityNode()
            self.preAttachPosition = entity_node.getLocalPosition()
            arrow.addChildFront(entity_node)

            entity_node_pos = entity_node.getLocalPosition()
            entity_node.setLocalPosition((entity_node_pos[0] - arrowPos[0], entity_node_pos[1] - arrowPos[1]))

        def deattach(self):
            self.movie.returnToParent()
            arrow = ArrowManager.getArrow()
            arrowPos = arrow.node.getLocalPosition()

            entity_node = self.movie.getEntityNode()
            entity_node_pos = entity_node.getLocalPosition()

            entity_node.setLocalPosition((entity_node_pos[0] + arrowPos[0], entity_node_pos[1] + arrowPos[1]))

        def checkBoundingBox(self):
            socket = self.movie.getSocket('chip')
            # BoundingBox_Chip = socket.getBoundingBox()
            BoundingBox_Chip = Mengine.getHotSpotPolygonBoundingBox(socket)
            # BoundingBox_Place = self.placeToMove.getBoundingBox()
            BoundingBox_Place = Mengine.getHotSpotPolygonBoundingBox(self.placeToMove)
            minX, maxX, minY, maxY = BoundingBox_Place.minimum.x, BoundingBox_Place.maximum.x, BoundingBox_Place.minimum.y, BoundingBox_Place.maximum.y

            if BoundingBox_Chip.minimum.x < minX:
                return False
            elif BoundingBox_Chip.maximum.x > maxX:
                return False
            elif BoundingBox_Chip.minimum.y < minY:
                return False
            elif BoundingBox_Chip.maximum.y > maxY:
                return False
            return True

        def borderAudit(self):
            if self.checkBoundingBox() is False:
                self.returnOnPreAttachPosition()
                return False
            else:
                self.onPlace = True
                return True

        def returnOnPreAttachPosition(self):
            self.node.setLocalPosition(self.preAttachPosition)

    def __init__(self):
        super(MoveChipsToRightPlaces, self).__init__()
        self.chips = {}
        self.param = None
        self.tc = None
        self.flagCheck = 0

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(MoveChipsToRightPlaces, self)._onPreparation()

    def _onActivate(self):
        super(MoveChipsToRightPlaces, self)._onActivate()

    def _onDeactivate(self):
        super(MoveChipsToRightPlaces, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.loadParam()
        self.setup()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    # ==================================================================================================================

    # -------------- _onPreparation methods ----------------------------------------------------------------------------
    def loadParam(self):
        self.param = MoveChipsToRightPlacesManager.getParam(self.EnigmaName)

    def setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        BG = Group.getObject('Movie_Environment_back')

        def setupObj(dict, objDict):
            for (ChipID, movieName) in dict.iteritems():
                placeToMove = BG.getSocket('place_{}'.format(ChipID))
                movie = Group.getObject(movieName)
                obj = MoveChipsToRightPlaces.Chip(movie, placeToMove)
                objDict[ChipID] = obj

        setupObj(self.param.chipDict, self.chips)

    # ==================================================================================================================

    # -------------- Task Chain ----------------------------------------------------------------------------------------
    def _runTaskChain(self):
        ClickHolder = Holder()

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            for (_, chip), tc_race in tc.addRaceTaskList(self.chips.iteritems()):
                # tc_race.addScope(self.newInventory)
                tc_race.addScope(chip.scopeClickDown)
                tc_race.addFunction(ClickHolder.set, chip)

            tc.addScope(self._resolveClickScope, ClickHolder)

    def newInventory(self):
        self.HOGItems = HOGManager.getHOGItems(self.EnigmaName)

        self.HOGInventory = HOGManager.getInventory(self.EnigmaName)
        self.HOGInventory.setEnable(True)

        for hogItem in self.HOGItems:
            itemObjectName = hogItem.objectName
            if itemObjectName not in self.FoundItems:
                continue
                pass

            item = self.ItemsGroup.getObject(itemObjectName)

            if item.getEnable() is False:
                continue
                pass

            item.setEnable(False)
            pass

        countItems = self.HOGInventory.getSlotCount()
        FindItems = self._findNewInventoryItems(countItems)
        self.object.setFindItems(FindItems)
        pass

    def _resolveClickScope(self, source, clickHolder):
        chip = clickHolder.get()
        source.addFunction(chip.attach)
        source.addScope(chip.scopeClickUp)
        source.addFunction(chip.deattach)
        source.addFunction(self.correctArt)

        # with source.addIfTask(lambda chip: chip.borderAudit(), chip) as (source_true, source_false):
        #     source_false.addTask('AliasMindPlay', MindID='ID_MIND_FAIL01')

        source.addFunction(chip.borderAudit)
        source.addFunction(self.checkWin)

    def correctArt(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        Environment_front = Group.getObject('Movie_Environment_front')
        Environment_front.getEntityNode().removeFromParent()
        Environment_front.returnToParent()

        Door_Use = Group.getObject('Movie_Door_Use')
        Door_Use.getEntityNode().removeFromParent()
        Door_Use.returnToParent()

    def checkWin(self):
        flagOnPlace = 0
        for (_, chip) in self.chips.iteritems():
            if chip.onPlace is True:
                flagOnPlace += 1

            if flagOnPlace == len(self.chips):
                self.enigmaComplete()

    # ==================================================================================================================

    # -------------- _cleanUp ------------------------------------------------------------------------------------------
    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.chips = {}

        self.param = None
        self.tc = None

    # ==================================================================================================================
