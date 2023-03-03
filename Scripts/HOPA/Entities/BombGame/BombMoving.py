Enigma = Mengine.importEntity("Enigma")

import math


class BombMoving(object):
    Move_None = 0
    Move_Cant = 1
    Move_Out = 2
    Move_Move = 3
    Move_Exploud = 4

    def __init__(self, game, pos):
        self.Game = game
        slot = self.Game.getSlot(pos)
        self.Item = slot.Item

        self.PrevPos = None
        self.CurrentPos = pos
        self.NextPos = None
        self.NextNextPos = None

        self.Dir = 0
        self.MoveVec = (0, 0)
        self.StartMove = False
        self.Result = -1

        self.Movies = []
        self.slotsExp = []
        self.ExpItems = []
        self.SpawnPrevent = []

        pass

    ###################################
    def Move(self):
        self.Movies = []
        self.Result = BombMoving.Move_None
        self.slotsExp = []
        self.ExpItems = []

        slot_self = self.Game.getSlot(self.CurrentPos)
        if (slot_self.Item.BombBlow is False):
            return

        self.NextPos = (self.CurrentPos[0] + self.MoveVec[0], self.CurrentPos[1] + self.MoveVec[1])
        slot_dir1 = self.Game.getSlot(self.NextPos)

        if (slot_dir1 is None):
            self.SpawnPrevent = []
            self.__MoveOut()
            return self.Result
        else:
            slot_dir1_Item = slot_dir1.Item
            if (slot_dir1_Item.Colis is True):
                if (self.StartMove is True or slot_dir1_Item == self.Game.item_Close_Block):
                    self.SpawnPrevent = []

                    self.__MoveExploud()
                    pass
                else:
                    self.__MoveCantMove()
                    pass
                return self.Result
            else:
                if (self.StartMove is False):
                    self.AddSpawnPreventLine()

                    id_Bomb = self.Item.ArrayPos + 1
                    blob_Inivse = self.Game.getItemProtoById(id_Bomb)
                    slot_self.setItemCheckSame(blob_Inivse)
                    slot_self.UpdateTypeVisual()
                    pass

                self.StartMove = True
                if (self.CurrentPos in self.SpawnPrevent):
                    self.SpawnPrevent.remove(self.CurrentPos)
                    pass

                self.__MoveInMove()
                return self.Result
            pass
        pass

    def AddSpawnPreventLine(self):
        pos = self.CurrentPos
        xPos = pos[0]
        yPos = pos[1]
        Dir = self.Game.Dir_Add[self.Dir]
        xDir = Dir[0]
        yDir = Dir[1]
        if (xDir != 0):
            if (xDir > 0):
                for X_New in range(xPos + 1, self.Game.FieldWidth):
                    posNew = (X_New, yPos)
                    if (self.__AddPrevent(posNew) is True):
                        break
                    pass
                pass
            else:
                for X_New in reversed(range(0, xPos)):
                    posNew = (X_New, yPos)
                    if (self.__AddPrevent(posNew) is True):
                        break
                    pass
                pass
            pass
        elif (yDir != 0):
            if (yDir > 0):
                for Y_New in range(yPos + 1, self.Game.FieldHeight):
                    posNew = (xPos, Y_New)
                    if (self.__AddPrevent(posNew) is True):
                        break
                    pass
                pass
            else:
                for Y_New in reversed(range(0, yPos)):
                    posNew = (xPos, Y_New)
                    if (self.__AddPrevent(posNew) is True):
                        break
                    pass
                pass
            pass
        self.Game.PreventSpawn.append(self)
        pass

    def __AddPrevent(self, pos):
        slot = self.Game.getSlot(pos)
        if (slot.Item.Colis is False):
            self.SpawnPrevent.append(pos)
            return False
            pass
        else:
            return True
            pass
        pass

    ###################
    def EndMove(self):
        if (self.Result == BombMoving.Move_Cant):
            pass
        elif (self.Result == BombMoving.Move_Out):
            pass
        elif (self.Result == BombMoving.Move_Move):
            self.__MoveInMoveEnd()
            pass
        elif (self.Result == BombMoving.Move_Exploud):
            self.__MoveExploudEnd()
            pass

        for mov in self.Movies:
            mov.onDestroy()
            pass

        self.Movies = []

        self.SpawnPrevent = []
        pass

    ############
    def __MoveExploud(self):
        slot_self = self.Game.getSlot(self.CurrentPos)

        self.slotsExp = self.Game.StartBombBlov(slot_self)
        for slotin in self.slotsExp:
            self.ExpItems.append(slotin.Item)
            slotin.setItemCheckSame(self.Game.item_Close_Block)
            slotin.UpdateTypeVisual()
            pass

        self.Result = BombMoving.Move_Exploud
        pass

    def __MoveExploudEnd(self):
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

        pass

    ############
    def __MoveInMove(self):
        slot_dir = self.Game.getSlot(self.NextPos)
        if (slot_dir.Item == self.Game.item_None_Open):
            id_Bomb = self.Item.ArrayPos + 1
            blob_Inivse = self.Game.getItemProtoById(id_Bomb)
            slot_dir.setItemCheckSame(blob_Inivse)
            slot_dir.UpdateTypeVisual()
            pass

        self.PrevPos = self.CurrentPos
        self.CurrentPos = self.NextPos
        self.NextPos = None

        self.Result = BombMoving.Move_Move
        pass

    def __MoveInMoveEnd(self):
        slot_Prev = self.Game.getSlot(self.PrevPos)

        id_Bomb = self.Item.ArrayPos + 1
        blob_Inivse = self.Game.getItemProtoById(id_Bomb)

        if (slot_Prev.Item == blob_Inivse):
            slot_Prev.setItemForce(self.Game.item_None_Open)
            slot_Prev.UpdateTypeVisual()
            pass
        pass

    ############
    def __MoveOut(self):
        slot_self = self.Game.getSlot(self.CurrentPos)
        if (slot_self.Item.BombBlow is True):
            slot_self.setItemForce(self.Game.item_None_Open)
            slot_self.UpdateTypeVisual()
            pass

        self.Result = BombMoving.Move_Out
        pass

    ############
    def __MoveCantMove(self):
        self.Result = BombMoving.Move_Cant
        pass

    ###################################

    def SetMoveDir(self, MouseStart, MouseEnd):
        dif_X = MouseEnd[0] - MouseStart[0]
        difA_X = math.fabs(dif_X)

        dif_Y = MouseEnd[1] - MouseStart[1]
        difA_Y = math.fabs(dif_Y)
        # dir 1 Top 2 Bot 3 Left 4 Right
        if (difA_X > difA_Y):
            big = difA_X
            small = difA_Y
            if (dif_X > 0):
                dir = 4
            else:
                dir = 3
            pass
        else:
            big = difA_Y
            small = difA_X
            if (dif_Y > 0):
                dir = 2
            else:
                dir = 1
            pass

        self.Dir = 0
        self.MoveVec = (0, 0)
        if (self.__checkRange(big, small) is False):
            return False
            pass

        self.Dir = dir
        self.MoveVec = self.Game.Dir_Add[dir]

        return True
        pass

    def HaveMoveDir(self):
        if (self.Dir == 0):
            return False
            pass
        return True
        pass

    def __checkRange(self, biger, smaller):
        if (biger > 40):
            return True
        return False
        # dist_Act = 30
        # dist_ActEtc = 20
        # if(biger > dist_Act and smaller < dist_ActEtc):
        #     return True
        #     pass
        # return False
        pass

    def getMovie(self, Holder):
        hold = []
        Holder[0] = hold
        self.Movies = []

        if (self.Result == BombMoving.Move_None):
            pass
        elif (self.Result == BombMoving.Move_Cant):
            pass
        elif (self.Result == BombMoving.Move_Out):
            movieNmae = self.Item.getMoveMovieNameOut(self.Dir)
            movie = self.Game.genBaseMovies(movieNmae)
            slot = self.Game.getSlot(self.CurrentPos)
            slot.setMovieSlotPos(movie)
            self.Movies.append(movie)
            hold.append((movie, True))
            pass
        elif (self.Result == BombMoving.Move_Move):
            movieNmae = self.Item.getMoveMovieName(self.Dir)
            movie = self.Game.genBaseMovies(movieNmae)
            slot = self.Game.getSlot(self.PrevPos)
            slot.setMovieSlotPos(movie)
            self.Movies.append(movie)
            hold.append((movie, True))
            pass
        elif (self.Result == BombMoving.Move_Exploud):
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

    pass
