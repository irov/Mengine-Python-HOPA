Enigma = Mengine.importEntity("Enigma")

class BombClick(object):
    def __init__(self, game, pos):
        self.Game = game
        slot = self.Game.getSlot(pos)
        self.Item = slot.Item

        self.CurrentPos = pos

        self.Movies = []
        self.slotsExp = []
        self.ExpItems = []
        pass

    def PreExploud(self):
        slot_self = self.Game.getSlot(self.CurrentPos)
        id_Bomb = self.Item.ArrayPos + 1
        blob_Inivse = self.Game.getItemProtoById(id_Bomb)
        slot_self.setItemCheckSame(blob_Inivse)
        slot_self.UpdateTypeVisual()
        pass

    def Exploud(self):
        for mov in self.Movies:
            mov.onDestroy()
            pass
        self.Movies = []

        slot_self = self.Game.getSlot(self.CurrentPos)
        if (slot_self.Item.BombBlow is False):
            return

        self.slotsExp = self.Game.StartBombBlov(slot_self)
        for slotin in self.slotsExp:
            self.ExpItems.append(slotin.Item)
            slotin.setItemCheckSame(self.Game.item_Close_Block)
            slotin.UpdateTypeVisual()
            pass
        pass

    def ExploudEnd(self):
        itemsBlowCount = {}

        for i, slotin in enumerate(self.slotsExp):
            if (slotin.Item == self.Game.item_Close_Block):
                if (slotin.setItemCheckSame(self.Game.item_None_Open) is True):
                    ItemBlow = self.ExpItems[i]
                    if (ItemBlow in itemsBlowCount):
                        itemsBlowCount[ItemBlow] = itemsBlowCount[ItemBlow] + 1
                        pass
                    else:
                        itemsBlowCount[ItemBlow] = 0
                        pass
                    itemSpawn = ItemBlow.ItemRandom()
                    if (itemSpawn is not None):
                        slotin.setItemCheckSame(itemSpawn)
                        pass
                    pass
                slotin.UpdateTypeVisual()
                pass
            pass

        self.Item.AddPoints(itemsBlowCount, self.Game.getSlot(self.CurrentPos))

        for mov in self.Movies:
            mov.onDestroy()
            pass

        self.Movies = []
        self.ExpItems = []
        pass

    def getPreExploudMovie(self):
        slotBase = self.Game.getSlot(self.CurrentPos)
        preExpName = self.Item.getPreExploudMovieName()
        if (preExpName != None):
            preMovie = self.Game.genBaseMovies(preExpName)
            slotBase.setMovieSlotPos(preMovie)
            self.Movies.append(preMovie)
            return preMovie
            pass
        return None
        pass

    def getMovie(self, Holder):
        hold = []
        Holder[0] = hold
        ################
        for i, slotin in enumerate(self.slotsExp):
            itemSlot = self.ExpItems[i]
            if (itemSlot.getItemType() == 0):
                movieSlotExpName = itemSlot.getExploudMovieName()
                if (movieSlotExpName != None):
                    movieExSlot = self.Game.genBaseMovies(movieSlotExpName)
                    slotin.setMovieSlotPos(movieExSlot)
                    self.Movies.append(movieExSlot)
                    hold.append((movieExSlot, False))
                    pass
                pass

            movieNmae = self.Item.getExploudMovieName()
            movie = self.Game.genExploudMovies(movieNmae)
            slotin.setMovieSlotPos(movie)
            self.Movies.append(movie)

            wait = False
            if (i == len(self.slotsExp) - 1):
                wait = True
                pass
            hold.append((movie, wait))
            pass
        pass

    pass