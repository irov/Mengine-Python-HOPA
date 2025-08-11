from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager

from MovieChanger import MovieChanger

class Pet(BaseEntity):
    def __init__(self):
        super(Pet, self).__init__()
        self.taken = False
        pass

    def _onActivate(self):
        self.movie_preparation()
        self.switcher = Notification.addObserver(Notificator.onPetSwitch, self.__switch)
        pass

    def _onDeactivate(self):
        Notification.notify(Notificator.onPetLeave)
        #        SceneName = SceneManager.getChangeSceneName()
        #        if TaskManager.existTaskChain('Pet_%s'%(SceneName,)):
        #            TaskManager.cancelTaskChain('Pet_%s'%(SceneName,))
        #            pass
        pass

    def movie_preparation(self):
        movieIdle = self.object.getObject("Movie_Idle")
        movieUse = self.object.getObject("Movie_Use")
        movieActive = self.object.getObject("Movie_Active")
        self.MovieChanger = MovieChanger(movieIdle, movieActive, movieUse)
        self.MovieChanger.setIdle()
        pass

    def __switch(self, up, params):
        if up:
            self.MovieChanger.setActive()
            if not params:
                return False
                pass

            socket, item_name, movie = params
            sceneName = SceneManager.getCurrentSceneName()
            InventoryItem = ItemManager.getItemInventoryItem(item_name)
            SceneName = SceneManager.getChangeSceneName()
            with TaskManager.createTaskChain(Cb=self._skip) as tc:
                with tc.addRaceTask(2) as (tc_leave, tc_give):
                    tc_leave.addListener(Notificator.onPetLeave)
                    tc_leave.addPrint("Skipping task chain Pet")
                    tc_give.addPrint("Run task chain Pet")
                    tc_give.addTask("TaskSocketPlaceInventoryItem", SocketName=socket.getName(), Taken=True, Pick=False,
                                    SocketGroup=self.object, InventoryItem=InventoryItem, ItemName=item_name)
                    tc_give.addListener(Notificator.onInventoryUpdateItem)
                    tc_give.addNotify(Notificator.onPetComplete, item_name, sceneName)
                    tc_give.addFunction(self.MovieChanger.setUse)
                    tc_give.addTask("TaskMoviePlay", Movie=self.MovieChanger.getUseMovie(), Wait=True)
                    tc_give.addFunction(self.MovieChanger.setIdle)
                    tc_give.addTask("TaskMoviePlay", Movie=movie, Wait=True)
                pass

        else:
            self.MovieChanger.setIdle()
        return False

    pass

    def setTaken(self):
        self.taken = True
        pass

    def _skip(self, isSkip):
        pass
