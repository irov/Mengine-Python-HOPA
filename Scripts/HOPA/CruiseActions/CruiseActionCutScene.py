from Foundation.GroupManager import GroupManager
from HOPA.CruiseAction import CruiseAction


class CruiseActionCutScene(CruiseAction):
    def _onAction(self, source):
        button = None
        if GroupManager.hasObject("CutScene_Interface", "Movie2Button_Next"):
            button = GroupManager.getObject("CutScene_Interface", "Movie2Button_Next")
        elif GroupManager.hasObject("CutScene_Interface", "Movie2Button_Skip"):
            button = GroupManager.getObject("CutScene_Interface", "Movie2Button_Skip")

        Position = button.getCurrentMovieSocketCenter() if button else (0.0, 0.0)
        source.addTask("AliasCruiseControlAction", Position=Position, Object=button)
        source.addNotify(Notificator.onCruiseActionEnd, self)
