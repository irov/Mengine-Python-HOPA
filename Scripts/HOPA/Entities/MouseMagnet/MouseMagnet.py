from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager
from HOPA.MouseMagnetManager import MouseMagnetManager


Enigma = Mengine.importEntity("Enigma")


class MouseMagnet(Enigma):
    def __init__(self):
        super(MouseMagnet, self).__init__()
        self.MousePositionProviderID = None
        self.Sockets = []
        self.Bounding_Box = []
        self.Movies = []

        self.Node_Mouse = None
        self.Node1 = None
        self.Node2 = None
        self.tc = None
        self.Timer = 200.0
        self.speed = 0.09
        self.affector = None
        self.Finish = None
        self.Start_Spike = True

    def _normalize(self, x, y, delta):
        if x <= delta:
            x = 0
        else:
            x = x / (delta * 2)
            if x > 3:
                x = 3
        if y <= delta:
            y = 0
        else:
            y = y / (delta * 2)
            if y > 3:
                y = 3
        if x == 3 and y == 3:
            x, y = 3 / (2.0 ** 0.5), 3 / (2.0 ** 0.5)
        return x, y

    def _Distance(self, pos1, pos2, difference=35):
        if ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5 < difference:
            return True
        else:
            return False

    def _Node_In_Box(self, pos, box):
        ball_size = 6.0
        if all([
            pos.x > (box.minimum.x - ball_size),
            pos.x < (box.maximum.x + ball_size),
            pos.y > (box.minimum.y - ball_size),
            pos.y < (box.maximum.y + ball_size)
        ]):
            return True
        else:
            return False

    def _Wall_Check(self, pos):
        for i in range(len(self.Bounding_Box)):
            Wall_border = self._Node_In_Box(pos, self.Bounding_Box[i])
            if Wall_border:
                center = self.Sockets[i].getWorldPolygonCenter()
                return Wall_border, center.x, center.y
        return False, 0, 0

    def _sign(self, a, b):
        if a - b < 0:
            return -1
        elif a - b > 0:
            return 1
        else:
            return 0

    def _Move_Chip(self):
        posBug = self.Node1.getWorldPosition()
        posTo = posBug
        posFrom = self.Node_Mouse.getWorldPosition()
        delta = 12.0
        speed = 1.35

        if self._Distance(posBug, posFrom, 3):
            return None
        x = abs(posFrom.x - posBug.x)
        y = abs(posFrom.y - posBug.y)
        x, y = self._normalize(x, y, delta)

        posTo.x += -(self._sign(posBug.x, posFrom.x) * (delta / 10) * x) * speed
        posTo.y += -(self._sign(posBug.y, posFrom.y) * (delta / 10) * y) * speed

        if self._Wall_Check(posTo)[0]:
            posTo.x += (self._sign(posBug.x, posFrom.x) * (delta / 10) * x) * speed
            posTo.y += (self._sign(posBug.y, posFrom.y) * (delta / 10) * y) * speed

            posTo.x += -(self._sign(posBug.x, posFrom.x) * (delta / 10) * x) * 0.7 * speed
            if self._Wall_Check(posTo)[0]:
                posTo.x += (self._sign(posBug.x, posFrom.x) * (delta / 10) * x) * 0.7 * speed
                posTo.y += -(self._sign(posBug.y, posFrom.y) * (delta / 10) * y) * 0.7 * speed
            if self._Wall_Check(posTo)[0]:
                return None

        self.Node1.setLocalPosition(posTo)  # safe changes
        return posTo

    def _IsGameEnd(self, pos):
        if pos is None:
            return
        if self._Node_In_Box(pos, self.Finish):
            self._Clean_Full()
            self.enigmaComplete()
        else:
            return

    def _update(self, dt):
        pos = self._Move_Chip()

        self._IsGameEnd(pos)
        return False

    def _start_affector(self):
        self.affector = Mengine.addAffector(self._update)

    def _end_affector(self):
        if self.affector is not None:
            Mengine.removeAffector(self.affector)
        self.affector = None

    def _Bounding(self, Socket_Movie):
        socket = Socket_Movie.getSocket(self.param.FinishSocket)
        self.Finish = Mengine.getHotSpotPolygonBoundingBox(socket)
        for i in range(self.param.WallNumber):
            socket = Socket_Movie.getSocket(self.param.WallSocketName + str(i))
            self.Sockets.append(socket)
            box = Mengine.getHotSpotPolygonBoundingBox(socket)
            self.Bounding_Box.append(box)

    def _playEnigma(self):
        self._load_param()
        self._setup()

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            if self.Start_Spike:
                ZoomOpenSpeed = DefaultManager.getDefaultFloat('ZoomOpenSpeed', 50)
                tc.addDelay(30000.0 / ZoomOpenSpeed)
                self.Start_Spike = not self.Start_Spike

            tc.addFunction(self._Bounding, self.Movies[1])
            tc.addTask("TaskMouseButtonClick", isDown=True)
            tc.addFunction(self._start_affector)
            with tc.addRepeatTask() as (tc_repeat, tc_until):
                tc_repeat.addNotify(Notificator.onSoundEffectOnObject, self.object, "MouseMagnet_Move")
                tc_repeat.addDelay(450)

                tc_until.addTask("TaskMouseButtonClick", isDown=False)
            tc.addFunction(self._end_affector)

    def _attachMovieToNode(self, movie, node):
        entity_node = movie.getEntityNode()
        node.addChild(entity_node)

    def __onMousePositionChange(self, touchID, position):
        self.Node_Mouse.setWorldPosition((position.x, position.y))

    def _setup(self):
        self.MousePositionProviderID = Mengine.addMousePositionProvider(None, None, self.__onMousePositionChange)

        entityNode = self.object.getEntityNode()
        Chip = self.object.generateObject(self.param.PrototypeChip, self.param.PrototypeChip)
        self.Movies.append(Chip)
        Walls = self.object.generateObject(self.param.PrototypeWalls, self.param.PrototypeWalls)
        self.Movies.append(Walls)
        self.Node1 = Mengine.createNode("Interender")
        self.Node2 = Mengine.createNode("Interender")
        self.Node_Mouse = Mengine.createNode("Interender")
        entityNode.addChild(self.Node1)
        entityNode.addChild(self.Node_Mouse)

        cort = (self.param.ChipStartX, self.param.ChipStartY)

        self.Node1.setLocalPosition(cort)
        self._attachMovieToNode(Chip, self.Node1)
        self._attachMovieToNode(Walls, entityNode)

    def _load_param(self):
        self.param = MouseMagnetManager.getParam(self.EnigmaName)

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._Clean_Full()
        self._playEnigma()

    def _pauseEnigma(self):
        self._Clean_Full()

    def _stopEnigma(self):
        self._Clean_Full()

    def _Clean_Full(self):
        self._end_affector()
        self.affector = None
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for movie in self.Movies:
            movie.onDestroy()
        self.Movies = []

        if self.MousePositionProviderID is not None:
            Mengine.removeMousePositionProvider(self.MousePositionProviderID)
            self.MousePositionProviderID = None

        self.MousePositionProviderID = None
        self.Sockets = []
        self.Bounding_Box = []
        self.Movies = []

        self.Node_Mouse = None
        self.Node1 = None
        self.Node2 = None
        self.tc = None
        self.Timer = 200.0
        self.speed = 0.09
        self.Finish = None
        self.Start_Spike = True

    def _onPreparationDeactivate(self):
        super(MouseMagnet, self)._onPreparationDeactivate()
        self._Clean_Full()

    def _onDeactivate(self):
        super(MouseMagnet, self)._onDeactivate()

    def _onActivate(self):
        super(MouseMagnet, self)._onActivate()

    def _onPreparation(self):
        super(MouseMagnet, self)._onPreparation()
