from Foundation.TaskManager import TaskManager
from HOPA.FeedStatesManager import FeedStatesManager

from StatesControl import StatesControl


Enigma = Mengine.importEntity("Enigma")


class FeedStates(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "Saves")

    def __init__(self):
        super(FeedStates, self).__init__()
        self.sockets = []
        self.sprites_map = {}
        pass

    def _stopEnigma(self):
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass
        StatesControl.clear_it()
        pass

    def _onDeactivate(self):
        super(FeedStates, self)._onDeactivate()
        StatesControl.play_object = None
        pass

    def _playEnigma(self):
        gameObjects = self.object.getObjects()

        for object in gameObjects:
            if object.getType() == "ObjectMovie":
                object.setEnable(False)
                pass
            pass

        self._preparationEnigma()
        predators = StatesControl.getPredators()
        with TaskManager.createTaskChain(Name=self.EnigmaName, Group=self.object, Cb=self.__complete) as tc:
            with tc.addRepeatTask() as (tc_do, tc_until):
                with tc_do.addParallelTask(2) as (tc_click, tc_listen):
                    tc_click.addTask("AliasSpinCircles", ObjectName=self.sockets[0], Sockets=self.sockets)  # events on socket
                    tc_listen.addListener(Notificator.onSpin, Filter=self.__socketFilter)
                    pass
                tc_until.addListener(Notificator.onEnigmaComplete, Filter=self.isactive)
                tc_until.addDelay(2 * 1000)  # speed fix
                pass
            pass
        pass

    def __complete(self, isSkip):
        self.enigmaComplete()
        self.object.setParam("Play", False)
        pass

    def isactive(self, *params):
        if self.object.getPlay() is False:
            return False
            pass
        return True
        pass

    def _preparationEnigma(self):
        movie_states = FeedStatesManager.getMovieStates(self.EnigmaName)
        ref = FeedStatesManager.getRef(self.EnigmaName)
        self.sockets = FeedStatesManager.getSockets(self.EnigmaName)
        sprites = FeedStatesManager.getSprites(self.EnigmaName)
        self.sprites_map = dict(zip(self.sockets, sprites))
        limit = FeedStatesManager.getLimits(self.EnigmaName)
        StatesControl.loadControl(movie_states, ref, self.sockets, limit)
        StatesControl.play_object = self
        pass

    def _skipEnigma(self):
        if self.object.getPlay() is False:
            return False
            pass
        StatesControl.skipStates()
        return True
        pass

    def completion(self):
        self.__complete(True)
        pass

    def _resetEnigma(self):
        StatesControl.resetStates()
        for socket in self.sockets:
            socketObj = self.object.getObject(socket)
            socketObj.setEnable(True)
            sprite_obj = self.sprites_map[socket]
            sprite_obj.setEnable(True)
            pass
        pass

    def __socketFilter(self, socket):
        if socket not in self.sockets:
            return False
            pass

        self.states_action(socket)
        return True
        pass

    def states_action(self, socket):
        state = StatesControl.getState(socket)
        self.suppressInteractive(False)
        cb = self.suppressInteractive
        socket = state.iterateInternalState(cb)
        if socket is not None:
            socket_obj = self.object.getObject(socket)
            socket_obj.setEnable(False)
            sprite_obj = self.sprites_map[socket]
            sprite_obj.setEnable(False)
            pass
        pass

    pass

    def suppressInteractive(self, flag=True):
        sockets = [self.object.getObject(socketName) for socketName in self.sockets]
        [socket.setInteractive(flag) for socket in sockets]
        pass

    def clearance(self):
        self.sprites_map = {}
