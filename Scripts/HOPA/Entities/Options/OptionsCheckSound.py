from HOPA.Entities.Options.OptionsManager import OptionsManager, XlsxOptionsSoundVolumeCheck
from Notification import Notification


class CheckSoundController(object):
    def __init__(self, optionsObject):
        self.soundCheckButtonList = self.createCheckAudioButtons(optionsObject)

    def createCheckAudioButtons(self, optionsObject):
        CheckAudioButtonsList = []

        soundCheckParams = OptionsManager.getSoundCheckParams()
        for param in soundCheckParams:
            scrollbar = optionsObject.Group.getObject(param.sliderMovieName)
            barMovie = scrollbar.entity.getBarMovie()

            if (len(param.checkSoundTracklist) == 0):
                msg = "Please add at least one sound to test to {} for slider bar movie '{}'"
                msg = msg.format(XlsxOptionsSoundVolumeCheck, param.sliderMovieName)
                Trace.log("Entity", 0, msg)

            if barMovie.hasSlot(param.sliderMovieSlotName):
                args = [optionsObject.Group, scrollbar, param.sliderMovieSlotName, param.playButtonPrototype,
                    param.stopButtonPrototype, param.checkSoundTracklist, self]

                if param.soundType == "Sound":
                    checkAudioButton = CheckSoundButton(*args)
                    CheckAudioButtonsList.append(checkAudioButton)
                elif param.soundType == "Voice":
                    checkAudioButton = CheckVoiceButton(*args)
                    CheckAudioButtonsList.append(checkAudioButton)
                elif param.soundType == "Music":
                    checkAudioButton = CheckMusicButton(*args)
                    CheckAudioButtonsList.append(checkAudioButton)
                else:
                    msg = "Options Entity wrong SoundType in {}, should be 'Sound', 'Voice' or 'Music'"
                    msg = msg.format(XlsxOptionsSoundVolumeCheck)
                    Trace.log("Entity", 0, msg)

            else:
                if _DEVELOPMENT:
                    msg = "Options Entity not found slot '{}' for slider bar movie '{}'"
                    msg = msg.format(param.sliderMovieSlotName, param.sliderMovieName)
                    Trace.log("Entity", 0, msg)

        return CheckAudioButtonsList

    def stopOtherAudio(self, buttonToIgnore):
        for button in self.soundCheckButtonList:
            if button == buttonToIgnore:
                continue

            button.stopAudio()

    def cleanUp(self):
        for button in self.soundCheckButtonList:
            button.cleanUp()


class CheckAudioButton(object):
    def __init__(self, groupObject, parentScrollbar, parentSlotName, playButtonProtName, stopButtonProtName,
                 checkAudioList, soundController):
        self.parentScrollbar = parentScrollbar
        self.checkAudio = checkAudioList

        self.playButton = groupObject.tryGenerateObjectUnique(playButtonProtName + parentScrollbar.name,
                                                              playButtonProtName, Enable=True)
        self.stopButton = groupObject.tryGenerateObjectUnique(stopButtonProtName + parentScrollbar.name,
                                                              stopButtonProtName, Enable=True)

        barMovie = parentScrollbar.entity.getBarMovie()
        slot = barMovie.getMovieSlot(parentSlotName)
        slot.addChild(self.playButton.getEntityNode())
        slot.addChild(self.stopButton.getEntityNode())

        self.playButton.setEnable(True)
        self.stopButton.setEnable(False)

        # subscribe eventButtonClicked to buttons EventSetState delegate
        self.playButton.entity.EventSetState += self.eventButtonClicked
        self.stopButton.entity.EventSetState += self.eventButtonClicked

        self.nextAudioIndex = 0
        self.currentAudioId = None
        self.bIsPlaying = False

        self.soundController = soundController

        self.validateSound()

    def eventButtonClicked(self, oldState, newState):
        if oldState != "Click":
            return

        if self.bIsPlaying:
            self.stopAudio()
        else:
            self.playAudio()

    def validateSound(self):
        for audioName in self.checkAudio:
            if not Mengine.hasResource(audioName):
                self.checkAudio.remove(audioName)

                msg = "Options CheckSound for '{}', Engine can\'t find Sound resource '{}'"
                msg = msg.format(self.parentScrollbar.name, audioName)
                Trace.log("Entity", 0, msg)

    def _playAudioImplementation(self):
        def soundEndCb(*args):
            self.currentAudioId = None
            self.stopAudio()

        audioName = self.checkAudio[self.nextAudioIndex]

        self.currentAudioId = Mengine.soundPlay(audioName, False, soundEndCb)

    def playAudio(self):
        if len(self.checkAudio) == 0:
            return

        Mengine.musicStop()  # Ambient music OFF

        self.soundController.stopOtherAudio(self)

        self.nextAudioIndex = (self.nextAudioIndex + 1) % len(self.checkAudio)

        self._playAudioImplementation()

        self.bIsPlaying = True
        self.changeButton(True)

    def _stopAudioImplementation(self):
        if self.currentAudioId is not None:
            Mengine.soundStop(self.currentAudioId)
            self.currentAudioId = None

    def stopAudio(self):
        if self.bIsPlaying:
            self._stopAudioImplementation()

            self.bIsPlaying = False
            self.changeButton(False)

            Notification.notify(Notificator.onBonusMusicPlaylistPlay, None)  # Ambient music ON

    def changeButton(self, bNewStateIsPlay):
        self.playButton.setEnable(not bNewStateIsPlay)
        self.stopButton.setEnable(bNewStateIsPlay)

    def cleanUp(self):
        self.stopAudio()

        self.playButton.entity.EventSetState -= self.eventButtonClicked
        self.stopButton.entity.EventSetState -= self.eventButtonClicked

        self.playButton.onDestroy()
        self.stopButton.onDestroy()


class CheckSoundButton(CheckAudioButton):
    pass


class CheckVoiceButton(CheckAudioButton):
    def _playAudioImplementation(self):
        def soundEndCb(*args):
            self.currentAudioId = None
            self.stopAudio()

        audioName = self.checkAudio[self.nextAudioIndex]

        self.currentAudioId = Mengine.voicePlay(audioName, False, soundEndCb)

    def _stopAudioImplementation(self):
        if self.currentAudioId is not None:
            Mengine.voiceStop(self.currentAudioId)
            self.currentAudioId = None


class CheckMusicButton(CheckAudioButton):
    def _playAudioImplementation(self):
        def soundEndCb(*args):
            self.currentAudioId = None
            self.stopAudio()

        audioName = self.checkAudio[self.nextAudioIndex]

        self.currentAudioId = Mengine.musicPlay(audioName, 0.0, False, soundEndCb)

    def _stopAudioImplementation(self):
        if self.currentAudioId is not None:
            Mengine.musicStop()
            self.currentAudioId = None
