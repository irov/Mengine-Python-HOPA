class Twist(object):
    def __init__(self, MovieList, MovieList_Rev, FinalStateInt, IndicatorMovie):
        self.Movies = MovieList
        self.Movies_Revert = MovieList_Rev
        self.FinalState = FinalStateInt - 1 if FinalStateInt > 0 else 0
        if (FinalStateInt == -1):
            self.FinalState = -1
            pass
        self.Depends = {}
        self.IndicatorMovie = IndicatorMovie
        #        self.DependRelation = DependRelationInt
        self.CurentState = 0
        pass

    def __repr__(self):
        return "CurrentState->" + str(self.CurentState)
        pass

    def next(self):
        current = self.Movies[self.CurentState]

        if self.CurentState >= len(self.Movies) - 1:
            self.CurentState = 0
        else:
            self.CurentState += 1
        self.enabler()
        return current
        pass

    def getNextMovie(self):
        check = self.CurentState + 1
        if check >= len(self.Movies):
            check = 0
        nextMovie = self.Movies[check]
        return nextMovie
        pass

    def prev(self):
        current = self.Movies_Revert[self.CurentState]

        if self.CurentState <= 0:
            self.CurentState = len(self.Movies_Revert) - 1
        else:
            self.CurentState -= 1
        self.enabler()
        return current
        pass

    def getDepends(self):
        MovieCollection = []
        for twist in self.Depends:
            MovieQueue = []
            roll_T = self.Depends[twist]
            if (roll_T > 0):
                for roll in range(roll_T):
                    MovieQueue.append(twist.next())
            elif (roll_T < 0):
                roll_T = -roll_T
                for roll in range(roll_T):
                    MovieQueue.append(twist.prev())
                pass
            MovieCollection.append(MovieQueue)
        return MovieCollection
        pass

    def setState(self, stateInt):
        self.CurentState = stateInt
        pass

    def getFinalState(self):
        return self.FinalState
        pass

    def getState(self):
        return self.CurentState
        pass

    def resetState(self):
        self.setState(0)

        pass

    def resetMovies(self):
        state = self.CurentState
        self.resetState()
        self.enabler()
        return self.Movies[state:]

    def setDepends(self, TwistObj, rollTimes):
        if self is TwistObj:  # no depends
            return False
        self.Depends[TwistObj] = rollTimes
        pass

    def getFirstMovie(self):
        return self.Movies[0]

    def inFinalState(self):
        if (self.FinalState == -1):
            return True
            pass

        if self.CurentState == self.FinalState:
            return True
        return False
        pass

    def getCurentMovie(self):
        return self.Movies[self.CurentState]
        pass

    def skipMovies(self):
        mustPlay = []
        if self.CurentState > self.FinalState:
            mustPlay = self.Movies[self.CurentState:] + self.Movies[:self.FinalState]

        else:
            mustPlay = self.Movies[self.CurentState:self.FinalState]
        self.CurentState = self.FinalState
        if mustPlay:
            self.enabler()
        return mustPlay

    def getIndicator(self):
        return self.IndicatorMovie

    def enabler(self, state=None):
        #        state = self.CurentState-1
        for movies in self.Movies:
            movies.setEnable(False)
            pass

        for movies in self.Movies_Revert:
            movies.setEnable(False)
            pass
        #        self.Movies[state].setEnable(True)
        pass

    pass


class MultiFinalTwist(Twist):
    # for multiply final state finite state machine

    def __init__(self, MovieList, MovieList_Rev, FinalStateList, IndicatorMovie, SkipBranchInt=0):
        super(MultiFinalTwist, self).__init__(MovieList, MovieList_Rev, FinalStateList[0], IndicatorMovie)
        self.FinalStateList = [state - 1 for state in FinalStateList if state > 0]
        self.SkipBranch = SkipBranchInt
        pass

    def skipMovies(self):
        mustPlay = []
        final_state = self.FinalStateList[self.SkipBranch]
        if self.CurentState > final_state:
            mustPlay = self.Movies[self.CurentState:] + self.Movies[:final_state]

        else:
            mustPlay = self.Movies[self.CurentState:final_state]
        self.CurentState = final_state
        if mustPlay:
            self.enabler()
        return mustPlay

    def inFinalState(self):
        if self.CurentState in self.FinalStateList:
            return True
            pass
        else:
            return False
            pass
        pass
