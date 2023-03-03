# coding=utf-8
"""
Using in 04_FashionMG in HolidayFun2
"""
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.AssemblyDesignerManager import AssemblyDesignerManager


Enigma = Mengine.importEntity("Enigma")
TEXT_ALIAS_SET_NAME = '$AliasSetName'


def _log(message, is_error=True):
    if _DEVELOPMENT is True:
        if is_error:
            Trace.log("Object", 1, message + "\n")
        else:
            print(message)


class AssemblyDesigner(Enigma):
    class MixinEffectsInterface(object):
        @staticmethod
        def scopePlayEffect(source, movie_effect, movie_main):
            slot_play = movie_effect.getMovieSlot('play_effect')

            movie_main_en = movie_main.getEntityNode()
            slot_parent = movie_main_en.getParent()

            source.addFunction(slot_play.addChild, movie_main_en)
            source.addTask("TaskMovie2Play", Movie2=movie_effect, Wait=True)
            source.addFunction(slot_parent.addChild, movie_main_en)

    class __Set(MixinEffectsInterface):
        def __init__(self, set_id, movie_carcass, types, movie_set_open, movie_set_close, set_name_not_complete_text_id,
                     set_name_complete_text_id):
            self.set_id = set_id
            self.movie_carcass = movie_carcass

            self.set_name_not_complete_text_id = set_name_not_complete_text_id
            self.set_name_complete_text_id = set_name_complete_text_id

            self.movie_carcass.setTextAliasEnvironment(self.set_id)

            self.completed = False
            self.movie_set_open = movie_set_open
            self.movie_set_close = movie_set_close

            self.assembly = {}
            self.__finish_items = types
            self.disableSet()
            for type_ in types.keys():
                self.assembly[type_] = None

            self.updateText()

        def runTests(self):
            if self.movie_set_open is not None and self.movie_set_close is not None:
                assert self.movie_set_open[0].hasSlot(
                    'play_effect') is True, "Movie2_SetOpenMinus dont has slot play_effect"
                assert self.movie_set_open[1].hasSlot(
                    'play_effect') is True, "Movie2_SetOpenPlus dont has slot play_effect"
                assert self.movie_set_close[0].hasSlot(
                    'play_effect') is True, "Movie2_SetCloseMinus dont has slot play_effect"
                assert self.movie_set_close[1].hasSlot(
                    'play_effect') is True, "Movie2_SetClosePlus dont has slot play_effect"

        def cleanUp(self):
            self.movie_carcass.getEntityNode().removeFromParent()
            self.movie_carcass.onDestroy()

            for movie_set_open in self.movie_set_open:
                movie_set_open.getEntityNode().removeFromParent()

            for movie_set_close in self.movie_set_close:
                movie_set_close.getEntityNode().removeFromParent()

        def updateText(self):
            text_id = self.set_name_complete_text_id
            if self.checkCompleted() is False:
                text_id = self.set_name_not_complete_text_id
            Mengine.setTextAlias(self.set_id, TEXT_ALIAS_SET_NAME, text_id)

        def checkCompleted(self):
            is_complete = True
            for finish_type_temp, finish_item_temp in self.__finish_items.iteritems():
                item_in_assembly = self.assembly.get(finish_type_temp, "NotFound")
                if item_in_assembly == "NotFound":
                    _log("Something went wrong. set {} not found type {}".format(self.set_id, finish_type_temp))
                    is_complete = False
                    break
                if item_in_assembly is None:
                    is_complete = False
                    break
                if item_in_assembly.item_id != finish_item_temp:
                    is_complete = False
                    break

            self.setCompleted(is_complete)
            return is_complete

        def setCompleted(self, value):
            self.completed = value

        def scopeOpenSet(self, source, motion_vector):
            if self.movie_set_open is None:
                _log("Set Open animation has not exist. \nPlease add Movie2_SetOpenPlus and Movie2_SetOpenMinus "
                     "if you want to have the animation", is_error=False)
                source.addDummy()
                return

            motion_vector = 0 if motion_vector == -1 else 1
            movie_set_open = self.movie_set_open[motion_vector]

            source.addScope(self.scopePlayEffect, movie_set_open, self.movie_carcass)

        def scopeCloseSet(self, source, motion_vector):
            if self.movie_set_close is None:
                _log("Set Close animation has not exist. \nPlease add Movie2_SetClosePlus and Movie2_SetCloseMinus "
                     "if you want have the animation", is_error=False)
                source.addDummy()
                return

            motion_vector = 0 if motion_vector == -1 else 1
            movie_set_close = self.movie_set_close[motion_vector]

            source.addScope(self.scopePlayEffect, movie_set_close, self.movie_carcass)

        def enableSet(self):
            self.movie_carcass.setEnable(True)
            self.updateText()

        def disableSet(self):
            self.movie_carcass.setEnable(False)

        def addItem(self, item):
            if self.assembly.get(item.item_type) is not None:
                return False

            if not self.movie_carcass.hasSlot(item.item_type):
                _log("Carcass movie set {} don`t has slot {}!!!. "
                     "\nPlease add this slot to movie carcass".format(self.set_id, item.item_type))
                return False

            self.assembly[item.item_type] = item
            item.itemRemoveFromShelf()
            item.setCurrentSet(self)

            item.movie_on_set.setEnable(True)
            item.movie_on_shelf.setEnable(False)

            type_item_slot = self.movie_carcass.getMovieSlot(item.item_type)
            type_item_slot.addChild(item.movie_on_set.getEntityNode())
            self.updateText()

            return True

        def removeItem(self, item):
            if self.assembly.get(item.item_type, None) is not item:
                _log("{} assembly don`t has item {}".format(self.set_id, item.item_id), is_error=False)
                return
            item.current_set = None
            self.assembly[item.item_type] = None
            self.setCompleted(False)

    class __Item(object):
        def __init__(self, item_id, item_type, movie_on_set, movie_on_shelf, shelf):
            self.item_id = item_id
            self.item_type = item_type
            self.movie_on_set = movie_on_set
            self.movie_on_shelf = movie_on_shelf
            self.current_set = None
            self.shelf = shelf

            self.current_movie = self.movie_on_shelf

            self.__temp_parent = None
            if shelf is not None:
                shelf.addItem(self)

        def runTests(self):
            assert self.shelf is not None, "{} not have shelf".format(self.item_id)

        def cleanUp(self):
            self.current_movie = None
            self.movie_on_set.onDestroy()
            self.movie_on_shelf.onDestroy()

        def setCurrentSet(self, set_):
            _log("item {} added on new set {}".format(self.item_id, set_.set_id), is_error=False)
            self.current_set = set_

        def getCurrentSet(self, set_):
            if self.current_set is None:
                _log("item {} not added on any set".format(self.item_id))

            return self.current_set

        def itemRemoveFromShelf(self):
            self.current_movie = self.movie_on_set
            self.detachFromCursor(return_to_parent=True)
            self.shelf.removeItem(self.item_id)
            self.shelf = None

        def scopeClick(self, source):
            source.addTask("TaskMovie2SocketClick", SocketName="socket", Movie2=self.current_movie, isDown=True)

        def attachToCursor(self):
            arrow = Mengine.getArrow()
            self.__temp_parent = self.current_movie.getEntityNode().getParent()
            self.movie_on_set.setEnable(False)
            self.movie_on_shelf.setEnable(True)
            arrow.addChildFront(self.movie_on_shelf.getEntityNode())

        def detachFromCursor(self, return_to_parent=False):
            self.movie_on_set.setEnable(False)
            self.movie_on_shelf.setEnable(False)
            self.movie_on_shelf.removeFromParent()
            if return_to_parent is True:
                if self.__temp_parent is None:
                    _log("Something went wrong. item {} must will be return on parent but parent is None!!!".format(self.item_id))
                    return
                self.__temp_parent.addChild(self.current_movie.getEntityNode())
            self.current_movie.setEnable(True)
            self.__temp_parent = None

    class __Shelf(MixinEffectsInterface):
        def __init__(self, shelf_id, movie_shelf, number_of_places, movie_shelf_open, movie_shelf_close):
            self.shelf_id = shelf_id
            self.movie_shelf = movie_shelf
            self.current_items = {}
            self.places = {}
            self.__number_of_places = number_of_places

            self.movie_shelf_open = movie_shelf_open
            self.movie_shelf_close = movie_shelf_close

            self.__registerPlaces(number_of_places)
            self.disableShelf()

        def cleanUp(self):
            self.movie_shelf.getEntityNode().removeFromParent()

            for movie_shelf_open in self.movie_shelf_open:
                movie_shelf_open.getEntityNode().removeFromParent()

            for movie_shelf_close in self.movie_shelf_close:
                movie_shelf_close.getEntityNode().removeFromParent()

        def runTests(self):
            assert len(self.places) == self.__number_of_places, "shelf {} has {} places, but must has {}".format(
                self.shelf_id, len(self.places), self.__number_of_places)
            if self.movie_shelf_open is not None and self.movie_shelf_close is not None:
                assert self.movie_shelf_open[0].hasSlot(
                    'play_effect') is True, "Movie2_ShelfOpenMinus dont has slot play_effect"
                assert self.movie_shelf_open[1].hasSlot(
                    'play_effect') is True, "Movie2_ShelfOpenPlus dont has slot play_effect"
                assert self.movie_shelf_close[0].hasSlot(
                    'play_effect') is True, "Movie2_ShelfCloseMinus dont has slot play_effect"
                assert self.movie_shelf_close[1].hasSlot(
                    'play_effect') is True, "Movie2_ShelfClosePlus dont has slot play_effect"

        def __registerPlaces(self, number_of_places):
            for i in range(1, number_of_places + 1):
                slot_name = "place_{}".format(i)
                if not self.movie_shelf.hasSlot(slot_name):
                    _log("Movie shelf {} don`t has slot {}!!!. \nPlease add this slot to movie or update NumberOfPlaces"
                         " param in **Shelves.xlsx".format(self.shelf_id, slot_name))
                    continue
                place = self.movie_shelf.getMovieSlot(slot_name)
                self.places[place] = None

        def getFreePlace(self):
            for place, item in self.places.iteritems():
                if item is None:
                    return place

        def getItemPlace(self, item_id):
            for place, item in self.places.iteritems():
                if item is None:
                    continue
                if item.item_id == item_id:
                    return place

        def scopeCloseShelf(self, source, motion_vector):
            if self.movie_shelf_close is None:
                _log("Set Close animation has not exist. "
                     "\nPlease add Movie2_ShelfClosePlus and Movie2_ShelfCloseMinus if you want have the animation",
                     is_error=False)
                source.addDummy()
                return

            motion_vector = 0 if motion_vector == -1 else 1
            movie_shelf_close = self.movie_shelf_close[motion_vector]

            source.addScope(self.scopePlayEffect, movie_shelf_close, self.movie_shelf)

        def scopeOpenShelf(self, source, motion_vector):
            if self.movie_shelf_open is None:
                _log("Set Open animation has not exist. "
                     "\nPlease add Movie2_ShelfOpenPlus and Movie2_ShelfOpenMinus if you want have the animation",
                     is_error=False)
                source.addDummy()
                return

            motion_vector = 0 if motion_vector == -1 else 1
            movie_shelf_open = self.movie_shelf_open[motion_vector]

            source.addScope(self.scopePlayEffect, movie_shelf_open, self.movie_shelf)

        def enableShelf(self):
            self.movie_shelf.setEnable(True)

        def disableShelf(self):
            self.movie_shelf.setEnable(False)

        def addItem(self, item):
            place = self.getFreePlace()
            if place is None:
                return False

            # item.detachFromCursor()

            item.shelf = self
            self.current_items[item.item_id] = item

            item.movie_on_set.setEnable(False)
            item.movie_on_shelf.setEnable(True)
            item.current_movie = item.movie_on_shelf
            place.addChild(item.movie_on_shelf.getEntityNode())
            self.places[place] = item
            return True

        def removeItem(self, item_id):
            if self.current_items.get(item_id, None) is None:
                _log("Shelf {} dont has item {}".format(self.shelf_id, item_id))
                return
            del self.current_items[item_id]
            place = self.getItemPlace(item_id)
            if place is None:
                _log("Warn!!! item {} doesnt have place in shelf {}".format(item_id, self.shelf_id))

            self.places[place] = None

    def __init__(self):
        super(AssemblyDesigner, self).__init__()
        self.shelves = {}
        self.items = {}
        self.sets = {}
        self.ordered_shelves = []
        self.ordered_sets = []
        self.tc_main = None
        self.current_set = None
        self.current_shelf = None

        self.params = None

    def __getCurrentSet(self):
        return self.current_set

    def __setCurrentSet(self, set_):
        _log("new current set is {}".format(set_.set_id), is_error=False)
        self.current_set = set_

    def __getCurrentShelf(self):
        return self.current_set

    def __setCurrentShelf(self, shelf):
        _log("new current shelf is {}".format(shelf.shelf_id), is_error=False)
        self.current_shelf = shelf

    def _playEnigma(self):
        self.__loadParams()
        self.__setupArt()
        self.__runParamsUnitTests()

        current_shelf = self.shelves.get(self.params.start_shelf_id)
        current_shelf.enableShelf()
        self.__setCurrentShelf(current_shelf)

        current_set = self.sets.get(self.params.start_set_id)
        current_set.enableSet()
        self.__setCurrentSet(current_set)

        self.__runTaskChains()

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self.__cleanUp()
        self._playEnigma()

    def _onPreparation(self):
        super(AssemblyDesigner, self)._onPreparation()

    def _onActivate(self):
        super(AssemblyDesigner, self)._onActivate()

    def _onDeactivate(self):
        super(AssemblyDesigner, self)._onDeactivate()
        self.__cleanUp()

    def __loadParams(self):
        self.params = AssemblyDesignerManager.getParams(self.EnigmaName)

    def __setupArt(self):
        def __setup_buttons():
            self.button_next_set = self.object.getObject("Movie2Button_NextSet")
            self.button_prev_set = self.object.getObject("Movie2Button_PrevSet")
            self.button_next_shelf = self.object.getObject("Movie2Button_NextShelf")
            self.button_prev_shelf = self.object.getObject("Movie2Button_PrevShelf")

            buttons_and_slots = (
                ("button_next_set", self.button_next_set),
                ("button_prev_set", self.button_prev_set),
                ("button_next_shelf", self.button_next_shelf),
                ("button_prev_shelf", self.button_prev_shelf)
            )

            for button_slot_name, button in buttons_and_slots:
                if not self.movie_content.hasSlot(button_slot_name):
                    _log("AssemblyDesigner.__setupArt"
                         "\nNot found slot {} in Movie2_Content"
                         "\nPlease add this slot".format(button_slot_name))

                    continue

                slot = self.movie_content.getMovieSlot(button_slot_name)
                slot.addChild(button.getEntityNode())

        def __create_shelves():
            shelves = self.params.shelves_params
            for shelf_id, (movie_name, number_of_places, _) in shelves.iteritems():
                movie_shelf = self.object.getObject(movie_name)
                if not self.movie_content.hasSlot("shelf"):
                    _log("AssemblyDesigner.__setupArt"
                         "\nNot found slot shelf in Movie2_Content"
                         "\nPlease add this slot")
                    continue

                slot_shelf = self.movie_content.getMovieSlot("shelf")

                movie_shelf_open = None
                movie_shelf_close = None
                if all([
                    self.object.hasObject("Movie2_ShelfOpenMinus"),
                    self.object.hasObject("Movie2_ShelfCloseMinus"),
                    self.object.hasObject("Movie2_ShelfOpenPlus"),
                    self.object.hasObject("Movie2_ShelfClosePlus"),
                ]):
                    movie_shelf_open_minus = self.object.getObject("Movie2_ShelfOpenMinus")
                    slot_shelf.addChild(movie_shelf_open_minus.getEntityNode())

                    movie_shelf_close_minus = self.object.getObject("Movie2_ShelfCloseMinus")
                    slot_shelf.addChild(movie_shelf_close_minus.getEntityNode())

                    movie_shelf_open_plus = self.object.getObject("Movie2_ShelfOpenPlus")
                    slot_shelf.addChild(movie_shelf_open_plus.getEntityNode())

                    movie_shelf_close_plus = self.object.getObject("Movie2_ShelfClosePlus")
                    slot_shelf.addChild(movie_shelf_close_plus.getEntityNode())

                    movie_shelf_open = (movie_shelf_open_minus, movie_shelf_open_plus)
                    movie_shelf_close = (movie_shelf_close_minus, movie_shelf_close_plus)
                else:
                    _log("Enigma {} don`t has Movie2_SetOpenMinus or Movie2_SetCloseMinus or "
                         "Movie2_SetOpenPlus or Movie2_SetClosePlus."
                         "\nPlease add this movie for add animation open and close set".format(self.EnigmaName),
                         is_error=False)

                slot_shelf.addChild(movie_shelf.getEntityNode())

                self.shelves[shelf_id] = self.__Shelf(shelf_id, movie_shelf, number_of_places, movie_shelf_open,
                                                      movie_shelf_close)
                self.ordered_shelves.append(shelf_id)

        def __create_items():
            items_params = self.params.items
            for item_param in items_params.values():
                if not self.object.hasPrototype(item_param.movie_name_on_set):
                    _log("movie {} doesnt exist".format(item_param.movie_name_on_set))
                    continue

                if not self.object.hasPrototype(item_param.movie_name_on_shelf):
                    _log("movie {} doesnt exist".format(item_param.movie_name_on_shelf))
                    continue
                movie_on_set = self.object.tryGenerateObjectUnique("{}_{}".format(item_param.item_id, item_param.movie_name_on_set),
                                                                   item_param.movie_name_on_set, Enable=True, Interactive=True)

                movie_on_shelf = self.object.tryGenerateObjectUnique("{}_{}".format(item_param.item_id, item_param.movie_name_on_shelf),
                                                                     item_param.movie_name_on_shelf, Enable=True, Interactive=True)

                shelf = self.shelves.get(item_param.shelf_id, None)
                if shelf is None:
                    _log("shelf {} doesnt exist. Can`t add item {}".format(item_param.shelf_id, item_param.item_id))

                self.items[item_param.item_id] = self.__Item(item_param.item_id, item_param.item_type,
                                                             movie_on_set, movie_on_shelf, shelf)

        def __create_sets():
            sets_params = self.params.finish_sets_params
            if not self.object.hasPrototype(self.params.carcass_movie_name):
                _log("{} has not prototype {}. Please add prototype in PSD or change params in AssemblyDesigner.xlsx "
                     "\nNow carcass movies don`t created".format(self.EnigmaName, self.params.carcass_movie_name))
                return

            if not self.movie_content.hasSlot("carcass"):
                _log("Movie2_Content has not slot carcass. Please add slot carcass! "
                     "\nNow carcass movie will be added on demon object")
                slot_carcass = self.object.getEntityNode()
            else:
                slot_carcass = self.movie_content.getMovieSlot("carcass")

            movie_set_open = None
            movie_set_close = None
            if all([
                self.object.hasObject("Movie2_SetOpenMinus"),
                self.object.hasObject("Movie2_SetCloseMinus"),
                self.object.hasObject("Movie2_SetOpenPlus"),
                self.object.hasObject("Movie2_SetClosePlus"),
            ]):
                movie_set_open_minus = self.object.getObject("Movie2_SetOpenMinus")
                slot_carcass.addChild(movie_set_open_minus.getEntityNode())

                movie_set_close_minus = self.object.getObject("Movie2_SetCloseMinus")
                slot_carcass.addChild(movie_set_close_minus.getEntityNode())

                movie_set_open_plus = self.object.getObject("Movie2_SetOpenPlus")
                slot_carcass.addChild(movie_set_open_plus.getEntityNode())

                movie_set_close_plus = self.object.getObject("Movie2_SetClosePlus")
                slot_carcass.addChild(movie_set_close_plus.getEntityNode())

                movie_set_open = (movie_set_open_minus, movie_set_open_plus)
                movie_set_close = (movie_set_close_minus, movie_set_close_plus)
            else:
                _log("Enigma {} don`t has Movie2_SetOpenMinus or Movie2_SetCloseMinus or "
                     "Movie2_SetOpenPlus or Movie2_SetClosePlus."
                     "\nPlease add this movie for add animation open and close set".format(self.EnigmaName), is_error=False)

            for set_id, (types, set_name_not_complete_text_id, set_name_complete_text_id) in sets_params.iteritems():
                movie_carcass = self.object.tryGenerateObjectUnique(set_id, self.params.carcass_movie_name,
                                                                    Enable=False, Interactive=True)

                slot_carcass.addChild(movie_carcass.getEntityNode())
                self.sets[set_id] = self.__Set(set_id, movie_carcass, types, movie_set_open, movie_set_close,
                                               set_name_not_complete_text_id, set_name_complete_text_id)
                self.ordered_sets.append(set_id)

        if not self.object.hasObject("Movie2_Content"):
            _log("{} don`t has Movie2_Content!"
                 "\nPlease add Movie2_Content for setup art!"
                 "\nMovie2_Content must have slots: \n\tbutton_next_shelf, \n\tbutton_prev_shelf, \n\tbutton_next_set,"
                 "\n\tbutton_prev_set, \n\tshelf, \n\tcarcass".format(self.EnigmaName))
        self.movie_content = self.object.getObject("Movie2_Content")

        __setup_buttons()
        __create_shelves()
        __create_items()
        __create_sets()

    def __runParamsUnitTests(self):
        def __run_tests():
            assert len(self.shelves) != 0
            assert len(self.items) != 0
            assert len(self.sets) != 0
            assert self.current_set is None
            assert self.current_shelf is None
            assert self.tc_main is None

            for shelf in self.shelves.values() + self.sets.values() + self.items.values():
                shelf.runTests()

        if _DEVELOPMENT is True:
            __run_tests()
            return

        try:
            __run_tests()
        except AssertionError:
            self.enigmaComplete()

    def __runTaskChains(self):
        self.tc_main = TaskManager.createTaskChain(Repeat=True)
        with self.tc_main as tc_main:
            with tc_main.addRaceTask(3) as (tc_item_click, tc_change_set, tc_change_shelf):
                tc_item_click.addScope(self.__scopeItemClick)
                tc_item_click.addFunction(self.__checkComplete)

                with tc_change_set.addRaceTask(2) as (tc_next_set, tc_prev_set):
                    tc_next_set.addTask("TaskMovie2ButtonClick", Movie2Button=self.button_next_set)
                    tc_next_set.addScope(self.__scopeChooseNewSet, 1)

                    tc_prev_set.addTask("TaskMovie2ButtonClick", Movie2Button=self.button_prev_set)
                    tc_prev_set.addScope(self.__scopeChooseNewSet, -1)

                with tc_change_shelf.addRaceTask(2) as (tc_next_shelf, tc_prev_shelf):
                    tc_next_shelf.addTask("TaskMovie2ButtonClick", Movie2Button=self.button_next_shelf)
                    tc_next_shelf.addScope(self.__scopeChooseNewShelf, 1)

                    tc_prev_shelf.addTask("TaskMovie2ButtonClick", Movie2Button=self.button_prev_shelf)
                    tc_prev_shelf.addScope(self.__scopeChooseNewShelf, -1)

    def __scopeItemClick(self, source):
        semaphore = Semaphore(False, "isAddingToCarcass")

        for item, tc_race in source.addRaceTaskList(self.items.values()):
            tc_race.addScope(item.scopeClick)
            tc_race.addFunction(item.attachToCursor)
            tc_race.addTask("TaskMouseButtonClick", isDown=False)
            with tc_race.addRaceTask(2) as (source_item_drop, source_skip):
                source_item_drop.addScope(self.__scopeTryAddItemToSet, item, semaphore)

                source_skip.addDelay(1)
                source_skip.addSemaphore(semaphore, From=False)
                source_skip.addFunction(item.detachFromCursor, return_to_parent=True)

    def __scopeTryAddItemToSet(self, source, item, semaphore):
        def __check_arrow_on_carcass():
            arrow = Mengine.getArrow()

            screen_position = Mengine.getNodeScreenPosition(arrow.cursorNode)
            hotspots_names = Mengine.pickAllHotspot(screen_position)

            if current_set.movie_carcass.getSocket('socket') in hotspots_names:
                return True
            return False

        def __scope_remove_item_from_set_and_add_to_shelf(source, item):
            shelf = self.current_shelf
            place = shelf.getFreePlace()
            if place is None:
                for shelf in self.shelves.values():
                    place = shelf.getFreePlace()
                    if place is None:
                        continue

                    with GuardBlockInput(source) as guard_source:
                        with guard_source.addParallelTask(2) as (source_old_set_close, source_new_set_open):
                            source_old_set_close.addScope(self.current_shelf.scopeCloseShelf, 1)
                            source_old_set_close.addFunction(self.current_shelf.disableShelf)

                            source_new_set_open.addFunction(shelf.enableShelf)
                            source_new_set_open.addScope(shelf.scopeOpenShelf, 1)

                        guard_source.addFunction(self.__setCurrentShelf, shelf)
                    break
                else:
                    _log("Something went wrong. any shelf has not free places!!!")
            source.addFunction(item.current_set.removeItem, item)
            source.addFunction(shelf.addItem, item)

        current_set = self.__getCurrentSet()

        source.addSemaphore(semaphore, To=True)
        if not __check_arrow_on_carcass():
            if item.shelf is not None and item.current_set is None:
                source.addFunction(_log, "Item {} is not above carcass of set {} ".format(item.item_id, current_set.set_id), is_error=False)
                source.addSemaphore(semaphore, To=False)
                source.addBlock()
                return
            else:
                source.addScope(__scope_remove_item_from_set_and_add_to_shelf, item)
                return

        if not current_set.addItem(item):
            source.addFunction(_log, "Item {} has been not added to set {}".format(item.item_id, current_set.set_id), is_error=False)
            source.addSemaphore(semaphore, To=False)
            source.addBlock()
            return

        source.addFunction(_log, "Item {} has been added to set {}".format(item.item_id, current_set.set_id), is_error=False)
        source.addDummy()

    def __checkComplete(self):
        for set_ in self.sets.values():
            if set_.checkCompleted() is False:
                return False

        self.enigmaComplete()
        return True

    def __scopeChooseNewSet(self, source, motion_vector):
        current_set_index = self.ordered_sets.index(self.current_set.set_id)
        new_set_index = (current_set_index + motion_vector) % len(self.ordered_sets)
        new_set_id = self.ordered_sets[new_set_index]
        new_set = self.sets[new_set_id]

        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (source_old_set_close, source_new_set_open):
                source_old_set_close.addScope(self.current_set.scopeCloseSet, motion_vector)
                source_old_set_close.addFunction(self.current_set.disableSet)

                source_new_set_open.addFunction(new_set.enableSet)
                source_new_set_open.addScope(new_set.scopeOpenSet, motion_vector)

            guard_source.addFunction(self.__setCurrentSet, new_set)

    def __scopeChooseNewShelf(self, source, motion_vector):
        current_shelf_index = self.ordered_shelves.index(self.current_shelf.shelf_id)
        new_shelf_index = (current_shelf_index + motion_vector) % len(self.ordered_shelves)
        new_shelf_id = self.ordered_shelves[new_shelf_index]
        new_shelf = self.shelves[new_shelf_id]

        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (source_old_set_close, source_new_set_open):
                source_old_set_close.addScope(self.current_shelf.scopeCloseShelf, motion_vector)
                source_old_set_close.addFunction(self.current_shelf.disableShelf)

                source_new_set_open.addFunction(new_shelf.enableShelf)
                source_new_set_open.addScope(new_shelf.scopeOpenShelf, motion_vector)

            guard_source.addFunction(self.__setCurrentShelf, new_shelf)

    def __cleanUp(self):
        if self.tc_main is not None:
            self.tc_main.cancel()
        self.tc_main = None

        for obj in self.items.values() + self.sets.values() + self.shelves.values():
            obj.cleanUp()

        self.shelves = {}
        self.items = {}
        self.sets = {}

        self.ordered_shelves = []
        self.ordered_sets = []

        self.current_set = None
        self.current_shelf = None

        self.params = None
