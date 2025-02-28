from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager


class RotateMiniSystem(object):
    TaskName = "RotateMiniSystem_Rotate"

    def __init__(self):
        self.circles = {"ConstBehavior": [], "SituatedBehavior": []}
        self.place_guide = 0
        self.rotating = False
        self.DragSystemInstance = None

    def getSituated(self):
        circle = self.circles['SituatedBehavior'][0]
        return circle

    def loadRotates(self, *rotates):
        for circles in rotates:
            if circles.isSituated():
                self.circles["SituatedBehavior"].append(circles)
            else:
                self.circles["ConstBehavior"].append(circles)
        self.DragSystemInstance.load(self.circles)
        pass

    def setDragSystem(self, drag_instance):
        self.DragSystemInstance = drag_instance
        pass

    def save_progress(self):
        save_data = {}
        for behavior, listOfCircles in self.circles.items():
            saved_frames_states = []
            for CircleIns in listOfCircles:
                frame_state = CircleIns.getCurrentFrame()
                saved_frames_states.append(frame_state)
                pass
            save_data[behavior] = saved_frames_states
        return save_data
        pass

    def restore_progress(self, saveDataDict):
        for behavior, listOfCircles in self.circles.items():
            if len(saveDataDict[behavior]) != len(listOfCircles):
                return

            for i, CircleIns in enumerate(listOfCircles):
                degree = saveDataDict[behavior][i]
                self.Rotate(CircleIns, degree)
                pass
            pass
        pass

    def Rotate(self, Circle, degree):
        self.rotating = True
        frame = degree
        Circle.updateFrame(frame)
        Movie = Circle.getMovie()
        speed = DefaultManager.getDefaultFloat("ZenSpeed", 1)
        speed *= 0.001  # speed fix

        duration = Movie.getDuration() - 1
        MovieEn = Movie.getEntity()
        Movie.setSpeedFactor(speed)
        current_timing = MovieEn.getTiming()
        rewind_timing = duration * frame / 360
        set_time = current_timing + rewind_timing
        if set_time >= duration:
            set_time = set_time - duration
            pass

            # Hard style
            with TaskManager.createTaskChain(Name=RotateMiniSystem.TaskName) as tc:
                tc.addFunction(MovieEn.setInterval, current_timing, duration)
                tc.addTask("TaskMoviePlay", Movie=Movie, Wait=True)
                tc.addFunction(MovieEn.setInterval, 0, duration - 1)
                tc.addFunction(MovieEn.setTiming, duration)
                tc.addFunction(MovieEn.setInterval, 0, set_time)
                tc.addTask("TaskMoviePlay", Movie=Movie, Wait=True)
                tc.addFunction(MovieEn.setInterval, 0, duration - 1)
                tc.addFunction(MovieEn.setTiming, set_time)
                tc.addNotify(Notificator.onEnigmaAction, False)
                pass
        else:
            with TaskManager.createTaskChain(Name=RotateMiniSystem.TaskName) as tc:
                tc.addFunction(MovieEn.setInterval, current_timing, set_time)
                tc.addTask("TaskMoviePlay", Movie=Movie, Wait=True)
                tc.addFunction(MovieEn.setInterval, 0, duration - 1)
                tc.addFunction(MovieEn.setTiming, set_time)
                tc.addNotify(Notificator.onEnigmaAction, False)
                pass
            pass
        pass

    def RotateBehavior(self, Circle):
        if TaskManager.existTaskChain(RotateMiniSystem.TaskName):
            return
            pass

        if Circle in self.circles["ConstBehavior"]:
            frames_rotate = self.constStep(Circle)
        else:
            frames_rotate = self.situatedStep(Circle)

        self.Rotate(Circle, frames_rotate)
        pass

    def constStep(self, Circle):
        slots = Circle.getCountSlots()
        frames = 360 / slots
        return frames
        pass

    def situatedStep(self, Circle):
        guides_global = self.getGuides("ConstBehavior")
        degree_diff = []
        for guide in guides_global:
            diff = Circle.calcGuidesToStep(guide)

            degree_diff.append(diff)
        minimal = min(degree_diff, key=lambda x: x if x > 0 else 360)
        ind = degree_diff.index(minimal)
        self.place_guide = guides_global[ind]
        return minimal
        pass

    def getGuides(self, typeBehavior):
        guides = []
        for circle in self.circles[typeBehavior]:
            guides += circle.getSlotGuides()
        return guides
        pass
