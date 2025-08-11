from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class DifficultyTimeScrollbarData(object):
    def __init__(self, time, time_min, time_max, scrollbar_obj):
        self.__time = self.__clampVal(time, time_min, time_max)
        self.__time_min = time_min
        self.__time_max = time_max
        self.__scrollbar_obj = scrollbar_obj

    def getScrollbarObject(self):
        return self.__scrollbar_obj

    @staticmethod
    def __clampVal(val, val_min, val_max):
        val = float(val)

        if val > val_max:
            return val_max

        if val < val_min:
            return val_min

        return val

    def setTime(self, time):
        self.__time = self.__clampVal(time, self.__time_min, self.__time_max)

    def setTimeNormalized(self, time_normalized):
        time_normalized = self.__clampVal(time_normalized, 0.0, 1.0)
        time = self.__time_min + time_normalized * (self.__time_max - self.__time_min)
        self.setTime(time)

    def getTime(self):
        return self.__time

    def getTimeMin(self):
        return self.__time_min

    def getTimeMax(self):
        return self.__time_max

    def getTimeNormalized(self):
        time_normalized = (self.__time - self.__time_min) / (self.__time_max - self.__time_min)
        return time_normalized

    def __deepcopy__(self, memodict={}):
        return DifficultyTimeScrollbarData(self.__time, self.__time_min, self.__time_max, self.__scrollbar_obj)

class Difficulty2Manager(Manager):
    s_difficulties = {}
    s_difficultiesParams = {}
    s_difficultiesScrollBars = {}
    s_difficultiesSettings = {}

    __module = None
    __param = None

    @staticmethod
    def _onFinalize():
        Difficulty2Manager.s_difficulties = {}
        Difficulty2Manager.s_difficultiesParams = {}
        Difficulty2Manager.s_difficultiesScrollBars = {}
        Difficulty2Manager.s_difficultiesSettings = {}

    @staticmethod
    def __loadParams(module, param):
        if module is None or param is None:
            return

        d_difficulties = {}
        d_difficultiesParam = {}
        d_difficultiesBars = {}
        d_difficultiesSettings = {}

        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            '''
            ID	SelectGroupName	SelectObjectName	SPARKLES_ON_ACTIVE_AREAS	TUTORIAL_AVAILABLE	
            PLUS_ITEM_INDICATED	CHANGE_ICON_ON_ACTIVE_AREAS	INDICATORS_ON_MAP	SPARKLES_ON_HO	
            HintTime	HintTimeClampMin	HintTimeClampMax	SkipTime	SkipTimeClampMin	SkipTimeClampMax
            '''

            id = record.get("ID")

            d_difficultiesSettings[id] = {
                "ID": record.get("ID"),
                "HintTime": record.get("HintTime"),
                "SkipTime": record.get("SkipTime"),
                "SparklesOnActiveAreas": record.get("SPARKLES_ON_ACTIVE_AREAS"),
                "Tutorial": record.get("TUTORIAL_AVAILABLE"),
                "PlusItemIndicated": record.get("PLUS_ITEM_INDICATED"),
                "ChangeIconOnActiveAreas": record.get("CHANGE_ICON_ON_ACTIVE_AREAS"),
                "IndicatorsOnMap": record.get("INDICATORS_ON_MAP"),
                "SparklesOnHOPuzzles": record.get("SPARKLES_ON_HO"),
            }

            selectGroupName = record.get("SelectGroupName")
            selectObjectName = record.get("SelectObjectName")

            selectObject = GroupManager.getObject(selectGroupName, selectObjectName)
            d_difficulties[id] = selectObject

            # game difficulty bool checkbox parameters:
            slots = []

            slots.append(("SPARKLES_ON_ACTIVE_AREAS", record.get("SPARKLES_ON_ACTIVE_AREAS")))
            slots.append(("TUTORIAL_AVAILABLE", record.get("TUTORIAL_AVAILABLE")))

            PLUS_ITEM_INDICATED = record.get("PLUS_ITEM_INDICATED", -1)
            if PLUS_ITEM_INDICATED != -1:
                slots.append(("PLUS_ITEM_INDICATED", PLUS_ITEM_INDICATED))

            slots.append(("CHANGE_ICON_ON_ACTIVE_AREAS", record.get("CHANGE_ICON_ON_ACTIVE_AREAS")))
            slots.append(("INDICATORS_ON_MAP", record.get("INDICATORS_ON_MAP")))
            slots.append(("SPARKLES_ON_HO", record.get("SPARKLES_ON_HO")))

            paramsDict = {}

            for i, (param_name, param_enable) in enumerate(slots):
                if param_enable is None:
                    obj = None
                else:
                    obj = GroupManager.getObject(selectGroupName, 'Movie2CheckBox_Slot{}'.format(i + 1))
                paramsDict[param_name] = [bool(param_enable), obj]

            d_difficultiesParam[id] = paramsDict

            # hint and skip scrollbar parameters:
            scrollBarDict = {}

            HintTime = float(record.get("HintTime", 60.0))

            HintTimeClampMin = float(record.get("HintTimeClampMin", 10.0))
            HintTimeClampMax = float(record.get("HintTimeClampMax", 500.0))
            HintTimeScrollbar = GroupManager.getObject(selectGroupName, 'Movie2Scrollbar_HintTime')
            HintScrollbar = DifficultyTimeScrollbarData(HintTime, HintTimeClampMin, HintTimeClampMax, HintTimeScrollbar)

            SkipTime = float(record.get("SkipTime", 60.0))

            SkipTimeClampMin = float(record.get("SkipTimeClampMin", 10.0))
            SkipTimeClampMax = float(record.get("SkipTimeClampMax", 500.0))
            SkipTimeScrollbar = GroupManager.getObject(selectGroupName, 'Movie2Scrollbar_SkipTime')
            SkipScrollbar = DifficultyTimeScrollbarData(SkipTime, SkipTimeClampMin, SkipTimeClampMax, SkipTimeScrollbar)

            scrollBarDict["Hint"] = HintScrollbar
            scrollBarDict["Skip"] = SkipScrollbar

            d_difficultiesBars[id] = scrollBarDict

        Difficulty2Manager.s_difficulties = d_difficulties
        Difficulty2Manager.s_difficultiesParams = d_difficultiesParam
        Difficulty2Manager.s_difficultiesScrollBars = d_difficultiesBars
        Difficulty2Manager.s_difficultiesSettings = d_difficultiesSettings

    @staticmethod
    def loadParams(module, param):
        Difficulty2Manager.__module = module
        Difficulty2Manager.__param = param

        Difficulty2Manager.__loadParams(module, param)

        return True

    @staticmethod
    def getDifficulties():
        Difficulty2Manager.__loadParams(Difficulty2Manager.__module, Difficulty2Manager.__param)

        if len(Difficulty2Manager.s_difficulties) == 0:
            Trace.log("Manager", 0, "Difficulty2Manager.getDifficulties: s_difficulties is empty")
            return

        return Difficulty2Manager.s_difficulties, Difficulty2Manager.s_difficultiesParams, Difficulty2Manager.s_difficultiesScrollBars
