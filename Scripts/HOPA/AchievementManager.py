from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager
from Foundation.Utils import getCurrentPlatform, getCurrentPublisher, getCurrentBusinessModel


class AchievementParam(object):
    def __init__(self, name, group_name, movie_unlocked, movie_locked, movie_text, task_id_name, task_id_description,
                 steps_to_complete, page, basic_name, steam_value, task):
        self.name = name
        self.group = group_name
        self.page = page
        self.steam_value = steam_value

        self.movie_unlocked = movie_unlocked
        self.movie_locked = movie_locked
        self.movie_text = movie_text

        self.task_id_name = task_id_name
        self.task_id_description = task_id_description

        self.task = AchievementManager.HUMAN_KEYS.get(task, task)
        self.steps_to_complete = steps_to_complete
        self.basic_name = basic_name


class ExternalAchievementParam(object):
    def __init__(self, record):
        self.id = AchievementManager.getRecordValue(record, "AchieveID", cast=str)
        self.name = AchievementManager.getRecordValue(record, "AchieveName", default=self.id)
        self.incremented = AchievementManager.getRecordValue(record, "Incremented", default=False, cast=bool)

        task = AchievementManager.getRecordValue(record, "Task")
        self.task = AchievementManager.HUMAN_KEYS.get(task, task)
        self.steps_to_complete = AchievementManager.getRecordValue(record, "Steps", cast=int)

        self._debug = AchievementManager.getRecordValue(record, "Debug", cast=bool, default=False)

    def __repr__(self):
        if _DEVELOPMENT is True:
            return "<{}: {}>".format(self.__class__.__name__, self.__dict__)
        else:
            return "<{} {!r}>".format(self.__class__.__name__, self.name)

    def toSave(self):
        if self._debug is True:
            if _DEVELOPMENT is False:
                return False
        return True


class AchievementManager(Manager):
    """
        Docs: https://wonderland-games.atlassian.net/wiki/spaces/HOG/pages/1869217793#AchievementManager
    """

    s_achievement_params = {}
    s_external_params = {}  # { service: {id: ExternalAchievementParam}, ... }

    HUMAN_KEYS = {
        "ItemCollect": "item_collect_complete_count",
        "Minigames": "minigames_complete_count",
        "NoHintHOGs": "hogs_complete_no_hint_count",
        "NoHintScenes": "scene_complete_no_hint_count",
        "UseHint": "hint_used_count",
        "CompleteLocations": "completed_locations",
        "UnlockAchievements": "unlocked_achievements",
        "CompleteTasks": "completed_missions",
        "PickItem": "items_picked"
    }

    __EXTERNAL_TABLES = {}  # { table_name: service }

    @staticmethod
    def loadInternalParams(records):
        for record in records:
            '''
            Name	GroupName   SteamValue	
            MovieUnlocked	MovieLocked MovieCursorText	
            Task_ID_Name	Task_ID_Description	
            Steps_To_Complete
            Basic_Name
            '''
            name = record.get("Name")
            steam_value = record.get("SteamValue")
            group_name = record.get("GroupName")

            page = record.get("Page")
            if page is not None:
                page = int(page)
            movie_unlocked = record.get("MovieUnlocked")
            movie_locked = record.get("MovieLocked")
            movie_text = record.get("MovieCursorText")

            task_id_name = record.get("Task_ID_Name")
            task_id_description = record.get("Task_ID_Description")

            steps_to_complete = record.get("Steps_To_Complete", None)
            task = record.get("Task", None)

            basic_name = record.get("Basic_Name", None)

            achievement = AchievementParam(name, group_name, movie_unlocked, movie_locked, movie_text, task_id_name,
                                           task_id_description, steps_to_complete, page, basic_name, steam_value, task)

            AchievementManager.s_achievement_params[name] = achievement

    @staticmethod
    def loadRedirector(records):
        """
            Append __EXTERNAL_TABLES, that will be used in loadExternalParams
        """

        current_business_model = getCurrentBusinessModel()
        current_platform = getCurrentPlatform()
        current_publisher = getCurrentPublisher()
        if current_publisher is None:
            return

        for record in records:
            Publisher = record.get("Publisher")
            if Publisher != str(current_publisher):
                continue

            Platform = record.get("Platform")
            if Platform != current_platform:
                continue

            BusinessModel = record.get("BusinessModel", "*")
            if BusinessModel != "*" and BusinessModel != current_business_model:
                continue

            table_name = record.get("ParamTableName", "").format(
                tag="AchievementsExternal", publisher=Publisher, platform=Platform)
            if table_name == "":
                Trace.log("Manager", 0, "AchievementManager [{}] [{}] [{}] table name can't be empty"
                          .format(Publisher, Platform, BusinessModel))
                continue

            service = record.get("Service", "")

            AchievementManager.__EXTERNAL_TABLES[table_name] = service

    @staticmethod
    def loadExternalParams(records, service):
        service_params_dict = {}
        for record in records:
            params = ExternalAchievementParam(record)
            if params.toSave() is False:
                continue
            service_params_dict[params.id] = params
        AchievementManager.s_external_params[service] = service_params_dict

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        if name == "AchievementsExternalSettings":  # Always should be first if you want to use External
            AchievementManager.loadRedirector(records)
        elif name == "Achievements":
            AchievementManager.loadInternalParams(records)
        elif name in AchievementManager.__EXTERNAL_TABLES:
            service = AchievementManager.__EXTERNAL_TABLES[name]
            AchievementManager.loadExternalParams(records, service)

        return True

    @staticmethod
    def getAchievementsParams():
        return AchievementManager.s_achievement_params

    # External

    @staticmethod
    def getExternalAchievementsParams():
        """ :returns: dict where key is service_name, and value is a dict {achieve_id: ExternalAchievementParams} """
        return AchievementManager.s_external_params

    @staticmethod
    def getExternalAchievementsParamsByService(service_name):
        """ :returns: dict {achieve_id: ExternalAchievementParams} of selected service """
        return AchievementManager.s_external_params.get(service_name, {})
