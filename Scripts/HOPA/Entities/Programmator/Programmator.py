from Executable import Executable
from Hand import Hand
from Partition import Partition, FinalPartition
from ProgrammatorManager import ProgrammatorManager
from Tap import Tap
from Wheel import Wheel

Enigma = Mengine.importEntity("Enigma")

class Programmator(Enigma):
    # static fields
    TapMovie = "Movie_Tap"
    ContainerMovie = "Movie_Container"
    FinalContainerMovie = "Movie_FinalContainer"
    CarrierForwardMovie = "Movie_Forward"
    TerminationMovie = "Movie_Terminate"

    def __init__(self):
        super(Programmator, self).__init__()
        self.ButtonHandler = None
        self.TapInstance = None
        self.names = None
        self.HandInstance = None
        self.ExecutableInstance = None
        self.WheelInstance = None
        self.partitions = []
        self.buttonToMovieGenerator = {}
        self.buttonQueue = []
        self.returns = []
        self.garbage = []
        pass

    def _stopEnigma(self):
        Notification.removeObserver(self.ButtonHandler)
        self.names = None
        for gb in self.garbage:
            #            print gb.getObject().getName()
            #            print gb.getParent()
            gb.removeFromParent()
        self.garbage = []

        self.TapInstance.onDeactivate()
        self.TapInstance = None
        for part in self.partitions:
            part.onDeactivate()
            pass
        self.partitions = []
        self.HandInstance.onDeactivate()
        self.HandInstance = None
        self.ExecutableInstance.onStop()
        self.ExecutableInstance = None
        self.WheelInstance.onDeactivate()
        self.WheelInstance = None
        self.FinalPartition.onDeactivate()
        self.FinalPartition = None
        self.returnToParent()
        pass

    def _playEnigma(self):
        self._preparation()
        self.ButtonHandler = Notification.addObserver(Notificator.onButtonClick, self.on_button_cb)
        pass

    def _skipEnigma(self):
        self.completeAll()
        pass

    def _preparation(self):
        demonObjects = self.object.getObjects()
        static_data = ProgrammatorManager.getGameData(self.EnigmaName)

        MovieContainer = self.object.getObject(Programmator.ContainerMovie)
        MovieContainerEn = MovieContainer.getEntity()
        container_slots = static_data.container_slots
        for top_slot, bot_slot in container_slots:
            topNode = MovieContainerEn.getMovieSlot(top_slot)
            botNode = MovieContainerEn.getMovieSlot(bot_slot)
            partition = Partition([botNode, topNode])
            self.partitions.append(partition)
            pass

        final_slots = static_data.final_container

        finalContainerMovie = self.object.getObject(Programmator.FinalContainerMovie)
        fcEntity = finalContainerMovie.getEntity()
        orderSlots = []
        for slotName in final_slots:
            slotNode = fcEntity.getMovieSlot(slotName)
            orderSlots.append(slotNode)
            pass
        partition = Partition(orderSlots)
        self.partitions.append(partition)

        win_order = static_data.win_order
        wheelsUp = static_data.wheel_up
        wheelsDown = static_data.wheel_down

        wheelsUp = [self.object.getObject(wheel) for wheel in wheelsUp]
        wheelsDown = [self.object.getObject(wheel) for wheel in wheelsDown]

        self.WheelInstance = Wheel(wheelsUp, wheelsDown, finalContainerMovie)

        self.FinalPartition = FinalPartition(partition, self.WheelInstance)
        self.FinalPartition.setWinOrder(win_order)
        finalContainerEn = finalContainerMovie.getEntity()
        self.returns.append(finalContainerEn)

        monkeys_movies = static_data.monkey_movies
        for n, mMovie in enumerate(monkeys_movies):
            movObject = self.object.getObject(mMovie)
            mEntity = movObject.getEntity()
            partition = self.partitions[n]
            partition.give(mEntity)
            self.returns.append(mEntity)
            pass

        buttons = static_data.buttons
        generators = static_data.task_movies
        orderedButtons = []
        for n, buttonName in enumerate(buttons):
            buttonObject = self.object.getObject(buttonName)
            orderedButtons.append(buttonObject)
            buttonObject.setEnable(True)
            buttonObject.setInteractive(True)
            buttonObject.setPosition((0, 0))
            generatorName = generators[n]
            self.buttonToMovieGenerator[buttonObject] = generatorName
            pass

        TapObject = self.object.getObject(Programmator.TapMovie)
        TapEntity = TapObject.getEntity()
        tap_slots = static_data.tap_slots
        tapNodes = []
        for tap_name in tap_slots:
            tapNode = TapEntity.getMovieSlot(tap_name)
            tapNodes.append(tapNode)
            pass

        self.TapInstance = Tap(tapNodes)
        self.names = self.name_generator()
        self.RunButton = self.object.getObject("Button_Hand")

        self.RunButton.setInteractive(True)

        hands = static_data.hands

        hand_order = []
        for handit in hands:
            handObj = self.object.getObject(handit)
            hand_order.append(handObj)
            handEn = handObj.getEntity()
            handEn.setFirstFrame()
            self.returns.append(handEn)
            pass

        movieTermination = self.object.getObject(Programmator.TerminationMovie)
        movieTermination.setEnable(False)
        moves_r = static_data.moves_r
        moves_l = static_data.moves_l
        moves_r = [self.object.getObject(moves) for moves in moves_r]
        moves_l = [self.object.getObject(moves) for moves in moves_l]
        movesRightEntity = [moves.getEntity() for moves in moves_r]
        movesLeftEntity = [moves.getEntity() for moves in moves_l]
        [movEntity.setFirstFrame() for movEntity in movesLeftEntity]
        [movEntity.setFirstFrame() for movEntity in movesRightEntity]

        self.returns.extend(movesLeftEntity)
        self.returns.extend(movesRightEntity)

        self.HandInstance = Hand((moves_r, moves_l), hand_order, self.partitions, movieTermination)
        self.ExecutableInstance = Executable(self.HandInstance)
        self.ExecutableInstance.setDepends(*orderedButtons)
        pass

    def name_generator(self):
        i = 0
        while True:
            yield "_%d" % i
            i += 1
            pass
        pass

    def on_button_cb(self, button):
        if button is self.RunButton:
            self.ExecutableInstance.loadInstruction(self.buttonQueue)
            self.buttonQueue = []
            cb = self._complete
            self.ExecutableInstance.execute(cb)
            self.TapInstance.flush()
            #            self.RunButton.setInteractive(False)
            return False
            pass

        if button not in self.buttonToMovieGenerator:
            return False
            pass
        generatorName = self.buttonToMovieGenerator[button]

        if self.TapInstance.isFull() is True:
            return False
            pass
        self.buttonQueue.append(button)
        task_movie = self.object.generateObject("%s%s" % (generatorName, self.names.next()), generatorName)
        self.TapInstance.push(task_movie)
        self.garbage.append(task_movie)
        if self.TapInstance.isFull() is True:
            self.RunButton.setInteractive(True)
            pass
        return False
        pass

    def _resetEnigma(self):
        self.HandInstance.onReset()
        pass

    def _complete(self, isSkip=None):
        embed_method = self.completeAll
        isWin = self.FinalPartition.checkWin(embed_method)
        pass

    def completeAll(self):
        self.object.setParam("Play", False)
        self.enigmaComplete()
        pass

    def returnToParent(self):
        for entity in self.returns:
            self.addChild(entity)
            pass
        self.returns = []
        pass
