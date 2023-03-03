from Foundation.DemonManager import DemonManager
from Foundation.StateManager import StateManager
from Foundation.System import System
from Notification import Notification


class SystemMana(System):
    s_currentMana = None

    def __init__(self):
        super(SystemMana, self).__init__()

        self.onManaHideObserver = None
        self.onManaShowObserver = None
        self.onManaIncreaseObserver = None
        self.onManaDeacreaseObserver = None
        pass

    def _onRun(self):
        inventoryState = StateManager.getState("StateInventory")
        if inventoryState == "INVENTORY_UP":
            self.__onInventoryUp()
            pass

        self.onManaHideObserver = Notification.addObserver(Notificator.onInventoryHide, self.__onManaHide)
        self.onManaShowObserver = Notification.addObserver(Notificator.onInventoryShow, self.__onManaShow)
        self.onInventoryUpObserver = Notification.addObserver(Notificator.onInventoryUp, self.__onInventoryUp)
        self.onManaIncreaseObserver = Notification.addObserver(Notificator.onManaIncrease, self.__onManaIncrease)
        self.onManaDeacreaseObserver = Notification.addObserver(Notificator.onManaDecrease, self.__onManaDecrease)
        pass

    def _onStop(self):
        Notification.removeObserver(self.onManaHideObserver)
        Notification.removeObserver(self.onManaShowObserver)
        Notification.removeObserver(self.onInventoryUpObserver)
        Notification.removeObserver(self.onManaIncreaseObserver)
        Notification.removeObserver(self.onManaDeacreaseObserver)
        pass

    def __onManaHide(self):
        Mana = DemonManager.getDemon("Mana")
        Mana.setParam("HideState", "Hide")
        return False
        pass

    def __onInventoryUp(self):
        Mana = DemonManager.getDemon("Mana")
        Mana.setParam("HideState", "Idle")
        return False
        pass

    def __onManaShow(self):
        Mana = DemonManager.getDemon("Mana")
        Mana.setParam("HideState", "Show")
        return False
        pass

    def __onManaIncrease(self, value):
        Mana = DemonManager.getDemon("Mana")
        currentMana = Mana.getManaCount()
        newValue = currentMana + value
        Mana.setManaCount(newValue)
        ManaEntity = Mana.getEntity()
        ManaEntity.playUpdateMovie()
        return False
        pass

    def __onManaDecrease(self, value):
        Mana = DemonManager.getDemon("Mana")
        currentMana = Mana.getManaCount()
        newValue = currentMana - value
        Mana.setManaCount(newValue)
        ManaEntity = Mana.getEntity()
        ManaEntity.playUpdateMovie()
        return False
        pass

    pass
