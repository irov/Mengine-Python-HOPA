from Foundation.MonetizationManager import MonetizationManager
from Foundation.System import System
# from Foundation.Utils import SimpleLogger
from Notification import Notification


# _Log = SimpleLogger("SystemProductGroups")


class SystemProductGroups(System):

    class GroupInfo(object):
        if _DEVELOPMENT is True:
            def __repr__(self):
                return "<Group {} [{}] ({})>".format(self.id, self.in_progress, self.subgroups.values())

        def __init__(self, params):
            self.id = params["GroupID"]
            self.in_progress = params.get("InProgress", False)
            self.timestamp_start_progress = params.get("StartProgressTimestamp")
            self.subgroups = {}

            subgroups_params = params.get("SubGroups", {})
            for subgroup_param in subgroups_params:
                subgroup = SystemProductGroups.SubGroupInfo(subgroup_param)
                self.addSubgroup(subgroup)

        def addSubgroup(self, subgroup):
            subgroup.parent_id = self.id
            self.subgroups[subgroup.id] = subgroup

        def getSubgroup(self, subgroup_id):
            return self.subgroups.get(subgroup_id)

        def reset(self):
            self.in_progress = False
            self.timestamp_start_progress = None
            for subgroup in self.subgroups.values():
                subgroup.reset()
            Notification.notify(Notificator.onProductGroupReset, self.id)

        def startProgress(self, subgroup_id):
            self.in_progress = True
            self.timestamp_start_progress = Mengine.getLocalDateTimeMs()
            subgroup = self.getSubgroup(subgroup_id)
            subgroup.startProgress()
            Notification.notify(Notificator.onProductGroupStartProgress, self.id)

    class SubGroupInfo(object):
        if _DEVELOPMENT is True:
            def __repr__(self):
                return "<SubGroup {} [{}]: {} - {}>".format(self.id, self.in_progress, self.product_ids, self.purchased)

        def __init__(self, params):
            self.id = params["SubGroupID"]
            self.parent_id = None
            # list of all products that contains in this SubGroup
            self.product_ids = params.get("ProductIDs", [])
            self.purchased = params.get("PurchasedProductIDs", [])
            # only one subgroup inside group could be in progress
            self.in_progress = params.get("InProgress", False)

        def reset(self):
            self.in_progress = False
            self.purchased = []

        def startProgress(self):
            self.in_progress = True

        def progress(self, product_id):
            if product_id not in self.product_ids:
                Trace.log("System", 0, "Subgroup [{}:{}] progress: product '{}' not found in my products".format(self.parent_id, self.id, product_id))
                return False

            if product_id in self.purchased:
                if _DEVELOPMENT is True:
                    Trace.log("System", 0, "Subgroup [{}:{}] progress: product '{}' already in purchased".format(self.parent_id, self.id, product_id))
                return True

            self.purchased.append(product_id)
            Notification.notify(Notificator.onProductGroupProgress, self.parent_id, self.id, product_id)
            return True

    data = {}  # { GroupID: GroupInfo (contains sub groups info), ... }
    prod_to_group = {}  # { product_id: [group_id, subgroup_id] }

    __SETTINGS_TIMESTAMP_TEMPLATE = "GR{}TIME"
    __SETTINGS_PURCHASED_TEMPLATE = "GR{}PURCH"

    def _onInitialize(self):
        from Foundation.AccountManager import AccountManager
        AccountManager.addCreateAccountExtra(SystemProductGroups.__addExtraAccountSettings)

    def _onRun(self):
        self._createData()  # initial value, then in onLoad update
        self.addObservers()

        return True

    def _onStop(self):
        SystemProductGroups.data = None
        SystemProductGroups.prod_to_group = None

    def _createData(self):
        groups = {}

        for product_info in MonetizationManager.getProductsInfo().values():
            group_id = product_info.group_id
            subgroup_id = product_info.subgroup_id

            if group_id is None or subgroup_id is None:
                # product must contain group_id and subgroup_id
                continue

            # create or get group
            if group_id in groups:
                group = groups[group_id]
            else:
                group_params = {"GroupID": group_id}
                group = SystemProductGroups.GroupInfo(group_params)
                groups[group_id] = group

            # handle subgroup
            if subgroup_id not in group.subgroups:
                subgroup = SystemProductGroups.SubGroupInfo({
                    "SubGroupID": subgroup_id,
                    "ProductIDs": [product_info.id],
                })
                group.addSubgroup(subgroup)
            else:
                subgroup = group.getSubgroup(subgroup_id)
                subgroup.product_ids.append(product_info.id)

            # save in which group-subgroup refers this product id
            SystemProductGroups.prod_to_group[product_info.id] = (group_id, subgroup_id)

        SystemProductGroups.data = groups

    # observers

    def addObservers(self):
        self.addObserver(Notificator.onPaySuccess, self._cbPaySuccess)

    def _cbPaySuccess(self, product_id):
        if product_id not in self.prod_to_group:
            return False

        group_id, subgroup_id = self.prod_to_group[product_id]

        group = self.getGroup(group_id)
        if group.in_progress is False:
            group.startProgress(subgroup_id)
            self._saveStartTimestampToAccount(group_id, group.timestamp_start_progress)

        subgroup = group.getSubgroup(subgroup_id)
        subgroup.progress(product_id)

        self._savePurchasedToAccount(group_id, subgroup_id)

        Mengine.saveAccounts()

        return False

    # getters

    @staticmethod
    def hasGroup(group_id):
        return group_id in SystemProductGroups.data

    @staticmethod
    def getGroup(group_id):
        return SystemProductGroups.data[group_id]

    @staticmethod
    def getActiveGroups():
        data = SystemProductGroups.data.values()
        active_groups = filter(lambda g: g.in_progress is True, data)
        return active_groups

    @staticmethod
    def getActiveSubgroup(group_id):
        group = SystemProductGroups.getGroup(group_id)

        active_subgroups = filter(lambda sg: sg.in_progress is True, group.subgroups.values())
        if len(active_subgroups) == 0:
            return

        return active_subgroups[0]

    # Groups limit handlers

    @classmethod
    def compareDateStructs(cls, date_struct1, date_struct2):
        """ compare two date structs and return True if day, month or year is different """
        if date_struct1.day != date_struct2.day:
            return True
        if date_struct1.month != date_struct2.month:
            return True
        if date_struct1.year != date_struct2.year:
            return True
        return False

    @classmethod
    def updateGroupsLimit(cls):
        today_date_struct = Mengine.getLocalDateStruct()

        def _filterCheckDate(group):
            if group.timestamp_start_progress is None:
                res = False
            else:
                date = Mengine.getLocalDateStructFromTimeMs(group.timestamp_start_progress)
                res = cls.compareDateStructs(today_date_struct, date)

            # _Log("(filter) [{}] {} => {}".format(group.id, group.timestamp_start_progress, res))

            return res

        update_groups = filter(_filterCheckDate, cls.data.values())
        for group in update_groups:
            group.reset()
            cls._resetGroupSaveOnAccount(group.id)

        if len(update_groups) != 0:
            Mengine.saveAccounts()

        # _Log("Updated {} groups: {}".format(len(update_groups), [group.id for group in update_groups]))

    # Save \ Load

    @staticmethod
    def __addExtraAccountSettings(accountID, isGlobal):
        if isGlobal is True:
            return

        for group_id in SystemProductGroups.data.keys():
            Mengine.addCurrentAccountSetting(SystemProductGroups.__SETTINGS_TIMESTAMP_TEMPLATE.format(group_id), u'', None)
            Mengine.addCurrentAccountSetting(SystemProductGroups.__SETTINGS_PURCHASED_TEMPLATE.format(group_id), u'', None)

    @staticmethod
    def _saveStartTimestampToAccount(group_id, timestamp):
        key = SystemProductGroups.__SETTINGS_TIMESTAMP_TEMPLATE.format(group_id)
        Mengine.changeCurrentAccountSetting(key, unicode(timestamp))

    @staticmethod
    def _loadStartTimestampFromAccount(group_id):
        key = SystemProductGroups.__SETTINGS_TIMESTAMP_TEMPLATE.format(group_id)
        if Mengine.hasCurrentAccountSetting(key) is False:
            return None

        save_value = Mengine.getCurrentAccountSetting(key)

        if len(save_value) != 0:
            timestamp = int(save_value)
            return timestamp
        else:
            return None

    @staticmethod
    def _savePurchasedToAccount(group_id, subgroup_id):
        group = SystemProductGroups.getGroup(group_id)
        subgroup = group.getSubgroup(subgroup_id)

        save = subgroup_id + ":" + ", ".join(subgroup.purchased)

        key = SystemProductGroups.__SETTINGS_PURCHASED_TEMPLATE.format(group_id)
        Mengine.changeCurrentAccountSetting(key, unicode(save))

    @staticmethod
    def _loadPurchasedFromAccount(group_id):
        key = SystemProductGroups.__SETTINGS_PURCHASED_TEMPLATE.format(group_id)
        save = Mengine.getCurrentAccountSetting(key)

        if len(save) == 0:
            return

        subgroup_id, raw_products = save.split(":")

        group = SystemProductGroups.getGroup(group_id)
        subgroup = group.getSubgroup(subgroup_id)

        if subgroup is None:
            Trace.log("System", 0, "SystemProductGroups failed load purchased - subgroup with id {!r} not found!".format(subgroup_id))
            return

        purchased_products = raw_products.split(", ")
        subgroup.purchased = purchased_products
        subgroup.startProgress()

    @staticmethod
    def _resetGroupSaveOnAccount(group_id):
        timestamp_key = SystemProductGroups.__SETTINGS_TIMESTAMP_TEMPLATE.format(group_id)
        Mengine.changeCurrentAccountSetting(timestamp_key, u'')
        purchased_key = SystemProductGroups.__SETTINGS_PURCHASED_TEMPLATE.format(group_id)
        Mengine.changeCurrentAccountSetting(purchased_key, u'')

    def _onSave(self):
        self.updateGroupsLimit()
        return {}

    def _onLoad(self, save_dict):
        for group_id, group in SystemProductGroups.data.items():
            group.timestamp_start_progress = self._loadStartTimestampFromAccount(group_id)
            group.in_progress = group.timestamp_start_progress is not None

            self._loadPurchasedFromAccount(group_id)
