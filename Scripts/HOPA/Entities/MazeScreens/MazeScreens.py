
Enigma = Mengine.importEntity("Enigma")


class MazeScreens(Enigma):

    def _playEnigma(self):
        pass # task chains

    def _skipEnigma(self):
        self._cleanFull()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._cleanFull()
        self._prepare()
        self._playEnigma()