from Foundation.TaskManager import TaskManager
from HOPA.ShootingRangeManager import ShootingRangeManager
from Notification import Notification

from BallStack import BallStack
from ChasingSystem import ChasingSystem
from Gun import Gun


Enigma = Mengine.importEntity("Enigma")


class ShootingRange(Enigma):
    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "Atitude")
        Type.addAction(Type, "GunPos")
        pass

    def __init__(self):
        super(ShootingRange, self).__init__()
        self.hits = 0
        self.hit_for_win = 3
        self.Gun = None

        pass

    def _stopEnigma(self):
        Notification.removeObserver(self.HedShots)
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass
        self.clean_all()
        self.clearance()
        pass

    def _skipEnigma(self):
        self.enigmaComplete()
        self.__complete(True)
        pass

    def _playEnigma(self):
        self.prepareEnigma()
        self.HedShots = Notification.addObserver(Notificator.onChased, self.onHit)
        pass

    def __complete(self, isSkip):
        # self.enigmaComplete()
        # self.object.setParam("Play", False)
        self.clean_all()
        pass

    def isactive(self, *params):
        if self.object.getPlay() is False:
            return False
            pass
        return True
        pass

    def prepareEnigma(self):
        movie_names = ShootingRangeManager.genGunMovies(self.EnigmaName)
        guns = [self.object.getObject(movie) for movie in movie_names]
        self.socketTarget = self.object.getObject("Socket_Target")
        stack = self.object.getObject("Movie_BallStack")
        stack.setEnable(False)
        BallStack.init_with(stack)
        shoots_limit = ShootingRangeManager.getLimit(self.EnigmaName)
        ball_movies = ShootingRangeManager.getBallsMovie(self.EnigmaName)
        ball_obj = [self.object.getObject(movie_name) for movie_name in ball_movies]
        generic = self.object  # .generateObject
        pattern = ShootingRangeManager.getBallSprite(self.EnigmaName)
        #        pattern = ["Sprite_Ball3","Sprite_Ball1","Sprite_Ball2"]
        #        marker = ["Sprite_KabanOn","Sprite_MedvedOn","Sprite_VolkOn"]
        marker = ShootingRangeManager.getMarks(self.EnigmaName)
        marker_obj = [self.object.getObject(name) for name in marker]
        for mark in marker_obj:
            mark.setEnable(False)
            pass
        self.Gun = Gun(guns, ball_obj, self.socketTarget, generic, pattern)
        self.Gun.setLimit(shoots_limit)
        MainLayer = self.getParent()
        win_dimention = MainLayer.getSize()
        self.Gun.setupGeometry(self.GunPos, self.Atitude, win_dimention)

        target_movie_names = ShootingRangeManager.getTargetMovie(self.EnigmaName)
        target_movies = [self.object.getObject(movie_name) for movie_name in target_movie_names]
        self.marker = dict(zip(target_movies, marker_obj))
        CarrierName = ShootingRangeManager.getCarriers(self.EnigmaName)
        #        movieCarrier = self.object.getObject("Movie_Carrier")
        movieCarrier = self.object.getObject(CarrierName)
        ChasingSystem.load(target_movies, movieCarrier, self.object)
        ChasingSystem.run_chase()
        pass

    def clearance(self):
        self.marker = {}
        self.hits = 0
        self.Gun = None
        pass

    def onHit(self, TargetInstance):
        self.hits += 1
        mov = TargetInstance.movie
        sprite = self.marker[mov]
        sprite.setEnable(True)
        return False
        pass

    def checkWin(self):
        if self.hits == self.hit_for_win:
            self.enigmaComplete()
            pass
        pass

    def _resetEnigma(self):
        self.clean_all()
        self.prepareEnigma()
        pass

    def clean_all(self):
        self.hits = 0
        if self.Gun is not None:
            self.Gun.destroy()
            self.Gun = None
            pass
        BallStack.reset()
        ChasingSystem.stop_chase()
        pass

    pass
