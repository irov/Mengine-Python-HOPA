import Trace

from Foundation.DatabaseManager import DatabaseManager

class PathChipsCryptManager(object):
    s_games = {}

    class PathChipsCryptGame(object):
        def __init__(self, transporters, slots, rules, chips, completeEffects, connections):
            self.transporters = transporters
            self.slots = slots
            self.rules = rules
            self.chips = chips
            self.completeEffects = completeEffects
            self.connections = connections
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            TransportersParam = record.get("Transporters")
            SlotsParam = record.get("Slots")
            RulesParam = record.get("Rules")
            ChipsParam = record.get("Chips")
            ConnectionsParam = record.get("Connections")
            CompleteEffects = record.get("CompleteEffects")

            PathChipsCryptManager.loadGame(module, Name, ChipsParam, SlotsParam, ConnectionsParam, TransportersParam, RulesParam, CompleteEffects)
            pass

        return True
        pass

    @staticmethod
    def loadGame(module, name, ChipsParam, SlotsParam, ConnectionsParam, TransportersParam, RulesParam, CompleteEffectsParam):
        chips = PathChipsCryptManager.loadGameChips(module, ChipsParam)
        slots = PathChipsCryptManager.loadGameSlots(module, SlotsParam)
        connections = PathChipsCryptManager.loadGameConnections(module, ConnectionsParam)
        transporters = PathChipsCryptManager.loadGameTransporters(module, TransportersParam)
        rules = PathChipsCryptManager.loadGameRules(module, RulesParam)
        completeEffects = PathChipsCryptManager.loadGameCompleteEffects(module, CompleteEffectsParam)

        game = PathChipsCryptManager.PathChipsCryptGame(transporters, slots, rules, chips, completeEffects, connections)
        PathChipsCryptManager.s_games[name] = game
        pass

    @staticmethod
    def loadGameChips(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        chips = {}
        for record in records:
            chipId = record.get("ChipId")
            objectName = record.get("ObjectName")
            movingPolicy = record.get("MovingPolicy")
            chips[chipId] = dict(ObjectName=objectName, MovingPolicy=movingPolicy)
            pass
        return chips
        pass

    @staticmethod
    def loadGameSlots(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        slots = {}
        for record in records:
            SlotId = record.get("SlotId")
            ChipId = record.get("ChipId")
            slots[SlotId] = ChipId
            pass
        return slots
        pass

    @staticmethod
    def loadGameConnections(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        connections = []
        for record in records:
            SlotFrom = record.get("SlotFrom")
            SlotTo = record.get("SlotTo")
            ObjectName = record.get("ObjectName")
            connection = (SlotFrom, SlotTo, ObjectName)
            connections.append(connection)
            pass
        return connections
        pass

    @staticmethod
    def loadGameTransporters(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        transporters = []
        for record in records:
            SlotFrom = record.get("SlotFrom")
            SlotTo = record.get("SlotTo")
            ObjectName = record.get("ObjectName")
            ActiveSlot = record.get("ActiveSlot")

            transporter = (SlotFrom, SlotTo, ActiveSlot, ObjectName)
            transporters.append(transporter)
            pass
        return transporters
        pass

    @staticmethod
    def loadGameRules(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        rules = {}
        for record in records:
            SlotId = record.get("SlotId")
            ChipId = record.get("ChipId")
            rules.setdefault(SlotId, []).append(ChipId)
            pass
        return rules
        pass

    @staticmethod
    def loadGameCompleteEffects(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        completeEffects = {}
        for record in records:
            SlotId = record.get("SlotId")
            objectName = record.get("ObjectName")
            groupName = record.get("GroupName")
            completeEffects[SlotId] = dict(ObjectName=objectName, GroupName=groupName)
            pass
        return completeEffects
        pass

    @staticmethod
    def getGame(name):
        if name not in PathChipsCryptManager.s_games:
            Trace.log("Manager", 0, "PathChipsCryptManager.getGame: not found game %s" % (name))
            return None
            pass
        game = PathChipsCryptManager.s_games[name]
        return game
        pass

    @staticmethod
    def hasGame(name):
        return name in PathChipsCryptManager.s_games
        pass

    pass