from Foundation.DefaultManager import DefaultManager
from Foundation.Notificator import Notificator
from Foundation.System import System
from HOPA.SoundEffectOnObjectManager import SoundEffectOnObjectManager

MSG_SOUND_404 = '[SystemSoundOnObject] Not found sound for tag "{}" and object "{}"'
MSG_SOUND_PLAY = '[SystemSoundOnObject] Play sound "{}" for object "{}" and tag "{}"'

BOOL_PRINT_DEBUG_MSG = DefaultManager.getDefaultBool("Print_To_Console_SoundEffectOnObject", False)

class SystemSoundOnObjects(System):
    def _onParams(self, params):
        super(SystemSoundOnObjects, self)._onParams(params)

        self.once_played_list = []
        pass

    def _onRun(self):
        self.addObserver(Notificator.onSoundEffectOnObject, self.__onSoundEffectOnObject)

        self.addObserver(Notificator.onTransitionEnable, self.__onTransitionEnable)
        self.addObserver(Notificator.onShiftNext, self.__onShiftNext)
        self.addObserver(Notificator.onButtonClick, self.__onButtonClick)
        self.addObserver(Notificator.onButtonMouseEnter, self.__onButtonMouseEnter)
        self.addObserver(Notificator.EditBoxKeyEvent, self.__EditBoxKeyEvent)
        self.addObserver(Notificator.onSocketClick, self.__onSocketClick)

        return True
        pass

    def __onSoundEffectOnObject(self, Obj, Tag):
        tag_objects = SoundEffectOnObjectManager.getObjectsByTag(Tag)

        if Obj in tag_objects:
            SoundName = SoundEffectOnObjectManager.getSound(Obj, Tag)
            pass
        else:
            SoundName = SoundEffectOnObjectManager.getSound(None, Tag)
            pass

        if SoundEffectOnObjectManager.getOnce(Obj, Tag) is True:
            if (Obj, Tag) in self.once_played_list:
                return False
                pass

            self.once_played_list.append((Obj, Tag))
            pass

        if SoundName is not None:
            Mengine.soundPlay(SoundName, False, None)
            pass

        return False
        pass

    def __onTransitionEnable(self, object, value):
        if value is False:
            return False
            pass

        self.__onSoundEffectOnObject(object, "TransitionEnable")

        return False
        pass

    def __onShiftNext(self, object):
        self.__onSoundEffectOnObject(object, "ShiftNext")

        return False
        pass

    def __onButtonClick(self, object):
        self.__onSoundEffectOnObject(object, "ButtonClick")

        return False
        pass

    def __onButtonMouseEnter(self, object):
        self.__onSoundEffectOnObject(object, "ButtonEnter")

        return False
        pass

    def __EditBoxKeyEvent(self, object, key):
        self.__onSoundEffectOnObject(object, "EditBoxKeyEvent")

        return False
        pass

    def __onSocketClick(self, object):
        self.__onSoundEffectOnObject(object, "SocketClick")

        return False
        pass

    def _onStop(self):
        pass

    def _onSave(self):
        return self.once_played_list
        pass

    def _onLoad(self, data_save):
        self.once_played_list = data_save
        pass

    pass