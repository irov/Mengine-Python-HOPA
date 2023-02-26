from Foundation.Notificator import Notificator
from HOPA.Macro.MacroCommand import MacroCommand

class MacroActions(object):
    ENABLE = 'Enable'
    DISABLE = 'Disable'
    INCREMENT = 'Increment'
    DECREMENT = 'Decrement'
    MANUAL = 'Manual'
    UPDATE_TEXT = 'UpdateText'

class MacroDragDropCounter(MacroCommand):
    def _onValues(self, values):
        self.action = values[0]

        self.text_id = values[1] if len(values) > 1 else None

        self.manual = True if len(values) > 2 and values[2] == MacroActions.MANUAL else False

        self.text_alpha = float(values[2]) if self.action == MacroActions.UPDATE_TEXT and len(values) > 2 and values[2] is not None else 0.0

        self.init_count = int(values[3]) if len(values) > 3 and values[3] is not None else 0

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if self.action not in [MacroActions.ENABLE, MacroActions.DISABLE, MacroActions.INCREMENT, MacroActions.DECREMENT, MacroActions.UPDATE_TEXT]:
                self.initializeFailed("Macro DragDropCounter should have 'Enable'/'Disable'/'Increment','Decrement' "
                                      "as value1, and text_id as optional value2, when value1 == 'Enable'"
                                      "and 'Manual' as optional value3 when value1 == 'Enable'"
                                      "and 'Counter Default Value' as value4 when value3 == 'Manual'")

    def _onGenerate(self, source):
        if self.action == MacroActions.ENABLE:
            source.addNotify(Notificator.onHOGDragDropMGInit, self.GroupName, self.text_id, self.manual, self.init_count)
            source.addNotify(Notificator.onHOGDragDropCounterFrameSwitch, self.GroupName, self.action)

        elif self.action == MacroActions.DISABLE:
            source.addNotify(Notificator.onHOGDragDropCounterFrameSwitch, self.GroupName, self.action)

        elif self.action == MacroActions.INCREMENT:
            source.addNotify(Notificator.onDragDropItemCreate, self.GroupName, str(), True)

        elif self.action == MacroActions.DECREMENT:
            source.addNotify(Notificator.onDragDropItemComplete, self.GroupName, str(), True)

        elif self.action == MacroActions.UPDATE_TEXT:
            source.addNotify(Notificator.onHOGDragDropUpdateText, self.GroupName, self.text_id, self.text_alpha)