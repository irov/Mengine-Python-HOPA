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
        if type_ in (MSTransition.Up, MSTransition.Down, MSTransition.Right, MSTransition.Left, MSTransition.Win):
            return True
        return False


class MSObject(object):
    Lever = "lever"
    Gate = "gate"
    Transition = "transition"

    @staticmethod
    def isValid(type_):
        if type_ in (MSObject.Lever, MSObject.Gate, MSObject.Transition):
            return True
        return False


class MazeScreensManager(Manager):

    CELL_TYPE_WALL = "X"
    s_enigmas = {}  # { enigma_name: Settings }

    class Settings(object):
        def __init__(self, EnigmaName, Graph, Rooms, ContentSlots):
            self.enigma_name = EnigmaName
            self.graph = Graph              # GraphParam
            self.rooms = Rooms              # { room_id: RoomParam }
            self.contents = ContentSlots    # { content_name: SlotParam[] }

    class RoomParam(object):
        def __init__(self, record):
            '''
                RoomId – числовой идентификатор комнаты
                ContentName – имя муви2 со слотами и задним фоном (можно анимировать)
                IsStart - является ли комната стартовой позицией
            '''
            self.id = MazeScreensManager.getRecordValue(record, "RoomId", cast=str, required=True)
            self.content_name = MazeScreensManager.getRecordValue(record, "ContentName", required=True)
            self.is_start = MazeScreensManager.getRecordValue(record, "IsStart", cast=bool, default=False)

    class SlotParam(object):
        def __init__(self, record):
            '''
                ContentName – имя “наполнителя” комнаты (муви2 со слотами).
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
            self.content_name = MazeScreensManager.getRecordValue(record, "ContentName", required=True)
            self.name = MazeScreensManager.getRecordValue(record, "SlotName", required=True)
            self.object_type = MazeScreensManager.getRecordValue(record, "ObjectType", required=True)
            self.prototype_name = MazeScreensManager.getRecordValue(record, "PrototypeName", required=True)

            self.group_id = None
            if self.object_type in [MSObject.Gate, MSObject.Lever]:
                self.group_id = MazeScreensManager.getRecordValue(record, "GroupId", required=True)

            self.transition_way = None
            if self.object_type == "transition":
                self.transition_way = MazeScreensManager.getRecordValue(record, "TransitionWay", required=True)

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

            result = MazeScreensManager.loadParam(module, EnigmaName, record)

            if result is False:
                Trace.log("Manager", 0, "MazeScreensManager fail to load params for {!r}".format(EnigmaName))
                return False

        return True

    @staticmethod
    def loadParam(module, enigma_name, record):

        RoomParamsName = record.get("RoomParams")
        RoomParams = MazeScreensManager._loadRoomParams(module, RoomParamsName, enigma_name)

        SlotParamsName = record.get("SlotParams")
        SlotParams = MazeScreensManager._loadSlotParams(module, SlotParamsName, enigma_name)

        GraphParamsName = record.get("GraphParams")
        GraphParams = MazeScreensManager._loadGraphParams(module, GraphParamsName, enigma_name)

        settings = MazeScreensManager.Settings(enigma_name, GraphParams, RoomParams, SlotParams)

        if MazeScreensManager._checkObjects(settings) is False:
            return False

        MazeScreensManager.s_enigmas[enigma_name] = settings

        return True

    @staticmethod
    def _loadGraphParams(module, name, enigma_name):
        records = DatabaseManager.getDatabaseRecords(module, name)
        if records is None:
            return None

        data = []

        for record in records:
            row = record.get("row")
            Cells = record.get("Cells", [])

            if _DEVELOPMENT:
                rooms = MazeScreensManager.getEnigmaRooms(enigma_name)

                is_valid = True

                for cell_id in Cells:
                    if cell_id == MazeScreensManager.CELL_TYPE_WALL:
                        continue

                    if cell_id not in rooms:
                        Trace.log("Manager", 0, "MazeScreensManager invalid cell id {!r} at {}".format(cell_id, row))
                        is_valid = False
                        continue

                    if is_valid is False:
                        continue

            data.append(Cells)

        param = MazeScreensManager.GraphParam(data)

        return param

    @staticmethod
    def _loadRoomParams(module, name, enigma_name):
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

        if _DEVELOPMENT is True:
            start_rooms_count = len([room for room in rooms.values() if room.is_start is True])
            if start_rooms_count != 1:
                Trace.log("Manager", 0, "MazeScreensManager only 1 room should be as start! Found {} rooms".format(start_rooms_count))
                return None

        return rooms

    @staticmethod
    def _loadSlotParams(module, name, enigma_name):
        records = DatabaseManager.getDatabaseRecords(module, name)
        if records is None:
            return None

        content_slots = {}
        for record in records:
            param = MazeScreensManager.SlotParam(record)

            is_valid = True

            if MSObject.isValid(param.object_type) is False:
                Trace.log("Manager", 0, "MazeScreensManager invalid object_type {!r}".format(param.object_type))
                is_valid = False

            if param.transition_way is not None:
                if MSTransition.isValid(param.transition_way) is False:
                    Trace.log("Manager", 0, "MazeScreensManager invalid transition_way {!r}".format(param.transition_way))
                    is_valid = False

            if is_valid is False:
                continue

            content_slots.setdefault(param.content_name, []).append(param)

        return content_slots

    @staticmethod
    def _checkObjects(settings):
        if _DEVELOPMENT is False:
            return True

        demon = EnigmaManager.getEnigmaObject(settings.enigma_name)

        for room in settings.rooms.values():
            if demon.hasPrototype(room.environment_movie) is False:
                Trace.log("Manager", 0, "MazeScreensManager room {!r}: environment prototype {!r} not found"
                          .format(room.id, room.environment_movie))

        for content_name in settings.contents.keys():
            if demon.hasPrototype(content_name) is False:
                Trace.log("Manager", 0, "MazeScreensManager content with name {!r} not found prototype".format(content_name))

        return True

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
    def getEnigmaContents(enigma_name):
        settings = MazeScreensManager.getSettings(enigma_name)
        return settings.contents

    @staticmethod
    def getContentSlots(enigma_name, content_name):
        settings = MazeScreensManager.getSettings(enigma_name)
        content_slots = settings.contents.get(content_name)
        return content_slots

    @staticmethod
    def getEnigmaGraph(enigma_name):
        settings = MazeScreensManager.getSettings(enigma_name)
        return settings.graph


