from HOPA.Macro.MacroCommand import MacroCommand

class MacroHOGItemActive(MacroCommand):
    def _onValues(self, values):
        self.HOGItemName = values[0]
        pass

    def _onGenerate(self, source):
        def __thisItem(name):
            if self.HOGItemName != name:
                return False
                pass

            return True
            pass

        source.addTask("TaskListener", ID=Notificator.onHOGInventoryAppendItem, Filter=__thisItem)
        pass
    pass