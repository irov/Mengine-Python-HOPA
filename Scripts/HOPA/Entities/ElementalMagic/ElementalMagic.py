from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.ArrowManager import ArrowManager

MOV_Magic_Empty_Idle = "Movie2_Magic_Empty_Idle"
MOV_Magic_Fire_Idle = "Movie2_Magic_Fire_Idle"
MOV_CONTENT = "Movie2_Content"
SLT_MAGIC = "magic"
BTN_MAGIC = "Movie2Button_ElementalMagic"


class ElementalMagic(BaseEntity):
    def __init__(self):
        super(ElementalMagic, self).__init__()
        self.tc = None

    # ====================== BaseEntity ================================================================================
    def _onPreparation(self):
        self.mov_magic_empty_idle = self.object.getObject(MOV_Magic_Empty_Idle)
        self.mov_magic_fire_idle = self.object.getObject(MOV_Magic_Fire_Idle)
        mov_content = self.object.getObject(MOV_CONTENT)

        self.slot_magic = mov_content.getMovieSlot(SLT_MAGIC)
        self.slot_magic.addChild(self.mov_magic_fire_idle.getEntityNode())
        self.mov_magic_empty_idle.setEnable(False)

    def _onActivate(self):
        if _DEVELOPMENT:
            self.runTaskChain()

    def _onDeactivate(self):
        self.cleanUp()

    # ====================== TaskChain =================================================================================
    def runTaskChain(self):
        movie = self.mov_magic_fire_idle

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addTask("TaskMovie2ButtonClick", GroupName="ElementalMagic", Movie2ButtonName=BTN_MAGIC)
            tc.addScope(self.scopeUseMagic, movie)
            tc.addTask("TaskMouseButtonClick")
            tc.addScope(self.scopeReturnMagic, movie)

    def scopeUseMagic(self, tc, movie):
        if movie is None:
            return

        tc.addFunction(self.detachFromSlot, movie)
        tc.addFunction(self.attachToCursor, movie)

    def scopeReturnMagic(self, tc, movie):
        if movie is None:
            return

        tc.addFunction(self.detachFromCursor, movie)
        tc.addFunction(self.attachToSlot, movie)

    def attachToCursor(self, movie):
        arrow = ArrowManager.getArrow()
        movie_node = movie.getEntityNode()
        ArrowManager.attachArrow(movie)
        arrow.addChildFront(movie_node)

    def detachFromCursor(self, movie):
        ArrowManager.removeArrowAttach()
        movie_entity = movie.getEntity()
        movie_entity.removeFromParent()

    def attachToSlot(self, movie):
        movie_node = movie.getEntityNode()
        self.slot_magic.addChild(movie_node)

    def detachFromSlot(self, movie):
        movie_node = movie.getEntityNode()
        self.slot_magic.removeChild(movie_node)

    # def attachToCursor(self, movie):
    #     cursor = Mengine.getArrow()
    #     movie.getEntityNode().removeFromParent()
    #     cursor.addChildFront(movie.getEntityNode())
    #
    # def detachFromCursor(self, movie):
    #     movie.getEntityNode().removeFromParent()
    #     self.slot_magic.addChild(self.mov_magic_fire_idle.getEntityNode())

    # ====================== CleanUp ===================================================================================
    def cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None
