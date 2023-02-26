import Trace
from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from HOPA.EnigmaManager import EnigmaManager

class SwitchChainsManager(object):
    s_switchChains = {}

    class SwitchChain(object):
        def __init__(self, switches, sceneName, group, demon, startOn):
            self.switches = switches
            self.sceneName = sceneName
            self.group = group
            self.demon = demon
            self.startOn = startOn
            pass
        pass

    @staticmethod
    def onFinalize():
        SwitchChainsManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ID = record.get("ID")
            Param = record.get("Param")
            startOn = record.get("startOn")

            switchChain = SwitchChainsManager.loadSwitchChain(ID, module, Param, startOn)

            if switchChain is None:
                Trace.log("HOGManager", 0, "SwitchChainsManager.loadPuzzles: invalid loadSwitchChain")
                return False
                pass

            SwitchChainsManager.s_switchChains[ID] = switchChain
            pass

        return True
        pass

    @staticmethod
    def loadSwitchChain(ID, module, param, startOn):
        records = DatabaseManager.getDatabaseRecords(module, param)

        switches = {}

        for record in records:
            Switch = record.get("Switch")
            Chains = record.get("Chains")

            switches[Switch] = Chains
            pass

        SceneName = EnigmaManager.getEnigmaSceneName(ID)
        GroupName = EnigmaManager.getEnigmaGroupName(ID)

        demon = EnigmaManager.getEnigmaObject(ID)

        group = GroupManager.getGroup(GroupName)

        switchChain = SwitchChainsManager.SwitchChain(switches, SceneName, group, demon, startOn)
        return switchChain
        pass

    @staticmethod
    def hasSwitchChain(id):
        return id in SwitchChainsManager.s_switchChains
        pass

    @staticmethod
    def getSwitchChain(id):
        switchChainObject = SwitchChainsManager.s_switchChains[id]
        demon = switchChainObject.demon

        return demon
        pass

    @staticmethod
    def getSwitchChainObjects(id):
        switchChainObject = SwitchChainsManager.s_switchChains[id]
        switches = switchChainObject.switches

        return switches
        pass

    @staticmethod
    def getStartOn(id):
        switchChainObject = SwitchChainsManager.s_switchChains[id]
        startOn = switchChainObject.startOn

        return startOn
        pass

    @staticmethod
    def getSwitchChainGroup(id):
        switchChainObject = SwitchChainsManager.s_switchChains[id]
        group = switchChainObject.group

        return group
        pass

    @staticmethod
    def getSceneName(id):
        switchChainObject = SwitchChainsManager.s_switchChains[id]
        sceneName = switchChainObject.sceneName

        return sceneName
        pass

    pass

pass