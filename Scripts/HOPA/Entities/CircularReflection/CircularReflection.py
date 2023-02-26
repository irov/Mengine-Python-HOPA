from Notification import Notification

from CircularReflectionManager import CircularReflectionManager
from Connections import Connectable

Enigma = Mengine.importEntity("Enigma")

class CircularReflection(Enigma):
    Movies = ["Movie_Circle1", "Movie_Circle2", "Movie_Circle3", "Movie_Circle4", "Movie_Receiver"]
    Sockets = ["Socket_Circle1", "Socket_Circle2", "Socket_Circle3", "Socket_Circle4", "Socket_Circle4"]

    def __init__(self):
        super(CircularReflection, self).__init__()
        self.RotorHandler = None
        self.SocketEnter = None
        self.SocketLeave = None
        self.socketToCircle = {}
        self.current_rotatable = None
        self.current_socket = None
        self.allow_rotate = False
        self.AtomicConnectables = []
        self.slotToSubMovie = {}
        self.receivers = []
        self.rotatableAngle = {}
        self.mouseTouchVec = None
        pass

    def _stopEnigma(self):
        #         self.clearence()    #!!!!!!!!!!!!!!!!
        self.current_socket = None
        self.suppressInteraction(False)
        Mengine.removeMouseMoveHandler(self._onMouseMove)
        Notification.removeObserver(self.SocketEnter)
        Notification.removeObserver(self.SocketLeave)
        Notification.removeObserver(self.RotorHandler)
        self.RotorHandler = None
        self.SocketEnter = None
        self.SocketLeave = None
        self.socketToCircle = {}
        self.AtomicConnectables = []
        self.socketToCircle = {}
        self.slotToSubMovie = {}
        pass

    def _playEnigma(self):
        self.RotorHandler = Notification.addObserver(Notificator.onMouseButtonEvent, self.rotate)
        self.SocketEnter = Notification.addObserver(Notificator.onSocketMouseEnter, self.onSocketEntered)
        self.SocketLeave = Notification.addObserver(Notificator.onSocketMouseLeave, self.onSocketLeaved)
        Mengine.addMouseMoveHandler(self._onMouseMove)
        self.preparate()
        pass

    def preparate(self):
        """
        Preparing objects, auxiliary instances and maps
        """
        collections = CircularReflectionManager.collections
        self.validateManagement(collections)
        self.subMovieMapping()
        for movie_name, socket_name in map(None, CircularReflection.Movies, CircularReflection.Sockets):
            movie_object = self.object.getObject(movie_name)
            socket_object = self.object.getObject(socket_name)
            entityMovie = movie_object.getEntity()

            centerName = "Center"
            if entityMovie.hasMovieSlot(centerName):
                centreNode = entityMovie.getMovieSlot(centerName)
                centreOffset = centreNode.getWorldPosition()
                entityMovie.setOrigin(centreOffset)
                movie_object.setPosition(centreOffset)
                pass

            if socket_object not in self.socketToCircle:
                self.socketToCircle[socket_object] = movie_object
                socket_object.setInteractive(True)
                pass
            # -----> bounds
            nested_dict = collections[movie_name]
            for input_name in nested_dict:
                outputs_list = nested_dict[input_name]

                input_slot = entityMovie.getMovieSlot(input_name)
                outputs_slots = []
                for o_name in outputs_list:
                    out_slot = entityMovie.getMovieSlot(o_name)
                    outputs_slots.append(out_slot)
                    pass
                cnInstance = Connectable(input_slot, outputs_slots, self)
                self.AtomicConnectables.append(cnInstance)
                if movie_name == "Movie_Circle1":  # hard style
                    cnInstance.setAsSource()
                    pass

                if movie_name == "Movie_Receiver":  # next hard style
                    cnInstance.setAsReceiver()
                    self.receivers.append(cnInstance)
                    pass
                pass
        pass

    def subMovieMapping(self):
        subMap = CircularReflectionManager.subMap
        for movieName in subMap:
            slotToMovieMap = subMap[movieName]
            movie = self.object.getObject(movieName)
            movieEn = movie.getEntity()
            for slotName, subMovieName in slotToMovieMap.items():
                slotNode = movieEn.getMovieSlot(slotName)
                movieNode = movieEn.getSubMovie(subMovieName)
                movieNode.disable()
                self.slotToSubMovie[slotNode] = movieNode
                pass
            pass
        pass

    def onSocketEntered(self, socket):
        if socket in self.socketToCircle:
            movie_object = self.socketToCircle[socket]

            self.current_rotatable = movie_object
            pass
        return False
        pass

    def onSocketLeaved(self, socket):
        if socket in self.socketToCircle:
            movie = self.socketToCircle[socket]
            if movie is self.current_rotatable:
                self.current_rotatable = None
                self.current_socket = socket
                pass
            pass
        return False
        pass

    def rotate(self, event):
        if event.isDown is True:
            self.allow_rotate = True
            self.clearence()
            self.suppressInteraction(False)
            arrow = Mengine.getArrow()
            self.mouseTouchVec = arrow.getLocalPosition()
        elif event.isDown is False:
            self.allow_rotate = False
            self.suppressInteraction(True)
            self.reconnect()
            pass
        return False

    def _onMouseMove(self, event):
        if self.allow_rotate is False:
            return False
            pass

        if self.current_rotatable is None:
            return False
            pass

        if self.mouseTouchVec is None:
            return False

        arrow = Mengine.getArrow()
        arrowPosition = arrow.getLocalPosition()
        basePosition = self.current_rotatable.getPosition()
        #         basePosition = self.mouseTouchVec
        #         print basePosition
        ddy = arrowPosition[1] - basePosition[1]
        ddx = arrowPosition[0] - basePosition[0]  # or 0.0001 # in be for divide by zero
        dr = (ddx, ddy)

        sq_length = (ddx ** 2 + ddy ** 2)
        if sq_length == 0:
            # zero assertion
            return False
            pass
        Angle = Mengine.signed_angle(dr)
        self.current_rotatable.setRotate(-Angle)
        return False
        pass

    def suppressInteraction(self, boolVal):
        defaultInteractive = int(not boolVal)
        [socket.setInteractive(boolVal) for socket in self.socketToCircle.keys() if socket.getInteractive() == defaultInteractive]
        if boolVal is False and self.current_socket is not None:
            self.current_socket.setInteractive(not boolVal)
            pass
        pass

    def reconnect(self):
        """
        Check for connection input and outputs Nodes.
        """
        for i in range(5):  # for sure
            for conn in self.AtomicConnectables:
                [conn.rebound(_conn) for _conn in self.AtomicConnectables]
                pass
            pass
        connected = [conn.markAsSource() for conn in self.AtomicConnectables if conn.is_emitting()]
        for connectable in self.receivers:
            if connectable.is_emitting() is False:
                return
                pass
        self._complete(True)
        pass

    def higlight(self, inputNode):
        """
        Turns enable and play on sub movie if inputNode connected with other outputNode
        """
        if inputNode not in self.slotToSubMovie:
            return
            pass
        subMovieNode = self.slotToSubMovie[inputNode]
        subMovieNode.enable()
        subMovieNode.play()
        pass

    def clearence(self):
        """
        Removes emitting state and turns sub movies off
        """
        [con.removeEmitter() for con in self.AtomicConnectables]
        for animatable in self.slotToSubMovie.values():
            animatable.disable()
            pass
        pass

    def validateManagement(self, collections):
        """
        Check if exist slot in movies
        """
        for movieName, nestedSlotDict in collections.items():
            slotNames = []
            movieObject = self.object.getObject(movieName)
            movieEntity = movieObject.getEntity()
            slotNames.extend(nestedSlotDict.values()[0])
            slotNames.extend(nestedSlotDict.keys())
            for slotName in slotNames:
                if movieEntity.hasMovieSlot(slotName) is False:
                    Trace.log("Entity", 0, "Slot %s doesnt exist in %s" % (slotName, movieName))
                    pass
                pass
            pass
        pass

    def _complete(self, isSkip):
        self.object.setParam("Play", False)
        self.enigmaComplete()
        pass