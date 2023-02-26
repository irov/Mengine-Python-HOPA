from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager
from Notification import Notification

class DragMiniSystem(object):

    def __init__(self):
        self.circles = {}  # {"ConstBehavior" :[], "SituatedBehavior":[]}
        self.group = None
        self.sockets = {}
        self.item_list = []
        self.clean_list = []
        self.slots = {}
        self.item_map = {}  # item in some node
        self.win_list = []
        pass

    class Slot(object):
        def __init__(self, slotNode, item, final_item):
            self.node = slotNode
            self.item = item or None
            self.final_item = final_item
            pass

        def getItem(self):
            return self.item
            pass

        def setItem(self, item):
            self.item = item
            pass

        def hasItem(self, itemEntity):
            if self.item is None:  # empty slot
                return False
                pass

            selfType, foreignType = type(self.item), type(itemEntity)
            if selfType != foreignType:  # if looking smth wrong
                Trace.log("System", 0, "Slot.hasItem look for wrong item type %s %s" % (foreignType, selfType))
                return False

            return self.item is itemEntity
            pass

        def getNode(self):
            return self.node
            pass

        def isEmpty(self):
            return self.item is None
            pass

        def swap(self, antherSlot):
            if antherSlot is self:
                return

            if antherSlot.isEmpty() is False:
                return
            node = antherSlot.getNode()
            self.item.removeFromParent()
            node.addChild(self.item)
            antherSlot.setItem(self.item)
            self.item = None
            pass

        def in_final(self):
            if self.item is self.final_item and self.item is not None:
                #                print self.final_item.getObject().getName(), "in Final"
                return True
                pass

            return False
            pass

        pass

    def load(self, circlesBehaviorDict):
        self.circles = circlesBehaviorDict
        self.bound_slots()
        pass

    def setup(self, group, item_list, win_list):
        self.group = group
        self.item_list = item_list
        self.win_list = win_list
        pass

    def bound_slots(self):
        for circle_list in self.circles.values():
            for circle in circle_list:
                slots = circle.getCountSlots()
                if not circle.isSituated():
                    prefix = "Inner_Socket"
                else:
                    prefix = "Ex_Socket"

                movie = circle.getMovie()
                movieEn = movie.getEntity()
                if prefix not in self.slots:
                    self.slots[prefix] = []
                    pass

                for slotInt in range(slots):
                    cs_id = "%d" % (slotInt,)
                    gen_socked = self.group.generateObject("%s%d" % (prefix, slotInt), "Socket_Slot")
                    socketEn = gen_socked.getEntity()
                    slotNode = movieEn.getMovieSlot(cs_id)
                    slotNode.addChild(socketEn)
                    gen_socked.setPosition((0, 0))
                    #                    gen_socked.setBlock(True)
                    gen_socked.setInteractive(True)

                    itemEn, final_En = None, None
                    if prefix == "Ex_Socket":
                        item_name = self.item_list[slotInt]
                        #
                        final_item_name = self.win_list[slotInt]
                        final_item = self.group.getObject(final_item_name)
                        final_En = final_item.getEntity()

                        item = self.group.getObject(item_name)
                        itemEn = item.getEntity()
                        slotNode.addChild(itemEn)
                        item.setPosition((0, 0))
                        self.clean_list.append(itemEn)

                    self.clean_list.append(socketEn)
                    #                    if itemEn:
                    #                        print slotInt,itemEn.getObject().getName(), final_En.getObject().getName()
                    node = self.Slot(slotNode, itemEn, final_En)
                    self.slots[prefix].append(node)
                    self.sockets[gen_socked] = node
                    pass
                pass
            pass
        pass

    def unbound_slots(self):
        for child in self.clean_list:
            child.removeFromParent()
            pass

        self.clean_list = []

        for gen_socked in self.sockets.iterkeys():
            gen_socked.removeFromParent()
            pass

        self.sockets = {}
        self.item_list = []
        self.sockets = {}
        self.slots = {}
        self.item_map = {}
        for behaviour_list in self.circles.values():
            behaviour_list[:] = []
            pass
        pass

    def getSlotSockets(self):
        return self.sockets.keys()

    def getSocketIndex(self, socket):  # smell bugs
        slot = self.sockets[socket]
        if slot in self.slots["Ex_Socket"]:
            return self.slots["Ex_Socket"].index(slot)
        elif slot in self.slots["Inner_Socket"]:
            return self.slots["Inner_Socket"].index(slot)
        else:
            return False
        pass

    def revertIndex(self, socket, exIn, inIn):
        socketIn = self.slots["Inner_Socket"][inIn]
        socketEx = self.slots["Ex_Socket"][exIn]
        if socketEx == socket or socketIn == socket:
            return True
        return False

    def swapSlotsByNumber(self, numEx, numInt, movie, guide):
        speed = DefaultManager.getDefaultFloat("ZenSpeed", 1)
        speed *= 0.001  # speed fix
        movie.setSpeedFactor(speed)
        exSlot = self.slots["Ex_Socket"][numEx]
        inSlot = self.slots["Inner_Socket"][numInt]

        movieEn = movie.getEntity()
        slotNode = movieEn.getMovieSlot("0")

        MainMovie = self.circles['ConstBehavior'][0].getMovie()
        MovieEn = MainMovie.getEntity()
        id = "%d" % numInt
        MainNode = MovieEn.getMovieSlot(id)

        if movieEn not in self.clean_list:
            self.clean_list.append(movieEn)
            pass
        MainNode.addChild(movieEn)
        if inSlot.isEmpty() and not exSlot.isEmpty():
            slotNode.addChild(exSlot.getItem())
            with TaskManager.createTaskChain() as tc:
                tc.addTask("TaskMoviePlay", Movie=movie, Wait=True, Reverse=True)
                tc.addTask("TaskFunction", Fn=exSlot.swap, Args=(inSlot,))
                tc.addTask("TaskFunction", Fn=self.is_win)
                tc.addTask("TaskNotify", ID=Notificator.onEnigmaAction, Args=(False,))
            pass

        elif not inSlot.isEmpty() and exSlot.isEmpty():
            slotNode.addChild(inSlot.getItem())
            with TaskManager.createTaskChain() as tc:
                tc.addTask("TaskMoviePlay", Movie=movie, Wait=True, Reverse=False)
                tc.addTask("TaskFunction", Fn=inSlot.swap, Args=(exSlot,))
                tc.addTask("TaskFunction", Fn=self.is_win)
                tc.addTask("TaskNotify", ID=Notificator.onEnigmaAction, Args=(False,))
            pass
        else:
            self.is_win()
            Notification.notify(Notificator.onEnigmaAction, False)
            pass

        pass

    def is_win(self):
        for slot in self.slots["Ex_Socket"]:
            if slot.in_final() is False:
                return False
                pass
            pass
        Notification.notify(Notificator.onEnigmaSkip)
        return True
        pass

    def save_progres(self):
        save_dict = {}  # "socket name:item name"
        for socket_object, slotInstance in self.sockets.items():
            socketName = socket_object.getName()
            itemEn = slotInstance.getItem()
            if itemEn is None:
                continue
            item_object = itemEn.getObject()
            item_name = item_object.getName()
            save_dict[socketName] = item_name
            pass
        return save_dict
        pass

    def restore_progress(self, save_dict):
        for socket_object, slotInstance in self.sockets.items():
            socketName = socket_object.getName()
            itemName = save_dict.get(socketName)
            if itemName is None:
                continue

            itemObject = self.group.getObject(itemName)
            itemEn = itemObject.getEntity()
            HoldSlotInstance = self.findNodeByItem(itemEn)
            HoldSlotInstance.swap(slotInstance)
            pass
        pass

    def findNodeByItem(self, itemEntity):
        for slotInstance in self.sockets.values():
            holdingItem = slotInstance.hasItem(itemEntity)
            if holdingItem is True:
                return slotInstance
        return None