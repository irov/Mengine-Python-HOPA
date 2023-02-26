import Foundation.Utils as Utils
from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager
from HOPA.ThimbleGameManager import ThimbleGameManager

Enigma = Mengine.importEntity("Enigma")

class ThimbleGame(Enigma):

    def __init__(self):
        super(ThimbleGame, self).__init__()
        self.moves = {}
        self.socket = {}
        self.shows = {}
        self.check = None
        self.chipPosition = None
        self.Data = []
        self.chip = None
        self.MovieSound = None
        self.MovieSoundQuestion = None
        pass

    def _onActivate(self):
        super(ThimbleGame, self)._onActivate()
        if self.object.hasObject("Movie_Sound") is True:
            self.MovieSound = self.object.getObject("Movie_Sound")
            pass
        if self.object.hasObject("Movie_SoundQuestion") is True:
            self.MovieSoundQuestion = self.object.getObject("Movie_SoundQuestion")
            pass
        pass

    def _playEnigma(self):
        self.ThimbleGame = ThimbleGameManager.getGame(self.EnigmaName)

        for id, socketName in self.ThimbleGame.sockets.items():
            socketObject = self.object.getObject(socketName)
            socketObject.setInteractive(True)
            self.socket[socketObject] = id
            pass

        for thimble, value in self.ThimbleGame.thimbles.items():
            self.Data.append(value)
            pass

        for id, shows in self.ThimbleGame.shows.items():
            showObject = self.object.getObject(shows)
            self.shows[id] = showObject
            pass

        for key, value in self.ThimbleGame.moves.items():
            movie = self.object.getObject(value)
            movie.setEnable(False)
            self.moves[key] = movie
            pass

        self.chipPosition = self.Data.index(1)

        self.MovieQuestion = self.object.getObject("Movie_Question")
        self.MovieQuestion.setEnable(False)
        self.chip = self.object.getObject("Sprite_Chip")
        self.chip.setEnable(False)
        self.chip.setPosition((0, 0))
        self.__playTasks()
        pass

    def __playTasks(self):
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass

        Movie = self.shows[self.chipPosition]
        with TaskManager.createTaskChain(Name=self.EnigmaName, Group=self.object) as tc_game:
            tc_game.addTask("TaskFunction", Fn=self.attachChip, Args=(Movie,))
            tc_game.addTask("TaskEnable", Object=self.MovieQuestion, Value=False)
            tc_game.addTask("TaskEnable", Object=Movie, Value=True)
            tc_game.addTask("TaskMoviePlay", Movie=Movie)
            tc_game.addTask("TaskMovieReverse", Movie=Movie, Reverse=True)
            tc_game.addTask("TaskMoviePlay", Movie=Movie)
            tc_game.addTask("TaskMovieReverse", Movie=Movie, Reverse=False)
            tc_game.addTask("TaskMovieLastFrame", MovieName=Movie.getName(), Value=False)
            tc_game.addTask("TaskFunction", Fn=self.deattachChip)
            tc_game.addTask("TaskFunction", Fn=self.enableShow, Args=(False,))
            tc_game.addTask("TaskScope", Scope=self.shakeThimbles)
            tc_game.addTask("TaskFunction", Fn=self.enableShow, Args=(True,))
            if self.MovieSoundQuestion is not None:
                tc_game.addTask("TaskMoviePlay", Movie=self.MovieSoundQuestion, Wait=False, Loop=False)
                pass
            tc_game.addTask("TaskEnable", Object=self.MovieQuestion, Value=True)
            tc_game.addTask("TaskListener", ID=Notificator.onSocketClick, Filter=self.clickOnThimble)
            tc_game.addTask("TaskEnable", Object=self.MovieQuestion, Value=False)
            pass
        pass

    def showChip(self, thimbleId):
        Movie = self.shows[thimbleId]
        with TaskManager.createTaskChain() as tc_chip:
            if thimbleId == self.chipPosition:
                tc_chip.addTask("TaskFunction", Fn=self.attachChip, Args=(Movie,))
            tc_chip.addTask("TaskEnable", Object=Movie, Value=True)
            tc_chip.addTask("TaskMoviePlay", Movie=Movie)
            tc_chip.addTask("TaskMovieReverse", Movie=Movie, Reverse=True)
            tc_chip.addTask("TaskMoviePlay", Movie=Movie)
            tc_chip.addTask("TaskMovieReverse", Movie=Movie, Reverse=False)
            tc_chip.addTask("TaskMovieLastFrame", Movie=Movie, Value=False)
            if thimbleId != self.chipPosition:
                tc_chip.addTask("TaskFunction", Fn=self.__playTasks)
            if thimbleId == self.chipPosition:
                tc_chip.addTask("TaskFunction", Fn=self.deattachChip)
                tc_chip.addTask("TaskFunction", Fn=self._complete)
            pass

        pass

    def attachChip(self, Movie):
        MovieEntity = Movie.getEntity()
        MovieSlot = MovieEntity.getMovieSlot("chip")
        sprite = self.chip.getEntity()
        self.chip.setEnable(True)
        MovieSlot.addChild(sprite)
        pass

    def deattachChip(self):
        sprite = self.chip.getEntity()
        sprite.removeFromParent()
        pass

    def shakeThimbles(self, scope):
        shakePull = []
        moviePull = []
        iterations = DefaultManager.getDefault("ThimbleGameShakePull", 8)

        for i in range(iterations):
            rand = [x for x in range(len(self.Data))]
            fr = Utils.rand_sample_list(rand, min(1, len(rand)))
            rand.remove(fr[0])
            to = Utils.rand_sample_list(rand, min(1, len(rand)))
            shakePull.extend([fr[0], to[0]])
            pass

        for i in range(iterations):
            tmpCheck = shakePull[i * 2:i * 2 + 2]
            if self.chipPosition in tmpCheck:
                if self.chipPosition == tmpCheck[0]:
                    self.chipPosition = tmpCheck[1]
                else:
                    self.chipPosition = tmpCheck[0]
                pass
            pass

        for i in range(iterations):
            tmpId = shakePull[i * 2:i * 2 + 2]
            check = [x for x in range(len(self.Data))]
            check.remove(tmpId[0])
            check.remove(tmpId[1])
            moviePull.append((self.moves[(tmpId[0], tmpId[1])], self.moves[(tmpId[1], tmpId[0])], self.shows[check[0]]))
            pass

        for movie1, movie2, movie3 in moviePull:
            with scope.addParallelTask(3) as (mv1, mv2, mvSound):
                mv1.addTask("TaskEnable", Object=movie1, Value=True)
                mv1.addTask("TaskEnable", Object=movie3, Value=True)
                mv1.addTask("TaskMoviePlay", Movie=movie1)
                mv1.addTask("TaskEnable", Object=movie1, Value=False)

                mv2.addTask("TaskEnable", Object=movie2, Value=True)
                mv2.addTask("TaskMoviePlay", Movie=movie2)
                mv2.addTask("TaskEnable", Object=movie2, Value=False)
                mv2.addTask("TaskEnable", Object=movie3, Value=False)

                if self.MovieSound is not None:
                    mvSound.addTask("TaskMoviePlay", Movie=self.MovieSound, Loop=False, Wait=False)
                    pass
                else:
                    mvSound.addTask("TaskDummy")
                    pass
                pass
            pass
        pass

    def enableShow(self, value):
        for show in self.shows.values():
            show.setEnable(value)
            pass
        pass

    def clickOnThimble(self, curSocket):
        if curSocket not in self.socket.keys():
            return False
            pass
        check = self.socket[curSocket]
        if check == self.chipPosition:
            self.showChip(check)
            return True
            pass
        self.showChip(check)
        return True
        pass

    def _complete(self):
        self.setComplete()
        pass