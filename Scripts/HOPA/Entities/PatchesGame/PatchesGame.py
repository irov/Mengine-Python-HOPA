from Foundation.TaskManager import TaskManager

Enigma = Mengine.importEntity("Enigma")

class PatchesGame(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(PatchesGame, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.Mov_Idle = []
        self.Mov_IdleOpen = []
        self.Mov_MouseEnter = []
        self.Mov_Opening = []

        self.Mov_Points = None
        self.Active = []
        self.Data = [0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0]
        self.Find = 0
        self.NeedFind = 0
        for d in self.Data:
            if (d == 1):
                self.NeedFind = self.NeedFind + 1
                pass
            pass

        self.Block = -1
        self.Win = -1
        pass

    def _skipEnigma(self):
        self.__Finita()
        self.enigmaComplete()
        pass

    def _playEnigma(self):
        self._DoPlay()
        pass

    def _DoPlay(self):
        self._playInit()
        pass

    def _playInit(self):
        self.Mov_Points = self.object.getObject("Movie_Points")
        for i in range(17):
            self.Active.append(False)
            self._Do_Slot(i)

            pass
        pass

    def _Do_Slot(self, i):
        mov_Idle = self.object.getObject("Movie_Idle%d" % (i + 1))
        mov_IdleOpen = self.object.getObject("Movie_IdleOpen%d" % (i + 1))
        mov_MouseEnter = self.object.getObject("Movie_MouseEnter%d" % (i + 1))
        mov_Opening = self.object.getObject("Movie_Opening%d" % (i + 1))

        self.Mov_Idle.append(mov_Idle)
        self.Mov_IdleOpen.append(mov_IdleOpen)
        self.Mov_MouseEnter.append(mov_MouseEnter)
        self.Mov_Opening.append(mov_Opening)

        mov_IdleOpen.setEnable(False)
        mov_MouseEnter.setEnable(False)
        mov_Opening.setEnable(False)

        self._Do_Alias(i)
        pass

    def _Do_Alias(self, i):
        sockName = "socket%d" % (i)

        Idle = self.Mov_Idle[i]
        IdleOpen = self.Mov_IdleOpen[i]
        MouseEnter = self.Mov_MouseEnter[i]
        Opening = self.Mov_Opening[i]

        Mov = [[[Idle, True]]]
        ######################################################
        def filterund():
            if (self.Active[i] is False and self.Win == -1 and self.Block == -1):
                return True
            return False
            pass

        def und():
            MouseEnter.setEnable(True)
            pass

        def undLeav():
            MouseEnter.setEnable(False)
            pass

        with TaskManager.createTaskChain(Name="PatchesGame_%d" % (i), Repeat=True) as tc:
            tc.addTask("TaskMovieSocketEnter", SocketName=sockName, Movie=self.Mov_Points, Filter=filterund)
            with tc.addRepeatTask() as (tc_do, tc_until):
                tc_do.addTask("TaskFunction", Fn=und)
                tc_do.addTask("TaskMoviePlay", Movie=MouseEnter, Wait=True)

                tc_until.addTask("TaskMovieSocketLeave", SocketName=sockName, Movie=self.Mov_Points)
                pass
            tc.addTask("TaskFunction", Fn=undLeav)
            pass
        ######################################################
        def click():
            Opening.setEnable(True)
            self.Active[i] = True
            dat = self.Data[i]
            if (dat == 0):
                self.Block = i
                pass
            else:
                self.Find = self.Find + 1
                if (self.Find == self.NeedFind):
                    self.Win = i
                    pass
                pass
            pass

        def End(vvv):
            if (self.Block != -1):
                if (self.Block == i):
                    self.__Finita()
                    self._DoPlay()
                    pass
                return
                pass

            if (self.Win != -1):
                if (self.Win == i):
                    self.__Finita()
                    self.enigmaComplete()
                    pass
                pass
            pass

        def AfterOpen():
            IdleOpen.setEnable(True)
            Mov[0] = [[IdleOpen, True]]
            pass

        def filter():
            if (self.Active[i] is False and self.Win == -1 and self.Block == -1):
                return True
            return False
            pass

        with TaskManager.createTaskChain(Name="PatchesGameClick_%d" % (i), Cb=End) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=self.Mov_Points, isDown=True, Filter=filter)
            tc.addTask("TaskFunction", Fn=click)
            tc.addTask("TaskMoviePlay", Movie=Opening, Wait=True)
            tc.addTask("TaskFunction", Fn=AfterOpen)
            pass

        ######################################################

        with TaskManager.createTaskChain(Name="PatchesGameIdle_%d" % (i), Repeat=True) as tc:
            tc.addTask("AliasMultyplMovePlay", Movies=Mov)
            pass
        pass

    def __Finita(self):
        for i in range(17):
            n1 = "PatchesGameClick_%d" % (i)
            if TaskManager.existTaskChain(n1) is True:
                TaskManager.cancelTaskChain(n1)
                pass

            n2 = "PatchesGame_%d" % (i)
            if TaskManager.existTaskChain(n2) is True:
                TaskManager.cancelTaskChain(n2)
                pass

            n3 = "PatchesGameIdle_%d" % (i)
            if TaskManager.existTaskChain(n3) is True:
                TaskManager.cancelTaskChain(n3)
                pass
            pass

        for i in range(len(self.Mov_Idle)):
            self.Mov_Idle[i].setEnable(False)
            self.Mov_IdleOpen[i].setEnable(False)
            self.Mov_MouseEnter[i].setEnable(False)
            self.Mov_Opening[i].setEnable(False)
            pass
        self.ReInitParamentrs()
        pass

    pass