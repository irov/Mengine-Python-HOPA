from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Notification import Notification

from ExtrasMusicManager import ExtrasMusicManager

class ExtrasMusic(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        pass

    def __init__(self):
        super(ExtrasMusic, self).__init__()
        self.playButtons = {}
        self.saveButtons = {}
        self.pauseButtons = {}
        self.resource = {}
        self.ButtonClickObserver = None
        self.currentTrack = None
        self.SystemMusic = None
        pass

    def _onPreparation(self):
        super(ExtrasMusic, self)._onPreparation()
        Data = ExtrasMusicManager.getData(self.object)
        self.playButtons = Data.getPlayButtons()
        self.pauseButtons = Data.getPauseButtons()
        self.saveButtons = Data.getSaveButtons()
        self.resource = Data.getResource()
        for button in self.saveButtons.keys():
            button.setInteractive(True)
            pass

        for button in self.playButtons.keys():
            button.setInteractive(True)
            pass

        for button in self.pauseButtons.keys():
            button.setInteractive(True)
            button.setEnable(False)
            pass
        pass

    def _onActivate(self):
        super(ExtrasMusic, self)._onActivate()
        self.ButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)
        self.SystemMusic = SystemManager.getSystem("SystemMusic")
        # self.SystemMusic.stopMusic()
        pass

    def __onButtonClick(self, button):
        if button in self.saveButtons.keys():
            trackResource = self.saveButtons[button]
            self.saveTrack(trackResource)
            return False
            pass
        if button in self.playButtons.keys():
            trackResource = self.playButtons[button]
            self.playTrack(trackResource, button)
            return False
            pass
        if button in self.pauseButtons.keys():
            trackResource = self.pauseButtons[button]
            self.stopTrack(trackResource, button)
            return False
            pass
        return False
        pass

    def stopTrack(self, trackResourceName, button):
        Mengine.musicStop()
        self.SystemMusic.onPlayMusic()
        button.setEnable(False)
        for but, track in self.playButtons.iteritems():
            if track == trackResourceName:
                but.setEnable(True)
                break
                pass
            else:
                continue
                pass
            pass
        self.currentTrack = None
        pass

    def playTrack(self, trackResourceName, button):
        button.setEnable(False)
        for but, track in self.pauseButtons.iteritems():
            if track == trackResourceName:
                but.setEnable(True)
                break
                pass
            else:
                continue
                pass
            pass
        if self.currentTrack is not None:
            for but, track in self.playButtons.iteritems():
                if track == self.currentTrack:
                    but.setEnable(True)
                    break
                    pass
                else:
                    continue
                    pass
                pass
            for but, track in self.pauseButtons.iteritems():
                if track == self.currentTrack:
                    but.setEnable(False)
                    break
                    pass
                else:
                    continue
                    pass
                pass
            pass
        if self.currentTrack is not None:
            Mengine.musicStop()
            pass
        else:
            self.SystemMusic.stopMusic()
            pass
        self.currentTrack = trackResourceName
        Mengine.musicPlayTrack(trackResourceName, 0, 0, True)
        pass

    def saveTrack(self, trackName):
        resource = self.resource[trackName][0]
        fileName = self.resource[trackName][1]
        validResource = Mengine.validResource(resource)
        if validResource is True:
            Mengine.copyUserMusic(resource, fileName)
            pass
        else:
            Trace.log("Entity", 0, "Resource not valid, copying not proceed...")
            pass

        with TaskManager.createTaskChain() as tc:
            tc.addTask("AliasFadeIn", FadeGroupName="Fade", To=0.5, Time=0.25 * 1000)  # speed fix
            tc.addTask("AliasMessageOKShow", TextID="ID_MUSICSAVE")
            tc.addTask("TaskButtonClick", GroupName="MessageOK", ButtonName="Button_OK")
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="MessageOK", Value=False)
            tc.addTask("AliasFadeOut", FadeGroupName="Fade", Time=0.25 * 1000, From=0.5)  # speed fix
            pass
        pass

    def _onDeactivate(self):
        super(ExtrasMusic, self)._onDeactivate()
        Notification.removeObserver(self.ButtonClickObserver)
        self.ButtonClickObserver = None

        if self.currentTrack is not None:
            Mengine.musicStop()
            self.SystemMusic.onPlayMusic()
            for but, track in self.playButtons.iteritems():
                if track == self.currentTrack:
                    but.setEnable(True)
                    break
                    pass
                else:
                    continue
                    pass
                pass
            for but, track in self.pauseButtons.iteritems():
                if track == self.currentTrack:
                    but.setEnable(False)
                    break
                    pass
                else:
                    continue
                    pass
                pass
            pass
        self.currentTrack = None

        for button in self.saveButtons.keys():
            button.setInteractive(False)
            pass

        for button in self.playButtons.keys():
            button.setInteractive(False)
            pass

        for button in self.pauseButtons.keys():
            button.setInteractive(False)
            pass

        self.saveButtons = {}
        self.playButtons = {}
        self.pauseButtons = {}
        self.resource = {}
        self.SystemMusic = None
        pass

    pass