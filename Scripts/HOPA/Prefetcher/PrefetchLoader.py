class PrefetchLoader(object):
    def __init__(self):
        self.queue = []
        self._loaded = []
        self.queueIndex = -1
        self.loading = False
        self.currentLoadingGroup = None
        self.force = False
        pass

    def forceLoading(self):
        self.force = True
        if self.currentLoadingGroup is None:
            return
            pass

        if self.isComplete() is True:
            return
            pass

        self.currentLoadingGroup.forceIncrease(self.onCompleteLoading)
        pass

    def isEmpty(self):
        if len(self.queue) == 0:
            return True
            pass
        return False
        pass

    def isComplete(self):
        if self.isLoading() is True:
            return False
            pass

        if self.queueIndex != (len(self.queue) - 1):
            return False
            pass

        return True
        pass

    def isLoading(self):
        return self.loading
        pass

    def addGroupPrefetch(self, groupPrefetch):
        priority = groupPrefetch.getPriority()
        nextIndex = self.queueIndex + 1
        size = len(self.queue)
        # priority!!
        while nextIndex < size:
            group = self.queue[nextIndex]
            groupPriority = group.getPriority()
            # print "priority %i - %i" %( priority,groupPriority)
            if priority >= groupPriority:
                # print "stopped priority %i - %i index %i" %( priority,groupPriority,nextIndex)
                break
            nextIndex += 1
            pass
        # self.queue.append(groupPrefetch)
        if nextIndex == self.queueIndex + 1:
            self.queue.append(groupPrefetch)
            pass
        else:
            # print "?????????????????????????????????????????????????????????????inserted ",nextIndex
            # self.queue.append(groupPrefetch)
            self.queue.insert(nextIndex, groupPrefetch)
            pass
        # print self.queue
        pass

    def start(self):
        if self.isLoading() is True:
            return
            pass

        if self.isEmpty() is True:
            return
            pass

        self.loading = True
        self._loadNext()
        pass

    def stop(self):
        self.loading = False

        if self.currentLoadingGroup is None:
            pass
        self.currentLoadingGroup.cancel()
        pass

    def unloadLoaded(self):
        # unload in  asc order
        loadedIndexes = range(self.queueIndex + 1)
        for i in loadedIndexes:
            groupPrefetch = self.queue[i]
            groupPrefetch.decrease()
            # print "after unloading  "
            # print groupPrefetch
            pass

        self.queue = []
        self.queueIndex = -1
        pass

    def unloadAll(self):
        for groupPrefetch in self.queue:
            groupPrefetch.decrease()
            # print "unloadAll after unloading  "
            # print groupPrefetch
            pass

        self.queue = []
        self.queueIndex = -1
        pass

    def onCompleteLoading(self, groupPrefetch):
        if groupPrefetch != self.currentLoadingGroup:
            pass

        if self.queueIndex == (len(self.queue) - 1):
            self.loading = False
            self.currentLoadingGroup = None
            return
            pass

        self._loadNext()
        pass

    def _loadNext(self):
        self.queueIndex += 1
        self.currentLoadingGroup = self.queue[self.queueIndex]
        # print "_loadNext"
        # print self.currentLoadingGroup
        if self.force is False:
            self.currentLoadingGroup.increase(self.onCompleteLoading)
            pass
        else:
            self.currentLoadingGroup.forceIncrease(self.onCompleteLoading)
            pass
        pass
