from Foundation.TaskManager import TaskManager
from HOPA.ColorCollectManager import ColorCollectManager

from Bulb import Bulb

Enigma = Mengine.importEntity("Enigma")

class ColorCollect(Enigma):

    @staticmethod
    def declareORM(Type):
        Type.addActionActivate(Type, "BulbAction", Update=ColorCollect._onBulbPlaced)
        pass

    def __init__(self):
        super(ColorCollect, self).__init__()
        self.bulbs = {}
        self.beginBySocket = {}
        self.endBySocket = {}
        self.arrowAttachItem = None
        self.bulbToAttach = None
        self.rules = {}
        self.socket = None
        pass

    def resetInitValues(self):
        self.bulbs = {}
        self.beginBySocket = {}
        self.endBySocket = {}
        self.arrowAttachItem = None
        self.bulbToAttach = None
        self.rules = {}
        self.socket = None
        pass

    def finalise(self):
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass

        for bulb in self.beginBySocket.values():
            bulb.finalise()
            pass
        self.resetInitValues()
        pass

    def _stopEnigma(self):
        super(ColorCollect, self)._stopEnigma()
        self.finalise()
        pass

    def _resetEnigma(self):
        self.resetInitValues()
        self._playEnigma()
        pass

    def _restoreEnigma(self):
        self._playEnigma()
        pass

    def _playEnigma(self):
        GameInitData = ColorCollectManager.getColorCollect(self.EnigmaName)
        self.rules = GameInitData.getRules()
        bulbs = GameInitData.getBulbs()
        itemsData = GameInitData.getItems()
        size = GameInitData.getSize()
        for key, value in bulbs.iteritems():
            beginSocketObj = self.object.getObject(value.getSocketBeginName())
            beginSocketObj.setInteractive(True)
            endSocketObj = self.object.getObject(value.getSocketEndName())
            endSocketObj.setInteractive(True)
            bulb = Bulb(self.object, key, value, itemsData, size)
            self.beginBySocket[beginSocketObj] = bulb
            self.endBySocket[endSocketObj] = bulb
            pass

        self.__playTasks()
        pass

    def checkComplete(self):
        for bulb in self.beginBySocket.values():
            bulbName = bulb.getName()
            items = bulb.getItems()
            for item in items:
                if item in self.rules.keys():
                    check = self.rules[item]
                    if check != bulbName:
                        return False
                        pass
                    pass
                pass
            pass
        return True
        pass

    def _onBulbPlaced(self, value):
        if self.checkComplete() is False:
            self.__playTasks()
            return False
            pass
        self.enigmaComplete()
        # self.setComplete()
        return False
        pass

    def __playTasks(self):
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass
        with TaskManager.createTaskChain(Name=self.EnigmaName) as tc:
            tc.addTask("TaskListener", ID=Notificator.onSocketClick, Filter=self.endSocketClick)
            tc.addTask("TaskScope", Scope=self.attachItemScope)
            pass
        pass

    def endSocketClick(self, curSocket):
        if curSocket not in self.endBySocket.keys():
            return False
            pass
        curBulb = self.endBySocket[curSocket]
        if curBulb.isItemToAttach() is False:
            return False
            pass
        self.arrowAttachItem = curBulb.removeAttachItem()
        self.socket = curSocket
        return True
        pass

    def attachItemScope(self, scope):
        def returnToBulb(socket):
            bulbToAttach = self.endBySocket[socket]
            bulbToAttach.attachItemToEnd(self.arrowAttachItem)
            self.__playTasks()
            pass

        def attachToBulb(socket):
            bulbToAttach = self.beginBySocket[socket]
            bulbToAttach.attachItemToBegin(self.arrowAttachItem)
            bulbToAttach.updateMovie()
            pass

        scope.addTask("TaskArrowAttach", Offset=False, Origin=True, Object=self.arrowAttachItem)

        with scope.addRaceTask(3) as (tc_end, tc_begin, tc_wrong):
            with tc_end.addRaceTask(len(self.endBySocket.keys())) as tcs:
                for tci, socket, bulb in zip(tcs, self.endBySocket.iterkeys(), self.endBySocket.itervalues()):
                    tci.addTask("TaskSocketUseItem", Socket=socket, AutoEnable=False, Item=self.arrowAttachItem)
                    tci.addTask("TaskRemoveArrowAttach")
                    tci.addTask("TaskFanItemInNone", FanItem=self.arrowAttachItem)
                    tci.addTask("TaskFunction", Fn=returnToBulb, Args=(socket,))
                    pass
                pass
            with tc_begin.addRaceTask(len(self.beginBySocket.keys())) as tcs:
                for tci, socket, bulb in zip(tcs, self.beginBySocket.iterkeys(), self.beginBySocket.itervalues()):
                    tci.addTask("TaskSocketUseItem", Socket=socket, AutoEnable=False, Item=self.arrowAttachItem)
                    tci.addTask("TaskRemoveArrowAttach")
                    tci.addTask("TaskFanItemInNone", FanItem=self.arrowAttachItem)
                    tci.addTask("TaskFunction", Fn=attachToBulb, Args=(socket,))
                    pass
                pass
            tc_wrong.addTask("TaskListener", ID=Notificator.onButtonClick)
            tc_wrong.addTask("TaskRemoveArrowAttach")
            tc_wrong.addTask("TaskFanItemInNone", FanItem=self.arrowAttachItem)
            tc_wrong.addTask("TaskFunction", Fn=returnToBulb, Args=(self.socket,))
            pass
        pass
    pass