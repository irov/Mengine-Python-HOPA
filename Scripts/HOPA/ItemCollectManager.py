from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager

class ItemCollectManager(Manager):
    s_items_collect = {}

    class ItemCollectParams(object):
        def __init__(self, Item, Icon, IconSilhouette, AllowedItems):
            self.Item = Item
            self.Idle = Icon
            self.Silhouette = IconSilhouette
            self.AllowedItems = AllowedItems

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            '''
                ItemName	ItemGroupName	Icon	IconSilhouette	ItemCollectGroup    AllowedItems
            '''
            ItemName = record.get('ItemName')
            ItemGroupName = record.get('ItemGroupName')
            Icon = record.get('Icon')
            IconSilhouette = record.get('IconSilhouette')
            ItemCollectGroup = record.get('ItemCollectGroup')
            AllowedItems = record.get('AllowedItems', [])

            if isinstance(GroupManager.getGroup(ItemGroupName), GroupManager.EmptyGroup):
                continue

            Item = GroupManager.getObject(ItemGroupName, ItemName)
            Icon_obj = GroupManager.getObject(ItemCollectGroup, Icon)
            IconSilhouette_obj = GroupManager.getObject(ItemCollectGroup, IconSilhouette)

            ItemCollect = ItemCollectManager.ItemCollectParams(Item, Icon_obj, IconSilhouette_obj, AllowedItems)
            ItemCollectManager.s_items_collect[ItemName] = ItemCollect
        return True

    @staticmethod
    def getItemCollectParams():
        return ItemCollectManager.s_items_collect