from Foundation.Notificator import Notificator
from HOPA.Macro.MacroCommand import MacroCommand

class MacroReturnToParent(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]

        self.WaitClick = bool(values[1]) if len(values) > 1 else False

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.ItemName)

        object_type = Object.getType()

        if object_type == 'ObjectItem':
            if self.WaitClick:
                source.addTask('TaskMouseButtonClick', isDown=False)

            source.addTask('AliasRemoveItemAttach', Item=Object)
            source.addNotify(Notificator.onMacroAttachItemRemoveObserver, self.ItemName)

        elif object_type == 'ObjectMovie' or object_type == 'ObjectMovie2':
            if self.WaitClick:
                source.addTask('TaskMouseButtonClick', isDown=False)

            source.addFunction(Object.returnToParent)
            source.addNotify(Notificator.onMacroAttachItemRemoveObserver, self.ItemName)