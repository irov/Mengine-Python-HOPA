ALIAS_PLATE_BONUS_MUSIC_TRACK_NAME = '$AliasPlateBonusMusicTrackName'

class MusicPlate(object):
    def __init__(self, plate_id, music_param, movie_plate, button_on, button_off):
        self.plate_id = plate_id
        self.music_param = music_param
        self.movie_plate = movie_plate
        self.button_on = button_on
        self.button_off = button_off
        self.is_play = False

        self.setPlay(False)
        self.setText()

    def setText(self):
        self.movie_plate.setTextAliasEnvironment('{}'.format(self.plate_id))
        Mengine.setTextAlias('{}'.format(self.plate_id), ALIAS_PLATE_BONUS_MUSIC_TRACK_NAME, self.music_param.track_name_id)

    def setPlay(self, value):
        self.button_on.setEnable(not value)
        self.button_off.setEnable(value)

        self.is_play = value

    def isPlay(self):
        return self.is_play

    def scopeButtonOnClick(self, source):
        source.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_on)

    def scopeButtonOffClick(self, source):
        source.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_off)

    def cleanUp(self):
        for obj in [self.button_on, self.button_off, self.movie_plate]:
            if obj is None:
                continue
            obj_node = obj.getEntityNode()
            obj_node.removeFromParent()

            obj.onDestroy()