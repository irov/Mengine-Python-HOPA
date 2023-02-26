from Foundation.DatabaseManager import DatabaseManager
from Foundation.Utils import isCollectorEdition

class BonusMusicManager(object):
    s_bonus_music = {}

    class MusicBonus:
        def __init__(self, music_id, playlist_id, slot_id, resource_name, track_name_id):
            self.music_id = music_id
            self.playlist_id = playlist_id
            self.slot_id = slot_id
            self.resource_name = resource_name
            self.track_name_id = track_name_id

    @staticmethod
    def loadParams(module, param):
        if isCollectorEdition() is False:
            return True

        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            music_id = record.get("MusicID")
            playlist_id = record.get("MusicPlaylistID")
            slot_id = record.get("SlotID")
            resource_name = record.get("ResourceName")
            track_name_id = record.get("TrackNameID")
            BonusMusicManager.s_bonus_music[music_id] = BonusMusicManager.MusicBonus(music_id, playlist_id, slot_id, resource_name, track_name_id)

        return True

    @staticmethod
    def getBonusMusic():
        return BonusMusicManager.s_bonus_music