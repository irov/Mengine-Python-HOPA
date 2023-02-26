from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.PuzzleDragDropManager import PuzzleDragDropManager
from Notification import Notification

Enigma = Mengine.importEntity("Enigma")

class PuzzleDragDrop(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)

        Type.addAction(Type, "Items")
        Type.addAction(Type, "Places")
        Type.addAction(Type, "HoldItems")
        Type.addAction(Type, "DisableItems")
        pass

    def __init__(self):
        super(PuzzleDragDrop, self).__init__()
        self.clean = []
        self.ParentLayer = "PuzzleDragDrop"
        self.winCase = []
        pass

    def _stopEnigma(self):
        self._positionSave()
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            self.__clean()
            pass
        Notification.removeObserver(self.Note)
        self.clearance()
        return True
        pass

    def _playEnigma(self):
        self.__Restore()
        self.Note = Notification.addObserver(Notificator.onPuzzleOutPlaced, fn=self.__rmvFromColection)
        self.PuzzleDragDrop = PuzzleDragDropManager.getPuzzleDragDrop(self.EnigmaName)
        self.winCase = self.PuzzleDragDrop.winCase
        self.ItemLinks = self.PuzzleDragDrop.getLinks()
        self.pair = dict(self.PuzzleDragDrop.elements)

        with TaskManager.createTaskChain(Name=self.EnigmaName, Group=self.object, Cb=self._complete) as tc:
            with tc.addParallelTask(len(self.PuzzleDragDrop.elements)) as tcs:
                for tci, element in zip(tcs, self.PuzzleDragDrop.elements):
                    pickItem = self.object.getObject(element[0])
                    pickItemEntity = pickItem.getEntity()
                    placeItem = self.object.getObject(element[1])
                    placeItem.setAlpha(0)
                    self.Items.append(pickItem)
                    self.clean.append(pickItem)

                    position = placeItem.getPosition()
                    with tci.addRepeatTask() as (tc_do, tc_until):
                        tc_do.addTask("AliasDragDropPuzzle", ItemName=element[0], SocketItemName=element[1])

                        tc_do.addTask("TaskObjectSetPosition", Object=pickItem, Value=position)
                        tc_do.addTask("TaskNodeSetPosition", Node=pickItemEntity, Value=position)
                        tc_do.addTask("TaskFunction", Fn=self.HoldItems.append, Args=(element[0],))
                        tc_do.addTask("TaskFunction", Fn=self.__isWin)
                        tc_until.addTask("TaskListener", ID=Notificator.onPuzzleDragDropWin)
                        pass

                tc.addTask("TaskDelay", Time=1 * 1000)  # speed fix
                pass
            pass
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def _autoWin(self):
        if self.object.getPlay() is False:
            return False
            pass
        TaskManager.cancelTaskChain(self.EnigmaName)
        for it, element in enumerate(self.winCase):
            placeItem = self.object.getObject(self.PuzzleDragDrop.elements[it][1])
            pickItem = self.object.getObject(element)
            position = placeItem.getPosition()
            pickItem.setOrigin((0, 0))
            pickItem.setPosition(position)
            pass

        with TaskManager.createTaskChain(Cb=self._complete) as tc:
            tc.addTask("TaskDelay", Time=1.5 * 1000)  # speed fix
            pass
        return True
        pass

    def _complete(self, isSkip):
        self.__clean()
        self.enigmaComplete()
        self.object.setParam("Play", False)
        pass

    def __clean(self):
        if self.clean == []:
            return
            pass
        for each in self.clean:
            entity = each.getEntity()
            self.addChild(entity)
            pass
        self.clean = []
        pass

    def _positionSave(self):
        for item in self.Items:
            self.object.changeParam("Places", item, item.getPosition())
            #            self.Places[item]=item.getPosition()
            pass
        pass

    def __Restore(self):
        items = self.Items
        place = self.Places
        if not items:
            return
            pass
        for item in items:
            Layer = SceneManager.getLayerScene(self.ParentLayer)
            itemEn = item.getEntity()
            Layer.addChild(itemEn)
            origin = item.getOrigin()
            if item.getName() in self.winCase:
                prev = item.getInteractive()
                #                print item.getName(), prev
                if prev != 0:
                    item.setInteractive(0)  # !!!!!!!!!!!!!!!!!!!!!!
                    pass
                pass
            item.setPosition((place[item][0] - origin[0], place[item][1] - origin[1]))
            pass

        disableObjects = self.object.getParam("DisableItems")

        for link in disableObjects:
            for item in link:
                ObjectPick = self.object.getObject(item)
                ObjectPick.setEnable(False)
                pass
            pass
        pass

    def clearance(self):
        self.pair = {}
        self.ItemLinks = None
        pass

    def __isWin(self):
        LastPick = self.HoldItems[-1]

        SocketName = self.pair[LastPick]
        LastObject = self.object.getObject(LastPick)
        SocketObject = self.object.getObject(SocketName)
        if LastPick in self.winCase:
            LastObject.setInteractive(False)
            SocketObject.setInteractive(False)
            self.disableLinks(LastPick)
            pass

        progres = self.HoldItems[-len(self.winCase):]  # for sure
        c = set(self.winCase) - set(progres)
        #        print "Need to find : %d puzzle elements "%len(c), c
        if c != set([]):
            return False
            pass

        Notification.notify(Notificator.onPuzzleDragDropWin)
        return True
        pass

    def __rmvFromColection(self, itemName):
        if itemName in self.HoldItems:
            self.HoldItems.remove(itemName)
            pass
        return False
        pass

    def disableLinks(self, LastPick):
        if LastPick not in self.ItemLinks:
            return
            pass
        LastObject = self.object.getObject(LastPick)
        LastObject.setInteractive(False)
        LastObject.setInteractive(False)

        LinksList = self.ItemLinks[LastPick]
        self.DisableItems.append(LinksList)
        for pick in LinksList:
            pickObj = self.object.getObject(pick)
            pickObj.setEnable(False)
            pass
        pass
    pass