from Foundation.TaskManager import TaskManager


class Target(object):
    def __init__(self, movie_obj, movie_carrier, enigmaObject):
        self.movie = movie_obj
        self.passed = False
        self.movie_carrier = movie_carrier
        self.hited = False
        self.movie.setEnable(False)
        self.inactive = True
        self.enigmaObject = enigmaObject
        pass

    def chase(self):
        self.movie.setEnable(True)
        self.inactive = False
        self.movie_en = self.movie.getEntity()
        movie_carrier_en = self.movie_carrier.getEntity()
        self.slotNode = self.movie_en.getMovieSlot("position")
        carriersNode = movie_carrier_en.getMovieSlot("hit")
        carriersNode.addChild(self.movie_en)
        self.movie_carrier.setEnable(True)
        self.movie_en.setFirstFrame()
        movie_carrier_en.setFirstFrame()
        movie_carrier_en.setTiming(1)

        enigmaEntity = self.enigmaObject.getEntity()

        with TaskManager.createTaskChain() as tc:
            with tc.addRaceTask(2) as (tc_play, tc_hited):
                tc_play.addDelay(0.5 * 1000)  # speed fix
                tc_play.addTask("TaskMoviePlay", Movie=self.movie_carrier)

                tc_hited.addListener(Notificator.onChased, Filter=self.filter)
                tc_hited.addTask("TaskMoviePlay", Movie=self.movie)
                tc_hited.addFunction(enigmaEntity.checkComplete)
                pass

            tc.addFunction(self.update_passed)
            tc.addFunction(self.cleanUpMovie)
            tc.addNotify(Notificator.onChase, self)
            pass
        pass

    def filter(self, target):
        if target == self:
            self.hited = True
            return True
            pass
        else:
            return False
            pass
        pass

    def cleanUpMovie(self, *skip):
        if not self.inactive:
            self.movie_en.removeFromParent()
            self.passed = True
            pass
        pass

    def update_passed(self):
        self.passed = True
        pass

    def get_passed(self, *args):
        return self.passed
        pass

    def getCurrentPosition(self):
        if self.hited:
            return
        vec3 = self.slotNode.getWorldPosition()
        return vec3[0]
