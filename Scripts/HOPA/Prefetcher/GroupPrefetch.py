from Foundation.Initializer import Initializer
from HOPA.Prefetcher.ResourceReference import ResourceReference


class GroupPrefetch(Initializer):
    PRIORITY_ZOOM = 100
    PRIORITY_COMMON = 0

    def __init__(self):
        super(GroupPrefetch, self).__init__()
        self.resourceReferences = {}
        self.name = None
        self.resourcesCategory = "Resources"
        self.count = 0
        self.priority = GroupPrefetch.PRIORITY_COMMON
        self.task = None

    def _onInitialize(self, group):
        super(GroupPrefetch, self)._onInitialize(group)
        self.name = group.getName()
        # print "group ->",group.getName()
        self.__collectObjectResource(group)

    def __collectObjectResource(self, group):
        def __visitResource(obj):
            objType = obj.getType()
            if objType == "ObjectSprite":
                resName = obj.getParam("SpriteResourceName")
                if resName is None:
                    return
                resource = self.__createResourceReference(resName)
                self.__addResource(resource)
            elif objType == "ObjectShift":
                resources = obj.getParam("Resources")
                for resName in resources:
                    resource = self.__createResourceReference(resName)
                    self.__addResource(resource)

        group.visitObjects(__visitResource)

    def __createResourceReference(self, resName):
        reference = ResourceReference(self.resourcesCategory, resName)
        return reference

    def __addResource(self, resourceReference):
        resourceName = resourceReference.getResourceName()
        if resourceName in self.resourceReferences:
            return
        self.resourceReferences[resourceName] = resourceReference

    def getName(self):
        return self.name

    def increase(self, callback):
        self.__increase(self.__loadThread, callback)

    def forceIncrease(self, callback):
        # print "*******************************forceIncrease " , self.count,self.name,self.task
        if self.task is not None:
            Mengine.cancelTask(self.task)
        self.__increase(self.__loadForce, callback)

    def __increase(self, loading, callback):
        #        #DANGER !!!!
        #        if self.isEmpty() is True:
        #            self.count += 1
        #            print self.resourceReferences
        #            callback(self)
        #            return

        if self.count == 0:
            loading(callback)
        else:
            self.count += 1
            # print "incremented ",self.getName()," count ",self.count
            callback(self)

    def __loadThread(self, callback):
        resources = self.getResources()
        # print "__loadThread loading group ",self.getName()," count ",self.count
        # print self
        names = []
        for resource in resources:
            name = resource.getResourceName()
            names.append(name)
            # print "--- before increase   name %s count %i" % (resource.getResourceName(),resource.getCountReference())
            # resource.increase()

        def loadCallback(state):
            # print "--CALLBACK---------------------------------------------"
            # print "-------------------------------------------------------"

            if state is False:
                # print "TASK CANCEL"
                self.task = None
                return False

            self.task = None
            self.count += 1
            callback(self)  # print self

        self.task = Mengine.loadImageResources(self.resourcesCategory, names, loadCallback)

    def __loadForce(self, callback):
        resources = self.getResources()
        # print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        # print "FORCE loading group ",self.getName()," count ",self.count
        names = []
        for resource in resources:
            name = resource.getResourceName()
            names.append(name)
            # print "--- before increase   name %s count %i" % (resource.getResourceName(),resource.getCountReference())
            resource.increase()
        self.count += 1
        callback(self)

    def decrease(self):
        self.count -= 1
        if self.count != 0:
            return
        self.__unload()

    def __unload(self):
        resources = self.getResources()
        # print "!!!!!!!!!!!!!!!!!!!!!!!!!!unloading group "
        # print self

        for resource in resources:
            # print "--- before decrease   name %s count %i" % (resource.getResourceName(),resource.getCountReference())
            resource.decrease()
        # print "!!!!!!!!!!!!!!!!!!!!!!!!!!unloading group "
        # print self

    def isEmpty(self):
        if len(self.resourceReferences) == 0:
            return True
        return False

    def getResources(self):
        refsList = self.resourceReferences.itervalues()
        return refsList

    def setPriority(self, priority):
        self.priority = priority

    def getPriority(self):
        return self.priority

    def __repr__(self):
        str = "GroupPrefetch: %s count %i %s \n" % (self.name, self.count, hex(id(self)))
        str += "Resources : \n"
        for resName, reference in self.resourceReferences.items():
            count = reference.getCountReference()
            str += ("%s count %i \n" % (resName, count))
        return str

