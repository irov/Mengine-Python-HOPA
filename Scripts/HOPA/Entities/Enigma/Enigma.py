from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.ZoomManager import ZoomManager

ID_EMPTY_TEXT = "ID_EMPTY_TEXT"

class Enigma(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate("Skiping")  # Enigma in skip state
        Type.addActionActivate("Skipped")  # set to True if Enigma was Skipped
        Type.addActionActivate("Play", Update=Enigma.__updatePlay)
        Type.addActionActivate("Playing")
        Type.addActionActivate("EnigmaName")
        Type.addActionActivate("EnigmaParams")
        Type.addActionActivate("Pause")
        Type.addActionActivate("Complete")

    def __init__(self):
        super(Enigma, self).__init__()

        self.isPlayNow = None
        self.tc_EnigmaSkip = None

        self.onEnigmaSkipObserver = None
        self.onEnigmaResetObserver = None

        # separation hogs from other minigames for achievemnts
        self.isHOG = False
        self.isMiniHOG = False

    def isSkiping(self):
        return self.Skiping

    def isSkipped(self):
        return self.Skipped

    def isPlay(self):
        return self.object.getPlay()

    def __updatePlay(self, value):
        if self.isPlayNow is value:
            return

        if self.isSkiping():
            return

        if self.Complete:
            return

        self.isPlayNow = value

        if value is True:
            self.playEnigma()
        else:
            self.stopEnigma()

    def _onPreparation(self):
        if self.Complete:
            return
        super(Enigma, self)._onPreparation()

        name = EnigmaManager.getEnigmaName(self.object)
        self.object.setEnigmaName(name)

        self._emptyInventoryText("MahjongInventory")
        self._emptyInventoryText("PuzzleInventory")
        self._emptyInventoryText("MiniPuzzleInventory")
        self._emptyInventoryText("MiniCountInventory")

    def _onActivate(self):
        if self.Complete:
            return
        super(Enigma, self)._onActivate()
        self.onEnigmaSkipObserver = Notification.addObserver(Notificator.onEnigmaSkip, self.__onEnigmaSkip)
        self.onEnigmaResetObserver = Notification.addObserver(Notificator.onEnigmaReset, self.__onEnigmaReset)

        Notification.notify(Notificator.onEnigmaActivate, self.object)

    def _onDeactivate(self):
        super(Enigma, self)._onDeactivate()

        Notification.removeObserver(self.onEnigmaSkipObserver)
        Notification.removeObserver(self.onEnigmaResetObserver)
        self.onEnigmaSkipObserver = None
        self.onEnigmaResetObserver = None

        Notification.notify(Notificator.onEnigmaDeactivate, self.object)

        if self.object.getPlay() is True:
            self.isPlayNow = False

            self.object.setPause(True)
            self.pauseEnigma()

    def enigmaComplete(self):
        if self.tc_EnigmaSkip is not None:
            self.tc_EnigmaSkip.cancel()
            self.tc_EnigmaSkip = None

        Enigma = EnigmaManager.getEnigma(self.EnigmaName)

        if Enigma.ZoomFrameGroup is not None:
            # zoom close before on notificator execution fix
            if Enigma.groupName is not None:
                if ZoomManager.hasZoom(Enigma.groupName):
                    zoom = ZoomManager.getZoom(Enigma.groupName)
                    if zoom is not None:
                        zoom.tempFrameGroupName = None

            Notification.notify(Notificator.onZoomEnigmaChangeBackFrameGroup)

        hasMovieWin = Enigma.hasMovieWinObject()
        if hasMovieWin is False:
            self.__onEnigmaComplete()
            return

        movie = Enigma.getMovieWinObject()
        movie_type = movie.getType()

        with TaskManager.createTaskChain() as tc:
            with GuardBlockInput(tc) as guard_source:
                if movie_type == "ObjectMovie2":
                    guard_source.addTask("TaskMovie2Play", Movie2=movie, Wait=True)
                elif movie_type == "ObjectMovie":
                    guard_source.addTask("TaskMoviePlay", Movie=movie, Wait=True)

                guard_source.addFunction(self.__onEnigmaComplete)

    def __onEnigmaComplete(self):
        self.object.setSkiping(False)
        self.object.setPlay(False)
        self.object.setPlaying(False)
        self.object.setPause(False)
        self.object.setComplete(True)

        Notification.notify(Notificator.onEnigmaComplete, self.object)

    def __onEnigmaSkip(self):
        if self.object is None:
            if _DEVELOPMENT is True:
                Trace.log("Entity", 0, "Enigma.__onEnigmaSkip: '{}'.object is None".format(self.getName()))
            return False
        if self.object.getPlay() is False:
            return False
        if self.Skiping:
            return False
        self.object.setSkiping(True)
        self.object.setSkipped(True)
        self.tc_EnigmaSkip = TaskManager.createTaskChain()
        with self.tc_EnigmaSkip as tc:
            with GuardBlockInput(tc) as guard_source:
                guard_source.addScope(self.skipEnigma)

        return False

    def skipEnigma(self, source):
        source.addScope(self._skipEnigmaScope)
        source.addFunction(self._skipEnigma)
        source.addFunction(self.enigmaComplete)

    def _skipEnigma(self):
        pass

    def _skipEnigmaScope(self, source):
        pass

    def __onEnigmaReset(self):
        if self.object.getPlay() is False:
            return False

        self._resetEnigma()

        return False

    def _resetEnigma(self):
        pass

    def playEnigma(self):
        Enigma = EnigmaManager.getEnigma(self.EnigmaName)
        if Enigma.ZoomFrameGroup is not None:
            Notification.notify(Notificator.onZoomEnigmaChangeFrameGroup, Enigma.ZoomFrameGroup)

        self._setInventoryText("MahjongInventory")
        self._setInventoryText("PuzzleInventory")
        self._setInventoryText("MiniPuzzleInventory")
        self._setInventoryText("MiniCountInventory")

        self.object.setPause(False)
        if self.Playing is False:
            self.object.setPlaying(True)

            Notification.notify(Notificator.onEnigmaStart, self.object)

            self._playEnigma()
        else:
            Notification.notify(Notificator.onEnigmaRestore, self.object)

            self._restoreEnigma()

        Notification.notify(Notificator.onEnigmaPlay, self.object)

    def _emptyInventoryText(self, demon_name):
        if not DemonManager.hasDemon(demon_name):
            return

        inventory = DemonManager.getDemon(demon_name)
        inventory.setTextID(ID_EMPTY_TEXT)

    def _setInventoryText(self, demon_name):
        if not DemonManager.hasDemon(demon_name):
            return

        inventory = DemonManager.getDemon(demon_name)
        inventory.setEnigmaName(self.EnigmaName)

        text_id = EnigmaManager.getEnigmaInventoryText(self.EnigmaName)
        inventory.setTextID(text_id)

    def _playEnigma(self):
        pass

    def _restoreEnigma(self):
        pass

    def stopEnigma(self):
        if self.Playing is False:
            return

        self.object.setPlaying(False)

        Notification.notify(Notificator.onEnigmaStop, self.object)

        self._stopEnigma()
        pass

    def _stopEnigma(self):
        pass

    def pauseEnigma(self):
        Notification.notify(Notificator.onEnigmaPause, self.object)

        self._pauseEnigma()
        pass

    def _pauseEnigma(self):
        pass
