from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.RotateCirclesWithChipsManager import RotateCirclesWithChipsManager


Enigma = Mengine.importEntity("Enigma")


class RotateCirclesWithChips(Enigma):
    # -------------- Classes -------------------------------------------------------------------------------------------
    class Chip(object):
        def __init__(self, id, movie):
            self.id = id
            self.movie = movie
            self.onCenter = 0
            self.node = self.movie.getEntityNode()
            self.rotateAngle = 0

        def getPosition(self):
            pos = self.node.getWorldPosition()
            return pos

        def scopeRotate(self, source, circle):
            toAngle = 0
            if circle.id != 'circle_center':
                toAngle = self.node.getAngle() + circle.angleTo
            elif circle.id == 'circle_center':
                toAngle = self.node.getAngle() - circle.angleTo

            source.addTask('TaskNodeRotateTo', Node=self.node, Time=circle.timeRotate, To=toAngle)

        def returnOnStart(self, source):
            self.rotateAngle = 0
            source.addTask('TaskNodeRotateTo', Node=self.node, Time=0.1, To=0)

    class Circle(object):
        def __init__(self, id, movie, numOfSlots, slotOnBG):
            self.id = id
            self.movie = movie
            self.numOfSlots = numOfSlots
            self.node = Mengine.createNode('Interender')
            entityNode = self.movie.getEntityNode()
            self.node.addChild(entityNode)
            slotOnBG.addChild(self.node)
            self.timeRotate = 1000  # ms
            self.flagRotate = 0
            self.Pi = 3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117
            self.angleTo = (self.Pi * 2 / self.numOfSlots)

        def getCircleSlots(self):
            circleSlots = []
            for i in range(1, self.numOfSlots + 1):
                circleSlots.append(self.movie.getMovieSlot('chip_{}'.format(i)))
            return circleSlots

        def scopeRotate(self, source):
            if self.id != 'circle_center':
                toAngle = self.node.getAngle() - self.angleTo
                self.flagRotate = (self.flagRotate - 1) % self.numOfSlots
            else:
                toAngle = self.node.getAngle() + self.angleTo
                self.flagRotate = (self.flagRotate + 1) % self.numOfSlots

            source.addTask('TaskNodeRotateTo', Node=self.node, Time=self.timeRotate, To=toAngle)

        def returnOnStart(self, source):
            self.flagRotate = 0
            source.addTask('TaskNodeRotateTo', Node=self.node, Time=0.1, To=0)

    class Combination(object):
        def __init__(self, Chip, Circle, SlotID, onCenter):
            self.Chip = Chip
            self.Circle = Circle
            self.SlotID = SlotID
            self.onCenter = onCenter

    # ==================================================================================================================

    def __init__(self):
        super(RotateCirclesWithChips, self).__init__()
        self.param = None
        self.chips = []
        self.circles = []
        self.tc = None
        self.startComb = []
        self.winsComb = []

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(RotateCirclesWithChips, self)._onPreparation()
        self.loadParam()  # self.setup()

    def _onActivate(self):
        super(RotateCirclesWithChips, self)._onActivate()

    def _onDeactivate(self):
        super(RotateCirclesWithChips, self)._onDeactivate()  # self._cleanUp()

    def _onPreparationDeactivate(self):
        super(RotateCirclesWithChips, self)._onPreparationDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.setup()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    # ==================================================================================================================

    # -------------- _onPreparation methods ----------------------------------------------------------------------------
    def loadParam(self):
        self.param = RotateCirclesWithChipsManager.getParam(self.EnigmaName)

    def setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)
        door_movie2 = "Movie2_door_closed"
        door_movie1 = "Movie_door_closed"

        for (ChipID, MovieName) in self.param.chips_dict.iteritems():
            Movie = Group.getObject(MovieName)
            chip = RotateCirclesWithChips.Chip(ChipID, Movie)
            self.chips.append(chip)

        for (CircleID, circleValue) in self.param.circles_dict.iteritems():
            if Group.hasObject(door_movie2):
                Movie_door_closed = Group.getObject(door_movie2)
            elif Group.hasObject(door_movie1):
                Movie_door_closed = Group.getObject(door_movie1)
            else:
                Trace.log("Entity", 0,
                          "Not found {!r} or {!r} objects in {!r} group!".format(door_movie2, door_movie1, GroupName))
                continue

            slotOnBG = Movie_door_closed.getMovieSlot(CircleID)

            Movie = Group.getObject(circleValue[0])
            circle = RotateCirclesWithChips.Circle(CircleID, Movie, circleValue[1], slotOnBG)
            self.circles.append(circle)

        self.setupComb()
        self.setupChipOnSlots()

    def setupComb(self):
        for chip in self.chips:
            startParam = self.buildComb(self.param.startComb_dict, chip)
            start = RotateCirclesWithChips.Combination(startParam[0], startParam[1], startParam[2], startParam[3])
            self.startComb.append(start)
            winsParam = self.buildComb(self.param.winsComb_dict, chip)
            wins = RotateCirclesWithChips.Combination(winsParam[0], winsParam[1], winsParam[2], winsParam[3])
            self.winsComb.append(wins)

    def buildComb(self, combDict, chip):
        returnValue = []
        for circle in self.circles:
            if circle.id == combDict[chip.id][0]:
                slotID = combDict[chip.id][2]
                returnValue = [chip, circle, slotID, combDict[chip.id][1]]
                break
        return returnValue

    def setupChipOnSlots(self):
        for starts in self.startComb:
            slot = starts.Circle.movie.getMovieSlot('chip_{}'.format(starts.SlotID))
            slot.addChild(starts.Chip.node)

    # ==================================================================================================================

    # -------------- Task Chain ----------------------------------------------------------------------------------------
    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._scopeClickOnCircle)

    def _scopeClickOnCircle(self, source):
        clickCircle = Holder()
        for circle, tc_race in source.addRaceTaskList(self.circles):
            movie_type = circle.movie.getType()

            if movie_type == "ObjectMovie2":
                tc_race.addTask("TaskMovie2SocketClick", Movie2=circle.movie, SocketName="circle")
            elif movie_type == "ObjectMovie":
                tc_race.addTask('TaskMovieSocketClick', Movie=circle.movie, SocketName='circle')

            tc_race.addFunction(clickCircle.set, circle)

        def holder_scopeClick(source, holder):
            clickCircle = holder.get()
            source.addScope(self.scopeClick, clickCircle)

        source.addScope(holder_scopeClick, clickCircle)

    def scopeClick(self, source, circle):
        chipsOnCircle = self.foundChipNearCircle(circle)

        with source.addIfTask(lambda: circle.id == 'circle_center') as (source_true, source_false):
            source_true.addFunction(self.attachChipOnCircle, chipsOnCircle, circle)

        with source.addParallelTask(3) as (tc_circle, tc_circleSoundEffect, tc_chips):
            tc_circle.addScope(circle.scopeRotate)
            tc_circleSoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, "RotateCirclesWithChips_RotateCircle")

            for (_, chip), tc_chip in tc_chips.addParallelTaskList(chipsOnCircle):
                tc_chip.addScope(chip.scopeRotate, circle)

        source.addFunction(self.checkChipOnCenter)

        with source.addIfTask(lambda: circle.id == 'circle_center') as (source_true, source_false):
            source_true.addFunction(self.deattachChipWithCenterCircle)

        source.addFunction(self.checkChipOnCenter)
        source.addFunction(self.checkWinComb)

    def attachChipOnCircle(self, slotNearChipList, circle):
        for (slot, chip) in slotNearChipList:
            if chip.onCenter is False and circle.id != 'circle_center':
                continue

            node = chip.movie.getEntityNode()
            node.removeFromParent()

            coef = circle.flagRotate % circle.numOfSlots

            node.setAngle(coef * circle.angleTo)
            slot.addChild(node)

    def deattachChipWithCenterCircle(self):
        for circle in self.circles:
            if circle.id != 'circle_center':
                self.attachChipOnCircle(self.foundChipNearCircle(circle), circle)
                pass

        for circle in self.circles:
            if circle.id != 'circle_center':
                continue

            circle.node.setAngle(0.0)
            circle.flagRotate = 0
            break

    def foundChipNearCircle(self, circle):
        slotNearChip = []
        circleSlots = circle.getCircleSlots()
        for chip in self.chips:
            chipPos = chip.getPosition()
            for slot in circleSlots:
                slotPos = slot.getWorldPosition()
                distance = self._calculateDistance(chipPos[0], chipPos[1], slotPos[0], slotPos[1])
                if distance <= 30:
                    couple = []
                    couple.append(slot)
                    couple.append(chip)
                    slotNearChip.append(couple)
        return slotNearChip

    def _calculateDistance(self, x1, y1, x2, y2):
        return Mengine.sqrtf((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

    def checkWinComb(self):
        chipFlag = 0
        for chip in self.chips:
            circle = self.checkBoundingBox(chip)
            for winChip in self.winsComb:
                # if chip.id == winChip.Chip.id and chip.onCenter == winChip.onCenter and circle.id == winChip.Circle.id:
                if chip.id == winChip.Chip.id and circle.id == winChip.Circle.id:
                    chipFlag += 1
        if chipFlag == len(self.chips):
            self._cleanUp()
            self.enigmaComplete()

    def checkBoundingBox(self, chip):
        for circle in self.circles:
            if circle.id != 'circle_center':
                boundingBoxCircle = self._getCirclesBorders(circle)
                chipPos = chip.getPosition()
                minX, maxX, minY, maxY = boundingBoxCircle.minimum.x, boundingBoxCircle.maximum.x, boundingBoxCircle.minimum.y, boundingBoxCircle.maximum.y
                if (chipPos[0] >= minX) and (chipPos[0] <= maxX) and (chipPos[1] >= minY) and (chipPos[1] <= maxY):
                    return circle

    def _getCirclesBorders(self, circle):
        socket = circle.movie.getSocket('circle')
        # boundingBoxCircle = socket.getBoundingBox()
        boundingBoxCircle = Mengine.getHotSpotPolygonBoundingBox(socket)
        return boundingBoxCircle

    def checkChipOnCenter(self):
        for chip in self.chips:
            chip.onCenter = 0
        for circle in self.circles:
            if circle.id == 'circle_center':
                chipsNearCenter = self.foundChipNearCircle(circle)

                for (_, chip) in chipsNearCenter:
                    chip.onCenter = 1

    # ==================================================================================================================

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.param = None

        for chip in self.chips:
            # chip.node.removeFromParent()
            chip.movie.returnToParent()

        self.chips = []
        self.startComb = []
        self.winsComb = []

        for circle in self.circles:
            circle.movie.returnToParent()
            # circle.node.removeFromParent()
            Mengine.destroyNode(circle.node)
        self.circles = []
