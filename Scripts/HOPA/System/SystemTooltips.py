from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from HOPA.TooltipsManager import TooltipsManager
from HOPA.TransitionManager import TransitionManager

ALIAS_ENV = ""
ALIAS_CURSOR_TEXT = "$CursorText"
ID_EMPTY_TEXT = "ID_EMPTY_TEXT"

class SystemTooltips(System):
    def _onInitialize(self):
        super(SystemTooltips, self)._onInitialize()
        self.__cleanupTooltipText()
        self.currentTooltip = None
        pass

    def _onRun(self):
        self.addObserver(Notificator.onSocketMouseEnter, self.__onSocketMouseEnter)
        self.addObserver(Notificator.onSocketMouseLeave, self.__onSocketMouseLeave)

        self.addObserver(Notificator.onTransitionMouseEnter, self.__onTransitionMouseEnter)
        self.addObserver(Notificator.onTransitionMouseLeave, self.__onTransitionMouseLeave)

        self.addObserver(Notificator.onMovie2ButtonMouseEnter, self.__onMovie2ButtonMouseEnter)
        self.addObserver(Notificator.onMovie2ButtonMouseLeave, self.__onMovie2ButtonMouseLeave)
        self.addObserver(Notificator.onMovie2ButtonClickEnd, self.__onMovie2ButtonMouseLeave)

        # self.addObserver(Notificator.onHintStartReloading, self.__onHintStartReloading)
        self.addObserver(Notificator.onHintReloadEnter, self.__onHintReloadEnter)
        self.addObserver(Notificator.onHintReloadLeave, self.__onHintReloadLeave)

        self.addObserver(Notificator.onTransitionBegin, self.__cleanupTooltipText)
        self.addObserver(Notificator.onZoomOpen, self.__cleanupTooltipText)
        self.addObserver(Notificator.onZoomForceOpen, self.__cleanupTooltipText)
        self.addObserver(Notificator.onJournalOpen, self.__cleanupTooltipText)
        self.addObserver(Notificator.onEnigmaSkip, self.__cleanupTooltipText)

        return True

    def _onStop(self):
        self.__cleanupTooltipText()

    # Text handle
    def __cleanupTooltipText(self, *_, **__):
        if self.existTaskChain("SystemToolTips_Updater") is True:
            self.removeTaskChain("SystemToolTips_Updater")

        Mengine.removeTextAliasArguments(ALIAS_ENV, ALIAS_CURSOR_TEXT)
        Mengine.setTextAlias(ALIAS_ENV, ALIAS_CURSOR_TEXT, ID_EMPTY_TEXT)

        return False

    def __setupTooltipText(self, text_id):
        if text_id is None:
            return

        Mengine.removeTextAliasArguments(ALIAS_ENV, ALIAS_CURSOR_TEXT)
        Mengine.setTextAlias(ALIAS_ENV, ALIAS_CURSOR_TEXT, text_id)

        # auto tooltip updater setup:

        if text_id == 'ID_TooltipHint':
            percentage_source = SystemManager.getSystem("SystemHint")
        elif text_id == 'ID_TooltipSkip':
            DemonSkipPuzzle = DemonManager.getDemon("SkipPuzzle")
            percentage_source = DemonSkipPuzzle.getEntity()
        else:
            return

        if DefaultManager.getDefaultBool("DefaultTooltipsAutoUpdateEnable", True) is True:
            self.__setupTooltipUpdater(percentage_source)
        else:
            current_percentage = str(percentage_source.getReloadPercentage()) + "%"
            Mengine.setTextAliasArguments(ALIAS_ENV, ALIAS_CURSOR_TEXT, current_percentage)

    def __setupTooltipUpdater(self, percentage_source):
        def _updateTooltip(source):
            percentage = source.getReloadPercentage()
            current_percentage = str(percentage) + "%"
            Mengine.setTextAliasArguments(ALIAS_ENV, ALIAS_CURSOR_TEXT, current_percentage)
            if percentage == 100:
                self.removeTaskChain("SystemToolTips_Updater")

        update_delay_time = DefaultManager.getDefaultInt("DefaultTooltipsUpdateSpeed", 500)

        if self.existTaskChain("SystemToolTips_Updater") is True:
            self.removeTaskChain("SystemToolTips_Updater")
        with self.createTaskChain("SystemToolTips_Updater", Repeat=True) as tc:
            tc.addFunction(_updateTooltip, percentage_source)
            tc.addDelay(update_delay_time)

    # Hint
    def __onHintStartReloading(self, reloadTime):
        # fixme: sometimes get text arguments error
        self.__cleanupTooltipText()
        self.__onHintReloadEnter()
        return False

    def __onHintReloadEnter(self):
        tooltip = TooltipsManager.getTooltipByID('Hint')

        if tooltip is None:
            Trace.log("System", 0, "SystemTooltips.__onHintReloadEnter not found tooltip '%s'" % ('Hint'))
            return False

        self.currentTooltip = 'Hint'

        text_id = tooltip.getTextID()

        self.__setupTooltipText(text_id)

        return False

    def __onHintReloadLeave(self):
        if self.currentTooltip != 'Hint':
            return False

        self.__cleanupTooltipText()

        return False

    # Socket
    def __onSocketMouseEnter(self, socket):
        socket_name = socket.getName()

        text_id = TooltipsManager.getTooltipTextIDByResourceName(socket_name)

        if text_id is None:
            return False

        self.currentTooltip = socket_name

        self.__setupTooltipText(text_id)

        return False

    def __onSocketMouseLeave(self, socket):
        socket_name = socket.getName()
        if self.currentTooltip == socket_name:
            self.__cleanupTooltipText()

        return False

    # Transition
    def __onTransitionMouseEnter(self, transition):
        text_id = TransitionManager.getTransitionSceneNameTo(transition)

        if text_id is None:
            return False

        self.currentTooltip = transition

        self.__setupTooltipText(text_id)

        return False

    def __onTransitionMouseLeave(self, transition):
        if self.currentTooltip == transition:
            self.__cleanupTooltipText()

        return False

    # Movie
    def __onMovie2ButtonMouseEnter(self, movie):
        movie_name = movie.getEntity().ResourceMovie

        text_id = TooltipsManager.getTransitionSocketSceneNameTo(movie_name)
        if text_id is None:
            return False

        self.currentTooltip = movie_name

        self.__setupTooltipText(text_id)

        return False

    def __onMovie2ButtonMouseLeave(self, movie):
        movie_name = movie.getEntity().ResourceMovie

        if self.currentTooltip == movie_name:
            self.__cleanupTooltipText()

        return False