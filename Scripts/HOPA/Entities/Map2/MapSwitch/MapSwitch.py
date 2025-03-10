from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager

from MapSwitchManager import MapSwitchManager


class MapSwitch(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

    def _onPreparation(self):
        super(MapSwitch, self)._onPreparation()

    def _onActivate(self):
        super(MapSwitch, self)._onActivate()
        self.cancelTaskChains()
        Data = MapSwitchManager.getData(self.object)
        with TaskManager.createTaskChain(Name="Chain_" + self.object.getName(), Repeat=True) as tc:
            with tc.addRaceTask(len(Data.keys())) as tci:
                for tcs, button in zip(tci, Data.keys()):
                    sceneName = Data[button]
                    tcs.addTask("TaskButtonClick", Button=button)
                    tcs.addFunction(TransitionManager.changeScene, sceneName, None, False)

    def _onDeactivate(self):
        super(MapSwitch, self)._onDeactivate()
        self.cancelTaskChains()

    def cancelTaskChains(self):
        if TaskManager.existTaskChain("Chain_" + self.object.getName()) is True:
            TaskManager.cancelTaskChain("Chain_" + self.object.getName())
