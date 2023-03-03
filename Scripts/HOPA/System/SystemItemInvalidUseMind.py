from Foundation.DatabaseManager import DatabaseManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.MindBranchManager import MindBranchManager
from Notification import Notification


class SystemItemInvalidUseMind(System):
    def __init__(self):
        super(SystemItemInvalidUseMind, self).__init__()

        self.mindIDs = []

        self.Module = None
        self.Param = None

        self.CurrentMindID = 0

        self.observe_sockets = {}
        self.Item_Socket = [None, None]
        pass

    def _onParams(self, params):
        super(SystemItemInvalidUseMind, self)._onParams(params)

        self.Module = params.get("Module", "Database")
        self.Param = params.get("Param", "ItemInvalidUseMind")
        pass

    def _onInitialize(self):
        super(SystemItemInvalidUseMind, self)._onInitialize()

        records = DatabaseManager.getDatabaseRecords(self.Module, self.Param)

        for record in records:
            MindIDs = record.get("MindIDs")

            self.mindIDs.append(MindIDs)
            pass
        pass

    def _onRun(self):
        branch_instances = MindBranchManager.gets_all()
        self.observe_sockets = dict((branch.SocketName, branch) for branch in branch_instances)

        self.addObserver(Notificator.onInventoryItemInvalidUse, self.__onItemInvalidUse)
        self.addObserver(Notificator.onItemInvalidUse, self.__onItemHOInvalidUse)

        self.addObserver(Notificator.onSocketUseItemInvalidUse, self.__onItemInvalidUse)

        return True
        pass

    def _onStop(self):
        pass

    def Invalid_Use(self):
        rand = Mengine.rand(len(self.mindIDs) - 1)
        mind = self.mindIDs[rand]

        with TaskManager.createTaskChain(Name="ItemInvalidUseMind") as tc:
            tc.addTask("AliasMindPlay", MindID=mind)

    def __onItemHOInvalidUse(self, item=0, socket='0'):
        ItemName = item.getName()
        self.Item_Socket[0] = ItemName
        # print " __onItemHOInvalidUse", ItemName, " "
        return False

    def __onItemInvalidUse(self, item, clickObject):
        SocketName = clickObject.getName()
        self.Item_Socket[1] = SocketName

        if item != None:
            ItemName = item.getName()
            self.Item_Socket[0] = ItemName
        # print "__onItemInvalidUse",self.Item_Socket[0], self.Item_Socket[1]

        # print "SystemItemInvalidUseMind __onItemInvalidUse", SocketName,
        if TaskManager.existTaskChain("ItemInvalidUseMind"):
            TaskManager.cancelTaskChain("ItemInvalidUseMind")
            pass

        mind = self.mindIDs[self.CurrentMindID]

        if len(self.mindIDs) <= self.CurrentMindID + 1:
            self.CurrentMindID = 0
            pass
        else:
            self.CurrentMindID = self.CurrentMindID + 1
            pass

        # print "0", self.Item_Socket[1], self.observe_sockets
        if self.Item_Socket[1] in self.observe_sockets:
            data = self.observe_sockets[SocketName]
            Item = data.getItemName()
            i = 0
            # while self.Item_Socket[0] is None:
            #     print "Optimal solution", i
            #     i += 1
            #     if i > 1000:
            #         return False
            # print Item, self.Item_Socket[0]
            if Item is self.Item_Socket[0]:
                mind = data.getMind()
                # print "mind", mind
                Notification.notify(Notificator.onTipShow, mind)
                # Notification.notify(Notificator.onGroupEnable, data.getGroupName(), True)
                # self.Item_Socket = [None, None]
            else:
                self.Invalid_Use()

                pass
            pass
        else:
            self.Invalid_Use()

        self.Item_Socket = [None, None]
        return False
        pass

    pass
