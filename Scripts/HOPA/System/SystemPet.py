from Foundation.System import System
from Notification import Notification

class SystemPet(System):
    def __init__(self):
        super(SystemPet, self).__init__()
        self.pets = {}
        pass

    def _onRun(self):
        self.addObserver(Notificator.onPetPush, self.addPet)
        self.addObserver(Notificator.onSceneEnter, self.check_scene)
        self.addObserver(Notificator.onZoomEnter, self.check_scene)
        self.addObserver(Notificator.onPetComplete, self.rmv_scene)
        return True
        pass

    def _onStop(self):
        pass

    def addPet(self, socket, item, scene, movie):
        listPack = [socket, item, movie]
        self.pets[scene] = listPack
        Notification.notify(Notificator.onPetSwitch, True, listPack)
        return False
        pass

    def check_scene(self, sceneName):
        if sceneName in self.pets:
            active = True
            params = self.pets[sceneName]
        else:
            active = False
            params = []
        Notification.notify(Notificator.onPetSwitch, active, params)
        return False
        pass

    def rmv_scene(self, item, scene):
        if scene in self.pets:
            self.pets.pop(scene)
        return False
        pass