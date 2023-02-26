from Foundation.ArrowManager import ArrowManager
from Foundation.TaskManager import TaskManager
from HOPA.PaperConnectGameManager import PaperConnectGameManager

Enigma = Mengine.importEntity("Enigma")

class PaperConnectGame(Enigma):
    Click_Pos = None

    class Paper(object):
        def __init__(self, Game, PapaerData):
            self.Name = None
            self.Game = Game
            self.PapaerData = PapaerData
            self.Movie = None

            self.Paper_Group = []
            self.Pos = None
            self.PosStart = None
            self.PosAnch = None

            self.doInit()
            pass

        def doInit(self):
            self.Paper_Group.append(self)
            MovieName = self.PapaerData.PaperMovieName
            self.Name = MovieName
            self.Movie = self.Game.object.getObject("Movie_%s" % (MovieName))

            Movie_PointsStart = self.Game.object.getObject("Movie_PointsStart")
            Movie_PointsStartEnt = Movie_PointsStart.getEntity()
            Movie_PointsStart.setEnable(False)
            Sub_MovieStart = Movie_PointsStartEnt.getSubMovie(MovieName)

            Movie_Points = self.Game.object.getObject("Movie_Points")
            Movie_PointsEnt = Movie_Points.getEntity()
            Movie_Points.setEnable(False)
            Sub_Movie = Movie_PointsEnt.getSubMovie(MovieName)

            self.PosStart = Sub_MovieStart.getLocalPosition()  # fish pos
            self.PosAnch = Sub_Movie.getOrigin()  # anchar
            Pos = Sub_Movie.getLocalPosition()

            self.Pos = (Pos[0] - self.PosAnch[0], Pos[1] - self.PosAnch[1])
            # self.Pos = Sub_Movie.getLocalPosition()
            self.setPosMovie()
            # self.Movie.setPosition(self.Pos)
            pass

        def addPaper(self, Paper):
            ar = self.Paper_Group
            if (ar == Paper.Paper_Group):
                return
                pass
            ar.extend(Paper.Paper_Group)

            for paper in ar:
                paper.Paper_Group = ar
                pass

            for paper in self.Paper_Group:
                paper.setPosIn(Paper.Pos)
                pass
            pass

        def addBotLayer(self):
            for paper in self.Paper_Group:
                data = paper.PapaerData
                if (data.Moving is False):
                    self.addBotLayerFr()
                    return
                    pass
                pass

            for paper in self.Paper_Group:
                ent = paper.Movie.getEntity()
                ent.removeFromParent()
                self.Game.MovieEntLay1.addChild(ent)
                pass
            pass

        def addBotLayerFr(self):
            for paper in self.Paper_Group:
                ent = paper.Movie.getEntity()
                ent.removeFromParent()
                self.Game.MovieEntLay1.addChildFront(ent)
                pass
            pass

        def addUpLayer(self):
            for paper in self.Paper_Group:
                data = paper.PapaerData
                if (data.Moving is False):
                    self.addBotLayerFr()
                    return
                    pass
                pass

            for paper in self.Paper_Group:
                ent = paper.Movie.getEntity()
                ent.removeFromParent()
                self.Game.MovieEntLay2.addChild(ent)
                pass
            pass

        def addPos(self, pos):
            for paper in self.Paper_Group:
                data = paper.PapaerData
                if (data.Moving is False):
                    return
                    pass
                pass

            for paper in self.Paper_Group:
                paper.addPosIn(pos)
                pass
            pass

        def addPosIn(self, pos):
            x = self.Pos[0] + pos[0]
            y = self.Pos[1] + pos[1]
            self.Pos = (x, y)
            self.setPosMovie()
            pass

        def setPos(self, pos):
            for paper in self.Paper_Group:
                data = paper.PapaerData
                if (data.Moving is False):
                    return
                    pass
                pass

            for paper in self.Paper_Group:
                paper.setPosIn(pos)
                pass
            pass

        def setPosIn(self, pos):
            self.Pos = pos
            self.setPosMovie()
            pass

        def setPosMovie(self):
            # x = self.Pos[0] - self.PosAnch[0]
            # y = self.Pos[1] - self.PosAnch[1]
            # self.Movie.setPosition((x, y))
            self.Movie.setPosition(self.Pos)
            pass
        pass

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(PaperConnectGame, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        ###PreInit
        self.Game = None
        self.Papers = {}
        self.MovieEntLay1 = None
        self.MovieEntLay2 = None
        self.BaseParrent = None
        pass

    def _playEnigma(self):
        self.__PreInit()
        self.__InitAlias()
        pass

    def _stopEnigma(self):
        self.__StopAlias()
        self.ReInitParamentrs()
        pass

    def __PreInit(self):
        self.MovieEntLay1 = self.object.getObject("Movie_Lay").getEntity()
        self.MovieEntLay2 = self.object.getObject("Movie_Lay2").getEntity()
        self.BaseParrent = self.MovieEntLay2.getParent()
        self.Game = PaperConnectGameManager.getGame(self.EnigmaName)
        for key, paper in self.Game.Parts.iteritems():
            papObj = PaperConnectGame.Paper(self, paper)
            self.Papers[key] = papObj
            pass
        pass

    def __InitAlias(self):
        for paper in self.Papers.itervalues():
            self.__InitAliasClickPaper(paper)
            pass
        pass

    def __StopAlias(self):
        for paper in self.Papers.itervalues():
            socketName = paper.Name
            name = "PaperClick_%s" % (socketName)
            if TaskManager.existTaskChain(name) is True:
                TaskManager.cancelTaskChain(name)
                pass
            pass
        pass

    def __InitAliasClickPaper(self, Paper):
        if (Paper.PapaerData.Moving is False):
            return
            pass
        Movie = Paper.Movie
        socketName = Paper.Name

        def _SetMousePos():
            PaperConnectGame.Click_Pos = Mengine.getCursorPosition()
            Paper.addUpLayer()
            ArrowManager.attachArrow(Movie)
            pass

        def _Mouse_Move():
            pos = Mengine.getCursorPosition()

            dif_X = pos[0] - PaperConnectGame.Click_Pos[0]
            dif_Y = pos[1] - PaperConnectGame.Click_Pos[1]

            res = Mengine.getContentResolution()
            lim = 75
            if (pos.x < lim):
                dif_X = 0
                pass

            if (pos.y < lim):
                dif_Y = 0
                pass

            if (pos.x > res.getWidth() - lim):
                dif_X = 0
                pass

            if (pos.y > res.getHeight() - lim - lim):
                dif_Y = 0
                pass

            if (dif_X == 0 and dif_Y == 0):
                return
                pass

            Paper.addPos((dif_X, dif_Y))
            PaperConnectGame.Click_Pos = pos
            pass

        with TaskManager.createTaskChain(Name="PaperClick_%s" % (socketName), Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=socketName, Movie=Movie, isDown=True)
            tc.addTask("TaskFunction", Fn=_SetMousePos)
            with tc.addRepeatTask() as (tc_rotate, tc_until):
                tc_rotate.addTask("TaskMouseMoveDistance", Distance=0)
                tc_rotate.addTask("TaskFunction", Fn=_Mouse_Move)

                tc_until.addTask("TaskMouseButtonClick", isDown=False)
                pass

            tc.addTask("TaskFunction", Fn=self._TryConnect, Args=(Paper,))
            pass

        pass

    def _TryConnect(self, MovePaper):
        ArrowManager.removeArrowAttach()
        data = MovePaper.PapaerData
        for connectData in data.ConectTo:
            paper = self.Papers[connectData]
            if (self.__checkConnect(MovePaper, paper)):
                MovePaper.addPaper(paper)
            pass

        MovePaper.addBotLayer()

        if (len(self.Game.Parts) == len(MovePaper.Paper_Group)):
            for paper in self.Papers.itervalues():
                self.BaseParrent.addChild(paper.Movie.getEntity())
                pass

            self.enigmaComplete()
            return
            pass
        pass

    def __checkConnect(self, paper1, paper2):
        dist = 144
        pos1 = paper1.Pos
        pos2 = paper2.Pos
        posS1 = paper1.PosStart
        posS2 = paper2.PosStart
        # ranX1 = abs(pos1[0] - posS1[0])
        # ranX2 = abs(pos2[0] - posS2[0])
        # ranY1 = abs(pos1[1] - posS1[1])
        # ranY2 = abs(pos2[1] - posS2[1])
        dif_X = pos1[0] - pos2[0]
        dif_Y = pos1[1] - pos2[1]
        sum = dif_X * dif_X + dif_Y * dif_Y
        if (sum <= dist):
            return True
            pass

        return False
        pass

    pass