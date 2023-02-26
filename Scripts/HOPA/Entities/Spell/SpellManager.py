from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class SpellManager(object):
    """
    deprecated
    """
    s_objects = {}
    s_ids = {}
    s_obj = {}
    s_cost = {}

    class SpellData(object):
        def __init__(self, socket, sprite, locked, prepared, ready, active, charge, use, invalid, overview, idle, hide, show, down):
            self.socket = socket
            self.sprite = sprite
            self.locked = locked
            self.prepared = prepared
            self.ready = ready
            self.active = active
            self.charge = charge
            self.use = use
            self.invalid = invalid
            self.overview = overview

            self.idle = idle
            self.hide = hide
            self.show = show
            self.down = down
            pass

        def getSocket(self):
            return self.socket
            pass

        def getLocked(self):
            return self.locked
            pass

        def getPrepared(self):
            return self.prepared
            pass

        def getActive(self):
            return self.active
            pass

        def getOverview(self):
            return self.overview
            pass

        def getReady(self):
            return self.ready
            pass

        def getCharge(self):
            return self.charge
            pass

        def getUse(self):
            return self.use
            pass

        def getInvalidUse(self):
            return self.invalid
            pass

        def getSprite(self):
            return self.sprite
            pass

        def getIdle(self):
            return self.idle
            pass

        def getHide(self):
            return self.hide
            pass

        def getShow(self):
            return self.show
            pass

        def getDown(self):
            return self.down
            pass

        pass

    @staticmethod
    def _onFinalize():
        SpellManager.s_objects = {}
        SpellManager.s_ids = {}
        SpellManager.s_cost = {}
        SpellManager.s_obj = {}
        pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            SpellID = values.get("SpellID")
            GroupName = values.get("GroupName")
            ObjectName = values.get("ObjectName")
            spellDemon = GroupManager.getObject(GroupName, ObjectName)

            Socket = None
            SocketName = values.get("SocketName")
            if SocketName is not None:
                Socket = spellDemon.getObject(SocketName)
                pass
            Sprite = None
            SpriteName = values.get("SpriteName")
            if SpriteName is not None:
                Sprite = spellDemon.getObject(SpriteName)
                pass
            LockedMovie = None
            LockedMovieName = values.get("LockedMovieName")
            if LockedMovieName is not None:
                LockedMovie = spellDemon.getObject(LockedMovieName)
                pass
            ReadyMovie = None
            ReadyMovieName = values.get("ReadyMovieName")
            if ReadyMovieName is not None:
                ReadyMovie = spellDemon.getObject(ReadyMovieName)
                pass
            ActiveMovie = None
            ActiveMovieName = values.get("ActiveMovieName")
            if ActiveMovieName is not None:
                ActiveMovie = spellDemon.getObject(ActiveMovieName)
                pass
            PreparedMovie = None
            PreparedMovieName = values.get("PreparedMovieName")
            if PreparedMovieName is not None:
                PreparedMovie = spellDemon.getObject(PreparedMovieName)
                pass
            ChargeMovie = None
            ChargeMovieName = values.get("ChargeMovieName")
            if ChargeMovieName is not None:
                ChargeMovie = spellDemon.getObject(ChargeMovieName)
                pass
            UseMovie = None
            UseMovieName = values.get("UseMovieName")
            if UseMovieName is not None:
                UseMovie = spellDemon.getObject(UseMovieName)
                pass
            InvalidUseMovie = None
            InvalidUseMovieName = values.get("InvalidUseMovieName")
            if InvalidUseMovieName is not None:
                InvalidUseMovie = spellDemon.getObject(InvalidUseMovieName)
                pass
            TipOverviewMovie = None
            TipOverviewMovieName = values.get("OverviewMovieName")
            if TipOverviewMovieName is not None:
                TipOverviewMovie = spellDemon.getObject(TipOverviewMovieName)
                pass
            IdleMovie = None
            HideMovie = None
            ShowMovie = None
            DownMovie = None
            IdleMovieName = values.get("IdleMovieName")
            if IdleMovieName is not None:
                IdleMovie = spellDemon.getObject(IdleMovieName)
                pass
            HideMovieName = values.get("HideMovieName")
            if HideMovieName is not None:
                HideMovie = spellDemon.getObject(HideMovieName)
                pass
            ShowMovieName = values.get("ShowMovieName")
            if ShowMovieName is not None:
                ShowMovie = spellDemon.getObject(ShowMovieName)
                pass
            DownMovieName = values.get("DownMovieName")
            if DownMovieName is not None:
                DownMovie = spellDemon.getObject(DownMovieName)
                pass

            spell = SpellManager.SpellData(Socket, Sprite, LockedMovie, PreparedMovie, ReadyMovie, ActiveMovie, ChargeMovie, UseMovie, InvalidUseMovie, TipOverviewMovie, IdleMovie, HideMovie, ShowMovie, DownMovie)

            SpellManager.s_objects[ObjectName] = spell
            SpellManager.s_ids[SpellID] = spellDemon
            SpellManager.s_obj[spellDemon] = SpellID
            pass

        return True
        pass

    @staticmethod
    def loadSpellCost(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            SpellID = values.get("SpellID")
            Value = values.get("Value")

            SpellManager.s_cost[SpellID] = Value
            pass
        pass

    @staticmethod
    def getSpellCost(spellId):
        if SpellManager.hasSpellCost(spellId) is False:
            return None
            pass
        record = SpellManager.s_cost[spellId]
        return record
        pass

    @staticmethod
    def hasSpellCost(spellId):
        if spellId not in SpellManager.s_cost:
            return False
            pass
        return True
        pass

    @staticmethod
    def getSpellData(name):
        if SpellManager.hasSpellData(name) is False:
            return None
            pass
        record = SpellManager.s_objects[name]
        return record
        pass

    @staticmethod
    def getAllSpellData():
        return SpellManager.s_objects
        pass

    @staticmethod
    def hasSpellData(name):
        if name not in SpellManager.s_objects:
            Trace.log("SpellManager", 0, "SpellManager.hasSpellData: : invalid param")
            return False
            pass
        return True
        pass

    @staticmethod
    def getSpellObject(id):
        if SpellManager.hasSpellObject(id) is False:
            return None
            pass
        object = SpellManager.s_ids[id]
        return object
        pass

    @staticmethod
    def getAllSpellObjects():
        return SpellManager.s_ids
        pass

    @staticmethod
    def getSpellID(obj):
        if SpellManager.hasSpellID(obj) is False:
            return None
            pass
        id = SpellManager.s_obj[obj]
        return id
        pass

    @staticmethod
    def hasSpellObject(id):
        if id not in SpellManager.s_ids:
            Trace.log("SpellManager", 0, "SpellManager.hasSpellObject: : invalid param")
            return False
            pass
        return True
        pass

    @staticmethod
    def hasSpellID(obj):
        if obj not in SpellManager.s_obj:
            Trace.log("SpellManager", 0, "SpellManager.hasSpellID: : invalid param")
            return False
            pass
        return True
        pass
    pass