from Foundation.Object.ObjectMovie2 import ObjectMovie2
from HOPA.Macro.MacroCommand import MacroCommand


class MacroAlphaIn(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]
        self.To = float(values[1])
        self.Time = float(values[2])

        self.From = None
        if len(values) > 3:
            self.From = float(values[3])

        self.composition_list = None  # work only for movie2

        if len(values) > 4:
            self.composition_list = list([str(i) for i in values[4].split(", ")])

    def _onGenerate(self, source):
        finderType, Object_ = self.findObject(self.ObjectName)

        if isinstance(Object_, ObjectMovie2):
            source.addTask("AliasMovie2AlphaTo", Movie2=Object_, To=self.To, From=self.From, Time=self.Time,
                           LayersAlphaToList=self.composition_list)

        else:
            source.addTask("AliasObjectAlphaTo", ObjectName=self.ObjectName, To=self.To, From=self.From, Time=self.Time)
