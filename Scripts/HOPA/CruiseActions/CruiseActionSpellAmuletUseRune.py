from Foundation.DemonManager import DemonManager
from Foundation.Notificator import Notificator
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.SpellsManager import SpellsManager, SPELLS_UI_DEMON_NAME, SPELL_AMULET_TYPE


class CruiseActionSpellAmuletUseRune(CruiseAction):
    def __init__(self):
        super(CruiseActionSpellAmuletUseRune, self).__init__()
        self.Point = None

    def _onParams(self, params):
        super(CruiseActionSpellAmuletUseRune, self)._onParams(params)
        self.Power_Name = params.get('Power_Name', None)
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionSpellAmuletUseRune')
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionSpellAmuletUseRune')

        demon_amulet = DemonManager.getDemon(SPELLS_UI_DEMON_NAME)
        object_name = SpellsManager.getSpellsUIButtonParam(SPELL_AMULET_TYPE).movie2_spell_button_ready
        self.Object = demon_amulet.getObject(object_name)

    def _onCheck(self):
        self.Point = self._getPosition()

        if self.Point is None:
            return False

        return True

    def __getAmuletPosition(self):
        socket_name = SpellsManager.getSpellAmuletParam().socket_name
        socket = self.Object.getSocket(socket_name)
        position = socket.getWorldPolygonCenter()
        return position

    def __getStoneButtonSocket(self, stone_button):
        stone_button_movie = stone_button.cur_button_movie
        stone_button_socket = stone_button_movie.getSocket("socket")

        if stone_button_socket is None:
            movies_states_buttons = stone_button.getMoviesStatesButtons()

            for movie in movies_states_buttons.values():
                movie_socket = movie.getSocket("socket")
                if movie_socket is not None:
                    return movie_socket

        return stone_button_socket

    def _getPosition(self):
        demon_spell_amulet = DemonManager.getDemon("SpellAmulet")
        amulet = demon_spell_amulet.getAmulet()

        if amulet.getCurState() == amulet.IDLE:
            power_name = self.Quest.params.get("PowerName")
            stone_button = demon_spell_amulet.getSpellAmuletStoneByPower(power_name)
            stone_button_socket = self.__getStoneButtonSocket(stone_button)

            if stone_button_socket is None:
                if _DEVELOPMENT is True:
                    Trace.log("No socket 'socket' in rune {!r} for calculate hint point".format(power_name))
                position = self.__getAmuletPosition()
            else:
                position = stone_button_socket.getWorldPolygonCenter()
        else:
            position = self.__getAmuletPosition()

        return position

    def _onAction(self):
        Obj = self.Quest.params.get("Object", None) if self.Quest else None

        if TaskManager.existTaskChain("CruiseActionDefault") is True:
            TaskManager.cancelTaskChain("CruiseActionDefault")

        with TaskManager.createTaskChain(Name="CruiseActionDefault") as tc:
            tc.addDelay(self.click_delay)
            tc.addTask("AliasCruiseControlAction", Position=self.Point, Object=Obj)
            tc.addDelay(self.move_delay)
            tc.addNotify(Notificator.onCruiseActionEnd, self)

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionDefault") is True:
            TaskManager.cancelTaskChain("CruiseActionDefault")
