from Foundation.TaskManager import TaskManager

from PuzzleManager import PuzzleManager


Enigma = Mengine.importEntity("Enigma")


class Puzzle(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "PlacedItems")
        pass

    def __init__(self):
        super(Puzzle, self).__init__()
        self.data = []
        pass

    def _stopEnigma(self):
        super(Puzzle, self)._stopEnigma()

        pass

    def _skipEnigma(self):
        self.autowin()
        pass

    def _restoreEnigma(self):
        self._playEnigma()
        pass

    def _resetEnigma(self):
        for itemName in self.PlacedItems:
            item = self.object.getObject(itemName)
            item.setEnable(True)
            pass
        self.object.setParam("PlacedItems", [])
        self.disableAll()
        self.playTasks()
        pass

    def disableAll(self):
        self.data = PuzzleManager.getPuzzle(self.EnigmaName)
        for element in self.data:
            itemName = element.getItemName()
            if itemName in self.PlacedItems:
                continue
                pass
            spriteName = element.getSprite()
            spriteObject = self.object.getObject(spriteName)
            spriteObject.setEnable(False)
        pass

    def _onPreparation(self):
        super(Puzzle, self)._onPreparation()
        self.disableAll()
        pass

    def _onActivate(self):
        super(Puzzle, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(Puzzle, self)._onDeactivate()
        if TaskManager.existTaskChain("PuzzleGame"):
            TaskManager.cancelTaskChain("PuzzleGame")
            pass
        pass

    def _playEnigma(self):
        self.playTasks()
        pass

    def playTasks(self):
        if TaskManager.existTaskChain("PuzzleGame"):
            TaskManager.cancelTaskChain("PuzzleGame")
            pass

        with TaskManager.createTaskChain(Name="PuzzleGame") as tc_game:
            with tc_game.addParallelTask(len(self.data)) as tci:
                for tcs, element in zip(tci, self.data):
                    placeName = element.getPlaceName()
                    itemName = element.getItemName()
                    if itemName in self.PlacedItems:
                        tcs.addDummy()
                        continue
                        pass

                    sprite = element.getSprite()
                    spriteObject = self.object.getObject(sprite)
                    placeObject = self.object.getObject(placeName)

                    tcs.addTask("AliasDragDropItem", ItemName=itemName, SocketObject=placeObject, Group=self.object)
                    tcs.addTask("TaskAppendParam", Object=self.object, Param="PlacedItems", Value=itemName)
                    tcs.addEnable(spriteObject)
                    pass
                pass
            tc_game.addFunction(self.autowin)
            pass
        pass

    def autowin(self):
        self.enigmaComplete()
        pass

    pass
