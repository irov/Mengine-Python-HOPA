from Foundation.GroupManager import GroupManager
from HOPA.Prefetcher.GroupPrefetch import GroupPrefetch

class GroupPrefetchManager:
    s_groupPrefetches = {}

    @staticmethod
    def getGroupPrefetch(groupName):
        if groupName in GroupPrefetchManager.s_groupPrefetches:
            groupPrefetch = GroupPrefetchManager.s_groupPrefetches[groupName]
            return groupPrefetch
            pass

        group = GroupManager.getGroup(groupName)
        if group is None:
            return None
            pass

        groupPrefetch = GroupPrefetch()
        groupPrefetch.onInitialize(group)
        GroupPrefetchManager.s_groupPrefetches[groupName] = groupPrefetch
        return groupPrefetch
        pass