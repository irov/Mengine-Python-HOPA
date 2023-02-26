from Foundation.TaskManager import TaskManager

from HOPA.ClickSequenceManager import ClickSequenceManager

Enigma = Mengine.importEntity("Enigma")

class ClickSequence(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(ClickSequence, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.Game = None
        self.Click_Seq_Now = 0
        self.Click_Seq_Len = 0

        self.Al_Names = []
        self.Movies = []
        self.Clicked = []
        pass

    def _skipEnigma(self):
        self.__Finita()
        self.enigmaComplete()
        pass

    def _playEnigma(self):
        self._Pre_Init()
        self._Init()
        pass

    def _restoreEnigma(self):
        pass

    def _stopEnigma(self):
        self.__Finita()
        pass

    def _Pre_Init(self):
        self.Game = ClickSequenceManager.getGame(self.EnigmaName)
        self.Click_Seq_Len = len(self.Game.Sequences)
        pass

    def _Init(self):
        for id, cli in enumerate(self.Game.Clikers):
            self.Clicked.append(False)
            self._Do_Alias(cli, id)
            pass
        pass

    def _Do_Alias(self, click, id):
        sockName = click.Socket
        Movie_Socket = self.object.getObject(click.Socket_Movie)
        Movie_Play = self.object.getObject(click.Movie_Play)
        Movie_Play.getEntity().setTiming(0)
        self.Movies.append(Movie_Play)
        # Movie_Play.setEnable(False)

        Al_Name = "ClickSequence_%s" % (sockName)
        self.Al_Names.append(Al_Name)

        def Filter():
            if (self.Clicked[id] is False):
                seqN = self.Game.Sequences[self.Click_Seq_Now]
                if (seqN.Socket is click.Socket and seqN.Socket_Movie is click.Socket_Movie):
                    self.Click_Seq_Now = self.Click_Seq_Now + 1
                    self.Clicked[id] = True
                    # print Movie_Play, "Play"
                    return True
                    pass

                self.Click_Seq_Now = 0
                for en, mov in enumerate(self.Movies):
                    self.Clicked[en] = False
                    mov.setPlay(False)
                    mov.setLastFrame(False)
                    pass
                pass
            return False
            pass

        def click_Bef():
            pass

        def click_Aft():
            if (self.Click_Seq_Now == self.Click_Seq_Len):
                self.enigmaComplete()
                return
                pass
            pass

        with TaskManager.createTaskChain(Name=Al_Name, Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=Movie_Socket, isDown=True, Filter=Filter)
            tc.addTask("TaskFunction", Fn=click_Bef)
            tc.addTask("TaskMoviePlay", Movie=Movie_Play, Wait=True)
            tc.addTask("TaskFunction", Fn=click_Aft)
            pass

        pass

    def __Finita(self):
        newNames = self.Al_Names[:]
        for name in newNames:
            self.__canTT(name)
            pass
        self.ReInitParamentrs()
        pass

    def __canTT(self, Name):
        if TaskManager.existTaskChain(Name) is True:
            TaskManager.cancelTaskChain(Name)
            pass
        pass

    pass