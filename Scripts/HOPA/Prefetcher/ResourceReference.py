class ResourceReference(object):
    def __init__(self, category, resourceName):
        self.__category = category
        self.__resourceName = resourceName
        pass

    def getResourceName(self):
        return self.__resourceName
        pass

    def getResourceCategory(self):
        return self.__category
        pass

    def __getReference(self):
        reference = Mengine.getResourceReference(self.__resourceName)
        return reference
        pass

    def getCountReference(self):
        reference = self.__getReference()
        if reference is None:
            return -9000
            pass

        count = reference.countReference()
        return count
        pass

    def increase(self):
        Mengine.directResourceCompile(self.__resourceName)
        # reference = self.__getReference()
        # reference.compile()
        pass

    def decrease(self):
        Mengine.directResourceRelease(self.__resourceName)
        # reference = self.__getReference()
        # reference.release()
        pass
