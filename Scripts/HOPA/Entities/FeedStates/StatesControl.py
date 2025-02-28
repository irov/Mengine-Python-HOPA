from Foundation.TaskManager import TaskManager


class StatesControl:
    predators = []
    foods = {}
    bound = []
    play_object = None

    class Predator(object):
        def __init__(self, movies):
            movie_idle, movie_eat, movie_away = movies
            self.movies = movies
            self.idle = movie_idle
            self.away = movie_away
            self.eat = movie_eat
            self.current_state = self.idle
            self.behavior_state = None
            self.__active = True
            self.setIdlle()
            pass

        def deactivate(self):
            self.__active = False
            pass

        def isactive(self):
            return self.__active

        def is_away(self):
            return self.current_state == self.away
            pass

        def reset(self):
            self.__active = True
            self.hideStates()
            self.setIdlle()
            pass

        def setIdlle(self):
            self.__disable_rest(self.idle)
            self.current_state = self.idle
            self.idle.setLoop(True)
            self.idle.setPlay(True)
            return self.current_state
            pass

        def setAway(self):
            self.__disable_rest(self.away)
            self.current_state = self.away
            self.away.setPlay(True)
            return self.current_state
            pass

        def hideStates(self):
            for mov in self.movies:
                mov.setEnable(False)
                mov.setPlay(False)
                pass
            pass

        def setBehavior(self, behavior_movie):
            self.behavior_state = behavior_movie
            pass

        def __disable_rest(self, movie):
            for mov in self.movies:
                if mov != movie:
                    mov.setEnable(False)
                    mov.setPlay(False)
                else:
                    mov.setEnable(True)
                    mov.setPlay(False)
                    pass
                pass
            pass

    class Feed(object):
        def __init__(self):
            self.limit = 2
            self.rest = 2
            self.correct_behavior = None  # Movie
            self.wrong_behavior = None
            self.wrong_subject = None
            self.correct_subject = None
            pass

        def setBranches(self, correct, wrong):
            self.correct_behavior = correct
            self.correct_behavior.setEnable(False)
            self.wrong_behavior = wrong
            self.wrong_behavior.setEnable(False)
            pass

        def set_associate(self, correct_subject, wrong_subject):  # predators objects
            self.correct_subject = correct_subject
            self.wrong_subject = wrong_subject

        def iterateInternalState(self, cb):
            if self.rest == 0:
                return

            if self.wrong_subject is not None and self.wrong_subject.isactive():
                self.rest -= 1
                self.wrong_subject.setBehavior(self.wrong_behavior)
                self.wrong_subject.hideStates()
                with TaskManager.createTaskChain() as tc:
                    tc.addEnable(self.wrong_behavior)
                    tc.addTask("TaskMoviePlay", Movie=self.wrong_behavior, Wait=True)
                    tc.addDisable(self.wrong_behavior)
                    tc.addFunction(self.wrong_subject.setIdlle)
                    tc.addFunction(cb)
                    tc.addFunction(StatesControl.isComplete)
                for socket_name, feeder in StatesControl.foods.iteritems():
                    if self == feeder:
                        return socket_name
                        pass
                    pass

            elif not self.correct_subject.isactive():
                pass
            else:
                self.correct_subject.deactivate()
                self.correct_subject.setBehavior(self.correct_behavior)
                self.correct_subject.hideStates()
                with TaskManager.createTaskChain() as tc:
                    tc.addEnable(self.correct_behavior)
                    tc.addTask("TaskMoviePlay", Movie=self.correct_behavior, Wait=True)
                    tc.addDisable(self.correct_behavior)
                    tc.addFunction(cb)
                    tc.addFunction(StatesControl.isComplete)
                #                    tc.addTask("TaskFunction", Fn = self.correct_subject.setAway)
                for socket_name, feeder in StatesControl.foods.iteritems():
                    if self == feeder:
                        return socket_name
                        pass
                    pass
                pass
            pass

        def set_limit(self, limit_num):
            if limit_num is None:
                limit_num = -1
            self.limit = limit_num
            self.rest = limit_num
            pass

        def reset_limit(self):
            self.rest = self.limit

    @staticmethod
    def loadControl(movieList, reference, sockets, limit):
        StatesControl.bound = reference

        for i, category in enumerate(movieList):
            feed = StatesControl.Feed()
            #            print sockets[i]
            predator = StatesControl.Predator(category[:-2])
            feed.setBranches(category[-1], category[-2])
            StatesControl.predators.append(predator)
            StatesControl.foods[sockets[i]] = feed
            feed.set_limit(limit[i])
            pass
        # asociate
        for i, relate in enumerate(StatesControl.bound):
            corect = StatesControl.predators[i]
            wrong = StatesControl.predators[relate]
            if wrong == corect:
                wrong = None
            StatesControl.foods[sockets[i]].set_associate(corect, wrong)
            pass
        pass

    @staticmethod
    def getPredators():
        return StatesControl.predators
        pass

    @staticmethod
    def getState(socket):
        return StatesControl.foods[socket]
        pass

    @staticmethod
    def isComplete():
        for predator in StatesControl.predators:
            if predator.isactive():
                return
        StatesControl.skip(True)

    @staticmethod
    def skipStates():
        with TaskManager.createTaskChain(Cb=StatesControl.skip) as tc:
            for feeder in StatesControl.foods.values():
                movie = feeder.correct_behavior
                tc.addFunction(feeder.correct_subject.hideStates)
                tc.addEnable(movie)
                tc.addTask("TaskMoviePlay", Movie=movie, Wait=True)
                tc.addDisable(movie)

    @staticmethod
    def resetStates():
        for predator in StatesControl.predators:
            predator.reset()

        for food in StatesControl.foods.values():
            food.reset_limit()

    @staticmethod
    def skip(*isSkip):
        if StatesControl.play_object is None:
            Trace.log("Manager", 0, "StatesControl.play_object is None")
            return
        StatesControl.play_object.completion()

    @staticmethod
    def clear_it():
        StatesControl.predators = []
        StatesControl.foods = {}
        StatesControl.bound = []
