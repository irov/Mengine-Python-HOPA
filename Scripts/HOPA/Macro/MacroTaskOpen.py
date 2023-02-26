from HOPA.Macro.MacroCommand import MacroCommand

class MacroTaskOpen(MacroCommand):
    def _onValues(self, values):
        self.NoteID = values[0]
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onTasksOpen, Args=(self.NoteID,))