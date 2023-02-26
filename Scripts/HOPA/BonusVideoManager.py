from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager
from Foundation.Utils import isCollectorEdition

class BonusVideoManager(Manager):
    s_videos = {}
    s_counter_received_videos = 0

    class State:
        def __init__(self, bg_name, cut_scene_name, journal_id):
            self.bgName = bg_name
            self.cutSceneName = cut_scene_name
            self.journalID = journal_id
            self.isReceived = False

    @staticmethod
    def loadParams(module, param):
        if isCollectorEdition() is False:
            return True

        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            bg_name = record.get("BgName")
            cut_scene_name = record.get("CutSceneName")
            journal_id = record.get("JournalID")

            if bg_name is not None:
                video_state = BonusVideoManager.State(bg_name, cut_scene_name, journal_id)
                BonusVideoManager.s_videos[journal_id] = video_state

        return True

    @staticmethod
    def getVideos():
        return BonusVideoManager.s_videos

    @staticmethod
    def getVideo(video_id):
        video = BonusVideoManager.s_videos.get(video_id, None)

        if video is None:
            Trace.log('Manager', 0, 'Video {} is not exist'.format(video_id))

        return video

    @staticmethod
    def incCounterReceivedVideos():
        BonusVideoManager.s_counter_received_videos += 1

    @staticmethod
    def getCounterReceivedVideos():
        return BonusVideoManager.s_counter_received_videos