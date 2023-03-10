from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.SpellsManager import SpellsManager
from HOPA.ZoomManager import ZoomManager


class MacroSpellAmuletWaitState(MacroCommand):
    """ Confluence: https://bit.ly/3FuSiHL """

    VALID_TARGETS = ['amulet', 'stone']

    def _onValues(self, values):  # SpellAmuletWaitState <target> <state> [power_type]
        # MACRO Amulet aim
        self.target = values[0]
        self.state = values[1]
        self.power_type = values[2] if len(values) > 2 else None

    def _onInitialize(self, *args, **kwds):
        if _DEVELOPMENT is True:
            if self.target not in self.VALID_TARGETS:
                self.initializeFailed("MacroSpellAmuletWaitState: invalid target {!r}, use one of them: {}".format(self.target, self.VALID_TARGETS))
            if self.power_type is not None and SpellsManager.getSpellAmuletStoneParam(self.power_type) is None:
                self.initializeFailed("MacroSpellAmuletWaitState: not found power_type '{}'".format(self.power_type))

    def __checkLocation(self):
        cur_scene = SceneManager.getCurrentSceneName()
        cur_group = ZoomManager.getZoomOpenGroupName()

        if cur_scene != self.SceneName:
            # print "WRONG CAST SCENE", cur_scene, self.SceneName
            return False
        if cur_group is not None:
            if cur_group != self.GroupName:
                # print "WRONG CAST GROUP", cur_group, self.GroupName
                return False
        return True

    def __filterAmuletStateUpdate(self, state):  # SpellAmulet
        if self.__checkLocation() is False:
            return False

        if state != self.state:
            # print "WRONG STATE", state, self.state
            return False
        return True

    def __filterSpellUIStateUpdate(self, button, state):  # SpellAmuletPowerButton
        if self.__checkLocation() is False:
            return False

        if self.power_type is not None:
            power_type = button.power_type
            if power_type != self.power_type:
                # print "WRONG POWER TYPE", power_type, self.power_type
                return False
        if state != self.state:
            # print "WRONG STATE", state, self.state
            return False
        return True

    def _onGenerate(self, source):
        if self.target == "amulet":
            source.addListener(Notificator.onSpellAmuletStateChange, Filter=self.__filterAmuletStateUpdate)
        elif self.target == "stone":
            source.addListener(Notificator.onSpellAmuletPowerButtonStateChange, Filter=self.__filterSpellUIStateUpdate)
        else:
            source.addDummy()

        # source.addPrint("------ COMPLETE {} : {} {}".format(self.target, self.state, self.power_type))
