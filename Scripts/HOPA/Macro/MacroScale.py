from HOPA.Macro.MacroCommand import MacroCommand

class MacroScale(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]

        self.To = tuple([float(i) for i in values[1].split(",")])

        self.Time = float(values[2])

        self.From = None
        if len(values) > 3:
            self.From = tuple([float(i) for i in values[3].split(",")])

        # self.Movie2SubCompName = None  # self.Movie2SubComp = None  #  # if len(values) > 4 and values[4] is not None:  #     self.Movie2SubCompName = str(values[4])

    def _onGenerate(self, source):
        source.addTask("AliasObjectScaleTo", ObjectName=self.ObjectName, To=self.To, From=self.From, Time=self.Time)