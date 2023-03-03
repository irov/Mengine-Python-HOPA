from HOPA.Macro.MacroCommand import MacroCommand


class MacroNotify(MacroCommand):
    def _onValues(self, values):
        self.notifyID = Notificator.getIdentity(values[0])
        self.Arguments = ()
        if len(values) > 1:
            self.Arguments = values[1:]
            pass
        pass

    def _onGenerate(self, source):
        args = tuple(self.Arguments)
        source.addTask("TaskNotify", ID=self.notifyID, Args=args)
        pass

    pass
