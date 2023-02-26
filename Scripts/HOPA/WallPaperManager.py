from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager
from Foundation.Utils import isCollectorEdition

class WallPaperManager(Manager):
    s_wallpapers = []
    s_wallpapers_default_status = []
    s_wallpapers_dict = {}

    class Wallpaper:
        def __init__(self, wp_id, movie_name, resource_name, status):
            self.wp_id = wp_id
            self.movie_name = movie_name
            self.resource_name = resource_name
            self.status = status

    @staticmethod
    def loadParams(module, param):
        if isCollectorEdition() is False:
            return True

        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            wp_id = record.get("WallPaperID")
            movie_name = record.get("MovieName")
            resource_name = record.get("ResourceName")
            status = record.get("Status")
            status = bool(int(status))

            wallpaper = WallPaperManager.Wallpaper(wp_id, movie_name, resource_name, status)

            WallPaperManager.s_wallpapers.append(wallpaper)
            WallPaperManager.s_wallpapers_default_status.append(wallpaper.status)
            WallPaperManager.s_wallpapers_dict[wp_id] = wallpaper
        return True

    @staticmethod
    def getWallpapers():
        return WallPaperManager.s_wallpapers

    @staticmethod
    def getWallpapersDefaultStatus():
        return WallPaperManager.s_wallpapers_default_status

    @staticmethod
    def getWallpaperByIndex(index):
        return WallPaperManager.s_wallpapers[index]

    @staticmethod
    def getWallpaperById(wp_id):
        wallpaper = WallPaperManager.s_wallpapers_dict.get(wp_id, None)
        if wallpaper is None:
            Trace.log('Manager', 0, 'Wallpaper {} is not exist'.format(wp_id))

        return wallpaper