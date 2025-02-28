from Foundation.TaskManager import TaskManager

from HOPA.SandGlassManager import SandGlassManager


Enigma = Mengine.importEntity("Enigma")


class Sandglass(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(Sandglass, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.Game = None
        self.ReInitParamentrs_Game()
        pass

    def ReInitParamentrs_Game(self):
        self.Points = {}
        self.Connects = []

        self.Active_Move = {}
        self.Active_Connects = []
        self.Active_Connects_Pass = []
        self.Play_Movies_Points = {}
        self.Play_Movies_Connects = {}
        self.Connects_End = {}
        self.Selected = -1
        self.Click_Prev = -1
        self.Click = -1
        self.AliasNames = []
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
        self.Game = SandGlassManager.getGame(self.EnigmaName)

        pass

    def __Init(self):
        self.__StartGame()
        pass

    def __Init_Game_Data(self):
        for point in self.Game.Points:
            Id = point.Id
            self.Active_Move[Id] = point
            self.Points[Id] = point
            pass

        for con in self.Game.Connects:
            self.Active_Connects.append(con)
            self.Connects.append(con)
            pass

        pass

    def __Do_Point_Atlas(self, point):
        Id = point.Id
        Points = self.object.getObject("Movie_Points")
        Movie0Idle_A = self.object.getObject(point.Movie_Idle_Active)
        Movie0Idle_P = self.object.getObject(point.Movie_Idle_Passive)
        Movie0Idle_S = self.object.getObject(point.Movie_Select)
        Movie0Idle_U = self.object.getObject(point.Movie_Use)
        Movie_None = self.object.generateObject("Movie_None_Point_Id", "Movie_None")

        Movie0Idle_A.setEnable(False)
        Movie0Idle_P.setEnable(False)
        Movie0Idle_S.setEnable(False)
        Movie0Idle_U.setEnable(False)

        mov_Play = [[(Movie_None, True)]]
        self.Play_Movies_Points[Id] = (mov_Play)

        def rea():
            if (self.Click == Id):
                Movie0Idle_A.setEnable(False)
                Movie0Idle_P.setEnable(False)
                Movie0Idle_S.setEnable(False)
                Movie0Idle_U.setEnable(True)
                # print "%s %s" % (Id, "Under")
                mov_Play[0] = [(Movie0Idle_U, True)]

                return
                pass

            if (self.Selected == Id):
                Movie0Idle_A.setEnable(False)
                Movie0Idle_P.setEnable(False)
                Movie0Idle_S.setEnable(True)
                Movie0Idle_U.setEnable(False)
                # print "%s %s" % (Id, "Select")
                mov_Play[0] = [(Movie0Idle_S, True)]
                return
                pass

            if (Id in self.Active_Move):
                Movie0Idle_A.setEnable(True)
                Movie0Idle_P.setEnable(False)
                Movie0Idle_S.setEnable(False)
                Movie0Idle_U.setEnable(False)
                # print "%s %s" % (Id, "Active")
                mov_Play[0] = [(Movie0Idle_A, True)]
                pass
            else:
                Movie0Idle_A.setEnable(False)
                Movie0Idle_P.setEnable(True)
                Movie0Idle_S.setEnable(False)
                Movie0Idle_U.setEnable(False)
                # print "%s %s" % (Id, "Pasive")
                mov_Play[0] = [(Movie0Idle_P, True)]
                pass
            pass

        sockName = point.Socket_Name

        def filter():
            if (Id == self.Click_Prev):
                return False
                pass
            if (Id in self.Active_Move):
                return True
                pass
            return False
            pass

        def select():
            mov = mov_Play[0][0][0]
            self.__Skip_Movie(mov)
            self.Selected = Id
            pass

        def Deselect():
            mov = mov_Play[0][0][0]
            self.__Skip_Movie(mov)
            self.Selected = -1
            pass

        def Click_In():
            self.Click_Prev = self.Click
            self.Click = Id
            self.__Recal_Ac()

            for movee in self.Play_Movies_Points.itervalues():
                self.__Skip_Movie(movee[0][0][0])
                pass

            if (len(self.Active_Connects) == 0):
                self.__Finita()
                self.enigmaComplete()
                return

            # if(len(self.Active_Move) == 0):
            #     print "Lose"
            #     self.__EndGame()
            #     self.__StartGame()
            #     return
            #     pass

            pass

        name_A1 = "Sandglass_Idle_%d" % (Id)
        name_A2 = "Sandglass_Poins_%d" % (Id)
        self.AliasNames.append(name_A1)
        self.AliasNames.append(name_A2)

        with TaskManager.createTaskChain(Name=name_A1, Repeat=True) as tc:
            tc.addFunction(rea)
            tc.addTask("AliasMultyplMovePlay", Movies=mov_Play)
            pass

        with TaskManager.createTaskChain(Name=name_A2, Repeat=True) as tc:
            with tc.addRaceTask(3) as (tc_L1, tc_L2, tc_Click):
                tc_L1.addTask("TaskMovieSocketEnter", SocketName=sockName, Movie=Points, Filter=filter,
                              isMouseEnter=False)
                # tc_L1.addTask("TaskPrint", Value = "select %s"%name_A2)
                tc_L1.addFunction(select)
                tc_L1.addNotify(Notificator.onSandGlassMouseEnterSocket)

                tc_L2.addTask("TaskMovieSocketLeave", SocketName=sockName, Movie=Points)
                tc_L2.addNotify(Notificator.onSandGlassMouseLeaveSocket)
                tc_L2.addFunction(Deselect)

                tc_Click.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=Points, Filter=filter)
                tc_Click.addFunction(Click_In)
                tc_Click.addFunction(Notificator.onSandGlassMouseClickSocket, Id)
                pass
            pass
        pass

    def __Recal_Ac(self):
        if (self.Click_Prev != -1):
            con = self.__Try_Connects_In_Active(self.Click_Prev, self.Click)
            self.Active_Connects.remove(con)
            # print con, " Remove"
            # print self.Active_Connects
            pass

        self.Active_Move = {}
        for con in self.Active_Connects:
            if (con.Id_From == self.Click or con.Id_To == self.Click):
                if (con.Id_From not in self.Active_Move):
                    self.Active_Move[con.Id_From] = self.Points[con.Id_From]
                    pass

                if (con.Id_To not in self.Active_Move):
                    self.Active_Move[con.Id_To] = self.Points[con.Id_To]
                    pass
                # if(self.Click not in self.Active_Move):
                #     self.Active_Move[self.Click] = self.Points[self.Click]
                #     pass

                pass
            pass

        if (len(self.Active_Move) != 0):
            del self.Active_Move[self.Click]
            pass
        pass

    def __Skip_Movie(self, mov):
        if (mov is None):
            return
            pass
        mov_Ent = mov.getEntity()
        dur = mov.getDuration() * 999
        mov_Ent.setTiming(dur)
        pass

    def __Do_Idle_Conencts(self, con, Id):
        from_C = con.Id_From
        to_C = con.Id_To

        Movie_Idle = self.object.getObject(con.Movie_Idle)
        Movie_Select = self.object.getObject(con.Movie_Select)
        Movie_Use = self.object.getObject(con.Movie_Use)
        Movie_None = self.object.generateObject("Movie_None_Con_Id", "Movie_None")

        Movie_Idle.setEnable(False)
        Movie_Select.setEnable(False)
        Movie_Use.setEnable(False)

        mov_Play = [[(Movie_None, True)]]
        self.Play_Movies_Connects[Id] = mov_Play
        paly_end = [0]
        self.Connects_End[Id] = paly_end

        def rea():
            if (paly_end[0] == 1):
                Movie_Idle.setEnable(False)
                Movie_Select.setEnable(False)
                Movie_Use.setEnable(True)
                mov_Play[0] = [(Movie_Use, True)]
                paly_end[0] = 2
                return
                pass

            in_c = self.__Try_Connects_In_Active(from_C, to_C)
            if (in_c is None or paly_end[0] == 2):
                Movie_Idle.setEnable(False)
                Movie_Select.setEnable(False)
                mov_Play[0] = [(Movie_None, True)]
                return
                pass

            if (self.Click == -1):
                if (self.Selected == from_C or self.Selected == to_C):
                    Movie_Idle.setEnable(False)
                    Movie_Select.setEnable(True)
                    mov_Play[0] = [(Movie_Select, True)]
                    return
                    pass
                pass
            else:
                if (self.Selected == from_C and self.Click == to_C) or (self.Click == from_C and self.Selected == to_C):
                    Movie_Idle.setEnable(False)
                    Movie_Select.setEnable(True)
                    mov_Play[0] = [(Movie_Select, True)]
                    return
                    pass
                pass

            Movie_Idle.setEnable(True)
            Movie_Select.setEnable(False)
            mov_Play[0] = [(Movie_Idle, True)]
            pass

        def filt_Und():
            if (self.Selected == from_C or self.Selected == to_C):
                mov = mov_Play[0][0][0]
                self.__Skip_Movie(mov)
                return True
                pass
            return False
            pass

        def skip_Current(click):
            if (from_C == self.Click_Prev and to_C == self.Click) or (from_C == self.Click and to_C == self.Click_Prev):
                paly_end[0] = 1
                for idd, movee in enumerate(self.Play_Movies_Connects.itervalues()):
                    if (self.Connects_End[idd] == 0):
                        self.__Skip_Movie(movee[0][0][0])
                        pass
                    pass
                self.__Skip_Movie(mov_Play[0][0][0])
                return True
                pass
            return False
            pass

        name_A1 = "Sandglass_Idle_Con_%d_%d" % (from_C, to_C)
        name_A2 = "Sandglass_Idle_Con_Change_%d_%d" % (from_C, to_C)
        name_A3 = "Sandglass_Click_Con_%d_%d" % (from_C, to_C)
        self.AliasNames.append(name_A1)
        self.AliasNames.append(name_A2)
        self.AliasNames.append(name_A3)

        with TaskManager.createTaskChain(Name=name_A1, Repeat=True) as tc:
            tc.addFunction(rea)
            tc.addTask("AliasMultyplMovePlay", Movies=mov_Play)
            pass

        with TaskManager.createTaskChain(Name=name_A2, Repeat=True) as tc:
            tc.addListener(Notificator.onSandGlassMouseEnterSocket, Filter=filt_Und)
            tc.addListener(Notificator.onSandGlassMouseLeaveSocket, Filter=filt_Und)
            pass

        with TaskManager.createTaskChain(Name=name_A3) as tc:
            tc.addListener(Notificator.onSandGlassMouseClickSocket, Filter=skip_Current)
            pass
        pass

    def __Reset_Aliase(self):
        name_A1 = "Sandglass_Reset"
        self.AliasNames.append(name_A1)

        Points = self.object.getObject("Movie_Points")
        sockName = "Reset"

        def res():
            self.__EndGame()
            self.__StartGame()
            pass

        with TaskManager.createTaskChain(Name=name_A1, Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=Points)
            tc.addFunction(res)
            pass
        pass

    def __find_Connects(self, point_Id):
        conects = []
        for con in self.Active_Connects:
            if (con.Id_From == point_Id or con.Id_To == point_Id):
                conects.append(con)
                pass
            pass
        return conects
        pass

    def __Try_Connects_In_Active(self, from_C, to_C):
        if (len(self.Active_Connects) == 0):
            return None
            pass
        for con in self.Active_Connects:
            if ((con.Id_From == from_C and con.Id_To == to_C) or (con.Id_From == to_C and con.Id_To == from_C)):
                return con
                pass
            pass
        return None
        pass

    def __StartGame(self):
        self.ReInitParamentrs_Game()

        self.__Init_Game_Data()
        for point in self.Game.Points:
            self.__Do_Point_Atlas(point)
            pass

        for id, con in enumerate(self.Game.Connects):
            self.__Do_Idle_Conencts(con, id)
            pass

        self.__Reset_Aliase()
        pass

    def __EndGame(self):
        for name_A in self.AliasNames:
            self.__canTT(name_A)
            pass
        pass

    def __Finita(self):
        self.__EndGame()
        for point in self.Game.Points:
            Movie0Idle_A = self.object.getObject(point.Movie_Idle_Active)
            Movie0Idle_P = self.object.getObject(point.Movie_Idle_Passive)
            Movie0Idle_S = self.object.getObject(point.Movie_Select)
            Movie0Idle_U = self.object.getObject(point.Movie_Use)

            Movie0Idle_A.setEnable(False)
            Movie0Idle_P.setEnable(False)
            Movie0Idle_S.setEnable(False)
            Movie0Idle_U.setEnable(False)
            pass

        for con in self.Game.Connects:
            Movie_Idle = self.object.getObject(con.Movie_Idle)
            Movie_Select = self.object.getObject(con.Movie_Select)
            Movie_Use = self.object.getObject(con.Movie_Use)

            Movie_Idle.setEnable(False)
            Movie_Select.setEnable(False)
            Movie_Use.setEnable(False)
            pass

        pass

    def __canTT(self, Name):
        if TaskManager.existTaskChain(Name) is True:
            TaskManager.cancelTaskChain(Name)
            pass
        pass

    pass
