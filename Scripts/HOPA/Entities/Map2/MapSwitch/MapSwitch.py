from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager

from MapSwitchManager import MapSwitchManager

class MapSwitch(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        pass

    def _onPreparation(self):
        super(MapSwitch, self)._onPreparation()
        pass

    def _onActivate(self):
        super(MapSwitch, self)._onActivate()
        self.cancelTaskChains()
        Data = MapSwitchManager.getData(self.object)
        with TaskManager.createTaskChain(Name="Chain_" + self.object.getName(), Repeat=True) as tc:
            with tc.addRaceTask(len(Data.keys())) as tci:
                for tcs, button in zip(tci, Data.keys()):
                    sceneName = Data[button]
                    tcs.addTask("TaskButtonClick", Button=button)
                    tcs.addTask("TaskFunction", Fn=TransitionManager.changeScene, Args=(sceneName, None, False,))
                    pass
                pass
            pass
        pass

    def _onDeactivate(self):
        super(MapSwitch, self)._onDeactivate()
        self.cancelTaskChains()

        pass

    def cancelTaskChains(self):
        if TaskManager.existTaskChain("Chain_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Chain_" + self.object.getName())
            pass
        pass
    pass