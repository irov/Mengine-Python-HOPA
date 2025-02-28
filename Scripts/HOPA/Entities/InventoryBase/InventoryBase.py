from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager


Print = DefaultManager.getDefault("DevDebugConsolePrintInventoryPanelAnim", True)


class InventoryBase(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

    def __init__(self):
        super(InventoryBase, self).__init__()
        self.Movie_Close_Open = None

    def debugPrint(self, msg):
        if _DEVELOPMENT and Print:
            Trace.log("Object", 1, msg.format(self.getName()))

    def Show_InventoryPanel(self, source):
        if not self.object.hasObject('Movie2_Open'):
            self.debugPrint("[info] ChildObject {}.Show_InventoryPanel() can't find object Movie2_Open. Please, add for Show/Hide inventory effect")
            return
        self.Movie_Close_Open = self.object.getObject("Movie2_Open")
        source.addScope(self.scope_InventoryPanel)

    def Hide_InventoryPanel(self, source):
        if not self.object.hasObject('Movie2_Return'):
            self.debugPrint("[info] ChildObject {}.Hide_InventoryPanel() can't find object Movie2_Return. Please, add for Show/Hide inventory effect")
            return

        if not self.object.hasObject('Movie2_Close'):
            self.debugPrint("[info] ChildObject {}.Hide_InventoryPanel() can't find object Movie2_Close. Please, add for Show/Hide inventory effect")
            return

        self.Movie_Close_Open = self.object.getObject("Movie2_Close")
        Movie_Return = self.object.getObject("Movie2_Return")

        source.addScope(self.scope_InventoryPanel)
        source.addEnable(Movie_Return)

    def scope_InventoryPanel(self, source):
        if not self.object.hasObject('Movie2_Return'):
            self.debugPrint("[info] ChildObject {}.scope_InventoryPanel() can't find object Movie2_Return. Please, add for Show/Hide inventory effect")
            return

        Movie_Return = self.object.getObject("Movie2_Return")

        source.addDisable(Movie_Return)
        source.addTask("TaskMovie2Play", Movie2=self.Movie_Close_Open, Wait=True, AutoEnable=True)

    def Folding_Inventory(self, source):
        if not SceneManager.hasLayerScene("InventoryLock"):
            return

        if not self.object.hasObject('Movie2_Fold'):
            self.debugPrint("[info] ChildObject {}.Folding_Inventory() can't find object Movie2_Fold. Please, add for Folding/Rising Inventory effect")
            return

        Movie2_Fold = self.object.getObject("Movie2_Fold")

        source.addTask("TaskMovie2Play", Movie2=Movie2_Fold, Wait=True, AutoEnable=True)

    def Rising_Inventory(self, source):
        if not SceneManager.hasLayerScene("InventoryLock"):
            return

        if not self.object.hasObject('Movie2_Rise'):
            self.debugPrint("[info] ChildObject {}.Rising_Inventory() can't find object Movie2_Rise. Please, add for Folding/Rising Inventory effect")
            return

        Movie2_Rise = self.object.getObject("Movie2_Rise")

        source.addTask("TaskMovie2Play", Movie2=Movie2_Rise, Wait=True, AutoEnable=True)

    def Rised_Inventory(self):
        if not SceneManager.hasLayerScene("InventoryLock"):
            return

        if not self.object.hasObject('Movie2_Fold'):
            self.debugPrint("[info] ChildObject {}.Rised_Inventory() can't find object Movie2_Fold. Please, add for Folding/Rising Inventory effect")
            return

        Movie2_Fold = self.object.getObject("Movie2_Fold")
        Movie2_Fold.setEnable(True)
        Movie2_Fold.setEnable(False)

    def Folded_Up_Inventory(self):
        if not SceneManager.hasLayerScene("InventoryLock"):
            return

        if not self.object.hasObject('Movie2_Rise'):
            self.debugPrint("[info] ChildObject {}.Folded_Up_Inventory() can't find object Movie2_Rise. Please, add for Folding/Rising Inventory effect")
            return

        Movie2_Rise = self.object.getObject("Movie2_Rise")
        Movie2_Rise.setEnable(True)
        Movie2_Rise.setEnable(False)

    def _onDeactivate(self):
        super(InventoryBase, self)._onDeactivate()
