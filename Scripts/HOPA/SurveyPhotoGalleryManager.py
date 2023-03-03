from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class SurveyPhotoGalleryManager(object):
    s_photos = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Button = record.get("ButtonName")
            MoviePhoto = record.get("MoviePhotoName")
            Group = record.get("GroupName")

            if GroupManager.hasObject(Group, Button) is False:
                Trace.log("Manager", 0, "SurveyPhotoGalleryManager.loadParams"
                                        "\n has not button object {} in group {}".format(Button, Group))
                continue

            button = GroupManager.getObject(Group, Button)

            if GroupManager.hasObject(Group, MoviePhoto) is False:
                Trace.log("Manager", 0, "SurveyPhotoGalleryManager.loadParams"
                                        "\n has not photo movie object {} in group {}".format(MoviePhoto, Group))
                continue

            movie_photo = GroupManager.getObject(Group, MoviePhoto)
            movie_photo.setEnable(False)

            SurveyPhotoGalleryManager.s_photos[button] = movie_photo
            pass

        return True
        pass

    @staticmethod
    def getButtons():
        return SurveyPhotoGalleryManager.s_photos.keys()

    @staticmethod
    def getPhotos():
        return SurveyPhotoGalleryManager.s_photos.items()

    @staticmethod
    def getPhoto(button):
        return SurveyPhotoGalleryManager.s_photos[button]
