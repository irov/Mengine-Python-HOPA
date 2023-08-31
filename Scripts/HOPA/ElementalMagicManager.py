from Foundation.Manager import Manager
from Foundation.DatabaseManager import DatabaseManager
from Foundation.DemonManager import DemonManager
from HOPA.QuestManager import QuestManager
from Foundation.SceneManager import SceneManager
from HOPA.ZoomManager import ZoomManager


QUEST_USE_MAGIC_NAME = "ElementalMagicUse"
QUEST_GET_ELEMENT_NAME = "ElementalMagicGet"


class ElementalMagicManager(Manager):

    s_demon_name = None
    s_config = None
    s_magic = {}            # technical params
    s_elements = {}         # ui params

    class Params(object):
        if _DEVELOPMENT:
            def __repr__(self):
                return "<{}: {}>".format(self.__class__.__name__, self.__dict__)

    class GeneralConfig(Params):
        """ general elemental magic params """
        def __init__(self, records):
            self._params = {}

            for record in records:
                key = record.get("Key")
                value = record.get("Value")
                self._params[key] = value

        def get(self, key, default=None):
            return self._params.get(key, default)

    class MagicParams(Params):
        """ technical params, used for Macro commands """
        def __init__(self, record):
            self.id = ElementalMagicManager.getRecordValue(record, "MagicId", required=True)
            self.element = ElementalMagicManager.getRecordValue(record, "ElementType", required=True)

    class ElementsParams(Params):
        """ user interface params for each element type """
        def __init__(self, record):
            self.element = ElementalMagicManager.getRecordValue(record, "ElementType", required=True)
            self.group_name = ElementalMagicManager.getRecordValue(record, "GroupName", required=True)
            self.state_Appear = ElementalMagicManager.getRecordValue(record, "PrototypeAppear")
            self.state_Idle = ElementalMagicManager.getRecordValue(record, "PrototypeIdle", required=True)
            self.state_Ready = ElementalMagicManager.getRecordValue(record, "PrototypeReady", required=True)
            self.state_Release = ElementalMagicManager.getRecordValue(record, "PrototypeRelease")

    @staticmethod
    def loadConfig(records):
        params = ElementalMagicManager.GeneralConfig(records)

        if _DEVELOPMENT is True:
            required_params = [
                "RingStateIdle",
                "RingStateReady",
                "DemonName",
            ]

            _check_failed = False
            for key in required_params:
                if params.get(key) is None:
                    Trace.log("Manager", 0, "ElementalMagicManager.loadConfig: required param {!r} not found".format(key))
                    _check_failed = True

            if _check_failed is True:
                return False

        ElementalMagicManager.s_config = params

        ElementalMagicManager.s_demon_name = ElementalMagicManager.getConfig("DemonName", default="ElementalMagic")

    @staticmethod
    def loadMagic(records):
        magic_id_example = "01_Fire_1"

        for record in records:
            param = ElementalMagicManager.MagicParams(record)

            if _DEVELOPMENT is True:
                # check if magic id is valid
                id_split = param.id.split("_")
                if len(id_split) != 3:
                    Trace.log("Manager", 0, "Magic id {!r} is invalid - example: {!r}".format(param.id, magic_id_example))
                    return False

                if id_split[0].isdigit() is False:
                    Trace.log("Manager", 0, "Magic id {!r} is invalid 1st part must be a digit - example: {!r}".format(param.id, magic_id_example))
                    return False
                if id_split[1].lower() != param.element.lower():
                    Trace.log("Manager", 0, "Magic id {!r} is invalid 2nd part must be an element type - example: {!r}".format(param.id, magic_id_example))
                    return False
                if id_split[2].isdigit() is False:
                    Trace.log("Manager", 0, "Magic id {!r} is invalid 3rd part must be an element type - example: {!r}".format(param.id, magic_id_example))
                    return False

                # check duplicates
                if param.id in ElementalMagicManager.s_magic:
                    Trace.log("Manager", 0, "Magic id {!r} is duplicated - please update its id".format(param.id))
                    return False

            ElementalMagicManager.s_magic[param.id] = param

    @staticmethod
    def loadElements(records):
        for record in records:
            param = ElementalMagicManager.ElementsParams(record)

            if _DEVELOPMENT is True:
                if param.element not in ElementalMagicManager.s_elements:
                    Trace.log("Manager", 0, "Element {!r} is duplicated! Remove it and try again".format(param.element))
                    return False

            ElementalMagicManager.s_elements[param.element] = param

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        if name == "ElementalMagic_Config":
            ElementalMagicManager.loadConfig(records)
        elif name == "ElementalMagic_Magic":
            ElementalMagicManager.loadMagic(records)
        elif name == "ElementalMagic_Elements":
            ElementalMagicManager.loadElements(records)

        return True

    # --- getters ------------------------------------------------------------------------------------------------------

    @staticmethod
    def getConfigs():
        """ returns GeneralConfig """
        return ElementalMagicManager.s_config

    @staticmethod
    def getElementsParams():
        """ returns dict {ElementType: ElementParams} """
        return ElementalMagicManager.s_elements

    @staticmethod
    def getMagicsParams():
        """ returns dict {MagicId: MagicParam} """
        return ElementalMagicManager.s_magic

    # specific

    @staticmethod
    def getConfig(key, default=None):
        return ElementalMagicManager.s_config.get(key, default)

    @staticmethod
    def getElementParams(element):
        return ElementalMagicManager.s_elements.get(element)

    @staticmethod
    def isElementExists(element):
        return element in ElementalMagicManager.getElementsParams()

    @staticmethod
    def getMagicParams(magic_id):
        return ElementalMagicManager.s_magic.get(magic_id)

    @staticmethod
    def getMagicsByElement(element):
        magics = [magic for magic in ElementalMagicManager.getMagicsParams().values()
                  if magic.element == element]
        return magics

    @staticmethod
    def getRingMovieParams():
        config = ElementalMagicManager.getConfigs()
        return {
            "Idle": [config.get("RingStateIdle"), True, True],
            "Ready": [config.get("RingStateReady"), True, False],
            "Attach": [config.get("RingStateAttach"), True, True],
            "Return": [config.get("RingStateReturn"), True, True],
            "Pick": [config.get("RingStatePick"), True, False],
            "Use": [config.get("RingStateUse"), True, False],
        }

    # --- user interaction ---------------------------------------------------------------------------------------------

    @staticmethod
    def getPlayerElement():
        demon = DemonManager.getDemon(ElementalMagicManager.s_demon_name)
        element = demon.getPlayerElement()
        return element

    @staticmethod
    def setPlayerElement(element):
        demon = DemonManager.getDemon(ElementalMagicManager.s_demon_name)
        demon.setPlayerElement(element)

    @staticmethod
    def getMagicRing():
        demon = DemonManager.getDemon(ElementalMagicManager.s_demon_name)
        ring = demon.getRing()
        return ring

    @staticmethod
    def getMagicUseQuest():
        scene_name = SceneManager.getCurrentSceneName()

        if scene_name is None:
            return

        zoom_name = ZoomManager.getCurrentGameZoomName()

        if zoom_name is not None:
            group_name = zoom_name
        else:
            group_name = SceneManager.getSceneMainGroupName(scene_name)

        quest = QuestManager.getSceneQuest(scene_name, group_name, QUEST_USE_MAGIC_NAME)

        return quest

    @staticmethod
    def isMagicReady():
        quest = ElementalMagicManager.getMagicUseQuest()
        return quest is not None
