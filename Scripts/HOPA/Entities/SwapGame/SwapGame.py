from Foundation.TaskManager import TaskManager


Enigma = Mengine.importEntity("Enigma")

import math


class SwapGame(Enigma):
    class Slot(object):
        def __init__(self, id):
            self.Id = id
            self.Movie = None
            self.Pos = None
            pass

        def set_Move(self, mov):
            self.Movie = mov
            self.Movie.setPosition(self.Pos)
            pass

        pass

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(SwapGame, self).__init__()
        self.ReInitParamentrs()
        pass

    def ReInitParamentrs(self):
        self.Movie_Names = ["Movie_Cr_1", "Movie_Cr_2", "Movie_Cr_3", "Movie_Cr_4", "Movie_Cr_5"]
        self.Movie_Points_Name = ["Movie_Points", "Movie_Points", "Movie_Points", "Movie_Points", "Movie_Points"]
        self.Movie_Points_Sub_Movie_Name = ["Cr_1", "Cr_2", "Cr_3", "Cr_4", "Cr_5"]
        self.Positions_Start_Id = [4, 1, 3, 2, 0]
        self.Positions_End_Id = [0, 1, 2, 3, 4]
        self.Positions_Now_Id = []

        self.Slots = []
        self.Movie_Points = None

        self.Click = None

        self.generatedObjects = []
        self.AliaseNames = []
        pass

    def _skipEnigma(self):
        self.__Finita()
        self.enigmaComplete()
        pass

    def _playEnigma(self):
        self._PreInit()
        self._InitAlias()
        pass

    def _PreInit(self):
        for id, sub in enumerate(self.Movie_Points_Sub_Movie_Name):
            self.Positions_Now_Id.append(self.Positions_Start_Id[id])
            slot = SwapGame.Slot(id)
            mov_name = self.Movie_Points_Name[id]
            mov = self.object.getObject(mov_name)

            mov_Sub = mov.getEntity().getSubMovie(self.Movie_Points_Sub_Movie_Name[id])
            pos = mov_Sub.getLocalPosition()
            PosAnch = mov_Sub.getOrigin()
            pos_Start = (pos[0] - PosAnch[0], pos[1] - PosAnch[1])
            slot.Pos = pos_Start
            self.Slots.append(slot)
            pass

        for id, name in enumerate(self.Movie_Names):
            mov = self.object.generateObject("%s %s" % (id, name), name)
            id_Slot = self.Positions_Start_Id[id]
            # print id, " ", id_Slot
            slot = self.Slots[id_Slot]
            slot.set_Move(mov)
            self.generatedObjects.append(mov)
            pass

        self.Movie_Points = self.object.getObject("Movie_Points")
        pass

    def _InitAlias(self):
        for id in range(len(self.Movie_Names)):
            self._InitAlias_Item(id)
            pass
        pass

    def _InitAlias_Item(self, id):
        sockName = "C_%d" % (id + 1)

        def click_():
            if (self.Click == id):
                return
                pass

            if (self.Click is None):
                self.Click = id
                pass
            else:
                dif = self.Click - id
                if (math.fabs(dif) > 1):
                    self.Click = None
                    return
                    pass

                slot1 = self.Slots[self.Click]
                slot2 = self.Slots[id]
                pos_Id1 = self.Positions_Now_Id[self.Click]
                pos_Id2 = self.Positions_Now_Id[id]
                mov1 = slot1.Movie
                mov2 = slot2.Movie

                slot1.set_Move(mov2)
                slot2.set_Move(mov1)

                self.Positions_Now_Id[self.Click] = pos_Id2
                self.Positions_Now_Id[id] = pos_Id1

                self.Click = None
                pass

            # print "[[[[[[[[[[[[[[[["
            # print self.Positions_Now_Id, " Now"
            # print self.Positions_End_Id, " End"

            for i, e_id in enumerate(self.Positions_End_Id):
                if (self.Positions_Now_Id[i] != e_id):
                    return
                    pass
                pass

            self.__Finita()
            self.enigmaComplete()
            pass

        name_Al = "SwapGame_%s" % (id)
        self.AliaseNames.append(name_Al)

        with TaskManager.createTaskChain(Name=name_Al, Repeat=True) as tc:
            tc.addTask("TaskMovieSocketClick", SocketName=sockName, Movie=self.Movie_Points, isDown=True)
            tc.addFunction(click_)
            pass
        pass

    def __Finita(self):
        for name_A in self.AliaseNames:
            self.__canTT(name_A)
            pass

        for object in self.generatedObjects:
            object.removeFromParent()
            pass
        self.Positions_Now_Id = []

        self.Slots = []
        self.Movie_Points = None

        self.Click = None

        self.generatedObjects = []
        self.AliaseNames = []
        pass

    def __canTT(self, Name):
        if TaskManager.existTaskChain(Name) is True:
            TaskManager.cancelTaskChain(Name)
            pass
        pass

    def _onDeactivate(self):
        super(SwapGame, self)._onDeactivate()
        self.__Finita()
        pass

    pass
