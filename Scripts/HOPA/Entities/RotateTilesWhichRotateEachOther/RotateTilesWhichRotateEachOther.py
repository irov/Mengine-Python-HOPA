from math import radians, degrees

from Event import Event
from Foundation.TaskManager import TaskManager
from HOPA.RotateTilesWhichRotateEachOtherManager import RotateTilesWhichRotateEachOtherManager
from Holder import Holder

Enigma = Mengine.importEntity("Enigma")

class Tile(object):
    def __init__(self, params, obj_generator, tiles_dict_ref, root_node):
        self.params = params

        self.tiles_dict_ref = tiles_dict_ref

        tiles_dict_ref[params.id] = self  # save self ref to tiles dict in enigma

        self.movie = obj_generator(str(self.params.id) + self.params.movie_proto, self.params.movie_proto, Enable=True, Interactive=True)

        self.node = self.movie.entity.node

        root_node.addChild(self.node)
        self.node.setLocalPosition(self.params.pos)
        self.node.setAngle(radians(self.params.start_rot))

        self.is_end_rotation = False

    def __setEndRotationValue(self):
        current = round(degrees(self.node.getAngle())) % 360.0
        end = self.params.finish_rot % 360.0

        self.is_end_rotation = current == end

    def scopeRotate(self, source, angle=None, time=None):
        if angle is None:
            angle = self.params.rot_step

        if time is None:
            time = self.params.rot_time

        source.addFunction(self.movie.setPlay, True)  # play anim and sound

        source.addTask("TaskNodeRotateTo", Node=self.node, To=radians(angle), Additive=True, Time=time)

        source.addFunction(self.movie.setPlay, False)  # stop play anim and sound

        source.addFunction(self.movie.setLastFrame, False)  # reset to first frame

        source.addFunction(self.__setEndRotationValue)

    def scopeRotateDependentTiles(self, source):
        for tile_id, angle in self.params.tiles_to_rotate:
            tile = self.tiles_dict_ref[tile_id]

            source.addScope(tile.scopeRotate, angle)

    def destroy(self):
        self.movie.entity.node.removeFromParent()
        self.movie.onFinalize()
        self.movie.onDestroy()

class RotateTilesWhichRotateEachOther(Enigma):

    def __init__(self):
        super(RotateTilesWhichRotateEachOther, self).__init__()
        self.params = None

        self.tiles = {}

        self.__tc_main = None

        self.is_reseting = False

        self.complete_event = Event('EnigmaComplete')

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def _loadParams(self):
        self.params = RotateTilesWhichRotateEachOtherManager.getParam(self.EnigmaName)

    def __setup(self):
        for tile_param in self.params.tiles:
            Tile(tile_param, self.object.generateObjectUnique, self.tiles, self.node)

    def __cleanUp(self):
        if self.__tc_main is not None:
            self.__tc_main.cancel()
            self.__tc_main = None

        for tile in self.tiles.values():
            tile.destroy()

        self.tiles = {}

    def checkComplete(self):
        for tile in self.tiles.values():
            if not tile.is_end_rotation:
                break

        else:  # this is correct, google it
            self.complete_event()

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def __runTaskChain(self):
        self.__tc_main = TaskManager.createTaskChain()
        with self.__tc_main as tc:
            tile_holder = Holder()

            def scopeRotate(source):
                source.addScope(tile_holder.value.scopeRotate)
                source.addScope(tile_holder.value.scopeRotateDependentTiles)

            ''' Enigma Main Gameplay Loop '''
            with tc.addRepeatTask() as (repeat, until):
                ''' Get Current Tile '''
                for (tile_id, tile), race in repeat.addRaceTaskList(self.tiles.iteritems()):
                    race.addEvent(tile.movie.onMovieSocketButtonEvent)
                    race.addFunction(tile_holder.set, tile)

                ''' Rotate Current Tile '''
                repeat.addScope(scopeRotate)

                ''' Check if MG Complete '''
                repeat.addFunction(self.checkComplete)

                ''' Brake Main Loop On Interrupt Gameplay Events '''
                until.addEvent(self.complete_event)

            ''' Handle On Interrupt Gameplay Events '''
            tc.addFunction(self.enigmaComplete)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(RotateTilesWhichRotateEachOther, self)._onPreparation()
        self._loadParams()
        self.__setup()

    def _onDeactivate(self):
        super(RotateTilesWhichRotateEachOther, self)._onDeactivate()
        self.__cleanUp()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _playEnigma(self):
        self.__runTaskChain()

    def _restoreEnigma(self):
        self.__runTaskChain()

    def _resetEnigma(self):
        if self.is_reseting:
            return

        self.is_reseting = True

        if self.__tc_main is not None:
            self.__tc_main.cancel()
            self.__tc_main = None

        def setNotReseting():
            self.is_reseting = False

        with TaskManager.createTaskChain() as tc:
            for tile, parallel in tc.addParallelTaskList(self.tiles.values()):
                rot_value = tile.params.start_rot % 360.0 - round(degrees(tile.node.getAngle())) % 360.0

                parallel.addScope(tile.scopeRotate, rot_value)

            tc.addFunction(self.__runTaskChain)

            tc.addFunction(setNotReseting)

    def _skipEnigmaScope(self, skip_source):
        if self.__tc_main is not None:
            self.__tc_main.cancel()
            self.__tc_main = None

        for tile in self.tiles.values():
            rot_value = tile.params.finish_rot % 360.0 - round(degrees(tile.node.getAngle())) % 360.0

            skip_source.addScope(tile.scopeRotate, rot_value)