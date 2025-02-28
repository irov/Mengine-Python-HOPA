from HOPA.Macro.MacroCommand import MacroCommand


class MacroEnable(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]

        '''
        For Layers exists too ways to define layers list to enable:
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

        self.ObjectTypeFilter = ["ObjectSocket", "ObjectZoom", "ObjectTransition", "ObjectItem"]

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            FinderType, Object = self.findObject(self.ObjectName)

            if self.hasObject(Object.name) is False:
                self.initializeFailed("MacroEnable not found Object %s in group %s" % (Object.name, self.GroupName))

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.ObjectName)
        ObjectType = Object.getType()

        if len(self.Layers) > 0 and (ObjectType == "ObjectMovie" or ObjectType == "ObjectMovie2"):
            for Layer in self.Layers:
                source.addTask("TaskDelParam", Object=Object, Param="DisableLayers", Value=Layer)

            return

        if ObjectType not in self.ObjectTypeFilter:
            source.addEnable(Object)

            return

        Quest = self.addQuest(source, "Enable", SceneName=self.SceneName, GroupName=self.GroupName, Object=Object)

        with Quest as tc_quest:
            tc_quest.addEnable(Object)
