from Foundation.Entity.BaseEntity import BaseEntity
from Notification import Notification

from SpinCirclesDependsPluginManager import SpinCirclesDependsPluginManager

class Depend(object):
    def __init__(self, Depend, Direction, Movie, L, R, InitValues):
        self.Depend = Depend
        self.Direction = Direction
        self.Movie = Movie
        self.OwnCheck = L
        self.dependCheck = R
        self.values = InitValues
        pass

    def getDependKey(self):
        return self.Depend
        pass

    def getDirection(self):
        return self.Direction
        pass

    def getL(self):
        return self.OwnCheck
        pass

    def getR(self):
        return self.dependCheck
        pass

    def setValues(self, value):
        self.values = value
        pass

    def getValues(self):
        return self.values
        pass

    def getMovie(self):
        return self.Movie
        pass

    def Check(self, depend):
        check = depend.getCheckValue(self.dependCheck)
        if self.values[self.OwnCheck] == check:
            self.Movie.setEnable(True)
            pass
        else:
            self.Movie.setEnable(False)
            pass
        pass

    def updateValues(self):
        if self.Direction == "Left":
            self.values = self.values[1:] + [self.values[0]]
            pass
        if self.Direction == "Right":
            self.values = [self.values[-1]] + self.values[:-1]
            pass
        pass

    def getCheckValue(self, index):
        return self.values[index]
        pass

    pass

class SpinCirclesDependsPlugin(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "StoreData")
        pass
    def __init__(self):
        super(SpinCirclesDependsPlugin, self).__init__()
        self.SpinMoveObserver = None
        pass

    def _onPreparation(self):
        super(SpinCirclesDependsPlugin, self)._onPreparation()
        Data = SpinCirclesDependsPluginManager.getData(self.object.getName())
        self.dependsCollection = {}
        for itemKey, value in Data.iteritems():
            dependKey = value.getDepend()
            direction = value.getDirection()
            movieName = value.getMovieName()
            movie = self.object.getObject(movieName)
            movie.setEnable(False)
            initValues = value.getInitValues()
            ownCheck = value.getL()
            check = value.getR()
            dep = Depend(dependKey, direction, movie, ownCheck, check, initValues)
            self.dependsCollection[itemKey] = dep
            pass

        pass

    def _onActivate(self):
        super(SpinCirclesDependsPlugin, self)._onActivate()
        self.__updateMovies()
        self.SpinMoveObserver = Notification.addObserver(Notificator.onSpinMove, self.__onSpinMove)
        pass

    def __onSpinMove(self, key):
        depend = self.dependsCollection[key]
        depend.updateValues()
        self.__updateMovies()
        return False
        pass

    def __updateMovies(self):
        for depend in self.dependsCollection.values():
            checkKey = depend.getDependKey()
            checkDepend = self.dependsCollection[checkKey]
            depend.Check(checkDepend)
            pass
        pass
    def _onDeactivate(self):
        super(SpinCirclesDependsPlugin, self)._onDeactivate()
        Notification.removeObserver(self.SpinMoveObserver)
        pass

    pass