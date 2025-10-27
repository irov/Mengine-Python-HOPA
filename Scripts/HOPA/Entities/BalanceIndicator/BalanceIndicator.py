from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.TaskManager import TaskManager
from HOPA.Entities.BalanceIndicator.GoldIndicator import GoldIndicator
from HOPA.Entities.BalanceIndicator.EnergyIndicator import EnergyIndicator
from HOPA.Entities.BalanceIndicator.AdvertisementIndicator import AdvertisementIndicator


class BalanceIndicator(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction("ShowGold",
                       Update=Functor(BalanceIndicator._cbUpdateShowIndicator, GoldIndicator.type.lower()))
        Type.addAction("ShowEnergy",
                       Update=Functor(BalanceIndicator._cbUpdateShowIndicator, EnergyIndicator.type.lower()))
        Type.addAction("ShowAdvertisement",
                       Update=Functor(BalanceIndicator._cbUpdateShowIndicator, AdvertisementIndicator.type.lower()))

    def __init__(self):
        super(BalanceIndicator, self).__init__()
        self.indicators = {}
        self.tc = None

    def __getIconProvider(self):
        provider = DefaultManager.getDefault("DefaultBalanceIndicatorIconProvider", "self")
        if provider == "current_store":
            provider = MonetizationManager.getGeneralSetting("GameStoreName", "GameStore")

        parent = None

        if provider != "self":
            if DemonManager.hasDemon(provider):
                parent = DemonManager.getDemon(provider)
            elif GroupManager.hasGroup(provider):
                parent = GroupManager.getGroup(provider)

        if parent is None:
            parent = self.object

        return parent

    def _onPreparation(self):
        self.indicators = {
            "gold": GoldIndicator(),
            "energy": EnergyIndicator(),
            "advertisement": AdvertisementIndicator(),
        }

        icon_provider_object = self.__getIconProvider()

        for indicator in self.indicators.values():
            indicator.prepare(self.object, icon_provider_object)
            indicator.setShow(self.object.getParam("Show" + indicator.type.title()))

    def _onActivate(self):
        self.tc = TaskManager.createTaskChain(Name="BalanceIndicatorHandler", Repeat=True)
        with self.tc as tc:
            for indicator, source_race in tc.addRaceTaskList(self.indicators.values()):
                source_race.addScope(indicator.scopeClick)
                source_race.addScope(indicator.scopeClicked)

    def _onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for indicator in self.indicators.values():
            indicator.cleanUp()
        self.indicators = {}

    def _cbUpdateShowIndicator(self, state, indicator_type):
        indicator = self.indicators.get(indicator_type)
        if indicator is not None:
            indicator.setShow(state)
