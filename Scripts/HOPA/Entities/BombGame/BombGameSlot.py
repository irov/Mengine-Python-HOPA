Enigma = Mengine.importEntity("Enigma")

class BombGameSlot(object):
    def __init__(self, Game, slotX, slotY, Pos, Movie, SocketName, Group):
        self.Game = Game
        self.slotX = slotX
        self.slotY = slotY
        self.Pos = Pos

        self.Movie = Movie
        self.SocketName = SocketName

        self.Group = Group

        self.Item = None

        self.MovieIdle = None
        self.SameCount = 0
        pass

    def setItemForce(self, Item):
        self.Item = Item
        self.SameCount = 0
        pass

    def setItemCheckSame(self, Item):
        if (self.Item == Item):
            self.SameCount = self.SameCount + 1
            pass
        else:
            if (self.SameCount <= 0):
                self.Item = Item
                self.SameCount = 0
                return True;
                pass
            else:
                self.SameCount = self.SameCount - 1
                pass
            pass
        return False;
        pass

    def UpdateTypeVisual(self):
        self.Clear()
        if (self.Item.ItemData is None):
            return
            pass

        self.MovieIdle = self.__CreateMovieIdle()
        pass

    def __CreateMovieIdle(self):
        MovieIdleName = self.Item.getIdleMovieName()
        if (MovieIdleName is None):
            return None
            pass

        Movie = self.Game.genBaseMovies(MovieIdleName)
        self.setMovieSlotPos(Movie)
        return Movie
        pass

    # def __CreateSpriteItem(self):
    #     Sprite = self.Item.Sprite_Item
    #     ItemEntity = Sprite.getEntity()
    #     pure = ItemEntity.generatePure()
    #     pure.enable()
    #
    #     offset = (0, 0)
    #     pos = (self.Pos[0] + offset[0], self.Pos[1] + offset[1])
    #     pure.setLocalPosition(pos)
    #     # prevent from scale with slot
    #     layerScene = self.Group.getScene()
    #     mainLayer = layerScene.getMainLayer()
    #     mainLayer.addChild(pure)
    #
    #     return pure
    #     pass

    def Clear(self):
        if (self.MovieIdle is None):
            return
            pass

        self.MovieIdle.onDestroy()
        self.MovieIdle = None
        pass

    #
    # def getExploudMovieName(self, Item):
    #     Expl = Item.getExploudMovieName()
    #     if(self.Item is not None):
    #         ExplType = self.Item.getExploudMovieName()
    #         if(ExplType is not None):
    #             Expl = ExplType
    #             pass
    #         pass
    #     return Expl
    #     pass

    def setMovieSlotPos(self, movie):
        movieEntity = movie.getEntity()
        movieEntity.setLocalPosition(self.Pos)
        pass

    def __str__(self):
        str = "x %d, y %d " % (self.slotX, self.slotY)
        return str
        pass

    pass