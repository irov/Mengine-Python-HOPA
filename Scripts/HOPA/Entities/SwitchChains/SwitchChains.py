from Foundation.TaskManager import TaskManager
from Functor import Functor
from HOPA.SwitchChainsManager import SwitchChainsManager

class SwitchChainElement(object):
    def __init__(self, group, switchName, chainsList):
        self.group = group

        self.switchName = switchName
        self.num = switchName[13:]

        self.chainList = chainsList

        self.socket = self._generateSocket("Socket_Switch")

        self.switch = self.group.getObject(switchName)

        movieOnName = "Movie_%sOn" % (self.num)
        self.movieOn = self.switch.getObject(movieOnName)

        movieOffName = "Movie_%sOff" % (self.num)
        self.movieOff = self.switch.getObject(movieOffName)

        self.state = None
        self._setState(movieOnName)
        self.movieOnAttachSocket()
        pass

    def _generateSocket(self, name):
        obj = self.group.generateObject(name + self.num, name)

        obj.setPosition((0, 0))

        return obj
        pass

    def setStateOn(self):
        socketEntity = self.socket.getEntity()
        socketEntity.removeFromParent()
        self._setState(self.movieOn.name)
        pass

    def setStateOff(self):
        socketEntity = self.socket.getEntity()
        socketEntity.removeFromParent()
        self._setState(self.movieOff.name)
        pass

    def _setState(self, state):
        self.switch.setSwitch(state)
        self.state = state
        pass

    def getState(self):
        return self.state
        pass

    def movieOnAttachSocket(self):
        self._movieAttachSocket(self.movieOn)
        pass

    def movieOffAttachSocket(self):
        self._movieAttachSocket(self.movieOff)
        pass

    def _movieAttachSocket(self, movie):
        movieEntity = movie.getEntity()

        slotSocket = movieEntity.getMovieSlot("socket")

        socketEntity = self.socket.getEntity()
        slotSocket.addChild(socketEntity)
        pass

    def _movieAttachSocket(self, movie):
        movieEntity = movie.getEntity()

        slotSocket = movieEntity.getMovieSlot("socket")

        socketEntity = self.socket.getEntity()
        slotSocket.addChild(socketEntity)
        pass

    def release(self):
        self.socket.removeFromParent()
        # socketEntity = self.socket.getEntity()
        # socketEntity.removeFromParent()
        self.socket = None
        pass

Enigma = Mengine.importEntity("Enigma")

class SwitchChains(Enigma):
    def __init__(self):
        super(SwitchChains, self).__init__()
        self.elements = {}
        pass

    def _stopEnigma(self):
        self.__detachSockets()

        pass

    def __detachSockets(self):
        for element in self.elements.values():
            element.release()
            if TaskManager.existTaskChain(element.switchName):
                TaskManager.cancelTaskChain(element.switchName)
                pass
            pass

        self.elements = {}
        pass

    def _resetEnigma(self):
        startOn = SwitchChainsManager.getStartOn(self.EnigmaName)
        for element in self.elements.values():
            if element.switchName in startOn:
                element.setStateOff()
                element.movieOffAttachSocket()
                continue

            element.setStateOn()
            element.movieOnAttachSocket()
            pass
        pass

    def _blockSockets(self):
        for element in self.elements.values():
            element.socket.setEnable(False)
            pass
        pass

    def _unBlockSockets(self):
        for element in self.elements.values():
            element.socket.setEnable(True)
            pass
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def _playEnigma(self):
        self.objects = SwitchChainsManager.getSwitchChainObjects(self.EnigmaName)
        objectsGroup = SwitchChainsManager.getSwitchChainGroup(self.EnigmaName)
        sceneName = SwitchChainsManager.getSceneName(self.EnigmaName)

        for switchName, chainsList in self.objects.iteritems():
            element = SwitchChainElement(objectsGroup, switchName, chainsList)
            self.elements[switchName] = element
            pass

        self._resetEnigma()

        def _checkReverse(isSkip, cb, chainElement):
            state = chainElement.getState()
            if state == chainElement.movieOff.name:
                cb(isSkip, 0)
                return
            cb(isSkip, 1)
            return

        for element in self.elements.values():
            with TaskManager.createTaskChain(Name=element.switchName, Group=objectsGroup, Repeat=True) as tc:
                tc.addTask("TaskFunction", Fn=self._unBlockSockets)
                tc.addTask("AliasObjectClick", SceneName=sceneName, Object=element.socket)
                tc.addTask("TaskNotify", ID=Notificator.onSwitchChainsClick, Args=(element,))
                tc.addTask("TaskFunction", Fn=self._blockSockets)

                with tc.addParallelTask(2) as (tc_1, tc_2):
                    with tc_1.addSwitchTask(2, Functor(_checkReverse, element)) as (tc_norm1, tc_rev1):
                        tc_norm1.addTask("TaskMoviePlay", Movie=element.movieOff, Wait=False)
                        tc_norm1.addTask("TaskFunction", Fn=element.setStateOn)
                        tc_norm1.addTask("TaskFunction", Fn=element.movieOnAttachSocket)

                        tc_rev1.addTask("TaskMoviePlay", Movie=element.movieOn, Wait=False)
                        tc_rev1.addTask("TaskFunction", Fn=element.setStateOff)
                        tc_rev1.addTask("TaskFunction", Fn=element.movieOffAttachSocket)
                        pass

                    with tc_2.addParallelTask(len(element.chainList)) as tc_chains:
                        for tc_chain, chainName in zip(tc_chains, element.chainList):
                            chainElement = self.elements[chainName]

                            with tc_chain.addSwitchTask(2, Functor(_checkReverse, chainElement)) as (tc_norm, tc_rev):
                                tc_norm.addTask("TaskMoviePlay", Movie=chainElement.movieOff, Wait=False)
                                tc_norm.addTask("TaskFunction", Fn=chainElement.setStateOn)
                                tc_norm.addTask("TaskFunction", Fn=chainElement.movieOnAttachSocket)

                                tc_rev.addTask("TaskMoviePlay", Movie=chainElement.movieOn, Wait=False)
                                tc_rev.addTask("TaskFunction", Fn=chainElement.setStateOff)
                                tc_rev.addTask("TaskFunction", Fn=chainElement.movieOffAttachSocket)
                                pass

                            pass
                        pass
                    pass
                tc.addTask("TaskFunction", Fn=self._checkWin)
                pass
            pass
        pass

    def _checkWin(self):
        for element in self.elements.values():
            if element.state != element.movieOff.name:
                return
                pass
            pass

        self._complete()
        pass

    def _autoWin(self):
        for element in self.elements.values():
            element.setStateOff()
            element.socket.setEnable(False)
            pass

        self._complete()
        pass

    def _complete(self):
        self.__detachSockets()

        self.object.setParam("Play", False)
        self.enigmaComplete()
        pass

    pass