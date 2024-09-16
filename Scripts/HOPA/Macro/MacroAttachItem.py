from Foundation.ArrowManager import ArrowManager
from Foundation.Notificator import Notificator
from Foundation.TaskManager import TaskManager
from HOPA.CursorManager import CursorManager
from HOPA.Macro.MacroCommand import MacroCommand
from Notification import Notification


class MacroAttachItem(MacroCommand):
    def __init__(self):
        super(MacroAttachItem, self).__init__()

        self.ItemName = None
        self.Object = None
        self.ObjectType = None
        self.AutoReturnToParent = None
        self.ReattachOnSceneInit = None
        self.OnSceneEnterReattachObserver = None
        self.AttachMovieFront = None

    def _onValues(self, values):
        self.ItemName = values[0]

        _, self.Object = self.findObject(self.ItemName)

        self.ObjectType = self.Object.getType()

        self.AutoReturnToParent = bool(values[1]) if len(values) > 1 else True

        if self.ObjectType == 'ObjectMovie' or self.ObjectType == 'ObjectMovie2':
            self.AttachMovieFront = bool(values[2]) if len(values) > 2 else True

        self.ReattachOnSceneInit = True
        self.OnSceneEnterReattachObserver = None

    def setOnSceneEnterReattachObserver(self):
        self.OnSceneEnterReattachObserver = Notification.addObserver(Notificator.onSceneInit, self.__reattachOnSceneInit)

    def removeOnSceneEnterReattachObserver(self):
        Notification.removeObserver(self.OnSceneEnterReattachObserver)

    def __reattachOnSceneInit(self, scene_name):
        if self.SceneName != scene_name:
            return False

        if self.ObjectType == 'ObjectItem':
            TaskManager.runAlias('AliasItemAttach', None, Item=self.Object)

        elif self.ObjectType == 'ObjectMovie' or self.ObjectType == 'ObjectMovie2':
            self.attach(self.Object)

        return False

    def _onGenerate(self, source):
        if self.ReattachOnSceneInit:
            with TaskManager.createTaskChain() as tc:
                tc.addListener(Notificator.onMacroAttachItemRemoveObserver,
                               Filter=lambda item_name: self.ItemName == item_name)
                tc.addFunction(self.removeOnSceneEnterReattachObserver)

            source.addFunction(self.setOnSceneEnterReattachObserver)

        if self.ObjectType == 'ObjectItem':
            source.addTask('AliasItemAttach', Item=self.Object)

            if self.AutoReturnToParent:
                source.addTask('TaskMouseButtonClick', isDown=False)
                source.addTask('AliasRemoveItemAttach', Item=self.Object)
                source.addNotify(Notificator.onMacroAttachItemRemoveObserver, self.ItemName)

        elif self.ObjectType == 'ObjectMovie' or self.ObjectType == 'ObjectMovie2':
            source.addFunction(self.attach, self.Object)

            if self.AutoReturnToParent:
                source.addTask('TaskMouseButtonClick', isDown=False)
                source.addFunction(self.Object.returnToParent)
                source.addNotify(Notificator.onMacroAttachItemRemoveObserver, self.ItemName)

    def attach(self, Object):
        """
        attach chip to arrow
        :return:
        """
        node = Object.getEntityNode()
        node.setLocalPosition((0, 0))
        node.setWorldPosition((0, 0))

        node.removeFromParent()
        arrow = Mengine.getArrow()
        arrow_node = arrow.getNode()
        CursorManager.macroAttached(Object)

        if self.AttachMovieFront:
            arrow_node.addChildFront(node)
        else:
            arrow_node.addChild(node)
