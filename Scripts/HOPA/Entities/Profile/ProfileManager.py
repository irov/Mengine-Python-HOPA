from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager


class ProfileManager(Manager):
    s_profiles = {}

    @staticmethod
    def _onFinalize():
        for profile in ProfileManager.s_profiles.itervalues():
            profile.selectButton.onDestroy()

        ProfileManager.s_profiles = {}

    class Profile(object):
        def __init__(self, bSelect, bDelete, bCreate, bEdit=None):
            self.selectButton = bSelect
            self.deleteButton = bDelete
            self.createButton = bCreate
            self.editButton = bEdit

        def getSelectButton(self):
            return self.selectButton

        def getSelectButtonName(self):
            return self.selectButton.getName()

        def getDeleteButton(self):
            return self.deleteButton

        def getDeleteButtonName(self):
            return self.deleteButton.getName()

        def getCreateButton(self):
            return self.createButton

        def getCreateButtonName(self):
            return self.createButton.getName()

        def getEditButton(self):
            return self.editButton

        def getEditButtonName(self):
            return self.editButton.getName()


    @staticmethod
    def loadParams(module, param):
        if param == "ProfileNameBlackList":
            ProfileManager.loadNameBlackList(module, "ProfileNameBlackList")
        if param == "Profile":
            ProfileManager.loadProfile(module, "Profile")

        return True

    @staticmethod
    def loadNameBlackList(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        BlackList = []
        for record in records:
            Params = record.get("Params")
            if Params == "Symbols":
                BlackList = record.get("Value")
                break

        ProfileEditBox = GroupManager.getObject("Profile_New", "Demon_EditBox_Name")
        ProfileEditBox.setBlackList(BlackList)

    @staticmethod
    def loadProfile(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            SelectProfile = "$SelectProfile"
            groupName = "Profile"
            Over = "_Over"
            selectButton = None
            deleteButton = None
            createButton = None
            editButton = None
            id = None

            id = record.get("Number_of_Buttons", None)

            # groupName = record.get("GroupName")
            # Group = GroupManager.getGroup(groupName)

            selectButtonName = record.get("SelectButton")
            deleteButtonName = record.get("DeleteButton")
            createButtonName = record.get("CreateButton")
            editButtonName = record.get("EditButton")

            objectDemon = GroupManager.getObject(groupName, "Demon_Profile")

            if deleteButtonName is not None:
                if objectDemon.hasObject(deleteButtonName) is False:
                    error_msg = "ProfileManager.loadProfile deleteButton {} not exist in demon Profile".format(deleteButtonName)
                    Trace.log("Manager", 0, error_msg)
                else:
                    deleteButton = objectDemon.getObject(deleteButtonName)

            if createButtonName is not None:
                if objectDemon.hasObject(createButtonName) is False:
                    error_msg = "ProfileManager.loadProfile createButton {} not exist in demon Profile".format(createButtonName)
                    Trace.log("Manager", 0, error_msg)
                else:
                    createButton = objectDemon.getObject(createButtonName)

            if editButtonName is not None:
                if objectDemon.hasObject(editButtonName) is False:
                    error_msg = "ProfileManager.loadProfile editButton {} not exist in demon Profile".format(
                        editButtonName)
                    Trace.log("Manager", 0, error_msg)
                else:
                    editButton = objectDemon.getObject(editButtonName)

            if selectButtonName is not None:
                if id is None:
                    return
                for i in range(id):
                    selectButton = objectDemon.generateObjectUnique(selectButtonName + str(i), selectButtonName)
                    selectButton.setEnable(True)
                    Mengine.setTextAlias(SelectProfile + "_" + str(i), SelectProfile + Over, "ID_PROFILE_DEFAULT_NAME" + Over)
                    Mengine.setTextAlias(SelectProfile + "_" + str(i), SelectProfile, "ID_PROFILE_DEFAULT_NAME")

                    # Mengine.setTextAlias(SelectProfile + "_" + str(i), SelectProfile, "ID_SelectProfile")
                    for movie in selectButton.eachMovies():
                        movie.setTextAliasEnvironment(SelectProfile + "_" + str(i))

                    profile = ProfileManager.Profile(selectButton, deleteButton, createButton, editButton)

                    ProfileManager.s_profiles[i] = profile

    @staticmethod
    def getProfiles():
        if len(ProfileManager.s_profiles) == 0:
            Trace.log("Manager", 0, "DifficultyManager.getDifficulties: s_profiles is empty")
            return None

        return ProfileManager.s_profiles

