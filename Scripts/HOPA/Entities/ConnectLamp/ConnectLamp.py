from Foundation.TaskManager import TaskManager

from HOPA.ConnectLampManager import ConnectLampManager


Enigma = Mengine.importEntity("Enigma")


class ConnectLamp(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(ConnectLamp, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.Game = None
        self.AliasNames = []

        self.Points = {}
        self.Connects = []

        self.Play_Movies_Points = {}
        self.Play_Movies_Connects = {}

        self.Point_Status = {}
        self.Point_Connect_Count = {}
        self.Point_Connect_Count_Need = {}

        self.Connects_Status = []
        self.Select = -1
        pass

    def _skipEnigma(self):
        self.__Finita()
        self.enigmaComplete()
        pass

    def _playEnigma(self):
        self.__PreInit()
        self.__Init()
        pass

    def __PreInit(self):
        self.Game = ConnectLampManager.getGame(self.EnigmaName)
        pass

    def __Init(self):
        for point in self.Game.Points:
            Id = point.Id
            self.Points[Id] = point
            self.Point_Status[Id] = False
            self.Point_Connect_Count[Id] = 0
            self.Point_Connect_Count_Need[Id] = point.Connect_Number
            pass

        for con in self.Game.Connects:
            self.Connects.append(con)
            self.Connects_Status.append(False)
            pass

        for point in self.Points.itervalues():
            self.__Do_Point_Atlas(point)
            pass

        for id, con in enumerate(self.Game.Connects):
            self.__Do_Connect_Atlas(con, id)
            pass
        pass

    def __Do_Point_Atlas(self, point):
        Id = point.Id
        Movie0Idle_A = self.object.getObject(point.Movie_Idle_Active)
        Movie0Idle_P = self.object.getObject(point.Movie_Idle_Passive)

        Movie0Idle_A.setEnable(False)
        Movie0Idle_P.setEnable(False)

        mov_Play = [[(Movie0Idle_A, True)]]
        self.Play_Movies_Points[Id] = (mov_Play)

        def rea():
            res = self.Point_Status[Id]
            if (res is True):
                Movie0Idle_A.setEnable(True)
                Movie0Idle_P.setEnable(False)
                mov_Play[0] = [(Movie0Idle_A, True)]
                pass
            else:
                Movie0Idle_A.setEnable(False)
                Movie0Idle_P.setEnable(True)
                mov_Play[0] = [(Movie0Idle_P, True)]
                pass
            pass

        name_A1 = "ConnectLamp_Idle_%d" % (Id)
        self.AliasNames.append(name_A1)

        with TaskManager.createTaskChain(Name=name_A1, Repeat=True) as tc:
            tc.addFunction(rea)
            tc.addTask("AliasMultyplMovePlay", Movies=mov_Play)
            pass
        pass

    def __Do_Connect_Atlas(self, con, Id):
        from_C = con.Id_From
        to_C = con.Id_To
        Points = self.object.getObject("Movie_Points")

        Movie_Idle = self.object.getObject(con.Movie_Idle)
        Movie_Select = self.object.getObject(con.Movie_Select)
        Movie_None = self.object.generateObject("Movie_None_Con_Id_%s" % (Id), "Movie_None")

        Movie_Idle.setEnable(False)
        Movie_Select.setEnable(False)
        Movie_None.setEnable(True)

        mov_Play = [[(Movie_None, True)]]
        self.Play_Movies_Connects[Id] = mov_Play

        def rea():
            Movie_Idle.setEnable(True)
            Movie_Select.setEnable(True)

            if (self.Select == Id):
                Movie_Idle.setEnable(False)
                Movie_Select.setEnable(True)
                mov_Play[0] = [(Movie_Select, True)]
                return
                pass

            res = self.Connects_Status[Id]
            if (res is True):
                Movie_Idle.setEnable(True)
                Movie_Select.setEnable(False)
                mov_Play[0] = [(Movie_Idle, True)]
                pass
            else:
                Movie_Idle.setEnable(False)
                Movie_Select.setEnable(False)
                mov_Play[0] = [(Movie_None, True)]
                pass
            pass

        name_A1 = "ConnectLamp_Con_%d_%d" % (from_C, to_C)
        name_A2 = "ConnectLamp_Con_Handle_%d_%d" % (from_C, to_C)
        self.AliasNames.append(name_A1)
        self.AliasNames.append(name_A2)

        with TaskManager.createTaskChain(Name=name_A1, Repeat=True) as tc:
            tc.addFunction(rea)
            tc.addTask("AliasMultyplMovePlay", Movies=mov_Play)

            # tc.addTask("TaskMoviePlay", Movie = Movie_None, Wait = False)
            # tc.addTask("TaskMoviePlay", Movie = Movie_Idle, Wait = False)
            # tc.addTask("TaskMoviePlay", Movie = Movie_Select, Wait = True)
            pass
        sockName = "socket_%d_%d" % (from_C, to_C)

        def select():
            self.__Skip_Movie(mov_Play[0][0][0])
            self.Select = Id
            pass

        def Deselect():
            self.__Skip_Movie(mov_Play[0][0][0])
            self.Select = -1
            pass

        def Click_In():
            self.__Skip_Movie(mov_Play[0][0][0])
            self.Select = -1

            if (self.Connects_Status[Id] is True):
                self.Connects_Status[Id] = False
                self.__Rec_Connect_Point(from_C, -1)
                self.__Rec_Connect_Point(to_C, -1)
            else:
                self.Connects_Status[Id] = True
                self.__Rec_Connect_Point(from_C, +1)
                self.__Rec_Connect_Point(to_C, +1)
                pass

            for st in self.Point_Status.itervalues():
                if (st is False):
                    return
                    pass
                pass

            self.__Finita()
            self.enigmaComplete()
            pass

        with TaskManager.createTaskChain(Name=name_A2, Repeat=True) as tc:
            with tc.addRaceTask(3) as (tc_L1, tc_L2, tc_Click):
                tc_L1.addTask("TaskMovieSocketEnter", SocketName=sockName, Movie=Points)
                tc_L1.addFunction(select)

                tc_L2.addTask("TaskMovieSocketLeave", SocketName=sockName, Movie=Points)
                tc_L2.addFunction(Deselect)

                tc_Click.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=Points)
                tc_Click.addFunction(Click_In)
                pass
            pass
        pass

    def __Rec_Connect_Point(self, id, add):
        cur = self.Point_Connect_Count[id]
        now = cur + add
        self.Point_Connect_Count[id] = now
        need = self.Point_Connect_Count_Need[id]
        stat = self.Point_Status[id]
        if (now == need):
            if (stat is True):
                return

            self.Point_Status[id] = True
            self.__Skip_Movie(self.Play_Movies_Points[id][0][0][0])
            pass
        else:
            if (stat is False):
                return

            self.Point_Status[id] = False
            self.__Skip_Movie(self.Play_Movies_Points[id][0][0][0])
            pass
        pass

    def __Skip_Movie(self, mov):
        if (mov is None):
            return
            pass

        mov.setLastFrame(True)

        # mov_Ent = mov.getEntity()
        # dur = mov.getDuration() * 999
        # mov_Ent.setTiming(dur)
        pass

    def __Finita(self):
        for name_A in self.AliasNames:
            self.__canTT(name_A)
            pass

        for point in self.Points.itervalues():
            Movie0Idle_A = self.object.getObject(point.Movie_Idle_Active)
            Movie0Idle_P = self.object.getObject(point.Movie_Idle_Passive)

            Movie0Idle_A.setEnable(False)
            Movie0Idle_P.setEnable(False)
            pass

        for con in self.Game.Connects:
            Movie_Idle = self.object.getObject(con.Movie_Idle)
            Movie_Select = self.object.getObject(con.Movie_Select)

            Movie_Idle.setEnable(False)
            Movie_Select.setEnable(False)
            pass

        pass

    def __canTT(self, Name):
        if TaskManager.existTaskChain(Name) is True:
            TaskManager.cancelTaskChain(Name)
            pass
        pass

    pass
