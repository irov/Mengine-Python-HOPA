from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager
from HOPA.EnigmaManager import EnigmaManager


class MSTransition(object):
    Up = "up"
    Down = "down"
    Right = "right"
    Left = "left"
    Win = "win"

    @staticmethod
    def isValid(type_):
        types = [MSTransition.Up, MSTransition.Down, MSTransition.Right, MSTransition.Left, MSTransition.Win]
        if type_ in types:
            return True
        return False


class MSObject(object):
    Lever = "lever"
    Gate = "gate"
    Transition = "transition"

    @staticmethod
    def isValid(type_):
        types = [MSObject.Gate, MSObject.Lever, MSObject.Transition]
        if type_ in types:
            return True
        return False


class MazeScreensManager(Manager):

    CELL_TYPE_WALL = "X"
    s_enigmas = {}  # { enigma_name: Settings }

    class Settings(object):
        def __init__(self, EnigmaName, Graph, Rooms, ContentSlots, Contents, WinMovieName):
            self.enigma_name = EnigmaName
            self.graph = Graph              # GraphParam
            self.rooms = Rooms              # { room_id: RoomParam }
            self.contents = Contents        # { content_id: content_name }
            self.slots = ContentSlots       # { content_id: SlotParam[] }
            self.win_movie_name = WinMovieName
            self.should_rotate_board = True

    class RoomParam(object):
        def __init__(self, record):
            '''
                RoomId – числовой идентификатор комнаты
                ContentId – id контента - имя муви2 со слотами и задним фоном (можно анимировать)
                IsStart - является ли комната стартовой позицией
            '''
            self.id = MazeScreensManager.getRecordValue(record, "RoomId", cast=str, required=True)
            self.content_id = MazeScreensManager.getRecordValue(record, "ContentId", cast=str, required=True)
            self.is_start = MazeScreensManager.getRecordValue(record, "IsStart", cast=bool, default=False)

    class SlotParam(object):
        def __init__(self, record):
            '''
                ContentId – id контента комнаты
                SlotName – имя слота на этом контенте.
                ObjectType – тип привязанного объекта (влияет на поведение).
                    lever – рычаг
                    gate – ворота
                    transition – проход
                PrototypeName – имя прототипа, который привязывается на слот.
                GroupId – идентификатор группы, к которой принадлежит объект.
                    Например, чтобы рычаг был связан с воротами, надо указать один идентификатор.
                    Тогда при использовании рычага группы 1 – все ворота
                    с такой же группой перейдут в состояние “открыто”.
                TransitionWay (только если ObjectType = transition) – направление прохода
                    up
                    down
                    right
                    left
            '''
            self.content_id = MazeScreensManager.getRecordValue(record, "ContentId", cast=str, required=True)
            self.name = MazeScreensManager.getRecordValue(record, "SlotName", cast=str, required=True)
            self.object_type = MazeScreensManager.getRecordValue(record, "ObjectType", required=True)
            self.prototype_name = MazeScreensManager.getRecordValue(record, "PrototypeName", required=True)

            is_group_required = self.object_type in [MSObject.Gate, MSObject.Lever]
            self.group_id = MazeScreensManager.getRecordValue(record, "GroupId", cast=str, required=is_group_required)

            is_way_required = self.object_type == "transition"
            self.transition_way = MazeScreensManager.getRecordValue(record, "TransitionWay", required=is_way_required)

    class GraphParam(object):
        def __init__(self, graph):
            self.data = graph
            self.width = len(graph[0])
            self.height = len(graph)

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record["EnigmaName"]

            result = MazeScreensManager._loadParam(module, EnigmaName, record)

            if result is False:
                Trace.log("Manager", 0, "MazeScreensManager fail to load params for {!r}".format(EnigmaName))
                return False

        return True

    @staticmethod
    def _loadParam(module, enigma_name, record):
        """ load all settings for given Enigma """

        RoomParamsName = record["RoomParams"]
        RoomParams = MazeScreensManager._loadRoomParams(module, RoomParamsName)

        ContentParamsName = record["ContentParams"]
        ContentParams = MazeScreensManager._loadContentParams(module, ContentParamsName)

        SlotParamsName = record["SlotParams"]
        SlotParams = MazeScreensManager._loadSlotParams(module, SlotParamsName)

        GraphParamsName = record["GraphParams"]
        GraphParams = MazeScreensManager._loadGraphParams(module, GraphParamsName)

        WinMovieName = record.get("WinMovieName")

        settings = MazeScreensManager.Settings(enigma_name, GraphParams, RoomParams, SlotParams, ContentParams, WinMovieName)

        if MazeScreensManager._checkGraph(settings) is False:
            return False

        if MazeScreensManager._checkObjects(settings) is False:
            return False

        MazeScreensManager.s_enigmas[enigma_name] = settings

        return True

    @staticmethod
    def _loadGraphParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)
        if records is None:
            return None

        data = []

        for record in records:
            Cells = [str(cell) for cell in record.get("Cells", [])]

            data.append(Cells)

        param = MazeScreensManager.GraphParam(data)

        return param

    @staticmethod
    def _loadRoomParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)
        if records is None:
            return None

        rooms = {}

        for record in records:
            param = MazeScreensManager.RoomParam(record)

            if param.id in rooms:
                Trace.log("Manager", 0, "MazeScreensManager duplicate room id {!r}".format(param.id))
                continue

            rooms[param.id] = param

        return rooms

    @staticmethod
    def _loadContentParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)
        if records is None:
            return None

        contents = {}
        for record in records:
            ContentId = str(record["ContentId"])
            ContentName = record["ContentName"]

            if ContentId in contents:
                Trace.log("Manager", 0, "MazeScreensManager duplicate content id {!r}".format(ContentId))
                continue

            contents[ContentId] = ContentName

        return contents

    @staticmethod
    def _loadSlotParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)
        if records is None:
            return None

        content_slots = {}
        for record in records:
            param = MazeScreensManager.SlotParam(record)

            content_slots.setdefault(param.content_id, []).append(param)

        return content_slots

    # load validation

    @staticmethod
    def _checkObjects(settings):
        if _DEVELOPMENT is False:
            return True

        is_valid = True
        demon = EnigmaManager.getEnigmaObject(settings.enigma_name)

        # general

        if settings.win_movie_name is not None and demon.hasObject(settings.win_movie_name) is False:
            Trace.log("Manager", 0, "MazeScreensManager [err] Win Movie2 (not prototype) {!r} not found in demon"
                      .format(settings.win_movie_name))

        # contents

        for content_id, content_name in settings.contents.items():
            if demon.hasPrototype(content_name) is False:
                Trace.log("Manager", 0, "MazeScreensManager [err] content [{}] prototype {!r} not found"
                          .format(content_id, content_name))
                is_valid = False

        # rooms

        start_rooms_count = 0
        for room in settings.rooms.values():
            if room.content_id not in settings.contents:
                Trace.log("Manager", 0, "MazeScreensManager [err] room [{}] content id {!r} not found"
                          .format(room.id, room.content_id))
                is_valid = False

            if room.is_start is True:
                start_rooms_count += 1

        if start_rooms_count != 1:
            Trace.log("Manager", 0, "MazeScreensManager only 1 room should be as start! Found {} start rooms"
                      .format(start_rooms_count))
            return None

        # slots

        for content_id, slots in settings.slots.items():
            if content_id not in settings.contents:
                Trace.log("Manager", 0, "MazeScreensManager [err] some slots (x{}) attached to unknown content id {!r}"
                          .format(len(slots), content_id))
                is_valid = False

            for slot in slots:
                if MazeScreensManager._checkSlotParam(slot, demon) is False:
                    is_valid = False

        return is_valid

    @staticmethod
    def _checkSlotParam(param, demon):
        is_valid = True

        if MSObject.isValid(param.object_type) is False:
            Trace.log("Manager", 0, "MazeScreensManager [err] SlotParam [{}:{}] invalid object_type {!r}"
                      .format(param.content_id, param.name, param.object_type))
            is_valid = False

        if param.transition_way is not None:
            if MSTransition.isValid(param.transition_way) is False:
                Trace.log("Manager", 0, "MazeScreensManager [err] SlotParam [{}:{}] invalid transition_way {!r}"
                          .format(param.content_id, param.name, param.transition_way))
                is_valid = False

        def _hasPrototype(prototype_name):
            if demon.hasPrototype(prototype_name) is False:
                Trace.log("Manager", 0, "MazeScreensManger [err] SlotParam [{}:{}] not found Prototype {!r} in {!r}"
                          .format(param.content_id, param.name, prototype_name, demon.getName()))
                return False
            return True

        def _checkLever(name):
            return all([_hasPrototype(name + "_" + state) for state in ("Ready", "Use", "Done")])
        def _checkGate(name):
            return all([_hasPrototype(name + "_" + state) for state in ("Close", "Opening", "Open")])
        def _checkTransition(name):
            return _hasPrototype(name)

        checkers = {
            MSObject.Lever: _checkLever,
            MSObject.Gate: _checkGate,
            MSObject.Transition: _checkTransition,
        }
        checker = checkers[param.object_type]
        if checker(param.prototype_name) is False:
            is_valid = False

        return is_valid

    @staticmethod
    def _checkGraph(settings):
        if _DEVELOPMENT is False:
            return True

        is_valid = True

        for row in settings.graph.data:
            for i, cell_id in enumerate(row):
                if cell_id == MazeScreensManager.CELL_TYPE_WALL:
                    continue

                if cell_id not in settings.rooms:
                    Trace.log("Manager", 0, "MazeScreensManager [err] invalid cell id {!r} at ({}, {})"
                              .format(cell_id, row, i))
                    is_valid = False

        return is_valid

    # public

    @staticmethod
    def getSettings(enigma_name):
        return MazeScreensManager.s_enigmas.get(enigma_name)

    @staticmethod
    def getEnigmaRooms(enigma_name):
        settings = MazeScreensManager.getSettings(enigma_name)
        return settings.rooms

    @staticmethod
    def getRoomParams(enigma_name, room_id):
        rooms = MazeScreensManager.getEnigmaRooms(enigma_name)
        room = rooms.get(room_id)
        return room

    @staticmethod
    def getEnigmaSlots(enigma_name):
        settings = MazeScreensManager.getSettings(enigma_name)
        return settings.slots

    @staticmethod
    def getContentSlots(enigma_name, content_id):
        settings = MazeScreensManager.getSettings(enigma_name)
        slots = settings.slots.get(content_id)
        return slots

    @staticmethod
    def getContentName(enigma_name, content_id):
        settings = MazeScreensManager.getSettings(enigma_name)
        name = settings.contents.get(content_id)
        return name

    @staticmethod
    def getEnigmaGraph(enigma_name):
        settings = MazeScreensManager.getSettings(enigma_name)
        return settings.graph


