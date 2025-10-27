from Foundation.ArrowManager import ArrowManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.HintManager import HintManager
from HOPA.ItemManager import ItemManager

from BoneBoardManager import BoneBoardManager
from BoneHelpChainManager import BoneHelpChainManager
from BoneHelper import HelpChain, CasualHelper
from BoneItem import BoneItem
from BoneMinds import BoneMinds

class BoneBoard(BaseEntity):
    CASUAL_HELP = "Movie_CasualHelper"

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction("HelperState")
        Type.addAction("BoneActivities")
        Type.addAction("ButtonAvailable")
        Type.addAction("UseAvailable")
        pass

    def __init__(self):
        super(BoneBoard, self).__init__()
        self.item_map = {}
        self.bones_inventory = {}
        self.bone_usage = {}
        self.item_group = {}
        self.activated = False
        self.BoneGroup = None
        self.Helper = None
        self.CasualHelper = None
        self.orderBoneItems = []
        self.current_view = None
        pass

    def _onActivate(self):
        self.preparation()
        pass

    def _onDeactivate(self):
        self.hideBoard()
        self._storing_save()
        self.orderBoneItems = []
        if self.CasualHelper is not None:
            self.CasualHelper.onDeactivate()
            pass
        pass

    def onPreparation(self):
        super(BoneBoard, self).onPreparation()
        pass

    def preparation(self):
        #        if self.activated:
        #            return

        def masking(item):
            if item is None or item == "":
                return None
            else:
                return self.BoneGroup.getObject(item)
            pass

        boneGroupName = BoneBoardManager.getGroup()

        self.BoneGroup = GroupManager.getGroup(boneGroupName)
        items = BoneBoardManager.getItems()
        self.items = [self.BoneGroup.getObject(it) for it in items]
        mask_prev = BoneBoardManager.getPrev()
        inv_item = BoneBoardManager.getInvItem()
        self.exel_str_item = dict(zip(inv_item, self.items))  # invitem -> bone item

        self.init_helper()
        self.mask_prev = map(masking, mask_prev)
        self.prev_item_pair = dict(zip(self.mask_prev, self.items))
        movie_add_name = BoneBoardManager.getMovieAdd()
        movie_use_name = BoneBoardManager.getMovieUse()
        movie_wrong_name = BoneBoardManager.getMovieWrong()
        movie_over_names = BoneBoardManager.getMovieOver()
        MovieAdds = [self.BoneGroup.getObject(movie_add) for movie_add in movie_add_name]
        MovieUses = [self.BoneGroup.getObject(movie_use) for movie_use in movie_use_name]
        MovieWrongs = [self.BoneGroup.getObject(movie_wrong) for movie_wrong in movie_wrong_name]
        MovieOvers = [self.BoneGroup.getObject(movie_over) for movie_over in movie_over_names]
        self.orderBoneItems = []
        for i, item in enumerate(self.items):
            Item = BoneItem(self.mask_prev[i], item, MovieUses[i], MovieWrongs[i], MovieAdds[i], MovieOvers[i])
            self.item_map[item] = Item
            # ------> appendix
            self.orderBoneItems.append(Item)
            pass

        self.ButtonBone = self.object.getObject("Button_Bone")
        self.SocketHide = self.BoneGroup.getObject("Socket_Back")
        self.ButtonBone.setEnable(self.activated)
        self.ButtonBone.setInteractive(True)
        self.MovieActive = self.object.getObject("Movie_On")
        self.MovieActive.setEnable(False)
        self._restoring_save()
        pass

    def _restoring_save(self):
        HelpCompletionState = self.object.getParam("HelperState")
        if HelpCompletionState is True and self.Helper is not None:
            self.Helper.turnOffHelp()
            pass

        availableButton = self.object.getParam("ButtonAvailable")
        if availableButton is True:
            self.ButtonBone.setEnable(True)
            self.ButtonBone.setInteractive(True)
            pass
        else:
            self.ButtonBone.setEnable(False)
            self.activated = False
            pass

        orderActivityList = self.object.getParam("BoneActivities")
        if orderActivityList == []:
            pass
        else:
            for standing, BoneItemInstance in enumerate(self.orderBoneItems):
                activity = orderActivityList[standing]
                if activity is True:
                    BoneItemInstance.restore_active()
                    pass
                else:
                    pass
                pass
            pass

        UseAvailableDict = self.object.getParam("UseAvailable")
        if UseAvailableDict != {}:
            for strItem, group in UseAvailableDict.items():
                #                groupObject = GroupManager.getGroup(group)
                self.on_bone_usage(strItem, group)
            pass
        pass

    def _storing_save(self):
        orderActivityList = []
        for BoneItemInstance in self.orderBoneItems:
            activity = BoneItemInstance.getActive()
            orderActivityList.append(activity)
            pass

        self.object.setParam("BoneActivities", orderActivityList)
        if self.Helper is not None:
            HelpCompletionState = self.Helper.isCompletion()
            HelpSkip = self.Helper.isSkipped()
            if HelpCompletionState is False and HelpSkip is True:
                HelpCompletionState = True
                pass
            self.object.setParam("HelperState", HelpCompletionState)
            pass

        UseAvailableDict = {}
        for keyItemInst in self.bone_usage.keys():
            itemStingKey = self.bone_usage.get(keyItemInst)
            groupName = self.item_group.get(keyItemInst)
            UseAvailableDict[itemStingKey] = groupName
        self.object.setParam("UseAvailable", UseAvailableDict)
        buttonAvailable = self.ButtonBone.getEnable()
        self.object.setParam("ButtonAvailable", buttonAvailable)
        pass

    def init_helper(self):
        movies = BoneHelpChainManager.getChainMovies()
        buttons = BoneHelpChainManager.getChainButtons()
        texts = BoneHelpChainManager.getChainTexts()

        for i, object in enumerate(movies):
            movie, button, text = movies[i], buttons[i], texts[i]
            movie.setEnable(False)
            button.setEnable(False)
            text.setEnable(False)
            pass
        self.Helper = HelpChain(movies, buttons, texts)

        if self.object.hasObject(BoneBoard.CASUAL_HELP) is False:
            return
            pass
        movie_casual_helper = self.object.getObject(BoneBoard.CASUAL_HELP)
        self.CasualHelper = CasualHelper(movie_casual_helper)
        pass

    def on_show_bones(self, button):
        if button is not self.ButtonBone:
            if self.Helper is not None:
                self.Helper.actionButton(button)
            return False
        else:
            if self.hideBoard():
                return False
                pass
            self.showBoard()
            if self.Helper is not None:
                self.Helper.iterate()
                self.Helper.turnOffHelp()
            pass
        pass
        return False

    def activate_button(self):
        if self.ButtonBone.getEnable() is True:
            self.ButtonBone.setInteractive(True)
            return
            pass
        self.ButtonBone.setEnable(True)
        self.MovieActive.setEnable(True)
        with TaskManager.createTaskChain() as tc:  # enabling button movie
            tc.addTask("TaskMoviePlay", Movie=self.MovieActive)
            tc.addFunction(self.ButtonBone.setEnable, True)
            tc.addFunction(self.MovieActive.setEnable, False)
            tc.addFunction(self.Helper.iterate)
            pass
        self.ButtonBone.setInteractive(True)
        self.object.setParam("ButtonAvailable", True)
        pass

    def instantlyBoneActivate(self, ExelKeyName):
        ItemName = self.exel_str_item.get(ExelKeyName)
        if ItemName is None:
            Trace.log("Entity", 0, "BoneBoard.instantlyBoneActivate cant find association with %s" % (ExelKeyName,))
            return False
            pass

        if self.item_map == {}:
            Trace.log("Entity", 0, " try activate empty BoneBoard!!!!")
            return False
            pass

        if isinstance(ItemName, str):
            Trace.log("Entity", 0, "BoneBoard.instantlyBoneActivate gets some str instance instead item %s" % ItemName)
            return False
            pass

        BoneInst = self.item_map.get(ItemName)
        if BoneInst is None:
            Trace.log("Entity", 0, "BoneBoard.instantlyBoneActivate not found such %s" % (ItemName,))
            return False
            pass
        BoneInst.set_active()
        BoneInst.make_action()
        return True
        pass

    def on_socket_click(self, socket):
        if socket == self.SocketHide:
            self.hideBoard()
            return False

        if socket not in self.prev_item_pair:
            return False

        attach = ArrowManager.getArrowAttach()
        if attach in self.bones_inventory:
            bone_item = self.prev_item_pair[socket]
            if self.bones_inventory[attach] != bone_item:
                BoneItem = self.item_map[bone_item]
                BoneItem.make_action()
                return False
                pass
            self.addItem(self.bones_inventory[attach])
            arrowItemEntity = attach.getEntity()
            arrowItemEntity.take()
            AttachName = attach.getName()
            Notification.notify(Notificator.onBoneAdd, AttachName, "done_")

        else:
            BoneMinds.play("ID_EMPTY_BONE")
            pass
        return False
        pass

    def hideBoard(self):
        if self.BoneGroup.getEnable():
            self.cancelHint()
            self.BoneGroup.onDisable()
            return True
        return False
        pass

    def showBoard(self):
        ChainName = "BoneBoardShowBoard"
        if TaskManager.existTaskChain(ChainName):
            TaskManager.cancelTaskChain(ChainName)
            return False
            pass

        elif self.BoneGroup is None:
            Trace.log("Entity", 0, "BoneBoard: Bone Group is None !!!! ")
            return False
            pass

        elif self.BoneGroup.getEnable() is True:
            return False
            pass

        with TaskManager.createTaskChain(Name=ChainName) as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName=self.BoneGroup.getName(), Value=True)
            pass
        pass

    def addItem(self, item):
        Item = self.item_map[item]
        Item.set_active()
        pass

    def on_bone_come(self, invItem, relatedItem):
        if not self.activated:
            self.activate_button()
            self.activated = True
            pass

        item_inv = ItemManager.getItemInventoryItem(invItem)
        itemObj = self.exel_str_item[relatedItem]
        self.bones_inventory[item_inv] = itemObj
        return False
        pass

    def on_item_click(self, item_clicked):
        if item_clicked in self.prev_item_pair:
            self.on_socket_click(item_clicked)
            return False
            pass

        attach = ArrowManager.getArrowAttach()
        if item_clicked in self.bone_usage:
            used_scene = self.item_group[item_clicked]
            sceneName = SceneManager.getCurrentSceneName()
            if used_scene != sceneName:
                BoneItem = self.item_map[item_clicked]
                BoneItem.make_action(wrong=True)
                return False
            str_key = self.bone_usage[item_clicked]
            del self.bone_usage[item_clicked]
            BoneItem = self.item_map[item_clicked]
            note_msg = "done:%s" % (str_key,)
            BoneItem.make_action(note_msg)
            pass

        elif item_clicked in self.item_map:
            BoneItem = self.item_map[item_clicked]
            BoneItem.make_action()
            pass
        return False
        pass

    def on_bone_usage(self, itemStingKey, sceneName=None):
        if self.activated is False:
            self.activate_button()
            self.activated = True
            pass
        if not isinstance(itemStingKey, str) or itemStingKey.startswith("done"):
            self.hideBoard()
            return False
        sceneName = sceneName or SceneManager.getCurrentSceneName()
        if itemStingKey in self.exel_str_item:
            item = self.exel_str_item[itemStingKey]
            self.bone_usage[item] = itemStingKey
            self.item_group[item] = sceneName
            BoneItem = self.item_map[item]
            BoneItem.make_useful()
            return False
            pass
        return False

    def cancelHint(self):
        HintManager.currentHintEnd()
        pass

    def onCasualShowHelp(self):
        if self.CasualHelper is None:
            return
            pass

        self.CasualHelper.onShow()
        pass

    def onCasualHideHelp(self):
        if self.CasualHelper is None:
            return
            pass

        self.CasualHelper.onHide()
        pass

    def onItemEntered(self, itemObject):
        TaskName = "BoneBoard_OverView"
        if itemObject in self.item_map:
            boneItemInst = self.item_map[itemObject]
            movie = boneItemInst.getOver()
            self.current_view = itemObject
            if TaskManager.existTaskChain(TaskName):
                TaskManager.cancelTaskChain(TaskName)
                pass

            with TaskManager.createTaskChain(Name=TaskName) as tc:
                with tc.addRaceTask(2) as (tc_view, tc_leave):
                    tc_view.addEnable(movie)
                    tc_view.addTask("TaskMoviePlay", Movie=movie, Loop=True)

                    tc_leave.addListener(Notificator.onItemMouseLeave, Filter=self.onLeaved)
                    tc_leave.addDisable(movie)
                    pass
                pass
            pass
        return False
        pass

    def onLeaved(self, itemObject):
        if itemObject == self.current_view:
            self.current_view = None
            return True
            pass
        return False
        pass

    pass
