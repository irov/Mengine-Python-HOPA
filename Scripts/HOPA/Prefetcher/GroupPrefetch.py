from Foundation.Initializer import Initializer
from HOPA.Prefetcher.ResourceReference import ResourceReference

class GroupPrefetch(Initializer):
    PRIORITY_ZOOM = 100
    PRIORITY_COMMON = 0

    def __init__(self):
        self.resourceReferences = {}
        self.name = None
        self.resourcesCategory = "Resources"
        self.count = 0
        self.priority = GroupPrefetch.PRIORITY_COMMON
        self.task = None
        pass

    def _onInitialize(self, group):
        super(GroupPrefetch, self)._onInitialize(group)
        self.name = group.getName()
        # print "group ->",group.getName()
        self.__collectObjectResource(group)
        pass

    def __collectObjectResource(self, group):
        def __visitResource(obj):
            objType = obj.getType()
            if objType == "ObjectSprite":
                resName = obj.getParam("SpriteResourceName")
                if resName == None:
                    return
                    pass
                resource = self.__createResourceReference(resName)
                self.__addResource(resource)
                pass
            elif objType == "ObjectShift":
                resources = obj.getParam("Resources")
                for resName in resources:
                    resource = self.__createResourceReference(resName)
                    self.__addResource(resource)
                    pass
                pass
            pass
        group.visitObjects(__visitResource)
        pass

    def __createResourceReference(self, resName):
        reference = ResourceReference(self.resourcesCategory, resName)
        return reference
        pass

    def __addResource(self, resourceReference):
        resourceName = resourceReference.getResourceName()
        if resourceName in self.resourceReferences:
            return
            pass
        self.resourceReferences[resourceName] = resourceReference
        pass

    def getName(self):
        return self.name
        pass

    def increase(self, callback):
        self.__increase(self.__loadThread, callback)
        pass

    def forceIncrease(self, callback):
        # print "*******************************forceIncrease " , self.count,self.name,self.task
        if self.task is not None:
            Mengine.cancelTask(self.task)
            pass
        self.__increase(self.__loadForce, callback)
        pass

    def __increase(self, loading, callback):
        #        #DANGER !!!!
        #        if self.isEmpty() is True:
        #            self.count += 1
        #            print self.resourceReferences
        #            callback(self)
        #            return
        #            pass

        if self.count == 0:
            loading(callback)
            pass
        else:
            self.count += 1
            # print "incremented ",self.getName()," count ",self.count
            callback(self)
            pass
        pass

    def __loadThread(self, callback):
        resources = self.getResources()
        # print "__loadThread loading group ",self.getName()," count ",self.count
        # print self
        names = []
        for resource in resources:
            name = resource.getResourceName()
            names.append(name)
            # print "----- before increase   name %s count %i" % (resource.getResourceName(),resource.getCountReference())
            # resource.increase()
            pass

        def loadCallback(state):
            # print "--CALLBACK---------------------------------------------"
            # print "-------------------------------------------------------"

            if state is False:
                # print "TASK CANCEL"
                self.task = None
                return False
                pass

            self.task = None
            self.count += 1
            callback(self)  # print self
        self.task = Mengine.loadImageResources(self.resourcesCategory, names, loadCallback)
        pass

    def __loadForce(self, callback):
        resources = self.getResources()
        # print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        # print "FORCE loading group ",self.getName()," count ",self.count
        names = []
        for resource in resources:
            name = resource.getResourceName()
            names.append(name)
            # print "----- before increase   name %s count %i" % (resource.getResourceName(),resource.getCountReference())
            resource.increase()
            pass
        self.count += 1
        callback(self)
        pass

    def decrease(self):
        self.count -= 1
        if self.count != 0:
            return
            pass
        self.__unload()
        pass

    def __unload(self):
        resources = self.getResources()
        # print "!!!!!!!!!!!!!!!!!!!!!!!!!!unloading group "
        # print self

        for resource in resources:
            # print "----- before decrease   name %s count %i" % (resource.getResourceName(),resource.getCountReference())
            resource.decrease()
            pass
        # print "!!!!!!!!!!!!!!!!!!!!!!!!!!unloading group "
        # print self
        pass

    def isEmpty(self):
        if len(self.resourceReferences) == 0:
            return True
            pass

        return False
        pass

    def getResources(self):
        refsList = self.resourceReferences.itervalues()
        return refsList
        pass

    def setPriority(self, priority):
        self.priority = priority
        pass

    def getPriority(self):
        return self.priority
        pass

    def __repr__(self):
        str = "GroupPrefetch: %s count %i %s \n" % (self.name, self.count, hex(id(self)))
        str += "Resources : \n"
        for resName, reference in self.resourceReferences.items():
            count = reference.getCountReference()
            str += ("%s count %i \n" % (resName, count))
            pass
        return str
    pass