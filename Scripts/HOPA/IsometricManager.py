from Foundation.DatabaseManager import DatabaseManager

class IsometricManager(object):
    s_animations = []

    class Animation(object):
        def __init__(self, Name, Type, Direction, Resource):
            self.Name = Name
            self.Type = Type
            self.Direction = Direction
            self.Resource = Resource
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        if IsometricManager.loadAnimations(module, param) is False:
            return False
            pass

        return True
        pass

    @staticmethod
    def loadAnimations(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            Type = record.get("Type")

            Direction = int(record.get("Direction"))
            GroupName = record.get("GroupName")
            MovieName = record.get("MovieName")

            ResourceName = "Movie%s_%s" % (GroupName, MovieName)
            Resource = Mengine.getResourceReference(ResourceName)
            animation = IsometricManager.Animation(Name, Type, Direction, Resource)

            IsometricManager.s_animations.append(animation)
            pass

        return True
        pass

    @staticmethod
    def getAnimations(Name, Type):
        resources = [None] * 8
        for animation in IsometricManager.s_animations:
            if animation.Name != Name:
                continue
                pass

            if animation.Type != Type:
                continue
                pass

            resources[animation.Direction] = animation.Resource
            pass

        return resources
        pass

    @staticmethod
    def getAnimation(Name, Type):
        for animation in IsometricManager.s_animations:
            if animation.Name != Name:
                continue
                pass

            if animation.Type != Type:
                continue
                pass

            return animation.Resource
            pass

        return None
        pass
    pass