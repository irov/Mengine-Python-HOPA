from Foundation.ArrowManager import ArrowManager
from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager
from Notification import Notification

from SpellManager import SpellManager


class Spell(BaseEntity):
    LOCKED = "Locked"
    PREPARED = "Prepared"
    READY = "Ready"
    ACTIVE = "Active"
    CHARGE = "Charge"

    IDLE = "Idle"
    HIDE = "Hide"
    SHOW = "Show"
    DOWN = "Down"

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "CurrentState", Update=Spell.__updateCurrentState)
        Type.addActionActivate(Type, "IsValidUse")
        Type.addActionActivate(Type, "AtmosphericUse")
        Type.addActionActivate(Type, "HideState", Update=Spell.__updateHideState)
        pass

    def __init__(self):
        super(Spell, self).__init__()
        self.lockedMovie = None
        self.activeMovie = None
        self.readyMovie = None
        self.preparedMovie = None
        self.chargeMovie = None
        self.useMovie = None
        self.invalidMovie = None
        self.overviewMovie = None
        self.Socket = None
        self.Sprite = None

        self.idleMovie = None
        self.hideMovie = None
        self.showMovie = None
        self.downMovie = None

        self.beginSpellObserver = None
        self.endSpellObserver = None

        self.isValidUse = False
        self.isOverview = False

        self.entitiesToRemove = []

        pass

    def getSocket(self):
        return self.Socket
        pass

    def __updateHideState(self, value):
        if value == Spell.HIDE:
            self.hideChain()
            pass
        elif value == Spell.IDLE:
            self.idleChain()
            pass
        elif value == Spell.SHOW:
            self.showChain()
            pass
        elif value == Spell.DOWN:
            self.downChain()
            pass
        pass

    def attachToSlot(self, slot):
        def innerAppendMethod(object):
            entity = object.getEntity()
            slot.addChild(entity)
            self.entitiesToRemove.append(entity)
            pass

        if self.Sprite is not None:
            innerAppendMethod(self.Sprite)
            pass

        if self.Socket is not None:
            innerAppendMethod(self.Socket)
            pass

        if self.lockedMovie is not None:
            innerAppendMethod(self.lockedMovie)
            pass

        if self.activeMovie is not None:
            innerAppendMethod(self.activeMovie)
            pass

        if self.readyMovie is not None:
            innerAppendMethod(self.readyMovie)
            pass

        if self.preparedMovie is not None:
            innerAppendMethod(self.preparedMovie)
            pass

        if self.chargeMovie is not None:
            innerAppendMethod(self.chargeMovie)
            pass

        if self.overviewMovie is not None:
            innerAppendMethod(self.overviewMovie)
            pass
        pass

    def removeFromParent(self):
        for entity in self.entitiesToRemove:
            entity.removeFromParent()
            pass
        self.entitiesToRemove = []
        pass

    def movieAttach(self, movie):
        movie.setEnable(True)
        movieEntity = movie.getEntity()
        slot = movieEntity.getMovieSlot("slot")
        self.attachToSlot(slot)
        pass

    def idleChain(self):
        if self.idleMovie is None:
            return
            pass
        if TaskManager.existTaskChain("Hide_" + self.object.getName()):
            TaskManager.cancelTaskChain("Hide_" + self.object.getName())
            pass
        self.removeFromParent()
        self.movieAttach(self.idleMovie)
        pass

    def hideChain(self):
        if self.hideMovie is None:
            return
            pass
        self.cancelHideTaskChains()
        self.removeFromParent()
        self.movieAttach(self.hideMovie)
        with TaskManager.createTaskChain(Name="Hide_" + self.object.getName()) as tc:
            if self.hideMovie is not None:
                tc.addTask("TaskMoviePlay", Movie=self.hideMovie)
                pass
            tc.addParam(self.object, "HideState", "Down")
            pass
        pass

    def showChain(self):
        if self.showMovie is None:
            return
            pass
        self.cancelHideTaskChains()
        self.removeFromParent()
        self.movieAttach(self.showMovie)
        with TaskManager.createTaskChain(Name="Show_" + self.object.getName()) as tc:
            if self.showMovie is not None:
                tc.addTask("TaskMoviePlay", Movie=self.showMovie)
                pass
            tc.addParam(self.object, "HideState", "Idle")
            pass
        pass

    def downChain(self):
        if self.downMovie is None:
            return
            pass

        self.removeFromParent()
        self.movieAttach(self.downMovie)
        pass

    def __updateCurrentState(self, value):
        # print " [ Spell ] __updateCurrentState", value
        if value == Spell.LOCKED:
            # print 1
            if self.readyMovie is not None:
                self.readyMovie.setEnable(False)
                pass
            self.__block(None, False)
            self.__lockedChain()
            pass
        elif value == Spell.READY:
            # print 2
            self.__block(None, True)
            self.__readyChain()
            pass
        elif value == Spell.PREPARED:
            # print 3
            self.__preparedChain()
            pass
        elif value == Spell.ACTIVE:
            # print 4
            self.__activeChain()
            pass
        elif value == Spell.CHARGE:
            # print 5
            self.__charging()
            pass
        pass

    def __prepareObjects(self):
        spellData = SpellManager.getSpellData(self.object.getName())
        self.Socket = spellData.getSocket()
        self.Sprite = spellData.getSprite()
        self.lockedMovie = spellData.getLocked()
        self.readyMovie = spellData.getReady()
        self.preparedMovie = spellData.getPrepared()
        self.activeMovie = spellData.getActive()
        self.chargeMovie = spellData.getCharge()
        self.useMovie = spellData.getUse()
        self.invalidMovie = spellData.getInvalidUse()
        self.overviewMovie = spellData.getOverview()
        self.idleMovie = spellData.getIdle()
        self.showMovie = spellData.getShow()
        self.hideMovie = spellData.getHide()
        self.downMovie = spellData.getDown()
        pass

    def __disableAllMovies(self):
        if self.lockedMovie is not None:
            self.lockedMovie.setEnable(False)
            pass
        if self.readyMovie is not None:
            self.readyMovie.setEnable(False)
            pass
        if self.preparedMovie is not None:
            self.preparedMovie.setEnable(False)
            pass
        if self.activeMovie is not None:
            self.activeMovie.setEnable(False)
            pass
        if self.chargeMovie is not None:
            self.chargeMovie.setEnable(False)
            pass
        if self.useMovie is not None:
            self.useMovie.setEnable(False)
            pass
        if self.invalidMovie is not None:
            self.invalidMovie.setEnable(False)
            pass
        if self.overviewMovie is not None:
            if self.isOverview is False:
                self.overviewMovie.setEnable(False)
                pass
            pass
        pass

    def _onPreparation(self):
        super(Spell, self)._onPreparation()
        self.__prepareObjects()
        self.__disableAllMovies()
        pass

    def __changeState(self, isSkip=False):
        currentState = self.object.getCurrentState()
        # print "currentState", currentState
        if currentState == Spell.CHARGE:
            setState = Spell.READY
            pass
        elif currentState == Spell.READY:
            setState = Spell.ACTIVE
            pass
        elif currentState == Spell.ACTIVE:
            setState = Spell.CHARGE
            pass
        else:
            return True
            pass
        self.object.setCurrentState(setState)
        return True
        pass

    def StartOverview(self):
        Difficulty = Mengine.getCurrentAccountSetting("Difficulty")
        if Difficulty != "Casual":
            return
            pass
        if self.CurrentState == Spell.LOCKED:
            return
            pass
        if self.overviewMovie is None:
            return
            pass
        self.isOverview = True
        self.overviewMovie.setEnable(True)
        self.overviewMovie.setLoop(True)
        self.overviewMovie.setPlay(True)
        pass

    def FinishOverview(self):
        Difficulty = Mengine.getCurrentAccountSetting("Difficulty")
        if Difficulty != "Casual":
            return
            pass
        if self.CurrentState == Spell.LOCKED:
            return
            pass
        if self.overviewMovie is None:
            return
            pass
        self.isOverview = False
        self.overviewMovie.setEnable(False)
        self.overviewMovie.setLoop(False)
        self.overviewMovie.setPlay(False)
        pass

    def __lockedChain(self):
        if ArrowManager.emptyArrowAttach() is False:
            attach = ArrowManager.getArrowAttach()
            if attach is self.useMovie:
                ArrowManager.removeArrowAttach()
                movieEntity = self.useMovie.getEntity()
                movieEntity.removeFromParent()
                pass
            pass

        if self.lockedMovie is None:
            return
            pass
        self.cancelTaskChains()
        self.__disableAllMovies()
        self.lockedMovie.setEnable(True)
        with TaskManager.createTaskChain(Name="Locked_" + self.object.getName(), Repeat=True) as tc_locked:
            tc_locked.addTask("TaskSocketClickEndUp", Socket=self.Socket, AutoEnable=False)
            with tc_locked.addParallelTask(2) as (tc_movie, tc_mind):
                tc_movie.addTask("TaskMoviePlay", Movie=self.lockedMovie, Wait=True)

                tc_mind.addTask("AliasMindPlay", MindID="ID_MIND_SPELL_LOCKED")
                pass
            tc_locked.addTask("TaskMovieLastFrame", Movie=self.lockedMovie, Value=False)
            pass
        pass

    def __preparedChain(self):
        if self.preparedMovie is None:
            return
            pass
        self.cancelTaskChains()
        self.__disableAllMovies()
        self.preparedMovie.setEnable(True)
        with TaskManager.createTaskChain(Name="Prepared_" + self.object.getName(), Repeat=True) as tc_prepared:
            tc_prepared.addTask("TaskSocketEnter", Socket=self.Socket, AutoEnable=False)
            with tc_prepared.addRaceTask(2) as (tc_leave, tc_click):
                tc_leave.addTask("TaskSocketLeave", Socket=self.Socket, AutoEnable=False)
                tc_leave.addTask("TaskMovieStop", Movie=self.preparedMovie)
                tc_leave.addTask("TaskMovieLastFrame", Movie=self.preparedMovie, Value=False)

                tc_click.addTask("TaskSocketClickEndUp", Socket=self.Socket, AutoEnable=False)
                tc_click.addFunction(TransitionManager.changeScene, "04_OccultLab_MG2")
                pass
            pass
        pass

    def __charging(self):
        if self.chargeMovie is None:
            self.__changeState()
            return
            pass
        self.cancelTaskChains()
        self.__disableAllMovies()
        if self.chargeMovie is not None:
            with TaskManager.createTaskChain(Name="Charge_" + self.object.getName(),
                                             Cb=self.__changeState) as tc_charge:
                tc_charge.addEnable(self.chargeMovie)
                tc_charge.addTask("TaskMoviePlay", Movie=self.chargeMovie, Wait=True)
                pass
            pass
        pass

    def __readyChain(self):
        # print " { Spell } __readyChain"
        self.cancelTaskChains()
        self.__disableAllMovies()
        self.readyMovie.setEnable(True)
        with TaskManager.createTaskChain(Name="Ready_" + self.object.getName(), Repeat=True) as tc_prepared:
            tc_prepared.addTask("TaskSocketEnter", Socket=self.Socket, AutoEnable=False)
            if self.readyMovie is not None:
                tc_prepared.addTask("TaskMoviePlay", Movie=self.readyMovie, Wait=False)
                pass
            with tc_prepared.addRaceTask(2) as (tc_leave, tc_click):
                tc_leave.addTask("TaskSocketLeave", Socket=self.Socket, AutoEnable=False)
                tc_leave.addTask("TaskMovieStop", Movie=self.readyMovie)
                tc_leave.addTask("TaskMovieLastFrame", Movie=self.readyMovie, Value=False)

                tc_click.addTask("TaskSocketClickEndUp", Socket=self.Socket, AutoEnable=False)
                tc_click.addFunction(self.__changeState)
                tc_click.addNotify(Notificator.onSpellBeginUse, self.object)
                pass
            pass
        pass

    def __activeChain(self):
        self.cancelTaskChains()
        self.__disableAllMovies()
        with TaskManager.createTaskChain(Name="Active_" + self.object.getName(), Cb=self.__changeState) as tc_active:
            tc_active.addNotify(Notificator.onSpellBeginUse, self.object)
            if self.AtmosphericUse is False:
                # tc_active.addTask("TaskPrint", Value = "111")
                tc_active.addFunction(self.__arrowSpell)
                # tc_active.addTask("TaskPrint", Value = "222")
                if self.activeMovie is not None:
                    tc_active.addEnable(self.activeMovie)
                    tc_active.addTask("TaskMoviePlay", Movie=self.activeMovie, Loop=True, Wait=False)
                    pass
                # tc_active.addTask("TaskPrint", Value = "333")
                tc_active.addListener(Notificator.onSpellEndUse)
                pass
            else:
                with tc_active.addSwitchTask(3, self.__isInvalidSpellUse) as (tc_ok, tc_invalid, tc_notMana):
                    tc_ok.addDummy()

                    tc_invalid.addScope(self.__invalidUseScope)

                    tc_notMana.addScope(self.__noManaScope)
                    pass
                # tc_active.addTask("TaskPrint", Value = "444")
                tc_active.addNotify(Notificator.onSpellEndUse, self.object)
                # tc_active.addTask("TaskPrint", Value = "555")
                pass
            pass
        pass

    def _onActivate(self):
        super(Spell, self)._onActivate()
        self.Socket.setEnable(True)
        self.Socket.setInteractive(True)
        self.beginSpellObserver = Notification.addObserver(Notificator.onSpellBeginUse, self.__block, False)
        self.endSpellObserver = Notification.addObserver(Notificator.onSpellEndUse, self.__block, True)
        pass

    def __block(self, object, value):
        # print "__block", value
        self.Socket.setEnable(value)
        return False
        pass

    def __arrowSpell(self):
        # print "__arrowSpell"
        def __Attach():
            if self.useMovie is None:
                return
                pass
            arrow = Mengine.getArrow()
            arrow_node = arrow.getNode()
            movieEntityNode = self.useMovie.getEntityNode()
            ArrowManager.attachArrow(self.useMovie)
            arrow_node.addChild(movieEntityNode)
            pass

        def __Deattach():
            if self.useMovie is None:
                return
                pass
            ArrowManager.removeArrowAttach()
            movieEntity = self.useMovie.getEntity()
            movieEntity.removeFromParent()
            pass

        with TaskManager.createTaskChain(Name="SpellAttach_" + self.object.getName()) as tc:
            # tc.addTask("TaskPrint", Value = "0000________00000000000000000")
            tc.addFunction(__Attach)
            if self.useMovie is not None:
                tc.addEnable(self.useMovie)
                tc.addTask("TaskMoviePlay", Movie=self.useMovie, Loop=True, Wait=False)
                pass
            # tc.addTask("TaskPrint", Value = "1111_________0000000000000000")
            tc.addTask("TaskMouseButtonClickEnd", isDown=False)
            # tc.addTask("TaskPrint", Value = "2222____________0000000000000000")
            if self.useMovie is not None:
                tc.addDisable(self.useMovie)
                pass
            # tc.addTask("TaskPrint", Value = "0000000000000000")
            tc.addFunction(__Deattach)
            # tc.addTask("TaskPrint", Value = "1111111111111111111")
            with tc.addSwitchTask(3, self.__isInvalidSpellUse) as (tc_ok, tc_invalid, tc_notMana):
                tc_ok.addDummy()

                tc_invalid.addScope(self.__invalidUseScope)
                # tc_invalid.addTask("TaskPrint", Value = "2222222222222222222222222")

                tc_notMana.addScope(self.__noManaScope)
                # tc_notMana.addTask("TaskPrint", Value = "333333333333333333333333333")
                pass
            # tc.addTask("TaskPrint", Value = "555555555555555555555555")
            tc.addNotify(Notificator.onSpellEndUse, self.object)
            pass
        pass

    def __invalidUseScope(self, scope):
        arrow = Mengine.getArrow()
        dir_arrow = dir(arrow)
        # print
        # for attr in dir_arrow:
        #     print attr
        #     pass
        # print
        arrow_node = arrow.getNode()
        pos = arrow_node.getWorldPosition()
        with scope.addParallelTask(2) as (tc_invalidMind, tc_invalidMovie):
            tc_invalidMind.addTask("AliasMindPlay", MindID="ID_MIND_SPELL_INVALIDUSE")

            if self.invalidMovie is not None:
                tc_invalidMovie.addTask("TaskObjectSetPosition", Object=self.invalidMovie, Value=pos)
                tc_invalidMovie.addEnable(self.invalidMovie)
                tc_invalidMovie.addTask("TaskMoviePlay", Movie=self.invalidMovie, Wait=True, Loop=False)
                tc_invalidMovie.addDisable(self.invalidMovie)
                pass
            tc_invalidMovie.addDummy()
            pass
        pass

    def __noManaScope(self, scope):
        arrow = Mengine.getArrow()
        arrow_node = arrow.getNode()
        pos = arrow_node.getWorldPosition()
        with scope.addParallelTask(2) as (tc_invalidMind, tc_invalidMovie):
            tc_invalidMind.addTask("AliasMindPlay", MindID="ID_MIND_SPELL_NO_MANA")

            if self.invalidMovie is not None:
                tc_invalidMovie.addTask("TaskObjectSetPosition", Object=self.invalidMovie, Value=pos)
                tc_invalidMovie.addEnable(self.invalidMovie)
                tc_invalidMovie.addTask("TaskMoviePlay", Movie=self.invalidMovie, Wait=True, Loop=False)
                tc_invalidMovie.addDisable(self.invalidMovie)
                pass
            tc_invalidMovie.addDummy()
            pass
        pass

    def __isInvalidSpellUse(self, isSkip, cb):
        check = self.object.getIsValidUse()
        if check is False:
            cb(isSkip, 1)
            return
            pass
        else:
            self.object.setIsValidUse(False)
            if DemonManager.hasDemon("Mana") is False:
                cb(isSkip, 0)
                return
                pass
            Mana = DemonManager.getDemon("Mana")
            Value = Mana.getManaCount()
            SpellID = SpellManager.getSpellID(self.object)
            SpellCost = SpellManager.getSpellCost(SpellID)
            if SpellCost is None:
                cb(isSkip, 0)
                return
                pass
            else:
                if SpellCost <= Value:
                    Notification.notify(Notificator.onManaDecrease, SpellCost)
                    cb(isSkip, 0)
                    return
                    pass
                else:
                    cb(isSkip, 2)
                    return
                    pass
                pass
            pass
        pass

    def _onDeactivate(self):
        super(Spell, self)._onDeactivate()
        self.cancelTaskChains()
        self.cancelHideTaskChains()
        self.removeFromParent()
        Notification.removeObserver(self.beginSpellObserver)
        Notification.removeObserver(self.endSpellObserver)
        if ArrowManager.emptyArrowAttach() is False:
            attach = ArrowManager.getArrowAttach()
            if attach is self.useMovie:
                ArrowManager.removeArrowAttach()
                movieEntity = self.useMovie.getEntity()
                movieEntity.removeFromParent()
                pass
            pass
        pass

    def cancelTaskChains(self):
        if TaskManager.existTaskChain("SpellAttach_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("SpellAttach_" + self.object.getName())
            pass
        if TaskManager.existTaskChain("Locked_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Locked_" + self.object.getName())
            pass
        if TaskManager.existTaskChain("Prepared_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Prepared_" + self.object.getName())
            pass
        if TaskManager.existTaskChain("Ready_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Ready_" + self.object.getName())
            pass
        if TaskManager.existTaskChain("Charge_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Charge_" + self.object.getName())
            pass
        if TaskManager.existTaskChain("Active_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Active_" + self.object.getName())
            pass
        pass

    def cancelHideTaskChains(self):
        if TaskManager.existTaskChain("Hide_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Hide_" + self.object.getName())
            pass
        if TaskManager.existTaskChain("Show_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Show_" + self.object.getName())
            pass
        pass

    pass
