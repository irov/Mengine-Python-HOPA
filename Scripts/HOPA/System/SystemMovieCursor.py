from Foundation.ArrowBlackListManager import ArrowBlackListManager
from Foundation.ArrowManager import ArrowManager
from Foundation.System import System
from HOPA.CursorManager import CursorManager

class SystemMovieCursor(System):
    custom_arrows = {}

    def __init__(self):
        super(SystemMovieCursor, self).__init__()
        self._update_enable_observer = None

    def _onInitialize(self):
        movie_types = ["ObjectMovie2", "ObjectMovie"]

        for obj, params in ArrowBlackListManager.s_ignores.items():
            if obj.getType() not in movie_types:
                continue
            socket_name = params.getSocketName()
            if socket_name is None:
                continue
            SystemMovieCursor.custom_arrows[obj] = params

    def _onFinalize(self):
        self._removeUpdateEnableObserver()

    def _removeUpdateEnableObserver(self):
        if self._update_enable_observer is not None:
            self.removeEventObserver(*self._update_enable_observer)
            self._update_enable_observer = None

    def _onRun(self):
        for obj, params in SystemMovieCursor.custom_arrows.items():
            self.addEvent(obj.onMovieSocketEnterEvent, self._onMovieEnter, params)
            self.addEvent(obj.onMovieSocketLeaveEvent, self._onMovieLeave, params)
        return True

    def _onMovieEnter(self, obj, name, hotspot, x, y, params):
        if name != params.getSocketName():
            return False

        modeName = params.getChangeType()
        cursor = CursorManager.s_cursors[modeName]

        if cursor.arrowItem is False:
            if ArrowManager.emptyArrowAttach() is False:
                return False

        CursorManager.setCursorMode(modeName, True)  # setCursorMode() -> updateArrowCursor()

        CursorManager.s_onObject = obj

        self._update_enable_observer = self.addEvent(obj.onMovieUpdateEnable, self._onMovieEnable, obj, params)

        return False

    def _onMovieLeave(self, obj, name, hotspot, params):
        if name != params.getSocketName():
            return False

        CursorManager._arrowLeaveFilter(obj)
        self._removeUpdateEnableObserver()

        return False

    def _onMovieEnable(self, val, obj, params):
        if val is True:
            return False
        self._onMovieLeave(obj, params.getSocketName(), None, params)
        return True