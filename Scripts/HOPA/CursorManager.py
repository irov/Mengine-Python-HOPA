from Foundation.ArrowBlackListManager import ArrowBlackListManager
from Foundation.ArrowManager import ArrowManager
from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.TaskManager import TaskManager
from HOPA.QuestManager import QuestManager
from Notification import Notification


class CursorManager(object):
    s_block_Cursore_Update_in_Puzzle = False
    s_block_Cursore_Update = False
    s_currentCursor = None
    s_currentCursorModeName = "Default"
    s_lastCursorModeName = None
    s_currentCursorChildren = []
    s_cursors = {}
    s_cursorObjects = {}

    s_currentCursorObjectsPakName = "Game"
    s_cursorObjectsPaks = {}

    s_cursorObjectsShow = {}
    s_cursorObjectsShowPaks = {}

    s_systemAttach = []
    s_macroAttached = []
    s_group = None
    s_onObject = None
    s_objectFilter = {}
    s_cursorChecks = {}

    onQuestRunObserver = None
    onQuestEndObserver = None
    onSceneEnterObserver = None
    onCursorModeObserver = None
    onSceneInit = None
    onSceneDeactivateObserver = None

    onCustomCursorObserver = None

    onMacroArrowAttach = None
    onMacroAttachItemRemove = None

    onEnigmaActivateObserver = None
    onEnigmaDeactivateObserver = None

    class Cursor(object):
        def __init__(self, iconName, enterFilterObserver, leaveFilterObserver, questType, cursorCheckAction, priority,
                     _type, arrowItem):
            self.icon = iconName
            self.enterFilterObserver = enterFilterObserver
            self.leaveFilterObserver = leaveFilterObserver
            self.questType = questType
            self.cursorCheckAction = cursorCheckAction
            self.priority = priority
            self.type = _type
            self.arrowItem = arrowItem

    @staticmethod
    def onInitialize():
        CursorManager.onQuestRunObserver = Notification.addObserver(Notificator.onQuestRun, CursorManager._onAddQuestFilter)

        CursorManager.onQuestEndObserver = Notification.addObserver(Notificator.onQuestEnd, CursorManager._onRemoveQuestFilter)

        CursorManager.onCursorModeObserver = Notification.addObserver(Notificator.onCursorMode, CursorManager.__onCursorModeFilter)

        CursorManager.onSceneInit = Notification.addObserver(Notificator.onSceneInit, CursorManager.__onSceneInit)

        CursorManager.onSceneDeactivateObserver = Notification.addObserver(Notificator.onSceneDeactivate, CursorManager.__onSceneDeactivateFilter)

        CursorManager.onCustomCursorObserver = Notification.addObserver(Notificator.onCustomCursor, CursorManager.__onCustomCursor)

        CursorManager.onMacroArrowAttach = Notification.addObserver(Notificator.onMacroArrowAttach, CursorManager.__changeArrowAttachedState)

        CursorManager.onEnigmaActivateObserver = Notification.addObserver(Notificator.onEnigmaActivate, CursorManager.__onPuzzleOpen)

        CursorManager.onEnigmaDeactivateObserver = Notification.addObserver(Notificator.onEnigmaDeactivate, CursorManager.__onPuzzleClose)

        CursorManager.onMacroAttachItemRemove = Notification.addObserver(Notificator.onMacroAttachItemRemoveObserver, CursorManager.__removeAttachItems)

    @staticmethod
    def onFinalize():
        CursorManager.__removeCursorChildren()

        CursorManager.s_currentCursor = None
        CursorManager.s_group = None
        CursorManager.s_onObject = None
        CursorManager.s_objectFilter = {}
        CursorManager.s_cursorChecks = {}
        CursorManager.s_macroAttached = []
        CursorManager.onMacroAttachItemRemove = None
        CursorManager.onEnigmaActivateObserver = None
        CursorManager.onEnigmaDeactivateObserver = None

        Notification.removeObserver(CursorManager.onQuestRunObserver)
        Notification.removeObserver(CursorManager.onQuestEndObserver)
        Notification.removeObserver(CursorManager.onCursorModeObserver)
        Notification.removeObserver(CursorManager.onSceneInit)
        Notification.removeObserver(CursorManager.onSceneDeactivateObserver)
        Notification.removeObserver(CursorManager.onCustomCursorObserver)
        Notification.removeObserver(CursorManager.onMacroArrowAttach)
        Notification.removeObserver(CursorManager.onMacroAttachItemRemove)
        Notification.removeObserver(CursorManager.onEnigmaActivateObserver)
        Notification.removeObserver(CursorManager.onEnigmaDeactivateObserver)

        for cursor in CursorManager.s_cursors.itervalues():
            if cursor.enterFilterObserver is not None:
                Notification.removeObserver(cursor.enterFilterObserver)

            if cursor.leaveFilterObserver is not None:
                Notification.removeObserver(cursor.leaveFilterObserver)

        CursorManager.cursors = {}

    @staticmethod
    def __onSceneInit(sceneName):
        CursorManager.setArrowCursor("Default")

        return False
        pass

    @staticmethod
    def __onSceneDeactivateFilter(sceneName):
        CursorManager.setLastCursorMode(None)
        CursorManager.__removeCursorChildren()

        return False

    @staticmethod
    def __onCustomCursor(value):
        if value:
            pak_name = "Game"
        else:
            pak_name = "System"

        CursorManager.changeCursorPak(pak_name)

        CursorManager.setLastCursorMode(None)

        CursorManager.updateArrowCursor(True)

        return False

    @staticmethod
    def __removeCursorChildren():
        if len(CursorManager.s_currentCursorChildren) != 0:
            for currentMovie in CursorManager.s_currentCursorChildren:
                if currentMovie.isActive() is False:
                    continue

                movieEntity = currentMovie.getEntity()
                movieEntity.removeFromParent()

                currentMovie.setEnable(False)

            CursorManager.s_currentCursorChildren = []
            CursorManager.s_onObject = None

    @staticmethod
    def getCursorChildren():
        return CursorManager.s_currentCursorChildren

    @staticmethod
    def importCursorCheck(module, _cursorCheckName, cursorCheckActionName):
        Name = "%s" % cursorCheckActionName
        FromName = module
        ModuleName = "%s.%s" % (FromName, Name)

        try:
            Module = __import__(ModuleName, fromlist=[FromName])
        except ImportError as ex:
            Trace.log("System", 0, "CursorManager.importCursorCheck: invalid import module '%s' from '%s' ex '%s'" % (Name, FromName, ex))
            return None

        cursorCheckAction = getattr(Module, Name)

        return cursorCheckAction

    @staticmethod
    def loadParams(module, param):
        if param == "Cursors":
            CursorManager.loadCursors(module, "HOPA.CursorCheck", "Cursors")

        if param == "CursorObjects":
            CursorManager.loadCursorObjects(module, "CursorObjects")

        return True

    @staticmethod
    def loadCursors(module, cursorModule, param):
        cursors_data = []
        cursors_enter_observers = []
        cursors_leave_observers = []

        ''' Load Cursors Data '''
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            ResourceName = record.get("ResourceName")
            EnterFilter = record.get("EnterFilter")

            if EnterFilter is not None:
                EnterFilter = Notificator.getIdentity(EnterFilter)

            LeaveFilter = record.get("LeaveFilter")
            if LeaveFilter is not None:
                LeaveFilter = Notificator.getIdentity(LeaveFilter)

            QuestType = record.get("QuestID")
            CursorCheck = record.get("CursorCheck")
            Priority = record.get("Priority", 0)
            Type = record.get("Type")
            ArrowItem = bool(record.get("ArrowItem", 1))

            if QuestType is not None and CursorCheck is None:
                Trace.msg_err("CursorManager.loadCursors: cursor %s have questType %s but not have check action (please add)" % (Name, QuestType))
                continue

            cursorCheckAction = None

            if CursorCheck is not None:
                cursorCheckAction = CursorManager.importCursorCheck(cursorModule, Name, CursorCheck)

            cursors_data.append(
                (Name, ResourceName, EnterFilter, LeaveFilter, QuestType, cursorCheckAction, Priority, Type, ArrowItem))

        '''  Load Leave Mouse '''
        for (Name, ResourceName, EnterFilter, LeaveFilter, QuestType, cursorCheckAction, Priority, Type,
        ArrowItem) in cursors_data:
            if LeaveFilter is not None:
                cursors_leave_observers.append(Notification.addObserver(LeaveFilter, CursorManager._arrowLeaveFilter))

            else:
                cursors_leave_observers.append(None)

        ''' Load Enter Mouse '''
        for (Name, ResourceName, EnterFilter, LeaveFilter, QuestType, cursorCheckAction, Priority, Type, ArrowItem) in cursors_data:
            if EnterFilter is not None:
                cursors_enter_observers.append(
                    Notification.addObserver(EnterFilter, CursorManager._arrowEnterFilter, Name))
            else:
                cursors_enter_observers.append(None)

        '''  Save Cursor Data With Observers Refs to CursorManager '''
        for index, (Name, ResourceName, EnterFilter, LeaveFilter, QuestType, cursorCheckAction, Priority, Type, ArrowItem) in enumerate(cursors_data):
            CursorManager.s_cursors[Name] = CursorManager.Cursor(ResourceName, cursors_enter_observers[index],
                                                                 cursors_leave_observers[index], QuestType,
                                                                 cursorCheckAction, Priority, Type, ArrowItem)

    @staticmethod
    def loadCursorObjects(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ModeName = record.get("ModeName")

            # Custom cursor
            GameCursorModeObject = record.get("CursorModeObject")
            GameCursorsGroup = record.get("CursorsGroup")

            if isinstance(GameCursorsGroup, GroupManager.EmptyGroup):
                continue
                pass

            GameCursorObject = GroupManager.getObject(GameCursorsGroup, GameCursorModeObject)

            if GameCursorObject is None:
                Trace.log("System", 0, "CursorManager.loadCursorObjects: invalid get object '%s' from '%s'" % (
                GameCursorModeObject, GameCursorsGroup))
                continue

            GameCursorObject.setEnable(False)

            if "Game" not in CursorManager.s_cursorObjectsPaks:
                CursorManager.s_cursorObjectsPaks["Game"] = {}
                pass

            CursorManager.s_cursorObjectsPaks["Game"][ModeName] = GameCursorObject

            # Custom cursor Show movie
            cursor_show_movie_name = GameCursorModeObject + "_Show"

            if "Game" not in CursorManager.s_cursorObjectsShowPaks:
                CursorManager.s_cursorObjectsShowPaks["Game"] = {}
                pass

            if GroupManager.hasObject(GameCursorsGroup, cursor_show_movie_name):
                cursor_show_movie = GroupManager.getObject(GameCursorsGroup, cursor_show_movie_name)
                cursor_show_movie.setEnable(False)

                CursorManager.s_cursorObjectsShowPaks["Game"][ModeName] = cursor_show_movie
                pass

            # system cursor mode
            SystemCursorModeObject = record.get("SystemCursorModeObject", GameCursorModeObject)
            SystemCursorsGroup = record.get("SystemCursorsGroup", GameCursorsGroup)

            SystemCursorObject = GroupManager.getObject(SystemCursorsGroup, SystemCursorModeObject)
            SystemCursorObject.setEnable(False)

            if "System" not in CursorManager.s_cursorObjectsPaks:
                CursorManager.s_cursorObjectsPaks["System"] = {}
                pass

            CursorManager.s_cursorObjectsPaks["System"][ModeName] = SystemCursorObject

            # System cursor Show movie
            cursor_show_movie_name = SystemCursorModeObject + "_Show"
            if "System" not in CursorManager.s_cursorObjectsShowPaks:
                CursorManager.s_cursorObjectsShowPaks["System"] = {}
                pass

            if GroupManager.hasObject(SystemCursorsGroup, cursor_show_movie_name):
                cursor_show_movie = GroupManager.getObject(SystemCursorsGroup, cursor_show_movie_name)
                cursor_show_movie.setEnable(False)

                CursorManager.s_cursorObjectsShowPaks["System"][ModeName] = cursor_show_movie
                pass

            # system attach
            SystemAttach = bool(record.get("SystemAttach"))

            if SystemAttach is False or None:
                continue

            CursorManager.s_systemAttach.append(ModeName)

        CursorManager.updateCursorObjects()

    @staticmethod
    def attachArrow(attach, movieAttach=True):
        if CursorManager.s_attach is attach:
            print("CursorManager attachArrow: You 'attach' already has this item.")
            return

        if CursorManager.s_attach is not None:
            oldAttach = CursorManager.s_attach
            CursorManager.s_attach = None
            Notification.notify(Notificator.onArrowDeattach, oldAttach)

        CursorManager.s_attach = attach

        currentMovie = CursorManager.getCurrentCursorMovie()
        movieEntity = currentMovie.getEntity()

        item = attach
        if item is not None:
            if movieEntity.hasMovieSlot("item") is True and movieAttach is True:
                itemEntityNode = item.getEntityNode()
                slotItem = movieEntity.getMovieSlot("item")
                pos = item.getArrowPoint()
                itemEntityNode.setLocalPosition((-pos[0], -pos[1]))
                item.setOrigin((0, 0))
                slotItem.addChild(itemEntityNode)

        Notification.notify(Notificator.onArrowAttach, attach)

    @staticmethod
    def hasSlotItem():
        currentMovie = CursorManager.getCurrentCursorMovie()
        if currentMovie.isActive() is False:
            return True

        movieEntity = currentMovie.getEntity()

        if movieEntity.hasMovieSlot("item") is True:
            return True

        return False

    @staticmethod
    def attachSlotItem(item):
        currentMovie = CursorManager.getCurrentCursorMovie()
        if currentMovie.isActive() is False:
            return True

        movieEntity = currentMovie.getEntity()

        if movieEntity.hasMovieSlot("item") is False:
            return

        if item is not None and movieEntity.hasMovieSlot("item") is True:
            itemEntityNode = item.getEntityNode()
            slotItem = movieEntity.getMovieSlot("item")
            pos = item.getArrowPoint()
            itemEntityNode.setLocalPosition((-pos[0], -pos[1]))
            item.setOrigin((0, 0))
            slotItem.addChild(itemEntityNode)

        return False

    @staticmethod
    def removeChildren():
        # arrow = CursorManager.getArrow()
        # arrow.removeAllChild()
        return

    @staticmethod
    def getCurrentCursorObjectsPakName():
        return CursorManager.s_currentCursorObjectsPakName

    @staticmethod
    def hasCursorPak(pak_name):
        return pak_name in CursorManager.s_cursorObjectsPaks

    @staticmethod
    def updateCursorObjects():
        CursorManager.s_cursorObjects = CursorManager.s_cursorObjectsPaks[CursorManager.s_currentCursorObjectsPakName]

        CursorManager.s_cursorObjectsShow = CursorManager.s_cursorObjectsShowPaks[
            CursorManager.s_currentCursorObjectsPakName]

    @staticmethod
    def changeCursorPak(pak_name):
        if not CursorManager.hasCursorPak(pak_name):
            Trace.log("Manager", 0, "CursorManager.changeCursorPak: No pak name {} in {}".format(pak_name, CursorManager.s_cursorObjectsPaks.keys()))
            return

        CursorManager.s_currentCursorObjectsPakName = pak_name

        CursorManager.updateCursorObjects()

    @staticmethod
    def hasCursorObjectShow(mode_name):
        return mode_name in CursorManager.s_cursorObjectsShow

    @staticmethod
    def getCursorObjectShow(mode_name):
        return CursorManager.s_cursorObjectsShow.get(mode_name)

    @staticmethod
    def hasCursorMode(modeName):
        if modeName not in CursorManager.s_cursors:
            return False

        return True

    @staticmethod
    def setCursorMode(modeName, force=False):
        if Mengine.hasTouchpad() and _DEVELOPMENT is False:
            return False

        if modeName not in CursorManager.s_cursors:
            return False

        CursorManager.s_currentCursorModeName = modeName

        return CursorManager.updateArrowCursor(force)

    @staticmethod
    def setArrowCursor(modeName, force=False):
        return CursorManager.setCursorMode(modeName, force)

    @staticmethod
    def setBlockCursorUpdate(block):
        CursorManager.s_block_Cursore_Update = block

    @staticmethod
    def updateArrowCursor(force):
        if Mengine.hasTouchpad() and _DEVELOPMENT is False:
            return

        usingCustomCursor = Mengine.getCurrentAccountSettingBool("CustomCursor")
        if usingCustomCursor:
            Mengine.setCursorMode(False)
        else:
            Mengine.setCursorMode(True)
            CursorManager.__removeCursorChildren()

        if CursorManager.s_block_Cursore_Update is True:
            CursorManager.s_currentCursorModeName = "Default"

        if CursorManager.s_currentCursorModeName is not None and CursorManager.s_currentCursorModeName not in CursorManager.s_cursors:
            Trace.log("CursorManager", 0,
                      "CursorManager.updateArrowCursor: current CursorModeName is not register %s." % (CursorManager.s_currentCursorModeName))
            return False

        if CursorManager.s_currentCursorModeName is None:
            CursorManager.s_currentCursor = None

            return False

        # not need update same cursor mode
        current_cursor_mode = CursorManager.getCursorMode()
        last_cursor_mode = CursorManager.getLastCursorMode()

        if usingCustomCursor and not force and current_cursor_mode == last_cursor_mode:
            return True

        cursor = CursorManager.s_cursors[CursorManager.s_currentCursorModeName]
        CursorManager.s_currentCursor = cursor

        if CursorManager.s_currentCursor is not None:
            if force is False and cursor.priority < CursorManager.s_currentCursor.priority:
                return False

        # PROBABLY DEPRECATED (NOT USED IN HOPA)

        WinCursors = Mengine.getCursorMode()

        if WinCursors is True:
            WinCursorsChange = DefaultManager.getDefaultBool("WinCursorsChange", True)
            if WinCursorsChange is True:
                iconName = CursorManager.s_currentCursor.icon
                Mengine.setCursorIcon(iconName)

        if CursorManager.s_currentCursorModeName not in CursorManager.s_cursorObjects:
            CursorManager.__removeCursorChildren()

            return True

        arrow = CursorManager.getArrow()

        SystemCursor = Mengine.getCursorMode()
        CursorSystemAttachX = None
        if SystemCursor is True:
            if CursorManager.s_currentCursorModeName not in CursorManager.s_systemAttach:
                item = ArrowManager.getArrowAttach()
                if item is not None:
                    itemEntity = item.getEntity()
                    arrow.addChild(itemEntity.node)

                return True

            CursorSystemAttach = DefaultManager.getDefaultBool("CursorSystemAttach", False)
            if CursorSystemAttach is False:
                return True

            CursorSystemAttachX = DefaultManager.getDefaultFloat("CursorSystemAttachX", 0)
            CursorSystemAttachY = DefaultManager.getDefaultFloat("CursorSystemAttachY", 0)

        currentMovie = CursorManager.getCurrentCursorMovie()
        lastMovie = CursorManager.getCursorModeMovie(last_cursor_mode)

        if currentMovie == lastMovie:
            return True

        CursorManager.__removeCursorChildren()

        if currentMovie.isActive() is False:
            return True

        currentMovieGroup = currentMovie.getGroup()

        if currentMovieGroup.getEnable() is False:
            return True

        # if TaskManager.existTaskChain("CursorShow"):
        #    TaskManager.cancelTaskChain("CursorShow")

        if usingCustomCursor:
            currentMovie.setEnable(True)
        CursorManager.setLastCursorMode(current_cursor_mode)

        movieEntity = currentMovie.getEntity()

        if movieEntity.hasMovieSlot("offset"):
            slotOffset = movieEntity.getMovieSlot("offset")
            pos = slotOffset.getLocalPosition()
            if CursorSystemAttachX is not None:
                pos = (pos.x + CursorSystemAttachX, pos.y + CursorSystemAttachY, pos.z)

            currentMovie.setOrigin(pos)

        item = ArrowManager.getArrowAttach()
        if item is not None:
            if movieEntity.hasMovieSlot("item") is True:
                itemEntityNode = item.getEntityNode()
                slotItem = movieEntity.getMovieSlot("item")
                pos = item.getArrowPoint()
                itemEntityNode.setLocalPosition((-pos[0], -pos[1]))
                item.setOrigin((0, 0))
                slotItem.addChild(itemEntityNode)

        arrow.addChild(movieEntity.node)
        # lastCursorMovie = CursorManager.s_currentCursorChildren[-1]
        CursorManager.s_currentCursorChildren.append(currentMovie)

        if len(CursorManager.s_currentCursorChildren) > 1:
            for child in CursorManager.s_currentCursorChildren[:-1]:
                child_entity = child.getEntity()
                child_entity.removeFromParent()
                child.setEnable(False)

        # = Cursor Show ====================================================

        if CursorManager.hasCursorObjectShow(current_cursor_mode):
            show_movie = CursorManager.getCursorObjectShow(current_cursor_mode)

            if show_movie is not None:
                # if lastCursorMovie is not None:
                #   lastCursorMovie.setEnable(False)

                show_movie_entity_node = show_movie.getEntityNode()
                arrow.addChild(show_movie_entity_node)

                show_movie.setEnable(True)
                currentMovie.setEnable(False)

                if TaskManager.existTaskChain("CursorShow"):
                    TaskManager.cancelTaskChain("CursorShow")

                with TaskManager.createTaskChain(Name="CursorShow", Cb=CursorManager.cursorShowCbEnd, CbArgs=(show_movie, currentMovie)) as tc:
                    tc.addScope(CursorManager.__scopePlayCursor, show_movie)

                return True

        # =================================================================
        return True

    @staticmethod
    def __scopePlayCursor(source, movie):
        if movie.getEnable():
            source.addTask("TaskMovie2Play", Movie2=movie)

    @staticmethod
    def cursorShowCbEnd(isSkip, show_movie, currentMovie):
        if not isSkip:
            # print 'enable', currentMovie.name
            currentMovie.setEnable(True)

        show_movie.setEnable(False)

        show_movie.returnToParent()

    @staticmethod
    def getCursorMode():
        return CursorManager.s_currentCursorModeName

    @staticmethod
    def getCurrentCursor():
        return CursorManager.s_currentCursor

    @staticmethod
    def getCurrentCursorMovie():
        currentMovie = CursorManager.s_cursorObjects[CursorManager.s_currentCursorModeName]

        return currentMovie

    @staticmethod
    def getCursorModeMovie(mode_name):
        cursor_movie = CursorManager.s_cursorObjects.get(mode_name)
        return cursor_movie

    @staticmethod
    def getLastCursorMode():
        return CursorManager.s_lastCursorModeName

    @staticmethod
    def setLastCursorMode(mode_name):
        CursorManager.s_lastCursorModeName = mode_name

    @staticmethod
    def _arrowEnterFilter(obj, modeName):
        cursor = CursorManager.s_cursors[modeName]

        if ArrowBlackListManager.isIgnore(obj) is True:
            modeName = ArrowBlackListManager.getChangeType(obj)
            cursor = CursorManager.s_cursors[modeName]

            if cursor.arrowItem is False:
                if ArrowManager.emptyArrowAttach() is False:
                    return False

            CursorManager.setCursorMode(modeName, True)  # setCursorMode() -> updateArrowCursor()

            CursorManager.s_onObject = obj
            return False

        if CursorManager.s_onObject == obj:
            return False

        if cursor.arrowItem is False:
            if ArrowManager.emptyArrowAttach() is False:
                return False

        if cursor.type is "Tip":
            if QuestManager.hasActiveTipObject(obj) is False:
                return False

            if CursorManager.setCursorMode(modeName) is True:  # setCursorMode() -> updateArrowCursor()
                CursorManager.s_onObject = obj
                return False

        if cursor.questType is not None:
            questType = cursor.questType

            if questType not in CursorManager.s_objectFilter:
                return False

            CheckAction = cursor.cursorCheckAction()

            CheckResult = False

            filters = CursorManager.s_objectFilter[questType]

            for params in filters.itervalues():
                if CheckAction.onCheck(obj, params) is True:
                    CheckResult = True
                    break

            if CheckResult is False:
                return False

        if CursorManager.s_block_Cursore_Update_in_Puzzle is False or ArrowManager.emptyArrowAttach() is True:
            if CursorManager.setCursorMode(modeName) is True:  # setCursorMode() -> updateArrowCursor()
                CursorManager.s_onObject = obj

        return False

    @staticmethod
    def _arrowLeaveFilter(obj):
        """ Bad Fix Reason:
        Let's suppose we have two sockets which intersect with names A and B.
        if we move cursor from A to B, we have next execution sequence:

            1. fired Notificator Enter Socket B.
            2. fired Notificator Leave Socket A.

        Which is cause next:
            Cursor will disappear OR will be set to default

        """

        def scope():
            if CursorManager.s_onObject is not obj:
                return

            ArrowItemCheck = DefaultManager.getDefaultBool("ArrowItemCheck", False)
            if ArrowItemCheck is True:
                if ArrowManager.emptyArrowAttach() is False:
                    CursorManager.s_onObject = None
                    CursorManager.setCursorMode("UseItem", True)  # setCursorMode() -> updateArrowCursor()
                    return

            CursorManager.s_onObject = None
            CursorManager.setCursorMode("Default", True)  # setCursorMode() -> updateArrowCursor()

        with TaskManager.createTaskChain() as tc:
            tc.addDelay(1.0)  # Bad Fix
            tc.addFunction(scope)

        return False

    @staticmethod
    def _onAddQuestFilter(quest):
        if quest is None:
            return False

        if quest.questType not in CursorManager.s_objectFilter:
            CursorManager.s_objectFilter[quest.questType] = {}

        CursorManager.s_objectFilter[quest.questType][quest] = quest.params
        return False

    @staticmethod
    def _onRemoveQuestFilter(quest):
        del CursorManager.s_objectFilter[quest.questType][quest]
        return False

    @staticmethod
    def __onCursorModeFilter(mode):
        # if Mengine.getCurrentAccountSettingBool("DifficultyCustomChangeIconOnActiveAreas") is False:
        #     mode = 'Default'

        arrow = Mengine.getArrow()
        arrow.onCursorMode(mode)

        CursorManager.updateArrowCursor(True)

        return False

    @staticmethod
    def getArrow():
        arrow = Mengine.getArrow()

        return arrow

    @staticmethod
    def macroAttached(attach):
        CursorManager.s_macroAttached.append(attach)

    @staticmethod
    def __getMacroAttached():
        return CursorManager.s_macroAttached

    @staticmethod
    def __changeArrowAttachedState(state):
        arrow_attached_movie = CursorManager.__getMacroAttached()
        if arrow_attached_movie is not None:
            for movie in arrow_attached_movie:
                movie.setEnable(state)

        return False

    @staticmethod
    def __removeAttachItems(item_name):
        arrow_attached_movie = CursorManager.__getMacroAttached()
        for indx, movie in enumerate(arrow_attached_movie):
            if movie.getName() is item_name:
                del CursorManager.s_macroAttached[indx]
                return False

        return False

    @staticmethod
    def __onPuzzleOpen(enigma_obj):
        CursorManager.s_block_Cursore_Update_in_Puzzle = True
        return False

    @staticmethod
    def __onPuzzleClose(enigma_obj):
        CursorManager.s_block_Cursore_Update_in_Puzzle = False
        return False
