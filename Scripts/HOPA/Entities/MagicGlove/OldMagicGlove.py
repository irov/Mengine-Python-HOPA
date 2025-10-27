from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.MagicGloveManager import MagicGloveManager


class MagicGlove(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction("Point")
        # addActionActivate means that update of this param will be after onActivate
        Type.addActionActivate("Runes",
                               Update=Type.__updateRunes,
                               Append=Type.__appendRunes,
                               Remove=Type.__delParam)
        Type.addAction("State", Update=Type.__updateState)

    def __init__(self):
        super(MagicGlove, self).__init__()
        self.tc = None
        self.tc_Glove_Change = None
        self.movies = {}
        self.movies_Ready = {}
        self.name = 0
        self.slower = 0
        self.MovieButtons = []
        self.MovieChange = []
        self.Glove_State = None

    def _onActivate(self):
        self.MovieButtons = []
        self.MovieChange = []
        Buttons = MagicGloveManager.getButtons()
        Change = MagicGloveManager.getMovies()
        for elem in Buttons:
            movie = self.object.getObject(elem)
            self.MovieButtons.append(movie)

        for elem in Change:
            movie = self.object.getObject(elem)
            self.MovieChange.append(movie)

        if len(self.MovieChange) == 0:
            return

        Glove = self.MovieChange[-1]
        self.Slot = Glove.getMovieSlot("Center")

        self.ButtonSwicher(0)

        self.Glove_State = "Idle"
        for Rune in self.Runes:
            self.ButtonSwicher(1)
            self.Glove_State = "Ready"
            break

        self.runTaskChain()
        pass

    def runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            for button, source in tc.addRaceTaskList(self.MovieButtons):
                # source.addPrint("TaskMovie2ButtonClick {}".format(button.getName()))
                source.addTask("TaskMovie2ButtonClick", Movie2Button=button)
            tc.addNotify(Notificator.onMagicGloveClick)
            tc.addScope(self.tryUseRune)

    def tryUseRune(self, source):
        if self.MovieButtons[0].getEnable() is True:
            Notification.notify(Notificator.onGroupEnable, "MagicGlove_0", True)
            return

        quest = self.object.getActiveUseRuneQuest()

        if quest is None:
            Notification.notify(Notificator.onGroupEnable, "MagicGlove_1", True)
            return

        RuneID = quest.params['Rune_ID']
        Object = quest.params['Object']
        if RuneID not in self.Runes:
            Notification.notify(Notificator.onGroupEnable, "MagicGlove_2", True)
            return

        if Object.getType() is "ObjectSocket":
            source.addNotify(Notificator.onStartUseRune, RuneID, Object)
            source.addScope(self.scopeUseRune, RuneID, Object)
            # source.addNotify(Notificator.onUseRune, RuneID, Object)

    def scopeUseRune(self, source, rune_id, socket):
        # rune_id="Idle"
        if rune_id == "Idle":
            return

        Rune = MagicGloveManager.getRune(rune_id)
        GroupName = Rune.RuneGroup
        MovieRuneReadyName = Rune.MovieReady
        IdleDeley = DefaultManager.getDefaultFloat("MagicGloveIdleDelay", 1.5) * 1000

        movie = self.movies_Ready[rune_id]
        movieIdle = self.movies[rune_id]
        movieIdle.setEnable(False)

        with source.addRaceTask(4) as (tc_Effect, tc_Notify, tc_Sound, tc_Idle):
            tc_Notify.addListener(Notificator.onZoomLeave)
            tc_Notify.addNotify(Notificator.onUseRune, rune_id, socket)
            tc_Notify.addScope(self._scopeMagicGloveAllStop, rune_id)
            tc_Notify.addFunction(self.FuncDelRune, rune_id)
            tc_Notify.addFunction(self._State_Idle)

            with tc_Effect.addParallelTask(2) as (tc_1, tc_2):
                tc_1.addScope(self._scopeMagicGloveWayEffect, rune_id, socket)

                # tc_2.addTask("AliasObjectAlphaTo", Object=movie, From=1.0, To=0.0, Time=900.0)

                with tc_1.addParallelTask(2) as (tc_target, tc_way):
                    tc_way.addScope(self._scopeMagicGloveWayEffectInterrupt, rune_id)

                    tc_target.addScope(self._scopeMagicGloveTargetEffect, rune_id, socket)
                    # tc_target.addFunction(self._State_Idle)
                    # tc_target.addScope(self._scopeMagicGloveTargetEffectInterrupt, rune_id)
                    tc_target.addNotify(Notificator.onUseRune, rune_id, socket)
                    # tc_target.addFunction(self._State_Idle)

            tc_Idle.addDelay(IdleDeley)
            tc_Idle.addFunction(self.FuncDelRune, rune_id)
            tc_Idle.addFunction(self._State_Idle)
            tc_Idle.addBlock()

            tc_Sound.addNotify(Notificator.onSoundEffectOnObject, self.object, 'MagicGlove_Clicked_Activate')
            tc_Sound.addBlock()

    def FuncDelRune(self, rune_id):
        self.object.delParam("Runes", rune_id)

    def _State_Idle(self):
        self.object.setParam("State", "Idle")

    def getPositionFrom(self):
        return self.Point

    def getPositionTo(self, socket):
        entity = socket.getEntity()
        hotspot = entity.getHotSpot()
        pos = hotspot.getWorldPolygonCenter()
        return pos

    def _Glove_Change(self, Bool, delay=50):
        if self.Glove_State == "Idle" and Bool is True:
            number = 1
            Movie = self.MovieChange[0]
            self.Glove_State = "Ready"

        elif self.Glove_State == "Ready" and Bool is False:
            number = 0
            Movie = self.MovieChange[1]
            self.Glove_State = "Idle"
        else:
            return
        # self.Tc_Cancel()
        self.tc_Glove_Change = TaskManager.createTaskChain(Repeat=False)
        with self.tc_Glove_Change as tc_1:
            tc_1.addFunction(self.ButtonSwicher)
            tc_1.addTask("TaskMovie2Play", Movie2=Movie, Wait=True, AutoEnable=True)
            tc_1.addFunction(self.ButtonSwicher, number)
            # tc_1.addFunction(self.Tc_Cancel)
            # tc_1.addFunction(self.runTaskChain)
            pass
        pass

    def _scopeMagicGloveWayEffect(self, source, rune_id=None, socket=None):
        P0 = self.getPositionFrom()
        P2 = self.getPositionTo(socket)

        rune_id = MagicGloveManager.getFirstRune()

        Rune = MagicGloveManager.getRune(rune_id)

        GroupName = Rune.EffectGroup
        MovieWayEffectName = Rune.MovieEffectWay

        p1x = P0[0] if P0[1] > P2[1] else P2[0]
        p1y = P2[1] if P0[1] > P2[1] else P0[1]

        P1 = (p1x, p1y)

        source.addTask("TaskObjectSetPosition", GroupName=GroupName, ObjectName=MovieWayEffectName, Value=P0)
        source.addTask("TaskMovie2Play", GroupName=GroupName, Movie2Name=MovieWayEffectName, Loop=True, Wait=False)

        source.addTask("AliasObjectBezier2To", GroupName=GroupName, ObjectName=MovieWayEffectName, Point1=P1, To=P2,
                       Speed=600 * 0.001)  # speed fix

    def _scopeMagicGloveWayEffectInterrupt(self, source, rune_id=None):
        rune_id = MagicGloveManager.getFirstRune()
        Rune = MagicGloveManager.getRune(rune_id)

        GroupName = Rune.EffectGroup
        MovieWayEffectName = Rune.MovieEffectWay

        MovieWayEffect = GroupManager.getObject(GroupName, MovieWayEffectName)
        if MovieWayEffect.getPlay() is False:
            return
            pass
        source.addTask("TaskMovie2Interrupt", Movie2=MovieWayEffect)
        source.addTask("TaskMovie2Stop", Movie2=MovieWayEffect)

    def _scopeMagicGloveAllStop(self, source, rune_id=None):
        rune_id = MagicGloveManager.getFirstRune()
        Rune = MagicGloveManager.getRune(rune_id)

        GroupName = Rune.EffectGroup
        MovieWayEffectName = Rune.MovieEffectWay

        MovieTargetEffectName = Rune.MovieEffectTarget

        MovieWayEffect = GroupManager.getObject(GroupName, MovieWayEffectName)
        if MovieWayEffect.getPlay() is True:
            source.addTask("TaskMovie2Stop", Movie2=MovieWayEffect)

        MovieTargetEffect = GroupManager.getObject(GroupName, MovieTargetEffectName)
        if MovieTargetEffect.getPlay() is True:
            source.addTask("TaskMovie2Stop", Movie2=MovieTargetEffect)

    def _scopeMagicGloveTargetEffect(self, source, rune_id=None, socket=None):
        rune_id = MagicGloveManager.getFirstRune()
        Position = self.getPositionTo(socket)

        Rune = MagicGloveManager.getRune(rune_id)

        GroupName = Rune.EffectGroup
        MovieTargetEffectName = Rune.MovieEffectTarget

        source.addTask("TaskObjectSetPosition", GroupName=GroupName, ObjectName=MovieTargetEffectName, Value=Position)
        source.addTask("TaskMovie2Play", GroupName=GroupName, Movie2Name=MovieTargetEffectName, Wait=True, AutoEnable=True)

    def _scopeMagicGloveTargetEffectInterrupt(self, source, rune_id=None):
        rune_id = MagicGloveManager.getFirstRune()
        Rune = MagicGloveManager.getRune(rune_id)

        GroupName = Rune.EffectGroup
        MovieTargetEffectName = Rune.MovieEffectTarget

        MovieTargetEffect = GroupManager.getObject(GroupName, MovieTargetEffectName)
        if MovieTargetEffect.getPlay() is False:
            return
            pass

        source.addTask("TaskMovie2Interrupt", Movie2=MovieTargetEffect)
        source.addTask("TaskMovie2Stop", Movie2=MovieTargetEffect)

    def __updateState(self, value):
        bolean_Glove_Light = False
        if self.MovieButtons == []:
            return

        if value == "Idle":
            number = 0
            for key in self.movies:
                self.movies[key].setEnable(True)
                self.movies_Ready[key].setEnable(False)
                number = 1
                pass
            if self.MovieButtons[-1].getEnable() is True:
                self.tc_light = TaskManager.createTaskChain(Repeat=False)
                with self.tc_light as tc_light:
                    tc_light.addFunction(self.ButtonEnabler, number)
                    tc_light.addTask("AliasObjectAlphaTo", Object=self.MovieButtons[-1], From=1.0, To=0.0, Time=333.0, Wait=True)
                    tc_light.addDisable(Object=self.MovieButtons[-1])
                    tc_light.addFunction(self.ButtonSwicher, number)
            return

        if value == "Ready":
            quest = self.object.getActiveUseRuneQuest()
            if quest is None:
                return

            RuneID = quest.params['Rune_ID']
            Object = quest.params['Object']

            if RuneID not in self.Runes:
                return
            for key in self.movies:
                self.movies[key].setEnable(False)
                self.movies_Ready[key].setEnable(True)
                bolean_Glove_Light = True

            if bolean_Glove_Light:
                self.tc_light = TaskManager.createTaskChain(Repeat=False)
                with self.tc_light as tc_light:
                    tc_light.addFunction(self.ButtonEnabler, -1)
                    tc_light.addEnable(Object=self.MovieButtons[-1])
                    tc_light.addTask("AliasObjectAlphaTo", Object=self.MovieButtons[-1], From=0.0, To=1.0, Time=333.0)

                    tc_light.addNotify(Notificator.onMagicGlowReady)
                    # Notification.notify(Notificator.onMagicGlowReady)
            return

    # def __updateState(self, value):
    #
    #     if value == 'Idle':
    #         pass
    #     elif value == 'Ready':
    #         pass
    #     pass

    def __appendRunes(self, key, value):
        self.__createRune(value)
        self._Glove_Change(True)

    def __delParam(self, index, value, old):
        self._destroy_All_Movies()
        self.name = 0
        self.__updateRunes(self.Runes)

    def __updateRunes(self, value):
        Checker = False
        for rune_id in value:
            self.__createRune(rune_id)
            Checker = True
        if Checker is False:
            self._Glove_Change(Checker)
            pass

    def __createRune(self, RuneID):
        Rune = MagicGloveManager.getRune(RuneID)
        GroupName = Rune.RuneGroup
        MovieRuneIdleName = Rune.MovieIdle
        MovieRuneReadyName = Rune.MovieReady

        movieIdle = GroupManager.generateObjectUnique(MovieRuneIdleName + str(self.name), GroupName, MovieRuneIdleName)
        movieIdle.setEnable(True)
        entity_node = movieIdle.getEntityNode()
        self.Slot.addChild(entity_node)

        movieReady = GroupManager.generateObjectUnique(MovieRuneReadyName + str(self.name), GroupName, MovieRuneReadyName)
        entity_node = movieReady.getEntityNode()
        self.Slot.addChild(entity_node)

        self.name += 1
        self.movies[RuneID] = movieIdle
        self.movies_Ready[RuneID] = movieReady
        self._Runes_Placement(self.movies)
        self._Runes_Placement(self.movies_Ready)
        movieReady.setEnable(False)

    def _Runes_Placement(self, movies_dict):
        cent = self.Slot.getWorldPosition()
        movies_list = []
        for key in movies_dict:
            movies_list.append(movies_dict[key])
        node1 = movies_list[0].getEntityNode()
        first_rune = node1.getWorldPosition()

        first_rune.x = cent.x + 0.0
        first_rune.y = cent.y - 30.0
        node1.setWorldPosition(first_rune)
        Runes_Number = len(movies_list)

        c = Mengine.cosf(6.3 / Runes_Number)
        s = Mengine.sinf(6.3 / Runes_Number)

        for i in range(len(movies_list) - 1):
            rune_pos = movies_list[i].getEntityNode().getWorldPosition()
            rx = rune_pos.x - cent.x
            ry = rune_pos.y - cent.y
            rune_pos.x = cent.x + rx * c - ry * s
            rune_pos.y = cent.y + rx * s + ry * c
            movies_list[i + 1].getEntityNode().setWorldPosition(rune_pos)
        pass

    def ButtonSwicher(self, Number="All_Off"):
        for elem in self.MovieButtons:
            elem.setEnable(False)
        self.ButtonEnabler(Number)

    def ButtonEnabler(self, Number="All_Off"):
        if Number == "All_Off":
            return
        self.MovieButtons[Number].setEnable(True)

    def Tc_Cancel(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

    def _destroy_All_Movies(self):
        for key in self.movies:
            movie = self.movies[key]
            movie.onDestroy()
        self.movies = {}
        for key in self.movies_Ready:
            movie = self.movies_Ready[key]
            movie.onDestroy()
        self.movies_Ready = {}

    def _onDeactivate(self):
        self.Tc_Cancel()

        if self.tc_Glove_Change is not None:
            self.tc_Glove_Change.cancel()
            self.tc_Glove_Change = None

        self._destroy_All_Movies()

        TaskManager.cancelTaskChain("MagicGloveCheat", False)
        pass

    pass
