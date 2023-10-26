from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.ScenarioManager import ScenarioManager
from HOPA.ZoomManager import ZoomManager


class MacroZoomInterrupt(MacroCommand):

    def _onInitialize(self):
        super(MacroZoomInterrupt, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ZoomManager.hasZoom(self.GroupName) is False:
                self.initializeFailed("Invalid found Zoom %s" % (self.GroupName))

    def _onGenerate(self, source):
        source.addDelay(1000.0)
        source.addTask("TaskZoomClose", ZoomName=self.GroupName, SceneName=self.SceneName, Value=True)

        ZoomObject = ZoomManager.getZoomObject(self.GroupName)

        if ZoomObject is None:
            return

        with source.addIfTask(self._checkIsSafe) as (tc_safe, tc_unsafe):
            tc_safe.addTask("TaskEnable", Object=ZoomObject, Value=False)
            tc_safe.addFunction(ZoomObject.setEnd, True)
            tc_unsafe.addPrint("WARNING: MacroZoomInterrupt failed - fix scenario and try again - zoom cannot be ended")

    def _checkIsSafe(self):
        """ check if this zoom Scenario could be closed forever
            if we have PickItem active macro commands here - we can't close it
        """
        return True
        # fixme: after re-enter game - it forget that some of paragraphs were completed

        pick_item_macro_commands = [
            "PickItem",
            "GiveItemTip",
            "AddItem",
        ]

        scenarios = ScenarioManager.getSceneRunScenarios(self.SceneName, self.GroupName)
        is_safe = True

        for runner in scenarios:
            scenario = runner.getScenario()
            for scenario_paragraph in scenario.getActiveParagraphs():
                for scenario_macro in scenario_paragraph.getAllCommands():
                    if scenario_macro.CommandType not in pick_item_macro_commands:
                        continue

                    is_safe = False
                    Trace.log("Macro", 0, "MacroZoomInterrupt failed - found active macro {!r}:{} {!r}"
                                          " - fix ScenarioMacro_{}: user should pick item before end zoom!!!"
                              .format(scenario_macro.CommandType, scenario_macro.Index,
                                      scenario_paragraph.Paragraphs, self.GroupName))

        return is_safe is True


