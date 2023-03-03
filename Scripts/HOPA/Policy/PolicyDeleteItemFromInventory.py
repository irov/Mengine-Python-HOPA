from Foundation.Task.TaskAlias import TaskAlias
from HOPA.HOGManager import HOGManager


class PolicyDeleteItemFromInventory(TaskAlias):
    def _onParams(self, params):
        super(PolicyDeleteItemFromInventory, self)._onParams(params)

        self.HOGItemName = params.get('HOGItemName')
        self.HOG = params.get('HOG')
        self.EnigmaName = params.get('EnigmaName')

    def _onGenerate(self, source):
        def __playMovie(scope):
            # Inventory can be switched during the time item flies.
            # Just to ensure we take movie from right inventory.
            HOGInventory = HOGManager.getInventory(self.EnigmaName)
            InventoryEntity = HOGInventory.getEntity()
            slot = InventoryEntity.getSlotByName(self.HOGItemName)
            if slot and slot.movie:
                scope.addTask("TaskMoviePlay", Movie=slot.movie, Wait=True)

        source.addTask("TaskScope", Scope=__playMovie)
