from Foundation.Task.TaskAlias import TaskAlias


class PolicyPickInventoryItemEffectEnd(TaskAlias):
    def _onParams(self, params):
        super(PolicyPickInventoryItemEffectEnd, self)._onParams(params)

        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onInitialize(self):
        super(PolicyPickInventoryItemEffectEnd, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.InventoryItem is None:
                self.initializeFailed("please setup InventoryItem")
                pass
            pass
        pass

    def _onGenerate(self, source):
        InventoryItemEntity = self.InventoryItem.getEntity()

        if InventoryItemEntity.effect is not None:
            with source.addFork() as source_fork:
                source_fork.addTask("TaskMovieInterrupt", Movie=InventoryItemEntity.effect)
                source_fork.addTask("TaskObjectDestroy", Object=InventoryItemEntity.effect)
                pass

            InventoryItemEntity.effect = None
            pass
        else:
            source.addDummy()
            pass
        pass

    pass
