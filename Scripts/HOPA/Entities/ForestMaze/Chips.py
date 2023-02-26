# coding=utf-8
import math
from abc import ABCMeta, abstractmethod

class Chip:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, chip_id, place_id, movie_chip):
        self.chip_id = chip_id
        self.place_id = place_id
        self.movie_chip = movie_chip

    @abstractmethod
    def scopeClick(self, source):
        source.addTask('TaskMovie2SocketClick', SocketName='socket', Movie2=self.movie_chip)

    @abstractmethod
    def cleanUp(self):
        self.movie_chip.onDestroy()

    def getPlaceID(self):
        return self.place_id

    def runChipParamsUnittests(self):
        assert self.chip_id is not None, "Error chip_id can not be {}".format(self.chip_id)
        assert self.place_id is not None, "Error place_id can not be {}".format(self.place_id)
        assert self.movie_chip is not None, "Error movie_chip can not be {}".format(self.movie_chip)

    def createSupportMovies(self, enigma_obj, params):
        pass

class PlayerChip(Chip):
    def __init__(self, chip_id, place_id, movie_chip, move_time=1000):
        super(PlayerChip, self).__init__(chip_id, place_id, movie_chip)
        self.disableGlow()
        self.run_movie = None
        self.move_time = move_time

    def runChipParamsUnittests(self):
        super(PlayerChip, self).runChipParamsUnittests()

        assert self.run_movie is not None, "Error run_movie can not be {}".format(self.run_movie)
        assert isinstance(self.move_time, (int, float)), "Error move_time={}. Must be number, not {}".format(self.move_time, type(self.move_time))

    def createSupportMovies(self, enigma_obj, place):
        support_movie_id = "{}_SupportMovie_RunMovie".format(self.chip_id)
        if place.other_params is not None and enigma_obj.object.hasPrototype(place.other_params[0]):
            self.run_movie = enigma_obj.object.tryGenerateObjectUnique(support_movie_id, place.other_params[0], Enable=False)
        else:
            self.run_movie = enigma_obj.object.tryGenerateObjectUnique(support_movie_id, place.movie_prototype_name, Enable=False)

            if _DEVELOPMENT is True:
                Trace.log("Object", 1, "Not found run_movie name for player chip {}."
                                       "\nMb you forgot add to {}_Places.xlsx in OthersParams or add this Movie in PSD?"
                                       "\nNow using movie {} for create run_movie name for player chip".format(self.chip_id, enigma_obj.EnigmaName, place.movie_prototype_name))

        enigma_obj_en = enigma_obj.object.getEntityNode()
        enigma_obj_en.addChild(self.run_movie.getEntityNode())

    def scopeClick(self, source):
        super(PlayerChip, self).scopeClick(source)

    def cleanUp(self):
        super(PlayerChip, self).cleanUp()

    def enableGlow(self):
        if 'glow' not in self.movie_chip.getParam('DisableLayers'):
            return
        self.movie_chip.delParam('DisableLayers', 'glow')

    def disableGlow(self):
        if 'glow' in self.movie_chip.getParam('DisableLayers'):
            return
        self.movie_chip.appendParam('DisableLayers', 'glow')

    def scopeSelect(self, source):
        source.addFunction(self.enableGlow)

    def scopeDeselect(self, source):
        source.addFunction(self.disableGlow)

    def scopeAppearance(self, source):
        pass

    def scopeDisappearance(self, source):
        pass

    def __setOnNewPlace(self, place_id, slot):
        self.place_id = place_id
        movie_chip_en = self.movie_chip.getEntityNode()
        movie_chip_en.removeFromParent()
        movie_chip_en.setLocalPosition((0, 0))
        slot.addChild(self.movie_chip.getEntityNode())

    def scopeMoveTo(self, source, new_place_id, new_place_slot):
        new_slot_wp = new_place_slot.getWorldPosition()
        current_slot_wp = self.movie_chip.getEntityNode().getWorldPosition()

        source.addDisable(self.movie_chip)
        source.addEnable(self.run_movie)
        source.addFunction(self.run_movie.getEntityNode().setWorldPosition, current_slot_wp)

        source.addTask("AliasObjectMoveTo", Object=self.run_movie, To=new_slot_wp, Time=self.move_time, Wait=True)
        source.addDisable(self.run_movie)
        source.addEnable(self.movie_chip)
        source.addFunction(self.__setOnNewPlace, new_place_id, new_place_slot)

class BlockChip(Chip):
    def __init__(self, chip_id, place_id, movie_chip):
        super(BlockChip, self).__init__(chip_id, place_id, movie_chip)

    def scopeClick(self, source):
        super(BlockChip, self).scopeClick(source)

    def cleanUp(self):
        super(BlockChip, self).cleanUp()

class EnemyChip(Chip):
    def __init__(self, chip_id, place_id, movie_chip, rotate_time=500):
        super(EnemyChip, self).__init__(chip_id, place_id, movie_chip)
        self.attack_movie = None

        self.rotate_time = rotate_time
        self.rotate_angle = 0

        movie_chip.getEntity().setSocketHandle("observed_area", "button", False)
        movie_chip.getEntity().setSocketHandle("observed_area", "enter", False)

    def runChipParamsUnittests(self):
        super(EnemyChip, self).runChipParamsUnittests()

        assert self.attack_movie is not None, "Error run_movie can not be {}".format(self.attack_movie)
        assert isinstance(self.rotate_time, (int, float)), "Error move_time={}. Must be number, not {}".format(self.rotate_time, type(self.rotate_time))

        assert isinstance(self.rotate_angle, (int, float)), "Error move_time={}. Must be number, not {}".format(self.rotate_angle, type(self.rotate_angle))

    def createSupportMovies(self, enigma_obj, place):
        support_movie_id = "{}_SupportMovie_AttackMovie".format(self.chip_id)

        if place.other_params is not None and enigma_obj.object.hasPrototype(place.other_params[0]):
            self.attack_movie = enigma_obj.object.tryGenerateObjectUnique(support_movie_id, place.other_params[0], Enable=False)
        else:
            self.attack_movie = enigma_obj.object.tryGenerateObjectUnique(support_movie_id, place.movie_prototype_name, Enable=False)

            if _DEVELOPMENT is True:
                Trace.log("Object", 1, "Not found enemy_attack_movie name for enemy chip {}."
                                       "\nMb you forgot add to {}_Places.xlsx in OthersParams or add this Movie in PSD?"
                                       "\nNow using movie {} for create enemy_attack_movie name for enemy chip".format(self.chip_id, enigma_obj.EnigmaName, place.movie_prototype_name))

        attack_movie_en = self.attack_movie.getEntityNode()

        enigma_obj_en = enigma_obj.object.getEntityNode()
        enigma_obj_en.addChild(attack_movie_en)

        chip_wp = self.movie_chip.getEntityNode().getWorldPosition()

        attack_movie_en.setWorldPosition(chip_wp)

        self.setupStartRotate(place.other_params)

    def setupStartRotate(self, params):
        if len(params) < 2:
            if _DEVELOPMENT is True:
                Trace.log("Object", 1, "Don`t have star rotate params for enemy {}"
                                       "\nThe enemy don`t have starting rotation"
                                       "\nIf you want setup start rotation for this enemy add second param in"
                                       "column OtherParams in *_Places.xlsx".format(self.chip_id))

            return
        self.__updateRotateAngle(int(params[1]))

        self.movie_chip.getEntityNode().setAngle(self.rotate_angle)
        self.attack_movie.getEntityNode().setAngle(self.rotate_angle)

    def scopeClick(self, source):
        super(EnemyChip, self).scopeClick(source)

    def cleanUp(self):
        super(EnemyChip, self).cleanUp()

    def __updateRotateAngle(self, angle):
        angle_in_radians = math.radians(angle)
        self.rotate_angle -= angle_in_radians

    def scopeRotateChip(self, source, angle):
        source.addFunction(self.__updateRotateAngle, angle)

        source.addTask("AliasObjectRotateTo", Object=self.movie_chip, To=self.rotate_angle, Time=self.rotate_time)
        source.addFunction(self.attack_movie.getEntityNode().setAngle, self.rotate_angle)

    def scopePlayAttackMovie(self, source):
        source.addDisable(self.movie_chip)
        source.addEnable(self.attack_movie)

        source.addTask("TaskMovie2Play", Movie2=self.attack_movie, Wait=True)

        source.addDisable(self.attack_movie)
        source.addEnable(self.movie_chip)

class EmptyChip(Chip):
    def __init__(self, chip_id, place_id, movie_chip):
        super(EmptyChip, self).__init__(chip_id, place_id, movie_chip)

        movie_chip.getEntity().setSocketHandle("nearby", "button", False)
        movie_chip.getEntity().setSocketHandle("nearby", "enter", False)

    def scopeClick(self, source):
        super(EmptyChip, self).scopeClick(source)

    def cleanUp(self):
        super(EmptyChip, self).cleanUp()

    def scopeFailClick(self, source):
        source.addDummy()

    def setOnNewPlace(self, place_id, slot):
        self.place_id = place_id
        self.movie_chip.removeFromParent()
        slot.addChild(self.movie_chip.getEntityNode())

class NeutralChip(Chip):
    def __init__(self, chip_id, place_id, movie_chip, move_time=1000):
        super(NeutralChip, self).__init__(chip_id, place_id, movie_chip)
        self.disableGlow()
        self.move_movie = None
        self.move_time = move_time

    def runChipParamsUnittests(self):
        super(NeutralChip, self).runChipParamsUnittests()
        assert self.move_movie is not None, "Error run_movie can not be {}".format(self.move_movie)
        assert isinstance(self.move_time, (int, float)), "Error move_time={}. Must be number, not {}".format(self.move_time, type(self.move_time))

    def createSupportMovies(self, enigma_obj, place):
        support_movie_id = "{}_SupportMovie_MoveMovie".format(self.chip_id)

        if place.other_params is not None and enigma_obj.object.hasPrototype(place.other_params[0]):
            self.move_movie = enigma_obj.object.tryGenerateObjectUnique(support_movie_id, place.other_params[0], Enable=False)
        else:
            self.move_movie = enigma_obj.object.tryGenerateObjectUnique(support_movie_id, place.movie_prototype_name, Enable=False)

            if _DEVELOPMENT is True:
                Trace.log("Object", 1, "Not found move_movie name for neutral chip {}. "
                                       "\nMb you forgot add to {}_Places.xlsx in OthersParams or add this Movie in PSD?"
                                       "\nNow using movie {} for create move_movie name for neutral chip".format(self.chip_id, enigma_obj.EnigmaName, place.movie_prototype_name))

        enigma_obj_en = enigma_obj.object.getEntityNode()
        enigma_obj_en.addChild(self.move_movie.getEntityNode())

    def scopeClick(self, source):
        super(NeutralChip, self).scopeClick(source)

    def cleanUp(self):
        super(NeutralChip, self).cleanUp()

    def enableGlow(self):
        if 'glow' not in self.movie_chip.getParam('DisableLayers'):
            return
        self.movie_chip.delParam('DisableLayers', 'glow')

    def disableGlow(self):
        if 'glow' in self.movie_chip.getParam('DisableLayers'):
            return
        self.movie_chip.appendParam('DisableLayers', 'glow')

    def scopeSelect(self, source):
        source.addFunction(self.enableGlow)

    def scopeDeselect(self, source):
        source.addFunction(self.disableGlow)

    def __setOnNewPlace(self, place_id, slot):
        self.place_id = place_id
        movie_chip_en = self.movie_chip.getEntityNode()
        movie_chip_en.removeFromParent()
        movie_chip_en.setLocalPosition((0, 0))
        slot.addChild(self.movie_chip.getEntityNode())

    def scopeMoveTo(self, source, new_place_id, new_place_slot):
        new_slot_wp = new_place_slot.getWorldPosition()
        current_slot_wp = self.movie_chip.getEntityNode().getWorldPosition()

        source.addDisable(self.movie_chip)
        source.addEnable(self.move_movie)
        source.addFunction(self.move_movie.getEntityNode().setWorldPosition, current_slot_wp)

        source.addTask("AliasObjectMoveTo", Object=self.move_movie, To=new_slot_wp, Time=self.move_time)
        source.addDisable(self.move_movie)
        source.addEnable(self.movie_chip)
        source.addFunction(self.__setOnNewPlace, new_place_id, new_place_slot)