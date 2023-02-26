from Foundation.TaskManager import TaskManager
from HOPA.RollingBallsManager import RollingBallsManager

from RollManager import RollManager
from Segment import SegmentSlot

Enigma = Mengine.importEntity("Enigma")

class RollingBalls(Enigma):
    def __init__(self):
        super(RollingBalls, self).__init__()
        self.checkSegments = {}

        self.movieSlots = []
        self.balls = {}
        self.generatedObjects = []
        self.currentMovie = None
        pass

    def _stopEnigma(self):
        self.finalize()
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def _autoWin(self):
        self.enigmaComplete()
        pass

    def generateBallView(self, generatorName):
        ID = len(self.generatedObjects)
        name = "%s_%i" % (generatorName, ID)
        obj = self.object.generateObject(name, generatorName)

        obj.setPosition((0, 0, 0))

        self.generatedObjects.append(obj)

        entity = obj.getEntity()

        return entity
        pass

    def finalize(self):
        if TaskManager.existTaskChain("RollingBalls") is True:
            TaskManager.cancelTaskChain("RollingBalls")
            pass

        for type, balls in self.balls.items():
            for ball in balls:
                ball.removeFromParent()
                pass
            pass

        self.balls = {}

        for obj in self.generatedObjects:
            obj.removeFromParent()
            obj.onDestroy()
            pass

        self.generatedObjects = []

        self.currentMovie = None
        pass

    def __checkComplete(self):
        if self.isComplete() is False:
            return
            pass

        self.enigmaComplete()
        pass

    def isComplete(self):
        for checkType in self.checkSegments:
            segmentList = self.checkSegments[checkType]
            if RollManager.isUniqueValueOnSegments(segmentList, checkType) is False:
                return False
                pass
            pass
        return True
        pass

    def clearMovie(self, movie):
        if movie.getEnable() is False:
            return
            pass

        movieEntity = movie.getEntity()
        for slot in self.movieSlots:
            node = movieEntity.getMovieSlot(slot.id)
            if node is None:
                continue
                pass
            node.removeChildren()
            pass
        pass

    def fillMovie(self, movie):
        if movie.getEnable() is False:
            return
            pass

        currentBalls = {}
        for ballType, nodeList in self.balls.items():
            currentBalls[ballType] = [node for node in nodeList]
            pass

        movieEntity = movie.getEntity()
        for slot in self.movieSlots:
            sprite = currentBalls[slot.value].pop()
            node = movieEntity.getMovieSlot(slot.id)
            node.removeChildren()
            node.addChild(sprite)
            pass
        pass

    def loadBalls(self, GameData):
        for ballType, ballData in GameData.balls.items():
            self.balls[ballType] = []
            pass

        for slot in self.movieSlots:
            ballData = GameData.balls[slot.value]
            generatorName = ballData["GeneratorName"]
            entityBall = self.generateBallView(generatorName)
            self.balls[slot.value].append(entityBall)
            pass
        pass

    def loadSegments(self, GameData):
        for segmentId in GameData.segments:
            segment = GameData.segments[segmentId]
            values = [SegmentSlot(slot.slotId, slot.ballType) for slot in segment.slots]
            self.movieSlots.extend(values)
            segmentId = RollManager.createSegment(values)
            segment.idInRoll = segmentId
            pass
        pass

    def loadRolls(self, GameData):
        for rollId in GameData.rolls:
            roll = GameData.rolls[rollId]
            segments = []
            for segment in roll.segments:
                segments.append(segment.idInRoll)
                pass
            roll.id = RollManager.createRoll(segments)
            pass
        pass

    def loadRules(self, GameData):
        for ballType in GameData.rules:
            segments = GameData.rules[ballType]
            self.checkSegments[ballType] = [segment.idInRoll for segment in segments]
            pass
        pass

    def setActiveMovie(self, newMovie):
        if self.currentMovie == newMovie:
            return
            pass

        if self.currentMovie is not None:
            self.clearMovie(self.currentMovie)
            self.currentMovie.setEnable(False)
            pass

        newMovie.setEnable(True)
        self.currentMovie = newMovie
        self.fillMovie(newMovie)
        pass

    def _playEnigma(self):
        GameData = RollingBallsManager.getGame(self.EnigmaName)

        self.loadSegments(GameData)
        self.loadBalls(GameData)
        self.loadRolls(GameData)
        self.loadRules(GameData)

        movieFirstCW = self.object.getObject("Movie_FirstMoveCW")
        movieFirstCCW = self.object.getObject("Movie_FirstMoveCCW")
        movieSecondCW = self.object.getObject("Movie_SecondMoveCW")
        movieSecondCCW = self.object.getObject("Movie_SecondMoveCCW")

        movieFirstCCW.setEnable(False)
        movieSecondCW.setEnable(False)
        movieSecondCCW.setEnable(False)

        RollIdFirst = GameData.rolls[0].id
        RollIdSecond = GameData.rolls[1].id
        self.setActiveMovie(movieFirstCW)

        def __enableButtons(value):
            button1 = self.object.getObject("Button_FirstCW")
            button2 = self.object.getObject("Button_FirstCCW")
            button3 = self.object.getObject("Button_SecondCW")
            button4 = self.object.getObject("Button_SecondCCW")
            button1.setInteractive(value)
            button2.setInteractive(value)
            button3.setInteractive(value)
            button4.setInteractive(value)
            pass

        with TaskManager.createTaskChain(Name="RollingBalls", Group=self.object, Repeat=True) as tc:
            with tc.addRaceTask(4) as (tc_button_first_cw, tc_button_first_ccw, tc_button_second_cw, tc_button_second_ccw):
                # ----------------------------
                tc_button_first_cw.addTask("TaskButtonClick", ButtonName="Button_FirstCW")
                tc_button_first_cw.addTask("TaskFunction", Fn=__enableButtons, Args=(False,))
                tc_button_first_cw.addTask("TaskFunction", Fn=self.setActiveMovie, Args=(movieFirstCW,))
                tc_button_first_cw.addTask("TaskMovieReverse", Movie=movieFirstCW, Reverse=False)
                tc_button_first_cw.addTask("TaskMoviePlay", Movie=movieFirstCW, Loop=False)
                tc_button_first_cw.addTask("TaskFunction", Fn=RollManager.moveRollCW, Args=(RollIdFirst,))
                tc_button_first_cw.addTask("TaskMovieLastFrame", Movie=movieFirstCW, Value=False)
                tc_button_first_cw.addTask("TaskFunction", Fn=self.fillMovie, Args=(movieFirstCW,))
                tc_button_first_cw.addTask("TaskFunction", Fn=__enableButtons, Args=(True,))

                # ----------------------------
                tc_button_first_ccw.addTask("TaskButtonClick", ButtonName="Button_FirstCCW")
                tc_button_first_ccw.addTask("TaskFunction", Fn=__enableButtons, Args=(False,))
                tc_button_first_ccw.addTask("TaskFunction", Fn=self.setActiveMovie, Args=(movieFirstCCW,))
                tc_button_first_ccw.addTask("TaskMovieReverse", Movie=movieFirstCCW, Reverse=False)
                tc_button_first_ccw.addTask("TaskMoviePlay", Movie=movieFirstCCW, Loop=False)
                tc_button_first_ccw.addTask("TaskFunction", Fn=RollManager.moveRollCCW, Args=(RollIdFirst,))
                tc_button_first_ccw.addTask("TaskMovieLastFrame", Movie=movieFirstCCW, Value=False)
                tc_button_first_ccw.addTask("TaskFunction", Fn=self.fillMovie, Args=(movieFirstCCW,))
                tc_button_first_ccw.addTask("TaskFunction", Fn=__enableButtons, Args=(True,))

                # ---------------------------------
                tc_button_second_cw.addTask("TaskButtonClick", ButtonName="Button_SecondCW")
                tc_button_second_cw.addTask("TaskFunction", Fn=__enableButtons, Args=(False,))
                tc_button_second_cw.addTask("TaskFunction", Fn=self.setActiveMovie, Args=(movieSecondCW,))
                tc_button_second_cw.addTask("TaskMovieReverse", Movie=movieSecondCW, Reverse=False)
                tc_button_second_cw.addTask("TaskMoviePlay", Movie=movieSecondCW, Loop=False)
                tc_button_second_cw.addTask("TaskFunction", Fn=RollManager.moveRollCW, Args=(RollIdSecond,))
                tc_button_second_cw.addTask("TaskMovieLastFrame", Movie=movieSecondCW, Value=False)
                tc_button_second_cw.addTask("TaskFunction", Fn=self.fillMovie, Args=(movieSecondCW,))
                tc_button_second_cw.addTask("TaskFunction", Fn=__enableButtons, Args=(True,))

                # ---------------------------------
                tc_button_second_ccw.addTask("TaskButtonClick", ButtonName="Button_SecondCCW")
                tc_button_second_ccw.addTask("TaskFunction", Fn=__enableButtons, Args=(False,))
                tc_button_second_ccw.addTask("TaskFunction", Fn=self.setActiveMovie, Args=(movieSecondCCW,))
                tc_button_second_ccw.addTask("TaskMovieReverse", Movie=movieSecondCCW, Reverse=False)
                tc_button_second_ccw.addTask("TaskMoviePlay", Movie=movieSecondCCW, Loop=False)
                tc_button_second_ccw.addTask("TaskFunction", Fn=RollManager.moveRollCCW, Args=(RollIdSecond,))
                tc_button_second_ccw.addTask("TaskMovieLastFrame", Movie=movieSecondCCW, Value=False)
                tc_button_second_ccw.addTask("TaskFunction", Fn=self.fillMovie, Args=(movieSecondCCW,))
                tc_button_second_ccw.addTask("TaskFunction", Fn=__enableButtons, Args=(True,))
                pass

            tc.addTask("TaskFunction", Fn=self.__checkComplete)
            pass
        pass
    pass