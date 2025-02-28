from Foundation.TaskManager import TaskManager
from Functor import Functor


class Executable(object):
    TaskName = "Programmattor_execution"

    def __init__(self, handInstance):
        self.instructionList = []
        self.hand = handInstance
        self.translateMap = {}
        self.escape = self.hand.moveBack
        pass

    def setDepends(self, objButtonRight, objButtonLeft, objButtonUp, objButtonDown):
        self.translateMap = {
            objButtonUp: self.hand.moveUp,
            objButtonDown: self.hand.moveDown,
            objButtonLeft: self.hand.moveLeft,
            objButtonRight: self.hand.moveRight,
        }
        pass

    def translateInstruction(self):
        translation = [self.translateMap[it] for it in self.instructionList]
        self.instructionList = []
        translation.append(self.escape)
        return translation
        pass

    def loadInstruction(self, inList):
        self.instructionList = inList
        pass

    def onStop(self):
        if TaskManager.existTaskChain(Executable.TaskName):
            TaskManager.cancelTaskChain(Executable.TaskName)
            pass
        pass

    def execute(self, taskCb):
        if TaskManager.existTaskChain(Executable.TaskName):
            return
            pass

        needToDo = self.translateInstruction()
        with TaskManager.createTaskChain(Name=Executable.TaskName, Cb=Functor(self.executionCb, taskCb)) as tc:
            for instruction in needToDo:
                tc.addScope(instruction)
                pass
            tc.addFunction(taskCb)
            pass
        pass

    def executionCb(self, isSkip, cb):
        self.hand.flushTerm()  # move out from termination state
        pass

    pass
