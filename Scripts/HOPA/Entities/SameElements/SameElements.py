from Foundation.TaskManager import TaskManager

from SameElementsManager import SameElementsManager


Enigma = Mengine.importEntity("Enigma")


class SameElements(Enigma):
    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addActionActivate(Type, "Collections")
        pass

    def __init__(self):
        super(SameElements, self).__init__()
        self.elements = {}
        self.elNum = 0
        pass

    def _onPreparation(self):
        super(SameElements, self)._onPreparation()
        pass

    def _onActivate(self):
        super(SameElements, self)._onActivate()
        pass

    def _playEnigma(self):
        collections = SameElementsManager.getCollections(self.EnigmaName)
        if len(self.Collections) == 0:
            tempDict = {}
            for collectionID, collection in collections.items():
                tempDict[collectionID] = []

                slots = collection.getSlots()
                movieName = collection.getMovieName()
                movie = self.object.getObject(movieName)
                movie.setPlay(True)
                movie.setLoop(True)

                for slotID, elName in slots.items():
                    ellFullName = self.__generateStartElement(movie, slotID, elName)
                    tempDict[collectionID].append([movieName, slotID, ellFullName, elName])
                    pass
                pass
            self.object.setCollections(tempDict)
            pass
        else:
            for collectionID, slots in self.Collections.items():
                newCollection = []
                for slotData in slots:
                    movieName, slotID, ellFullName, elName = slotData
                    movie = self.object.getObject(movieName)
                    movie.setPlay(True)
                    movie.setLoop(True)

                    ellFullName = self.__generateStartElement(movie, slotID, elName)
                    self.__changeElement(newCollection, collectionID, slotID, ellFullName, elName)
                    pass
                self.object.changeParam("Collections", collectionID, newCollection)
                pass
            pass

        self.__clickChangeButtons()
        self.__clickCollectionButtons()
        pass

    def _restoreEnigma(self):
        self._playEnigma()
        pass

    def __findElement(self, collectionID, slotID):
        Collection = self.Collections[collectionID]
        for slotData in Collection:
            movieName, tempSlotID, elementFullName, elName = slotData
            if slotID == tempSlotID:
                element = self.elements[elementFullName]
                elementEntityNode = element.getEntityNode()
                movie = self.object.getObject(movieName)
                movieEntity = movie.getEntity()
                slot = movieEntity.getMovieSlot(str(slotID))
                break
                pass
            pass

        return elementFullName, elName, elementEntityNode, slot
        pass

    def __checkWin(self):
        for slots in self.Collections.values():
            for slotData in slots:
                movieName1, slotID1, ellFullName1, elName1 = slotData
                curIndex = slots.index(slotData)

                if curIndex + 1 == len(slots):
                    continue
                    pass
                nextData = slots[curIndex + 1]
                movieName2, slotID2, ellFullName2, elName2 = nextData

                if elName1 != elName2:
                    return
                    pass
                pass
            pass

        self.object.setCollections({})
        self.enigmaComplete()
        pass

    def __changeElement(self, newCollection, collectionID, slotID, newElementName, elNewName):
        Collection = self.Collections[collectionID]
        for slotData in Collection:
            movieName, tempSlotID, elementFullName, elName = slotData
            if slotID == tempSlotID:
                break
                pass
            pass

        newCollection.append([movieName, slotID, newElementName, elNewName])
        pass

    def __changeCollectionElements(self, newCollection, collectionID, slotID):
        Collection = self.Collections[collectionID]
        slotsCount = len(Collection)
        if slotID == slotsCount:
            newIndex = 1
            pass
        else:
            newIndex = slotID + 1
            pass

        for slotData in Collection:
            movieName, tempSlotID, newElementName, elNewName = slotData
            if slotID == tempSlotID:
                break
                pass
            pass

        newCollection.append([movieName, newIndex, newElementName, elNewName])
        element = self.object.getObject(newElementName)
        elementEntityNode = element.getEntityNode()
        movie = self.object.getObject(movieName)
        movieEntity = movie.getEntity()
        movieSlot = movieEntity.getMovieSlot(str(newIndex))

        movieSlot.addChild(elementEntityNode)
        pass

    def __changeElements(self, buttonData):
        Collection1ID = buttonData.getCollectionID1()
        Slot1ID = buttonData.getSlot1ID()

        Collection2ID = buttonData.getCollectionID2()
        Slot2ID = buttonData.getSlot2ID()

        element1FullName, el1Name, elementEntity1, slot1 = self.__findElement(Collection1ID, Slot1ID)
        element2FullName, el2Name, elementEntity2, slot2 = self.__findElement(Collection2ID, Slot2ID)

        slot1.addChild(elementEntity2)
        newCollection1 = []
        self.__changeElement(newCollection1, Collection1ID, Slot1ID, element2FullName, el2Name)

        Collection1 = self.Collections[Collection1ID]
        for slotData in Collection1:
            movieName, tempSlotID, elementFullName, elName = slotData
            if Slot1ID != tempSlotID:
                newCollection1.append([movieName, tempSlotID, elementFullName, elName])
                pass
            pass

        self.object.changeParam("Collections", Collection1ID, newCollection1)

        slot2.addChild(elementEntity1)
        newCollection2 = []
        self.__changeElement(newCollection2, Collection2ID, Slot2ID, element1FullName, el1Name)

        Collection2 = self.Collections[Collection2ID]
        for slotData in Collection2:
            movieName, tempSlotID, elementFullName, elName = slotData
            if Slot2ID != tempSlotID:
                newCollection2.append([movieName, tempSlotID, elementFullName, elName])
                pass
            pass

        self.object.changeParam("Collections", Collection2ID, newCollection2)
        pass

    def __clickChangeButtons(self):
        buttons = SameElementsManager.getButtonsChange(self.EnigmaName)
        buttonsCount = len(buttons)
        with TaskManager.createTaskChain(Name="SameElementsChangeButtons", Group=self.object, Repeat=True) as tc:
            with tc.addRaceTask(buttonsCount) as tcc:
                for tc_b, buttonName in zip(tcc, buttons.keys()):
                    collectionID = buttons[buttonName]
                    tc_b.addTask("TaskButtonClick", ButtonName=buttonName)
                    tc_b.addFunction(self.__changeElements, collectionID)
                    tc_b.addFunction(self.__checkWin)
                    pass
                pass
            pass
        pass

    def __changeCollection(self, collectionID):
        newCollection = []
        slots = self.Collections[collectionID]
        for slotData in slots:
            movieName, slotID, ellFullName, elName = slotData
            self.__changeCollectionElements(newCollection, collectionID, slotID)
            pass
        self.object.changeParam("Collections", collectionID, newCollection)
        pass

    def __clickCollectionButtons(self):
        buttons = SameElementsManager.getButtonCollections(self.EnigmaName)
        buttonsCount = len(buttons)
        with TaskManager.createTaskChain(Name="SameElementsCollectionButtons", Group=self.object, Repeat=True) as tc:
            with tc.addRaceTask(buttonsCount) as tcc:
                for tc_b, buttonName in zip(tcc, buttons.keys()):
                    buttonData = buttons[buttonName]
                    tc_b.addTask("TaskButtonClick", ButtonName=buttonName)
                    tc_b.addFunction(self.__changeCollection, buttonData)
                    pass
                pass
            pass
        pass

    def __generateStartElement(self, movie, id, elName):
        self.elNum += 1
        ellFullName = elName + str(self.elNum)
        element = self.object.generateObject(ellFullName, elName)
        element.setPosition((0, 0))
        elementEntityNode = element.getEntityNode()

        movieEntity = movie.getEntity()
        movieSlot = movieEntity.getMovieSlot(str(id))
        movieSlot.addChild(elementEntityNode)

        self.elements[ellFullName] = element
        return ellFullName
        pass

    def _onDeactivate(self):
        super(SameElements, self)._onDeactivate()
        self.__cleanData()
        pass

    def __cleanData(self):
        for el in self.elements.values():
            el.removeFromParent()
            el.onDestroy()
            pass
        self.elements = {}
        self.elNum = 0

        if TaskManager.existTaskChain("SameElementsChangeButtons"):
            TaskManager.cancelTaskChain("SameElementsChangeButtons")
            pass
        pass

        if TaskManager.existTaskChain("SameElementsCollectionButtons"):
            TaskManager.cancelTaskChain("SameElementsCollectionButtons")
            pass
        pass

    pass
