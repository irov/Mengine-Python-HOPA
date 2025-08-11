from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.Entities.Options.Options import Options

class OptionsMore(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, 'Arrow', Activate=True, Update=OptionsMore._updateArrow)
        # Type.addAction(Type, 'FullScreen', Activate=True, Update=OptionsMore._updateFullScreen)
        Type.addAction(Type, 'WideScreen', Activate=True, Update=OptionsMore._updateWideScreen)

    def _updateArrow(self, value):
        Mengine.changeCurrentAccountSetting("CustomCursor", unicode(value))
        # Mengine.changeCurrentAccountSetting("Cursor", unicode(value))

    def _updateFullScreen(self, value):
        if value is None:
            return
        Mengine.changeCurrentAccountSetting("Fullscreen", unicode(value))

    def _updateWideScreen(self, value):
        Mengine.changeCurrentAccountSettingBool("Widescreen", value)

    def __init__(self):
        super(OptionsMore, self).__init__()
        self.listWithCheckBoxesNames = ['Arrow', 'WideScreen']
        pass

    def _onPreparation(self):
        # self.startValueArrow = Mengine.getCurrentAccountSettingBool('Cursor')
        self.startValueArrow = Mengine.getCurrentAccountSettingBool('CustomCursor')
        self.startValueFullScreen = Mengine.getCurrentAccountSettingBool('Fullscreen')
        self.startValueWideScreen = Mengine.getCurrentAccountSettingBool('Widescreen')

        GroupManager.getObject('OptionsMore', 'Movie2CheckBox_Arrow').setParam('Value', self.startValueArrow)
        GroupManager.getObject('OptionsMore', 'Movie2CheckBox_FullScreen').setParam('Value', self.startValueFullScreen)
        GroupManager.getObject('OptionsMore', 'Movie2CheckBox_WideScreen').setParam('Value', self.startValueWideScreen)

        self.object.setParam("Arrow", self.startValueArrow)
        self.object.setParam("WideScreen", self.startValueWideScreen)  # self.object.setParam()

    def _onFullscreenFilter(self, value):
        checkBoxFullScreen = GroupManager.getObject('OptionsMore', 'Movie2CheckBox_FullScreen')
        checkBoxFullScreen.setParam('Value', value)
        # Mengine.changeCurrentAccountSettingBool("Fullscreen", value)

        return False

    def cancel(self):
        Mengine.changeCurrentAccountSetting("Fullscreen", unicode(self.startValueFullScreen))
        self.object.setParam('Arrow', self.startValueArrow)
        self.object.setParam('WideScreen', self.startValueWideScreen)
        GroupManager.getObject('OptionsMore', 'Movie2CheckBox_Arrow').setParam('Value', self.startValueArrow)
        GroupManager.getObject('OptionsMore', 'Movie2CheckBox_FullScreen').setParam('Value', self.startValueFullScreen)
        GroupManager.getObject('OptionsMore', 'Movie2CheckBox_WideScreen').setParam('Value', self.startValueWideScreen)

    def setOptionsStarVolumeValues(self, volume_values):
        Options.setStartVolumeValues(volume_values[0], volume_values[1], volume_values[2])

    def _onActivate(self):
        self.onFullscreenObserver = Notification.addObserver(Notificator.onFullscreen, self._onFullscreenFilter)

        with TaskManager.createTaskChain(Name='OptionsMore_Ok', Repeat=True) as Ok:
            Ok.addTask('TaskMovie2ButtonClick', GroupName='OptionsMore', Movie2ButtonName='Movie2Button_OK')
            Ok.addScope(self.scopeClose, "OptionsMore")
            Ok.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
            volume_values = Options.getStartVolumeValues()
            Ok.addScope(self.scopeOpen, "Options")
            Ok.addFunction(self.setOptionsStarVolumeValues, volume_values)
            Ok.addTask('TaskSceneLayerGroupEnable', LayerName='OptionsMore', Value=False)

            # if GroupManager.hasObject("OptionsMore", 'Movie_Close') is True:
            #     with GuardBlockInput(Ok) as guard_source:
            #         with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
            #             guard_source_movie.addTask("TaskMoviePlay", GroupName="OptionsMore",
            #                                        MovieName="Movie_Close", Wait=True)
            #
            #             guard_source_movie.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
            #
            #     if GroupManager.hasObject("Options", 'Movie_Open') is True:
            #         with GuardBlockInput(Ok) as guard_source:
            #             with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
            #                 guard_source_movie.addTask("TaskMoviePlay", GroupName="Options",
            #                                            MovieName="Movie_Open", Wait=True)
            #                 guard_source_movie.addTask('TaskSceneLayerGroupEnable', LayerName='OptionsMore',
            #                                            Value=False)
            #
            # else:
            #     Ok.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
            #     Ok.addTask('TaskSceneLayerGroupEnable', LayerName='OptionsMore', Value=False)

        with TaskManager.createTaskChain(Name='OptionsMore_Cancel', Repeat=True) as Cancel:
            Cancel.addTask('TaskMovie2ButtonClick', GroupName='OptionsMore', Movie2ButtonName='Movie2Button_Cancel')
            Cancel.addFunction(self.cancel)
            Cancel.addScope(self.scopeClose, "OptionsMore")
            Cancel.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
            volume_values = Options.getStartVolumeValues()
            Cancel.addScope(self.scopeOpen, "Options")
            Cancel.addFunction(self.setOptionsStarVolumeValues, volume_values)
            Cancel.addTask('TaskSceneLayerGroupEnable', LayerName='OptionsMore', Value=False)

        with TaskManager.createTaskChain(Name='OptionsMore_Cancel_Click_Out', Repeat=True) as Cancel:
            Cancel.addTask('TaskMovie2SocketClick', GroupName='OptionsMore',
                           Movie2Name='Movie2_BG', SocketName="close", isDown=True)
            Cancel.addFunction(self.cancel)
            Cancel.addScope(self.scopeClose, "OptionsMore")
            Cancel.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
            volume_values = Options.getStartVolumeValues()
            Cancel.addScope(self.scopeOpen, "Options")
            Cancel.addFunction(self.setOptionsStarVolumeValues, volume_values)
            Cancel.addTask('TaskSceneLayerGroupEnable', LayerName='OptionsMore', Value=False)

            # if GroupManager.hasObject("OptionsMore", 'Movie_Close') is True:
            #     with GuardBlockInput(Cancel) as guard_source:
            #         with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
            #             guard_source_movie.addTask("TaskMoviePlay", GroupName="OptionsMore",
            #                                        MovieName="Movie_Close", Wait=True)
            #
            #             guard_source_movie.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
            #
            #             if GroupManager.hasObject("Options", 'Movie_Open') is True:
            #                 with GuardBlockInput(Cancel) as guard_source:
            #                     with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
            #                         guard_source_movie.addTask("TaskMoviePlay", GroupName="Options",
            #                                                    MovieName="Movie_Open", Wait=True)
            #
            #                         guard_source_movie.addTask('TaskSceneLayerGroupEnable', LayerName='OptionsMore',
            #                                                    Value=False)
            #
            #
            # else:
            #     Cancel.addTask('TaskSceneLayerGroupEnable', LayerName='OptionsMore', Value=False)
            #     Cancel.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)

        with TaskManager.createTaskChain(Name='OptionsMore_CheckBox', GroupName='OptionsMore', Repeat=True) as CheckBox:
            with CheckBox.addRaceTask(2) as (FullScreen, Others):
                for checkBoxName, race in Others.addRaceTaskList(self.listWithCheckBoxesNames):
                    race_checkbox = GroupManager.getObject('OptionsMore', 'Movie2CheckBox_{}'.format(checkBoxName))

                    with race.addRaceTask(2) as (true, false):
                        true.addTask('TaskMovie2CheckBox', Value=True, Movie2CheckBox=race_checkbox)
                        true.addFunction(self.object.setParam, checkBoxName, True)

                        false.addTask('TaskMovie2CheckBox', Value=False, Movie2CheckBox=race_checkbox)
                        false.addFunction(self.object.setParam, checkBoxName, False)

                with FullScreen.addRaceTask(2) as (true, false):
                    fullscreen_checkbox = GroupManager.getObject('OptionsMore', 'Movie2CheckBox_FullScreen')

                    true.addTask('TaskMovie2CheckBox', Value=True, Movie2CheckBox=fullscreen_checkbox)
                    true.addFunction(Mengine.changeCurrentAccountSetting, "Fullscreen", unicode(True))

                    false.addTask('TaskMovie2CheckBox', Value=False, Movie2CheckBox=fullscreen_checkbox)
                    false.addFunction(Mengine.changeCurrentAccountSetting, "Fullscreen", unicode(False))

    def scopeOpen(self, source, GropName):
        MovieName = "Movie2_Open"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def scopeClose(self, source, GropName):
        MovieName = "Movie2_Close"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def SceneEffect(self, source, GropName, MovieName):
        if GroupManager.hasObject(GropName, MovieName) is True:
            Movie = GroupManager.getObject(GropName, MovieName)
            with GuardBlockInput(source) as guard_source:
                with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                    guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True, AutoEnable=True)

                    # guard_source_fade.addTask('AliasFadeOut', FadeGroupName='Fade', From=0.5, Time=250.0)

    def setParams(self):
        Fullscreen = Mengine.getCurrentAccountSettingBool('Fullscreen')

        checkBoxFullScreen = GroupManager.getObject('OptionsMore', 'MovieCheckBox_FullScreen')
        checkBoxFullScreen.setParam('Value', Fullscreen)

    def _onDeactivate(self):
        if TaskManager.existTaskChain('OptionsMore_Ok'):
            TaskManager.cancelTaskChain('OptionsMore_Ok')

        if TaskManager.existTaskChain('OptionsMore_Cancel'):
            TaskManager.cancelTaskChain('OptionsMore_Cancel')

        if TaskManager.existTaskChain('OptionsMore_CheckBox'):
            TaskManager.cancelTaskChain('OptionsMore_CheckBox')

        if TaskManager.existTaskChain('OptionsMore_Cancel_Click_Out'):
            TaskManager.cancelTaskChain('OptionsMore_Cancel_Click_Out')

        Notification.removeObserver(self.onFullscreenObserver)
