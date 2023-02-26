import Trace

from Foundation.DatabaseManager import DatabaseManager

class RotateAndSwapChipsManager(object):
    s_games = {}

    class RotateAndSwapChipsGame(object):
        def __init__(self, chips, slots, connections, rules, connectionsSlots, slotsControllers):
            self.chips = chips
            self.slots = slots
            self.connections = connections
            self.rules = rules
            self.connectionsSlots = connectionsSlots
            self.slotsControllers = slotsControllers
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            Slots = record.get("Slots")
            Rules = record.get("Rules")
            Chips = record.get("Chips")
            Connections = record.get("Connections")
            ConnectionsSlots = record.get("ConnectionsSlots")
            SlotsControllers = record.get("SlotsControllers")

            RotateAndSwapChipsManager.loadGame(Name, module, Chips, Slots, Connections, Rules, ConnectionsSlots, SlotsControllers)
            pass

        return True
        pass

    @staticmethod
    def loadGame(name, module, Chips, Slots, Connections, Rules, ConnectionsSlots, SlotsControllers):
        chips = RotateAndSwapChipsManager.loadGameChips(module, Chips)
        slots = RotateAndSwapChipsManager.loadGameSlots(module, Slots)
        connections = RotateAndSwapChipsManager.loadGameConnections(module, Connections)
        rules = RotateAndSwapChipsManager.loadGameRules(module, Rules)
        connectionsSlots = RotateAndSwapChipsManager.loadGameConnectionsSlots(module, ConnectionsSlots)
        slotsControllers = RotateAndSwapChipsManager.loadGameSlotsControllers(module, SlotsControllers)

        game = RotateAndSwapChipsManager.RotateAndSwapChipsGame(chips, slots, connections, rules, connectionsSlots, slotsControllers)
        RotateAndSwapChipsManager.s_games[name] = game
        return game
        pass

    @staticmethod
    def loadGameChips(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        chips = {}
        for record in records:
            chipId = record.get("ChipId")
            statesObjectName = record.get("StatesObjectName")
            startAngle = record.get("StartAngle")
            startSlotId = record.get("StartSlotId")
            chips[chipId] = dict(StatesObjectName=statesObjectName, StartAngle=startAngle, StartSlotId=startSlotId)
            pass
        return chips
        pass

    @staticmethod
    def loadGameSlots(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        slots = {}
        for record in records:
            SlotId = record.get("SlotId")
            MovieSlotName = record.get("MovieSlotName")
            ButtonCW = record.get("ButtonCW")
            ButtonCCW = record.get("ButtonCCW")

            slots[SlotId] = dict(MovieSlotName=MovieSlotName, ButtonCW=ButtonCW, ButtonCCW=ButtonCCW)
            pass
        return slots
        pass

    @staticmethod
    def loadGameConnections(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        connections = {}
        for record in records:
            connectionId = record.get("ConnectionId")
            movieObjectName = record.get("MovieObjectName")
            connections[connectionId] = dict(MovieObjectName=movieObjectName)
            pass
        return connections
        pass

    @staticmethod
    def loadGameConnectionsSlots(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        connectionsSlots = {}
        for record in records:
            connectionId = record.get("ConnectionId")
            slotId = record.get("SlotId")
            MovieSlotName = record.get("MovieSlotName")

            slot = dict(SlotId=slotId, MovieSlotName=MovieSlotName)
            connectionsSlots.setdefault(connectionId, []).append(slot)
            pass
        return connectionsSlots
        pass

    @staticmethod
    def loadGameRules(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        rules = {}
        for record in records:
            SlotId = record.get("SlotId")
            ChipId = record.get("ChipId")
            Angle = record.get("Angle")

            rules[ChipId] = dict(SlotId=SlotId, Angle=Angle)
            pass
        return rules
        pass

    @staticmethod
    def loadGameSlotsControllers(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        slotsControllers = {}
        for record in records:
            ControllerId = record.get("ControllerId")
            SlotId = record.get("SlotId")
            DeltaAngle = record.get("DeltaAngle")
            ButtonName = record.get("ButtonName")

            slotsControllers[ControllerId] = dict(SlotId=SlotId, DeltaAngle=DeltaAngle, ButtonName=ButtonName)
            pass
        return slotsControllers
        pass

    @staticmethod
    def getGame(name):
        if name not in RotateAndSwapChipsManager.s_games:
            Trace.log("Manager", 0, "RotateAndSwapChipsManager.getGame: not found game %s" % (name))
            return None
            pass
        game = RotateAndSwapChipsManager.s_games[name]
        return game
        pass

    @staticmethod
    def hasGame(name):
        return name in RotateAndSwapChipsManager.s_games
        pass

    pass