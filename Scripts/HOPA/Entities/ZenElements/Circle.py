class Circle(object):
    def __init__(self, DetailsDict):
        self.currentFrame = 0
        self.situatedBehavior = False
        self.Slots = None
        self.Movie = None
        self.Socket = None
        self.__dict__.update(DetailsDict)

        #        Need Movie with 360 frames!!
        self.slotsGuides = [360 * slot / self.Slots for slot in range(self.Slots)]
        pass

    def getCurrentFrame(self):
        return self.currentFrame

    def setSituated(self):
        self.situatedBehavior = True
        pass

    def isSituated(self):
        return self.situatedBehavior

    def updateFrame(self, frame):
        self.__updateGuide(frame)

        jumpedFrame = self.currentFrame + frame
        if jumpedFrame >= 360:
            self.currentFrame = jumpedFrame - 360
            if self.currentFrame == 0:
                self.currentFrame = 1
                pass
            pass
        else:
            self.currentFrame = jumpedFrame
            pass
        return self.currentFrame
        pass

    def getCountSlots(self):
        return self.Slots

    def __updateGuide(self, frame):
        for i, guide in enumerate(self.slotsGuides):
            new_guide = guide + frame
            if new_guide >= 360:
                self.slotsGuides[i] = new_guide - 360
            else:
                self.slotsGuides[i] = new_guide
        pass

    def get_slot_by_guide(self, guide):
        if guide in self.slotsGuides:
            #            print guide,self.slotsGuides.index(guide),self.slotsGuides
            return self.slotsGuides.index(guide)
        else:
            return None
        pass

    def calcGuidesToStep(self, frame):
        degrees = []
        for guide in self.slotsGuides:
            if frame < guide:
                degree = 360 - guide + frame
            else:
                degree = frame - guide
            degrees.append(degree)
            pass
        return min(degrees)
        pass

    def getSlotGuides(self):
        return self.slotsGuides
        pass

    def getMovie(self):
        return self.Movie
        pass

    def getSocket(self):
        return self.Socket
        pass

    pass
