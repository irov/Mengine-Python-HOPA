from Foundation.DefaultManager import DefaultManager
from Foundation.System import System
from HOPA.MusicManager import MusicManager


class Track(object):

    def __init__(self, resource_sound_name, loop=False):
        self.resource_sound_name = resource_sound_name
        self.play = False
        self.pos = 0.0
        self.loop = loop
        self.easing = "easyLinear"

    def fadeOut(self, fade_time=500.0, end_track=None):
        self.play = True
        self.pos = Mengine.musicGetPosMs()
        duration = Mengine.musicGetLengthMs()
        # #print "duration",duration, "pos", self.pos
        # print " >>>> fadeOut", self.resource_sound_name
        self.pos = 0.0
        Mengine.musicFadeOut(self.resource_sound_name, self.pos, self.loop, fade_time, self.easing, end_track)

    def fadeIn(self, fade_time=50.0):
        # print " >>>> fadeIn", self.resource_sound_name
        self.play = False
        self.pos = Mengine.musicGetPosMs()
        Mengine.musicFadeIn(fade_time, self.easing, None)


class Playlist(object):
    def __init__(self):
        self.tracks = {}
        self.tracks_list = []

        self.cur_track_id = None

        self.EventMusicPlaySchedulerId = 0

        self.Handler = None

        self.pause = False
        self.track = None

    def add_track(self, track_id, track):
        if track is None:
            return

        self.tracks[track_id] = track
        self.tracks_list.append(track_id)

    def play(self, InserTrack=False):
        # Trace.log("Manager", 0, "InserTrack %s" % (InserTrack))
        if not self.tracks_list:
            return
        if self.cur_track_id is None:
            self.cur_track_id = self.tracks_list[0]

        self.track = self.tracks[self.cur_track_id]

        fade_out_time = DefaultManager.getDefaultFloat('DefaultMusicFadeOutTime', 1000.0)
        self.track.fadeOut(fade_out_time, self.__end_track)

    def __end_track(self, id=None, is_removed=None):
        # print "__end_track", id, is_removed
        if id == 2:
            # #print "__end_track Track is skiped",id
            return
        # #print " __end_track is False"
        if id == 3:
            # self.EventMusicPlaySchedulerId = 0
            # Mengine.musicStop()
            self.track.fadeIn()
            Mengine.musicStop()

            self.cur_track_id = self.get_next_track_id()
            if self.cur_track_id == "Next":
                next_track_index = 0
                self.cur_track_id = self.tracks_list[next_track_index]
                return

            self.play()

    def get_next_track_id(self):
        # #print "current_track_id", self.cur_track_id
        cur_track_index = self.tracks_list.index(self.cur_track_id)
        next_track_index = cur_track_index + 1

        if next_track_index == len(self.tracks_list):
            next_track_index = 0

        next_track_id = self.tracks_list[next_track_index]

        if next_track_id == "Next":
            next_track_index += 1
            next_list = self.tracks_list[next_track_index]
            # #print "Change Play list from macro to ", next_list
            Notification.notify(Notificator.onMusicPlatlistPlay, next_list)
        # #print "next_track_id", next_track_id
        return next_track_id

    def stop(self):
        if self.track is None:
            return
        self.track.fadeIn()

        # Mengine.musicStop()
        # if self.track is None:
        #     Mengine.musicStop()
        #     self.cur_track_id = self.tracks_list[0]
        #     if self.EventMusicPlaySchedulerId != 0:
        #         Mengine.scheduleGlobalRemove(self.EventMusicPlaySchedulerId)
        #     self.EventMusicPlaySchedulerId = 0
        #     return
        #
        # self.track.fadeIn()
        # self.track.pos = 0.0
        # self.cur_track_id = self.tracks_list[0]
        # if self.EventMusicPlaySchedulerId != 0:
        #     Mengine.scheduleGlobalRemove(self.EventMusicPlaySchedulerId)
        # self.EventMusicPlaySchedulerId = 0

    def next_track(self):
        # #print "!!! playlist next_track"
        self.stop()
        self.cur_track_id = self.get_next_track_id()
        # #print "self.cur_track_id",self.cur_track_id
        self.play()

        # def music_pause(self):
        #     if not self.pause:
        #         # #print "music_pause on"
        #         Mengine.musicPause()
        #         self.pause = not self.pause
        #     elif self.pause:
        #         # #print "music_pause off"
        #         Mengine.musicResume()
        #         self.pause = not self.pause
        #     else:
        #         # #print "music_pause Boolean error"

        pass

    def set_track(self, TrackID):
        self.cur_track_id = TrackID
        self.play()
        pass

    def get_track(self):
        return self.cur_track_id


class SystemMusicPlaylists(System):
    def __init__(self):
        super(SystemMusicPlaylists, self).__init__()

        self.playlists = {}
        self.cur_playlist_id = None
        self.cur_track = None
        self.ObjectPlaylist = None
        self.State_Before_menu = None
        self.hold_playlist_id = None

    def _onInitialize(self):
        super(SystemMusicPlaylists, self)._onInitialize()

        music_playlists_data = MusicManager.getMusicPlaylists()

        for playlist_id, track_data in music_playlists_data.iteritems():
            new_playlist = Playlist()

            for track_id, resource_sound_name in track_data:
                # #print " !!!!!!!! id='{}' r='{}'".format(track_id, resource_sound_name)
                new_track = Track(resource_sound_name)

                new_playlist.add_track(track_id, new_track)

            self.playlists[playlist_id] = new_playlist

    def _onRun(self):
        self.addObserver(Notificator.onMusicPlatlistPlay, self.__onMusicPlaylistPlay)
        self.addObserver(Notificator.onBonusMusicPlaylistPlay, self.__onBonusMusicPlaylistPlay)
        self.addObserver(Notificator.onMusicMenuReturn, self.__onMusicMenuReturn)

        return True

    def __onBonusMusicPlaylistPlay(self, playlist_id):
        # print 'playlist_id', playlist_id
        # print 'self.hold_playlist_id', self.hold_playlist_id
        # print 'self.cur_playlist_id', self.cur_playlist_id
        if self.hold_playlist_id is None:
            self.hold_playlist_id = self.cur_playlist_id

        if playlist_id is None:
            self.__onMusicPlaylistPlay(self.hold_playlist_id)
            self.hold_playlist_id = None
            return False

        self.__onMusicPlaylistPlay(playlist_id)
        return False

    def __onMusicPlaylistPlay(self, playlist_id=None):
        PlaylistMenu = "Playlist_Menu"
        if playlist_id == PlaylistMenu:
            if self.cur_playlist_id != None and self.cur_track != None:
                track = self.playlists[self.cur_playlist_id].get_track()
                ##print "Save List and track", self.cur_playlist_id,track
                if track != None:
                    self.State_Before_menu = (self.cur_playlist_id, track)
        if self.cur_playlist_id == playlist_id:
            ##print "Same Play List!!!!!!!!!!!!!!",playlist_id
            pass

        if playlist_id not in self.playlists:
            ##print "WARING!!!!!!!!!!!!!!!!!!!!!!!"
            ##print "Wrong playlist_id"
            return False

        if self.cur_playlist_id != None:
            cur_playlist = self.playlists[self.cur_playlist_id]
            cur_playlist.stop()

        playlist = self.playlists[playlist_id]
        # #print "playlist_id: ", playlist_id
        playlist.play()

        self.cur_playlist_id = playlist_id
        self.cur_track = playlist.cur_track_id
        return False

    def next_track(self):
        # print " >>> NEXT MUSIC PLAYLIST TRACK"
        if self.cur_playlist_id is not None:
            # print "before cur_playlist_id, cur_track",self.cur_playlist_id,   self.cur_track
            Playlist = self.playlists[self.cur_playlist_id]
            Playlist.next_track()
            self.cur_track = Playlist.cur_track_id  # print "after Id",  self.cur_track
        pass

    def __onMusicMenuReturn(self):
        if self.State_Before_menu is None:
            return False
        playlist_id, track = self.State_Before_menu
        # print " __onMusicMenuReturn", playlist_id,track
        self.__onMusicPlaylistPlay(playlist_id)
        # print "1"
        self._set_List_and_Track(track)
        return False

    def _onStop(self):
        # print "SystemMusicPlaylists _onStop"
        if self.cur_playlist_id is not None:
            playlist = self.playlists[self.cur_playlist_id]
            playlist.stop()
        self.playlists = {}
        self.cur_playlist_id = None

    def _set_List_and_Track(self, track):
        if self.cur_playlist_id is None:
            return
        playlist = self.playlists[self.cur_playlist_id]
        playlist.stop()
        playlist.set_track(track)
        # #print " track", track
        self.cur_track = track

    def _onSave(self):
        if self.cur_playlist_id == "Playlist_Menu":
            save = self.State_Before_menu  # (cur_playlist_id, track)
            return save
        else:
            if self.playlists is None or self.cur_playlist_id is None:
                return
            if self.cur_playlist_id not in self.playlists:
                Trace.log("System", 0,
                          "SystemMusicPlaylists: playlist {} not in playlists".format(self.cur_playlist_id))
                return

            track = self.playlists[self.cur_playlist_id].get_track()
            save = (self.cur_playlist_id, track)

            return save

    def _onLoad(self, data_save):
        if data_save is None:
            return

        self.cur_playlist_id, self.cur_track = data_save
        self.State_Before_menu = (self.cur_playlist_id, self.cur_track)
