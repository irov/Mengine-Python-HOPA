from Foundation.TaskManager import TaskManager
from HOPA.ZenElementsManager import ZenElementsManager

from Circle import Circle
from DragMiniSystem import DragMiniSystem
from RotateMiniSystem import RotateMiniSystem

Enigma = Mengine.importEntity("Enigma")

class ZenElements(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "ItemParentMap")
        Type.addAction(Type, "Frames")
        pass

    def __init__(self):
        super(ZenElements, self).__init__()
        self.socket_ref = {}
        self.DragSystemInstance = None
        self.RotateSystemInstance = None
        self.InteractionBlock = False
        pass

    def _onDeactivate(self):
        super(ZenElements, self)._onDeactivate()
        self.DragSystemInstance = None
        self.RotateSystemInstance = None
        pass

    def _stopEnigma(self):
        self.saveProgress()
        self.DragSystemInstance.unbound_slots()
        if TaskManager.existTaskChain(self.EnigmaName):
            TaskManager.cancelTaskChain(self.EnigmaName)
            pass
        self.clearance()
        self.InteractionBlock = False
        pass

    def saveProgress(self):
        itemMapToParent = self.DragSystemInstance.save_progres()
        frames = self.RotateSystemInstance.save_progress()
        self.object.setParam("Frames", frames)
        self.object.setParam("ItemParentMap", itemMapToParent)
        pass

    def restoreProgress(self):
        if self.ItemParentMap != {}:
            self.DragSystemInstance.restore_progress(self.ItemParentMap)
            pass
        if self.Frames != {}:
            self.RotateSystemInstance.restore_progress(self.Frames)
            pass
        pass

    def _skipEnigma(self):
        self.__complete(True)
        pass

    def _playEnigma(self):
        self.preparation()
        with TaskManager.createTaskChain(Name=self.EnigmaName, Group=self.object, Cb=self.__complete) as tc:
            with tc.addRepeatTask() as (tc_do, tc_until):
                with tc_do.addParallelTask(2) as (tc_al, tc_list):
                    tc_al.addTask("AliasSpinCircles", ObjectName=self.socket_ref.keys()[0], Sockets=self.socket_ref.keys() + self.gen_sockets.keys())

                    tc_list.addTask("TaskListener", ID=Notificator.onSpin, Filter=self.__socketFilter)

                tc_do.addTask("TaskFunction", Fn=self.DragSystemInstance.is_win)
                tc_until.addTask("TaskListener", ID=Notificator.onEnigmaSkip)
                pass
            pass
        pass

    def __complete(self, isSkip):
        self.DragSystemInstance.unbound_slots()
        self.setComplete()
        self.object.setParam("Play", False)
        pass

    def _autoWin(self):
        if self.object.getPlay() is False:
            return False
            pass
        self.__complete(True)
        return True
        pass

    def __socketFilter(self, socket):
        if self.InteractionBlock is True:
            return True

        if socket in self.socket_ref:
            self.action_socket = socket
            self.rotation_action()
            return True
            pass
        elif socket in self.gen_sockets:
            self.action_socket = socket
            self.drug_drop(socket)
            return True
            pass

        return False
        pass

    def rotation_action(self):
        if self.action_socket in self.socket_ref:
            Circle = self.socket_ref[self.action_socket]
            self.RotateSystemInstance.RotateBehavior(Circle)
            pass
        pass

    def preparation(self):
        InternDetail = ZenElementsManager.getInternalMovieDetail(self.EnigmaName)
        ExternalDetail = ZenElementsManager.getExternalMovieDetail(self.EnigmaName)
        self.swap_movie = self.object.getObject("Movie_Swap")
        ItemList = ZenElementsManager.getItems(self.EnigmaName)
        WinList = ZenElementsManager.getWinPlacement(self.EnigmaName)
        internal_socket = InternDetail["Socket"]
        ex_socket = ExternalDetail["Socket"]
        InternalCircle = Circle(InternDetail)
        ExternalCircle = Circle(ExternalDetail)  # ^D
        ExternalCircle.setSituated()
        self.InternalCircle = InternalCircle
        self.ExternalCircle = ExternalCircle
        self.DragSystemInstance = DragMiniSystem()
        self.RotateSystemInstance = RotateMiniSystem()
        self.DragSystemInstance.setup(self.object, ItemList, WinList)
        self.RotateSystemInstance.setDragSystem(self.DragSystemInstance)
        self.RotateSystemInstance.loadRotates(InternalCircle, ExternalCircle)
        self.socket_ref[internal_socket] = InternalCircle
        self.socket_ref[ex_socket] = ExternalCircle
        self.gen_sockets = dict((socket.getName(), socket) for socket in self.DragSystemInstance.getSlotSockets())
        self.restoreProgress()
        pass

    def clearance(self):
        self.socket_ref = {}
        self.gen_sockets = {}
        self.action_socket = None
        pass

    def drug_drop(self, socket):
        guide = self.RotateSystemInstance.place_guide
        contolExIndex = self.ExternalCircle.get_slot_by_guide(guide)
        controlInIndex = self.InternalCircle.get_slot_by_guide(guide)
        socketObj = self.gen_sockets[self.action_socket]
        slot_index = self.DragSystemInstance.getSocketIndex(socketObj)
        if self.action_socket.startswith("Ex") and contolExIndex != slot_index:
            return False
        elif self.action_socket.startswith("In") and controlInIndex != slot_index:
            return False
            pass
        inn, ex = controlInIndex, contolExIndex

        self.DragSystemInstance.swapSlotsByNumber(ex, inn, self.swap_movie, guide)
        pass

    pass