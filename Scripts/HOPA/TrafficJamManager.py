from Foundation.DatabaseManager import DatabaseManager
from HOPA.EnigmaManager import EnigmaManager


class TrafficJamManager(object):
    s_trafficjams = {}

    class TrafficJam(object):
        def __init__(self, elements, sceneName, group, obj):
            self.elements = elements
            self.sceneName = sceneName
            self.group = group
            self.obj = obj

    class TrafficElement(object):
        def __init__(self, sprite, horizontal, size, pos, main):
            self.sprite = sprite
            self.horizontal = horizontal
            self.size = size
            self.pos = pos
            self.main = main

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            Param = record.get("Param")

            hog = TrafficJamManager.loadTrafficJam(Name, module, Param)

            if hog is None:
                Trace.log("HOGManager", 0, "TrafficJamManager.loadPuzzles: invalid load puzzle %s" % (Name))
                return False

        return True

    @staticmethod
    def loadTrafficJam(name, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        elements = []
        for record in records:
            Item = record.get("Item")
            Horizontal = bool(record.get("Horizontal"))
            Size = record.get("Size")
            X = record.get("X")
            Y = record.get("Y")
            Main = bool(record.get("Main"))

            te = TrafficJamManager.TrafficElement(Item, Horizontal, Size, (X, Y), Main)
            elements.append(te)
            pass

        trafficjam_obj = EnigmaManager.getEnigmaObject(name)
        trafficjam_group = trafficjam_obj.getGroup()
        sceneName = EnigmaManager.getEnigmaSceneName(name)

        trafficjam = TrafficJamManager.TrafficJam(elements, sceneName, trafficjam_group, trafficjam_obj)

        TrafficJamManager.s_trafficjams[name] = trafficjam

        return trafficjam
        pass

    @staticmethod
    def getTrafficJam(name):
        if name not in TrafficJamManager.s_trafficjams:
            Trace.log("Manager", 0, "TrafficJamManager.getTrafficJam: not found trafficjam %s" % (name))
            return None
            pass

        trafficjam = TrafficJamManager.s_trafficjams[name]

        return trafficjam
        pass

    @staticmethod
    def hasTrafficJam(name):
        return name in TrafficJamManager.s_trafficjams
        pass

    @staticmethod
    def getTrafficJamObject(name):
        desc = TrafficJamManager.getTrafficJam(name)

        if desc is None:
            return None
            pass

        return desc.obj
        pass

    @staticmethod
    def getPuzzleElement(name):
        desc = TrafficJamManager.getTrafficJam(name)

        if desc is None:
            return None
            pass

        return desc.elements
