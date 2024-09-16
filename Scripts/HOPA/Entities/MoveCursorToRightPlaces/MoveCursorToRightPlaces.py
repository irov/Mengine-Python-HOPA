from Foundation.ArrowManager import ArrowManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.MoveCursorToRightPlacesManager import MoveCursorToRightPlacesManager


Enigma = Mengine.importEntity("Enigma")


class MoveCursorToRightPlaces(Enigma):
    class Place(object):
        def __init__(self, place_id, movie_place, movie_chip):
            self.place_id = place_id
            self.movie_place = movie_place
            self.movie_chip = movie_chip

        def setEnableChip(self, flag):
            self.movie_chip.setEnable(flag)

    def __init__(self):
        super(MoveCursorToRightPlaces, self).__init__()
        self.tc = None
        self.param = None
        self.places = {}

        self.movie_light = None
        self.movie_light_en = None
        self.movie_light_node_parent = None

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(MoveCursorToRightPlaces, self)._onPreparation()
        self._loadParam()
        self._setup()

    def _onActivate(self):
        super(MoveCursorToRightPlaces, self)._onActivate()

    def _onDeactivate(self):
        super(MoveCursorToRightPlaces, self)._onDeactivate()
        self._cleanUp()

    # ==================================================================================================================

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self._runTaskChain()

    def _restoreEnigma(self):
        self._runTaskChain()

    def _resetEnigma(self):
        self._cleanUp()
        self._loadParam()
        self._setup()
        self._runTaskChain()

    def _skipEnigma(self):
        for (_, place) in self.places.iteritems():
            place.movie_place.setEnable(False)

    # ==================================================================================================================
    def _loadParam(self):
        self.param = MoveCursorToRightPlacesManager.getParam(self.EnigmaName)

    def _setup(self):
        group_name = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        group = GroupManager.getGroup(group_name)

        if group.hasObject(self.param.AttachOnCursor):
            self.movie_light = group.getObject(self.param.AttachOnCursor)
            self.movie_light_en = self.movie_light.getEntityNode()
            self.movie_light_node_parent = self.movie_light_en.getParent()

        for (place_id, movie_name) in self.param.Places.iteritems():
            movie_place = group.getObject(movie_name)

            movie_chip = None
            movie_place_type = movie_place.getType()
            if movie_place_type is 'ObjectMovie':
                movie_chip = group.getObject('Movie_chip_{}'.format(place_id))

            elif movie_place_type is 'ObjectMovie2':
                movie_chip = group.getObject('Movie2_chip_{}'.format(place_id))

            else:
                Trace.log("Group", 0, "Group %s can't find chip with ID=%s and type=%s. Chip and Place should be same type!" % (group_name, place_id, movie_place_type))

            movie_place.setEnable(True)
            if movie_chip is not None:
                movie_chip.setEnable(False)
            place = MoveCursorToRightPlaces.Place(place_id, movie_place, movie_chip)
            self.places[place_id] = place

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=False)
        with self.tc as tc:
            tc.addFunction(self.attachMovieLight, True)
            tc.addScope(self.socketEnter)
            tc.addFunction(self.complete)

    def attachMovieLight(self, attach):
        if self.movie_light_node_parent is None:
            return

        if self.movie_light.getLoop():
            self.movie_light.setPlay(True)

        if attach:
            arrow = Mengine.getArrow()
            arrow_node = arrow.getNode()
            arrow_node.addChild(self.movie_light_en)
        else:
            self.movie_light_node_parent.addChild(self.movie_light_en)

    def socketEnter(self, source):
        for (place_id, place), parallel in source.addParallelTaskList(self.places.iteritems()):
            movie_chip_type = place.movie_chip.getType()

            if movie_chip_type is 'ObjectMovie':
                parallel.addTask('TaskMovieSocketEnter', SocketName='place', Movie=place.movie_place, isMouseEnter=False)
                parallel.addFunction(place.setEnableChip, True)
                parallel.addTask('TaskMoviePlay', Movie=place.movie_chip, Wait=False)

            elif movie_chip_type is 'ObjectMovie2':
                parallel.addTask('TaskMovie2SocketEnter', SocketName='place', Movie2=place.movie_place, isMouseEnter=False)
                parallel.addFunction(place.setEnableChip, True)
                parallel.addTask('TaskMovie2Play', Movie2=place.movie_chip, Wait=False)

            else:
                Trace.log("Group", 1, "Movie with ID=%s has wrong type=%s. Chip and Place should be same type!" % (place_id, movie_chip_type))

    def complete(self):
        for (_, place) in self.places.iteritems():
            place.movie_place.setEnable(False)

        self.enigmaComplete()

    def _cleanUp(self):
        self.param = None

        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for place in self.places.values():
            place.movie_chip.setLastFrame(True)
        self.places = {}

        self.attachMovieLight(False)
