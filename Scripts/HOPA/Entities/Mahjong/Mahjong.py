from Foundation.DefaultManager import DefaultManager
from Foundation.Notificator import Notificator
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.Entities.Mahjong.MahjongManager import MahjongManager
from HOPA.QuestManager import QuestManager
from Holder import Holder
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")


class Mahjong(Enigma):
    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "FoundPairs", Append=Type._appendFoundPairs)

    def _appendFoundPairs(self, index, value):
        self.Inventory.appendParam("FoundItems", [value, ])
        self._update_buttons()
        Notification.notify(Notificator.onMahjongFoundPair, self.EnigmaName, value)

    def __init__(self):
        super(Mahjong, self).__init__()

        self.pair_buttons = []
        self.data_pairs = None

        self.current_button_name = None

        self.Inventory = None
        self.quest_pairs = []

        self.isHOG = True

    def _load_data(self):
        self.data_pairs = MahjongManager.getData(self.EnigmaName)
        self.Inventory = MahjongManager.getInventory(self.EnigmaName)
        self.Inventory.setParams(Enable=True, ItemsCount=len(self.data_pairs))

        for pair in self.object.getFoundPairs():
            if [pair, ] not in self.Inventory.getFoundItems():
                self.Inventory.appendParam("FoundItems", [pair, ])

    def _get_group_object(self, obj_name):
        if obj_name is None:
            return None

        Group = self.object.getGroup()
        button = Group.getObject(obj_name)
        return button

    def _get_button_pair(self, button):
        for data_pair in self.data_pairs:
            button1 = self._get_group_object(data_pair.getButton1Name())
            button2 = self._get_group_object(data_pair.getButton2Name())

            if button is button1 or button is button2:
                return button1, button2

        return None, None

    def _enable_button(self, button, value):
        button.setEnable(value)

        if value is True:
            button.setParam("Interactive", 1)

    def _reset_button(self, button):
        button_type = button.getType()
        if button_type == "ObjectMovie2Button":
            button.setParam("Block", False)
            return
        button_entity = button.getEntity()
        button.setParam("BlockState", False)
        button_entity.setState("onUp")

    def _update_buttons(self):
        for data_pair in self.data_pairs:
            button1_name, button2_name, checkbox_name = data_pair.getButton1Name(), data_pair.getButton2Name(), data_pair.getCheckBox()

            button1, button2 = self._get_group_object(button1_name), self._get_group_object(button2_name)

            enable_value = not (button1_name, button2_name) in self.FoundPairs

            self._enable_button(button1, enable_value)
            self._reset_button(button1)

            self._enable_button(button2, enable_value)
            self._reset_button(button2)

    def _update_checkboxes(self):
        for data_pair in self.data_pairs:
            checkbox_name = data_pair.getCheckBox()

            if checkbox_name is None:
                continue

            checkbox = self._get_group_object(checkbox_name)
            checkbox.setParam("Value", False)

    def _filter(self, EnigmaName, my_pair, pair):
        if self.EnigmaName != EnigmaName:
            return False
        if my_pair != pair:
            return False
        return True

    def _filter_Movie2Button(self, btn, holder):
        name = btn.getName()
        for (btn1, btn2) in self.quest_pairs:
            if name is btn1 or name is btn2:
                holder.set(btn)
                return True

        return False

    def _Quest_Generator(self, source):
        SceneName = EnigmaManager.getEnigmaSceneName(self.EnigmaName)
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        for data_pair in self.data_pairs:
            button1_name, button2_name = data_pair.getButton1Name(), data_pair.getButton2Name()
            self.quest_pairs.append((button1_name, button2_name))

        for (btn1, btn2), tc_parallel in source.addParallelTaskList(self.quest_pairs):
            button1, button2 = self._get_group_object(btn1), self._get_group_object(btn2)
            Quest = QuestManager.createLocalQuest("Mahjong", SceneName=SceneName, GroupName=GroupName, Object=button1,
                                                  Object2=button2)
            with QuestManager.runQuest(tc_parallel, Quest) as tc_quest:
                tc_quest.addListener(Notificator.onMahjongFoundPair, self._filter, (btn1, btn2))

    def _playEnigma(self):
        self._load_data()
        self._update_buttons()
        self._update_checkboxes()
        ButtonNameHolder = Holder()

        def _filter(btn, holder):
            holder.set(btn)
            return True

        with TaskManager.createTaskChain(Name="MahjongQuests") as tc_quest:
            tc_quest.addScope(self._Quest_Generator)

        with TaskManager.createTaskChain(Name="Mahjong", Repeat=True) as tc:
            with tc.addRaceTask(2) as (tc_button, tc_movie2):
                tc_button.addListener(Notificator.onButtonClickEndUp, _filter, ButtonNameHolder)
                tc_movie2.addListener(Notificator.onMovie2ButtonClickEnd, self._filter_Movie2Button, ButtonNameHolder)
            tc.addScope(self._button_click_scope, ButtonNameHolder)
            tc.addFunction(self._check_complete)

    def _skipEnigmaScope(self, source):
        pairs = []
        for data_pair in self.data_pairs:
            button1_name, button2_name, checkbox_name = data_pair.getButton1Name(), data_pair.getButton2Name(), data_pair.getCheckBox()

            if (button1_name, button2_name) in self.FoundPairs:
                continue

            pairs.append((button1_name, button2_name))

        for (button1_name, button2_name), tc_parallel in source.addParallelTaskList(pairs):
            button1, button2 = self._get_group_object(button1_name), self._get_group_object(button2_name)
            tc_parallel.addScope(self._play_hide_effect, button1, button2)
            tc_parallel.addFunction(self.object.appendParam, "FoundPairs", (button1_name, button2_name))

    def _check_complete(self):
        if self._is_complete() is True:
            self.enigmaComplete()

    def _is_complete(self):
        for data_pair in self.data_pairs:
            button1_name, button2_name = data_pair.getButton1Name(), data_pair.getButton2Name()

            if (button1_name, button2_name) not in self.FoundPairs:
                return False

        return True

    def flickerEffect(self, source, button):
        onUp = button.getParam("onUp")

        ResourceName = onUp["Resource"]
        Resource = Mengine.getResourceReference(ResourceName)

        sprite = Mengine.createSprite("Sprite_Find_Effect", Resource)
        sprite.enable()

        Position = Mengine.vec2f(*onUp["Position"])

        spriteCenter = sprite.getLocalImageCenter()

        newPosition = Position + spriteCenter

        node = Mengine.createNode("Interender")
        node.setLocalPosition(newPosition)

        self.object.getEntityNode().addChild(node)

        sprite.setOrigin(spriteCenter)
        node.addChild(sprite)

        source.addDisable(button)

        FullFlashingTime = DefaultManager.getDefaultFloat('Mahjong_FlickerEffect_FullFlashingTime', 1000)
        NumberOfFlashing = DefaultManager.getDefaultInt('Mahjong_FlickerEffect_NumberOfFlashing', 2)
        ScaleTo = DefaultManager.getDefaultTuple('Mahjong_FlickerEffect_ScaleTo', (1.2, 1.2, 1.2))

        time = FullFlashingTime / (2 * NumberOfFlashing)
        with source.addForTask(NumberOfFlashing) as (it, sourceFor):
            sourceFor.addTask('TaskNodeScaleTo', Node=sprite, To=ScaleTo, Time=time)
            sourceFor.addTask('TaskNodeScaleTo', Node=sprite, To=(1.0, 1.0, 1.0), Time=time)
        source.addFunction(sprite.disable)

    def _play_hide_effect(self, source, button1, button2):
        MahjongHidePairsTime = DefaultManager.getDefault("MahjongHidePairsTime", 500.0)

        if self.EnigmaName == '03_ShelvesHO2':
            with source.addParallelTask(2) as (tc_button1, tc_button2):
                tc_button1.addScope(self.flickerEffect, button1)
                tc_button2.addScope(self.flickerEffect, button2)
        else:
            sync_movie_1_name = None
            sync_movie_2_name = None
            sync_movie_1 = None
            sync_movie_2 = None

            for data in self.data_pairs:
                if button1.getName() is data.getButton1Name():
                    sync_movie_1_name = data.getButton1SyncMovie()
                if button2.getName() is data.getButton2Name():
                    sync_movie_2_name = data.getButton2SyncMovie()

            if sync_movie_1_name is not None:
                sync_movie_1 = self._get_group_object(sync_movie_1_name)

            if sync_movie_2_name is not None:
                sync_movie_2 = self._get_group_object(sync_movie_2_name)

            with source.addParallelTask(4) as (tc_button1, tc_sync_movie1, tc_button2, tc_sync_movie2):
                tc_button1.addTask("TaskNodeAlphaTo", Node=button1.getEntityNode(), From=1.0, To=0.0,
                                   Time=MahjongHidePairsTime)

                if sync_movie_1 is not None:
                    tc_sync_movie1.addEnable(sync_movie_1)
                    tc_sync_movie1.addTask("TaskNodeAlphaTo", Node=sync_movie_1.getEntityNode(), From=0.0, To=1.0,
                                           Time=MahjongHidePairsTime)

                tc_button2.addTask("TaskNodeAlphaTo", Node=button2.getEntityNode(), From=1.0, To=0.0,
                                   Time=MahjongHidePairsTime)

                if sync_movie_2 is not None:
                    tc_sync_movie2.addEnable(sync_movie_2)
                    tc_sync_movie2.addTask("TaskNodeAlphaTo", Node=sync_movie_2.getEntityNode(), From=0.0, To=1.0,
                                           Time=MahjongHidePairsTime)

    def _get_button_check_box(self, button):
        button_name = button.getName()

        for data_pair in self.data_pairs:
            button1_name, button2_name, checkbox_name = data_pair.getButton1Name(), data_pair.getButton2Name(), data_pair.getCheckBox()
            if button_name in (button1_name, button2_name):
                return self._get_group_object(checkbox_name)

        return None

    def _play_cancel_on_checkbox(self, source, checkbox):
        if checkbox is None:
            return

        checkbox_value = checkbox.getParam("Value")

        if checkbox_value is False:
            return

        checkbox_entity = checkbox.getEntity()

        movie_button = checkbox_entity.MovieButtonTrue
        movie_button_entity = movie_button.getEntity()

        source.addFunction(movie_button_entity.setState, "Click")

        with source.addFork() as fork:
            def _filter(obj):
                if obj is movie_button_entity:
                    return True
                return False

            fork.addListener(Notificator.onMovie2ButtonClickEnd, Filter=_filter)
            fork.addParam(checkbox, "Value", False)

    def _play_cancel_on_all_checkboxes(self, source):
        for data_pair in self.data_pairs:
            button1_name, button2_name, checkbox_name = data_pair.getButton1Name(), data_pair.getButton2Name(), data_pair.getCheckBox()
            if checkbox_name is None:
                continue

            checkbox = self._get_group_object(checkbox_name)

            source.addScope(self._play_cancel_on_checkbox, checkbox)

    def _play_close_effect(self, source, button1, button2):
        button_type = button1.getType()
        with source.addParallelTask(2) as (source_button1, source_button2):
            if button_type == "ObjectMovie2Button":
                source_button1.addParam(button1, "Block", False)
                source_button2.addParam(button2, "Block", False)
            else:
                source_button1.addParam(button1, "Interactive", 1)
                source_button1.addParam(button1, "BlockState", False)
                source_button1.addTask("TaskButtonChangeState", Button=button1, NewState="onUp")

                source_button2.addParam(button2, "Interactive", 1)
                source_button2.addParam(button2, "BlockState", False)
                source_button2.addTask("TaskButtonChangeState", Button=button2, NewState="onUp")

        source.addScope(self._play_cancel_on_all_checkboxes)

    def _play_choose_effect(self, source, button):
        button_type = button.getType()
        if button_type == "ObjectMovie2Button":
            return
        source.addTask("TaskButtonChangeState", Button=button, NewState="onDown")
        source.addParam(button, "Interactive", 0)

    def _is_valid_pair_for_current_button(self, button):
        pair = self._get_button_pair(button)

        current_button = self._get_group_object(self.current_button_name)

        if button in pair and current_button in pair:
            return True

        return False

    def _button_click_scope(self, source, holder):
        button = holder.get()
        button_type = button.getType()
        button1, button2 = self._get_button_pair(button)

        if button_type == "ObjectMovie2Button":
            source.addParam(button, "Block", True)
        else:
            source.addParam(button, "BlockState", True)

        if self.current_button_name is not None:
            """ CASE WHEN WE CHOOSE SECOND BUTTON """

            current_button = self._get_group_object(self.current_button_name)

            if self._is_valid_pair_for_current_button(button) is True:
                # if energy feature is disabled - it just starts ScopeCb with button1, button2
                source.addTask("AliasEnergyConsume", Action="CombineItems", ScopeCb=self.__scope_valid_click,
                               CbArgs=[button1, button2],  # if energy not enough - imagine that we did invalid click
                               FailScopeCb=self.__scope_invalid_click, FailCbArgs=[button, current_button])
            else:
                source.addScope(self.__scope_invalid_click, button, current_button)

            self.current_button_name = None

        else:
            """ CASE WHEN WE CHOOSE FIRST BUTTON """

            self.current_button_name = button.getName()
            source.addScope(self._play_choose_effect, button)

    def __scope_valid_click(self, source, button1, button2):
        """ _button_click_scope - when we choose valid second button """

        source.addNotify(Notificator.onSoundEffectOnObject, self.object, "Mahjong_FoundPair")
        with source.addParallelTask(2) as (SoundEffect, HideEffect):
            HideEffect.addScope(self._play_hide_effect, button1, button2)
            SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'Mahjong_HideEffect')
        source.addScope(self._play_cancel_on_all_checkboxes)
        source.addFunction(self.object.appendParam, "FoundPairs", (button1.getName(), button2.getName()))

    def __scope_invalid_click(self, source, clicked_button, current_button):
        """ _button_click_scope - when we choose invalid second button """

        source.addScope(self._play_close_effect, clicked_button, current_button)

    def _restoreEnigma(self):
        self._playEnigma()

    def _onDeactivate(self):
        super(Mahjong, self)._onDeactivate()

        TaskManager.cancelTaskChain("Mahjong", exist=False)
        TaskManager.cancelTaskChain("MahjongQuests", exist=False)
        TaskManager.cancelTaskChain("MahjongSyncMovie2", exist=False)

        if self.Inventory is not None:
            self.Inventory.setEnable(False)
        self.Inventory = None
