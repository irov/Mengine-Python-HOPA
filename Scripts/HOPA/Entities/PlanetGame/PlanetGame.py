from HOPA.PlanetGameManager import PlanetGameManager

from Planet import Planet


Enigma = Mengine.importEntity("Enigma")


class PlanetGame(Enigma):

    @staticmethod
    def declareORM(Type):
        Type.addActionActivate(Type, "Planets", Change=PlanetGame._changePlanetValue)
        pass

    def __init__(self):
        super(PlanetGame, self).__init__()
        self.planetList = []
        self.planetDataList = []
        pass

    def _stopEnigma(self):
        super(PlanetGame, self)._stopEnigma()
        self.finalise()
        pass

    def _resetEnigma(self):
        for planet in self.planetList:
            planet.resetPlanet()
            pass
        pass

    def _playEnigma(self):
        self.planetDataList = PlanetGameManager.getPlanetGame(self.EnigmaName)
        for value in self.planetDataList:
            planet = Planet(self.object, value)
            planet.onInitialize()
            self.planetList.append(planet)
            pass
        pass

    def _changePlanetValue(self, planet, value):
        if self.completeCheck() is True:
            self.enigmaComplete()
            pass
        pass

    def finalise(self):
        for planet in self.planetList:
            planet.onFinalize()
            pass

        self.planetList = []
        self.checkDict = {}
        pass

    def completeCheck(self):
        for planet in self.planetDataList:
            name = planet.getMovieName()
            duration = planet.getDuration()
            winTiming = planet.getWinTiming()
            accuracy = planet.getAccuracy()
            planets = self.object.getPlanets()
            if name not in planets.keys():
                return False
                pass
            checkTiming = planets[name]
            rightWin = winTiming + accuracy
            leftWin = winTiming - accuracy

            if leftWin < 0:
                leftWin = duration + (winTiming - accuracy)
                if (checkTiming >= leftWin and checkTiming <= duration) or (checkTiming >= 0 and checkTiming <= rightWin):
                    continue
                    pass
                return False
                pass
            if (checkTiming <= rightWin) and (checkTiming >= leftWin):
                continue
                pass
            return False
        return True
        pass

    pass
