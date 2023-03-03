from HOPA.Macro.MacroCommand import MacroCommand


class MacroDisable(MacroCommand):
    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) == 0:
                self.initializeFailed("Macro %s not add any param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
                pass
            pass

        self.ObjectName = values[0]

        '''
        For Layers exists too ways to define layers list to disable:
        1) each layer in separate cell
        2) all layers in one cell with ", " separator
        '''
        self.Layers = []
        if len(values) > 1:
            layers_in_one_cell_list = list([str(i) for i in values[1].split(", ")])

            if len(layers_in_one_cell_list) > 1:
                self.Layers = layers_in_one_cell_list

            else:
                self.Layers = list(values[1:])

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            FinderType, Object = self.findObject(self.ObjectName)

            if Object is None:
                self.initializeFailed("MacroDisable not found Object %s in group %s" % (self.ObjectName, self.GroupName))

            elif self.hasObject(Object.name) is False:
                self.initializeFailed("MacroDisable not found Object %s in group %s" % (Object.name, self.GroupName))

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.ObjectName)
        ObjectType = Object.getType()

        if len(self.Layers) > 0 and (ObjectType == "ObjectMovie" or ObjectType == "ObjectMovie2"):
            for Layer in self.Layers:
                source.addTask("TaskAppendParam", Object=Object, Param="DisableLayers", Value=Layer)

            return

        source.addTask("TaskEnable", Object=Object, Value=False)
