from Foundation.DemonManager import DemonManager
from HOPA.HintActions.HintActionDefault import HintActionDefault
from HOPA.SpellsManager import SpellsManager, SPELLS_UI_DEMON_NAME, SPELL_AMULET_TYPE


class HintActionSpellAmuletUsePower(HintActionDefault):
    def _onParams(self, params):
        super(HintActionSpellAmuletUsePower, self)._onParams(params)

        object_name = SpellsManager.getSpellsUIButtonParam(SPELL_AMULET_TYPE).movie2_spell_button_ready

        self.Object = DemonManager.getObject(SPELLS_UI_DEMON_NAME, object_name)
        self.DemonSpellAmulet = DemonManager.getDemon("SpellAmulet")

    def _onCheck(self):
        amulet_button = self.DemonSpellAmulet.getSpellAmuletButton(self.Quest.params["PowerType"])

        if amulet_button.getLocked() is True:
            return False

        return True

    def _getHintObject(self):
        return self.Object

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

    def _getHintPosition(self, _object):
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
