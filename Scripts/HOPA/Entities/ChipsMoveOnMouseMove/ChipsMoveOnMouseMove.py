from Foundation.TaskManager import TaskManager
from HOPA.ChipsMoveOnMouseMoveManager import ChipsMoveOnMouseMoveManager


Enigma = Mengine.importEntity("Enigma")


class ChipsMoveOnMouseMove(Enigma):
    def __init__(self):
        super(ChipsMoveOnMouseMove, self).__init__()
        self.Bug_Number = None
        self.Bug_Number_Left = None
        self.tc = None
        self.Movie_BG = None
        self.Node_Mouse = None
        self.Movie2_Sockets = None
        self.Bug_Chain = 40
        self.Rotator = 0

        self.Bugs = []
        self.Nodes1 = []
        self.Nodes2 = []
        self.Nodes3 = []
        self.Sockets = []
        self.Rotational_Direction = []
        self.Rotational_Speed = []
        self.Counter = []
        self.MousePositionProviderID = None
        self.Bound = True
        self.Timer = 9000.0
        self.skip_sem = None

    def _onActivate(self):
        super(ChipsMoveOnMouseMove, self)._onActivate()

    def _onPreparation(self):
        super(ChipsMoveOnMouseMove, self)._onPreparation()

    def _playEnigma(self):
        self._load_param()
        self._setup()

        self.semaphores = [Semaphore(False, "Bug_{}".format(n)) for n in range(self.Bug_Number)]

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            with tc.addParallelTask(4) as (tc_move, tc_rot1, tc_movie, tc_bug):
                for ii, source1 in tc_move.addParallelTaskList(self.Counter):
                    with source1.addWhileTask() as source11:
                        source11.addScope(self._scopeMove_Node2, ii, self.Nodes2[ii], self.Timer)
                for ii, source2 in tc_rot1.addParallelTaskList(self.Counter):
                    with source2.addWhileTask() as source22:
                        source22.addScope(self._scope_rot, ii, self.Timer)
                for ii, source4 in tc_movie.addParallelTaskList(self.Counter):
                    with source4.addWhileTask() as source44:
                        source44.addTask("TaskMovie2Play", Movie2=self.Bugs[ii])  # , Loop=True, Wait=False)
                for ii, source6 in tc_bug.addParallelTaskList(self.Counter):
                    source6.addDelay(300.0)
                    source6.addFunction(self._Bounding)
                    with source6.addRepeatTask() as (tc_repeat, tc_until):
                        tc_repeat.addScope(self._scopeMove_Bug, ii, self.Timer)
                        tc_repeat.addScope(self._Catch_The_Bug, ii, self.Timer)

                        tc_until.addSemaphore(self.semaphores[ii], From=True)
                        tc_until.addScope(self._IsGameEnd)

        pass

    def _setup_params(self):
        self.Bug_Number = len(self.param.Bugs)
        for i in range(self.Bug_Number):
            self.Counter.append(i)
            self.Rotational_Speed.append((2 + Mengine.rand(100) / 50) / 2)
            if i % 2 == 0:
                self.Rotational_Direction.append(1)
            else:
                self.Rotational_Direction.append(-1)

        self.Rotator = self.Bug_Number
        self.Bug_Number_Left = self.Bug_Number

        self.Movie_BG = self.object.getObject(self.param.MovieBG)

        for elem in self.param.Layers:
            if elem not in self.Movie_BG.getParam("DisableLayers"):
                self.Movie_BG.appendParam("DisableLayers", elem)

        pass

    def _setup(self):
        self._setup_params()

        entityNode = self.object.getEntityNode()
        self.Node_Mouse = Mengine.createNode("Interender")
        entityNode.addChild(self.Node_Mouse)

        self.MousePositionProviderID = Mengine.addMousePositionProvider(None, None, None, self.__onMousePositionChange)
        for i in range(self.Bug_Number):
            Movie2Object = self.object.generateObject("Movie2_Bug" + str(i), self.param.Bugs[i])
            Node1 = Mengine.createNode("Interender")
            Node2 = Mengine.createNode("Interender")
            Node3 = Mengine.createNode("Interender")

            entityNode.addChild(Node1)
            Node1.addChild(Node2)
            Node2.addChild(Node3)
            self._attachMovieToNode(Movie2Object, Node3)

            x = 475 + Mengine.rand(360)
            y = 150 + Mengine.rand(380)
            cort = (x, y)

            Node1.setLocalPosition(cort)
            cort = (self.Bug_Chain, self.Bug_Chain)
            Node2.setLocalPosition(cort)

            Node3.setLocalPosition(cort)

            self.Nodes1.append(Node1)
            self.Nodes2.append(Node2)
            self.Nodes3.append(Node3)
            self.Bugs.append(Movie2Object)

        self.Movie2_Sockets = self.object.generateObject("Movie2_BG_Sockets", "Movie2_BG_Sockets")
        self._attachMovieToNode(self.Movie2_Sockets, entityNode)

        self.Sockets.append(self.Movie2_Sockets.getSocket('BoundingBox'))
        self.Sockets.append(self.Movie2_Sockets.getSocket('Finish1'))
        self.Sockets.append(self.Movie2_Sockets.getSocket('Finish2'))

    pass

    def _attachMovieToNode(self, movie, node):
        entity_node = movie.getEntityNode()
        node.addChild(entity_node)

    def _scopeMove_Node2(self, source, i, node, time=None):
        posTo = self.Nodes3[i].getLocalPosition()
        posTo.x += Mengine.rand(self.Bug_Chain * 4) - self.Bug_Chain * 2
        posTo.y += Mengine.rand(self.Bug_Chain * 4) - self.Bug_Chain * 2

        if time is None or time == 0.0:
            node.setLocalPosition(posTo)
        else:
            source.addTask("TaskNodeMoveTo", Node=node, To=posTo, Time=time)

    def _scope_rot(self, source, i, time):
        rot = (self.Rotational_Direction[i] * self.Rotator * self.Rotational_Speed[i]) / 4
        with source.addParallelTask(2) as (tc_rot1, tc_rot2):
            tc_rot1.addTask('TaskNodeRotateTo', Node=self.Nodes2[i], To=rot, Time=time)
            tc_rot2.addTask('TaskNodeRotateTo', Node=self.Nodes3[i], To=-rot, Time=time)
            tc_rot2.addFunction(self._Next_rot)

    def _scopeMove_Bug(self, source, i, time):
        posBug = self.Nodes3[i].getWorldPosition()
        posTo = self.Nodes1[i].getWorldPosition()
        posFrom = self.Node_Mouse.getWorldPosition()
        Zoom_border = self._Node_Out_Box(posBug, self.Sockets[0])
        speed = 0.09

        if Zoom_border[0]:
            posTo.x += Zoom_border[1]
            posTo.y += Zoom_border[2]
        elif self._Distance(posBug, posFrom, 55):
            posTo.x += (self._sign(posBug.x, posFrom.x) * (75) - (posBug.x - posFrom.x))
            posTo.y += (self._sign(posBug.y, posFrom.y) * (75) - (posBug.y - posFrom.y))
            source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipsMoveOnMouseMove_Bug_Escape')
        else:
            source.addDelay(self.Timer / 100)
            return

        source.addScope(self._scopeMove_Bug1, i, posTo, time * speed)

    def _scopeMove_Bug1(self, source, i, posTo, time):
        if time is None or time == 0.0:
            self.Nodes1[i].setLocalPosition(posTo)
        else:
            source.addTask("TaskNodeMoveTo", Node=self.Nodes1[i], To=posTo, Time=time)

    def _sign(self, a, b):
        if a - b < 0:
            return -1
        elif a - b > 0:
            return 1
        else:
            return 0

    def __onMousePositionChange(self, touchID, position):
        self.Node_Mouse.setWorldPosition((position.x, position.y))

    def _Node_Out_Box(self, pos, box):
        Cage = False
        X_Change = 0
        Y_Change = 0
        Back_move = 60
        if pos.x < box.minimum.x:
            Cage = True
            X_Change = Back_move
        elif pos.x > box.maximum.x:
            Cage = True
            X_Change = - Back_move

        if pos.y < box.minimum.y:
            Cage = True
            Y_Change = Back_move
        elif pos.y > box.maximum.y:
            Cage = True
            Y_Change = - Back_move
        return Cage, X_Change, Y_Change

    def _Node_In_Box(self, pos, box):
        if pos.x > box.minimum.x and pos.x < box.maximum.x and pos.y > box.minimum.y and pos.y < box.maximum.y:
            return True
        else:
            return False

    def _IsGameEnd(self, source):
        if self.Bug_Number_Left < 1:
            self._BG_fix()
            self.enigmaComplete()
        else:
            return

        pass

    def _IS_Bug_In_Box(self, Bug):
        Bug = Bug.getWorldPosition()
        box1 = self._Node_In_Box(Bug, self.Sockets[1])
        box2 = self._Node_In_Box(Bug, self.Sockets[2])
        if box1 or box2:
            return True
        else:
            return False
            pass
        pass

    def _Put_Bug_In_box(self, i):
        if self.param.Layers[i] in self.Movie_BG.getDisableLayers():
            self.Movie_BG.delParam("DisableLayers", self.param.Layers[i])
            self.Bug_Number_Left += -1

    def _Catch_The_Bug(self, source, i, time):
        if self._IS_Bug_In_Box(self.Nodes3[i]):
            with source.addParallelTask(2) as (parallel_1, parallel_2):
                parallel_1.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ChipsMoveOnMouseMove_Bug_Caught')
                parallel_2.addTask("TaskNodeAlphaTo", Node=self.Nodes1[i], From=1, To=0, Time=time / 13)
            source.addFunction(self._Put_Bug_In_box, i)
            source.addSemaphore(self.semaphores[i], To=True)

    def _Distance(self, pos1, pos2, difference=35):
        if ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5 < difference:
            return True
        else:
            return False
        pass

    def _Bounding(self):
        if self.Bound:
            for i in range(len(self.Sockets)):
                # self.Sockets[i]= self.Sockets[i].getBoundingBox()
                self.Sockets[i] = Mengine.getHotSpotPolygonBoundingBox(self.Sockets[i])
            self.Bound = False
        pass

    def _Next_rot(self):
        self.Rotator += 1

    def _BG_fix(self):
        for elem in self.param.Layers:
            if elem in self.Movie_BG.getParam("DisableLayers"):
                self.Movie_BG.delParam("DisableLayers", elem)
        self._Clean_Full()

    def _load_param(self):
        self.param = ChipsMoveOnMouseMoveManager.getParam(self.EnigmaName)

    def _skipEnigma(self):
        self._BG_fix()

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
        self.Bug_Number_Left = 100

        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.semaphores = []

        if self.MousePositionProviderID is not None:
            Mengine.removeMousePositionProvider(self.MousePositionProviderID)
        self.MousePositionProviderID = None

        for movie in self.Bugs:
            movie.onDestroy()
        self.Bugs = []
        if self.Movie2_Sockets != None:
            self.Movie2_Sockets.onDestroy()
            self.Movie2_Sockets = None
        self.Bug_Number_Left = None
        self.Rotator = self.Bug_Number

        if self.Node_Mouse is not None:
            Mengine.destroyNode(self.Node_Mouse)
            self.Node_Mouse = None

        for node in self.Nodes3:
            Mengine.destroyNode(node)
        self.Nodes3 = []

        for node in self.Nodes2:
            Mengine.destroyNode(node)
        self.Nodes2 = []

        for node in self.Nodes1:
            Mengine.destroyNode(node)
        self.Nodes1 = []

        self.Bug_Number = None
        self.Bug_Number_Left = None
        self.tc = None
        self.Movie_BG = None
        self.Node_Mouse = None
        self.finigh_polygon = None
        self.Bounding_Box = 0
        self.Bug_Chain = 40
        self.Rotator = 0

        self.Bugs = []
        self.Nodes1 = []
        self.Nodes2 = []
        self.Nodes3 = []
        self.Screen_Size = []
        self.Rotational_Direction = []
        self.Rotational_Speed = []
        self.Counter = []
        self.MousePositionProviderID = None
        self.Timer = 12000.0
        self.skip_sem = None
        pass

    def _onPreparationDeactivate(self):
        super(ChipsMoveOnMouseMove, self)._onPreparationDeactivate()
        self._Clean_Full()

    def _onDeactivate(self):
        super(ChipsMoveOnMouseMove, self)._onDeactivate()  # self._Clean_Full()
