from Foundation.Object.DemonObject import DemonObject

class ObjectAchievementsInGameMenu(DemonObject):
    # Just add here queue type:
    s_queue_types = ["Achievements", "Collectibles", "Morphs"]

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, "isOpen")

        for type_ in ObjectAchievementsInGameMenu.s_queue_types:
            Type.addParam(Type, "{}Queue".format(type_))

    def _onParams(self, params):
        super(ObjectAchievementsInGameMenu, self)._onParams(params)
        self.initParam("isOpen", params, False)

        for type_ in ObjectAchievementsInGameMenu.s_queue_types:
            self.initParam("{}Queue".format(type_), params, [])

    def getQueue(self):
        queue = {type_: self.getParam(type_) for type_ in ObjectAchievementsInGameMenu.s_queue_types}
        return queue

    def isQueueEmpty(self):
        for type_ in ObjectAchievementsInGameMenu.s_queue_types:
            queue = self.getParam("{}Queue".format(type_))
            if len(queue) != 0:
                return False

        return True

    def popParam(self, param_name):
        list_ = self.getParam(param_name)
        if len(list_) == 0:
            return
        el = list_.pop(0)
        self.setParam(param_name, list_)
        return el