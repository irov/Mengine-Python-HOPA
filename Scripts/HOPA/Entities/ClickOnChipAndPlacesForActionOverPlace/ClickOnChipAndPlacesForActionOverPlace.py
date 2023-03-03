from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.ClickOnChipAndPlacesForActionOverPlaceManager import ClickOnChipAndPlacesForActionOverPlaceManager
from HOPA.EnigmaManager import EnigmaManager


Enigma = Mengine.importEntity("Enigma")


class ClickOnChipAndPlacesForActionOverPlace(Enigma):
    class Place(object):
        def __init__(self, id, MovieGreen, MovieBlue, MovieYellow, MovieSilver, socketName):
            self.id = id
            self.type = 'Place'
            self.MovieGreen = MovieGreen
            self.MovieBlue = MovieBlue
            self.MovieYellow = MovieYellow
            self.MovieSilver = MovieSilver
            self.socketName = socketName
            self.parent = None

        def findCorrectMovie(self, chip):
            if chip is None:
                return self.MovieSilver
            elif chip.id == 1:
                return self.MovieGreen
            elif chip.id == 2:
                return self.MovieBlue
            elif chip.id == 3:
                return self.MovieYellow

        def getAllMovies(self):
            return self.MovieGreen, self.MovieBlue, self.MovieYellow, self.MovieSilver

        def setParent(self, source, chip):
            # Here must be Sound Slot

            acttiveMovie = self.findCorrectMovie(self.parent)
            movie = self.findCorrectMovie(chip)
            self.parent = chip
            # if movie == acttiveMovie:
            #     source.addPrint("setParent movie == acttivateMovie so return")
            #     return
            with source.addParallelTask(2) as (parallel_1, parallel_2):
                if movie is not None:
                    parallel_1.addFunction(movie[0].setEnable, True)
                    parallel_1.addScope(self.changeAlpha, movie[0].getEntityNode(), 1.0, 0.0)
                if acttiveMovie is not None:
                    parallel_2.addScope(self.changeAlpha, acttiveMovie[1].getEntityNode(), 0.0, 1.0)
                    parallel_2.addFunction(acttiveMovie[1].setEnable, False)

        def changeAlpha(self, source, node, To, From):
            changeAlphaTime = DefaultManager.getDefaultFloat('ClickOnChipAndPlacesForActionOverPlace_ChangeAlphaTime', 500)
            source.addTask("TaskNodeAlphaTo", Node=node, From=From, To=To, Time=changeAlphaTime)

    class Chip(object):
        def __init__(self, id, movie):
            self.id = id
            self.type = 'Chip'
            self.movie = movie
            self.node = movie.getEntityNode()

        def scopeClickDown(self, source):
            if "Movie2" in self.movie.getName():
                source.addTask("TaskMovie2SocketClick", Movie2=self.movie, SocketName='chip', isDown=True)
            else:
                source.addTask("TaskMovieSocketClick", Movie=self.movie, SocketName='chip', isDown=True)
            source.addFunction(self.movie.delParam, 'DisableLayers', 'Sprite_Chip_Scale')
            source.addFunction(self.movie.appendParam, 'DisableLayers', 'Sprite_Chip')

        def scopeClickUp(self, source):
            source.addTask("TaskMouseButtonClick", isDown=False)
            source.addFunction(self.movie.delParam, 'DisableLayers', 'Sprite_Chip')
            source.addFunction(self.movie.appendParam, 'DisableLayers', 'Sprite_Chip_Scale')

    def __init__(self):
        super(ClickOnChipAndPlacesForActionOverPlace, self).__init__()
        self.tc = None
        self.param = None
        self.BG = None
        self.chips = {}
        self.places = {}
        self.currentActiveChip = None
        self.selectedPlace = None

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(ClickOnChipAndPlacesForActionOverPlace, self)._onPreparation()

    def _onActivate(self):
        super(ClickOnChipAndPlacesForActionOverPlace, self)._onActivate()

    def _onDeactivate(self):
        super(ClickOnChipAndPlacesForActionOverPlace, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._loadParam()
        self._setup()
        self._runTaskChain()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        with TaskManager.createTaskChain(Name='Reset') as reset_tc:
            with reset_tc.addParallelTask(2) as (parallel_1, parallel_2):
                for (placeID, place), parallel in parallel_1.addParallelTaskList(self.places.iteritems()):
                    if place.parent is not None:
                        parallel.addScope(place.changeAlpha, place.findCorrectMovie(place.parent)[0].getEntityNode(), 0.0, 1.0)
                    place.parent = None

                if self.selectedPlace is not None:
                    # with parallel_2.addIfTask(lambda: self.selectedPlace is None) as (true, false):
                    parallel_2.addScope(self.selectedPlace.changeAlpha,
                                        self.selectedPlace.findCorrectMovie(None)[1].getEntityNode(), 0.0, 1.0)
                    parallel_2.addFunction(self.setSelectedPlace, None)

    def _skipEnigmaScope(self, source):
        SkipPlaces = self.param.Skip
        source.addFunction(self.setSelectedPlace, None)

        def cleanPlate(place):
            for moviesList in place.getAllMovies():
                for movie in moviesList:
                    if movie is not None:
                        movie.setEnable(False)

        for (placeID, place), parallel in source.addParallelTaskList(self.places.iteritems()):
            parallel.addFunction(cleanPlate, place)
            parallel.addFunction(place.findCorrectMovie(self.chips[SkipPlaces[placeID]])[0].setEnable, True)
            parallel.addScope(place.changeAlpha,
                              place.findCorrectMovie(self.chips[SkipPlaces[placeID]])[0].getEntityNode(), 1.0, 0.0)
            place.parent = self.chips[SkipPlaces[placeID]]

        source.addScope(self.complete)

    # ==================================================================================================================

    def _loadParam(self):
        self.param = ClickOnChipAndPlacesForActionOverPlaceManager.getParam(self.EnigmaName)

    def _setup(self):
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        Group = GroupManager.getGroup(GroupName)

        if Group.hasObject('Movie2_Cap_Idle') is True:
            self.BG = Group.getObject('Movie2_Cap_Idle')
        elif Group.hasObject('Movie_Cap_Idle') is True:
            self.BG = Group.getObject('Movie_Cap_Idle')
        else:
            Trace.log("Entity", 0, "ClickOnChipAndPlacesForActionOverPlace: Scene hasn't BG movie 'Movie2_Cap_Idle'")
            return

        def getMovie(movieName):
            movie = None
            movieWin = None
            if movieName[0] is not None:
                movie = Group.getObject(movieName[0])
                movie.setEnable(False)

            if movieName[1] is not None:
                movieWin = Group.getObject(movieName[1])
                movieWin.setEnable(False)
            return movie, movieWin

        for (placeID, MoviesName) in self.param.Places.iteritems():
            MovieGreen, MovieBlue, MovieYellow, MovieSilver = \
                getMovie(MoviesName[0]), getMovie(MoviesName[1]), getMovie(MoviesName[2]), getMovie(MoviesName[3])
            socketName = 'place_{}'.format(placeID)
            place = ClickOnChipAndPlacesForActionOverPlace.Place(placeID, MovieGreen, MovieBlue, MovieYellow, MovieSilver, socketName)
            self.places[placeID] = place

        for (ChipID, MovieName) in self.param.Chips.iteritems():
            movie = Group.getObject(MovieName)
            movie.appendParam('DisableLayers', 'Sprite_Chip_Scale')
            chip = ClickOnChipAndPlacesForActionOverPlace.Chip(ChipID, movie)
            self.chips[ChipID] = chip

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addScope(self._resolveClick)

    def _resolveClick(self, source):
        ClickObject = Holder()

        def holder_scopeClick(source, holder):
            ClickObject = holder.get()
            if ClickObject.type == 'Chip':
                source.addScope(self.resolveClickOnChip, ClickObject)
            elif ClickObject.type == 'Place':
                source.addScope(self.resolveClickOnPlace, ClickObject)

        with source.addRaceTask(2) as (clickOnPlace, clickOnChip):
            for place, race in clickOnPlace.addRaceTaskList(self.places.values()):
                if "Movie2" in self.BG.getName():
                    race.addTask('TaskMovie2SocketClick', SocketName=place.socketName, Movie2=self.BG)
                else:
                    race.addTask('TaskMovieSocketClick', SocketName=place.socketName, Movie=self.BG)
                race.addFunction(ClickObject.set, place)

            for chip, race in clickOnChip.addRaceTaskList(self.chips.values()):
                race.addScope(chip.scopeClickDown)
                race.addNotify(Notificator.onSoundEffectOnObject, self.object,
                               'ClickOnChipAndPlacesForActionOverPlace_ClickOnChipDown')
                race.addScope(chip.scopeClickUp)
                race.addNotify(Notificator.onSoundEffectOnObject, self.object,
                               'ClickOnChipAndPlacesForActionOverPlace_ClickOnChipUp')
                race.addFunction(ClickObject.set, chip)

        source.addScope(holder_scopeClick, ClickObject)
        source.addScope(self.checkWin)

    def setSelectedPlace(self, place):
        self.selectedPlace = place

    def resolveClickOnChip(self, source, chip):
        if self.selectedPlace is not None:
            with source.addParallelTask(2) as (paintPlace, soundEffect):
                paintPlace.addScope(self.selectedPlace.setParent, chip)
                paintPlace.addFunction(self.setSelectedPlace, None)
                soundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object,
                                      'ClickOnChipAndPlacesForActionOverPlace_PaintEffect')

    def resolveClickOnPlace(self, source, place):
        source.addNotify(Notificator.onSoundEffectOnObject, self.object,
                         'ClickOnChipAndPlacesForActionOverPlace_ClickOnPlace')

        if self.selectedPlace is None:
            source.addScope(self.EnableSelect, place)
            source.addFunction(self.setSelectedPlace, place)
        elif self.selectedPlace is not None:
            if self.selectedPlace == place:
                source.addScope(self.DisableSelect, place)
                source.addFunction(self.setSelectedPlace, None)
            elif self.selectedPlace != place:
                with source.addParallelTask(2) as (parallel_1, parallel_2):
                    parallel_1.addScope(self.EnableSelect, place)
                    parallel_2.addScope(self.DisableSelect, self.selectedPlace)
                source.addFunction(self.setSelectedPlace, place)

    def EnableSelect(self, source, place):
        if place.parent is not None:
            with source.addParallelTask(2) as (parallel_1, parallel_2):
                parallel_1.addFunction(place.findCorrectMovie(place.parent)[1].setEnable, True)
                parallel_1.addScope(place.changeAlpha, place.findCorrectMovie(place.parent)[1].getEntityNode(), 1.0, 0.0)
                parallel_2.addScope(place.changeAlpha, place.findCorrectMovie(place.parent)[0].getEntityNode(), 0.0, 1.0)
                parallel_2.addFunction(place.findCorrectMovie(place.parent)[0].setEnable, False)
        elif place.parent is None:
            source.addFunction(place.findCorrectMovie(place.parent)[1].setEnable, True)
            source.addScope(place.changeAlpha, place.findCorrectMovie(place.parent)[1].getEntityNode(), 1.0, 0.0)

    def DisableSelect(self, source, place):
        if place.parent is not None:
            with source.addParallelTask(2) as (parallel_1, parallel_2):
                parallel_1.addFunction(place.findCorrectMovie(place.parent)[0].setEnable, True)
                parallel_1.addScope(place.changeAlpha, place.findCorrectMovie(place.parent)[0].getEntityNode(), 1.0, 0.0)
                parallel_2.addScope(place.changeAlpha, place.findCorrectMovie(place.parent)[1].getEntityNode(), 0.0, 1.0)
                parallel_2.addFunction(place.findCorrectMovie(place.parent)[1].setEnable, False)
        elif place.parent is None:
            source.addScope(place.changeAlpha, place.findCorrectMovie(place.parent)[1].getEntityNode(), 0.0, 1.0)
            source.addFunction(place.findCorrectMovie(place.parent)[1].setEnable, False)

    def checkWin(self, source):
        flag = False
        for (_, place) in self.places.iteritems():
            if place.parent is None:
                break
            NeighboringPlaces = self.param.NeighboringPlaces[place.id]
            for NeighboringPlaceID in NeighboringPlaces:
                if self.places[NeighboringPlaceID].parent == place.parent:
                    flag = True
                    break
            if flag is True:
                break
        else:
            source.addScope(self.complete)

    def complete(self, source):
        for (_, place), parallel in source.addParallelTaskList(self.places.iteritems()):
            with parallel.addParallelTask(2) as (parallel_1, parallel_2):
                parallel_1.addScope(place.changeAlpha, place.findCorrectMovie(place.parent)[0].getEntityNode(), 1.0, 0.0)
                parallel_1.addFunction(place.findCorrectMovie(place.parent)[0].setEnable, False)
                parallel_2.addFunction(place.findCorrectMovie(place.parent)[1].setEnable, True)
                parallel_2.addScope(place.changeAlpha, place.findCorrectMovie(place.parent)[1].getEntityNode(), 0.0, 1.0)

        self.enigmaComplete()

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None
        self.param = None
        self.BG = None
        self.currentActiveChip = None
        self.chips = {}
        self.places = {}
