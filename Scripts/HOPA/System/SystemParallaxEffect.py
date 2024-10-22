from Foundation.Animators.AnimatorEasing import AnimatorEasing
# = parallax debug ==============================================================================
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ParallaxEffectManager import ParallaxEffectManager


def animator_sandbox(system, scene_name):
    global LOG_ENABLE
    LOG_ENABLE = True

    solid_size = Mengine.vec2f(100.0, 100.0)

    surface = Mengine.createSurface("SurfaceSolidColor")
    surface.setSolidColor((0.0, 0.0, 0.0, 1.0))
    surface.setSolidSize(solid_size)

    shape = Mengine.createNode("ShapeQuadFixed")
    shape.setName("DEBUG_SOLID")
    shape.setSurface(surface)

    current_scene_name = SceneManager.getCurrentSceneName()
    current_scene = SceneManager.getCurrentScene()
    current_scene_main_layer = current_scene.getMainLayer()
    current_scene_main_layer.addChild(shape)

    offset_x = -(solid_size.x / 2)
    offset_y = -(solid_size.y / 2)

    resolution = Mengine.getContentResolution()
    width = resolution.getWidth()
    height = resolution.getHeight()

    shape.setWorldPosition((width / 2 + offset_x, height / 2 + offset_y))

    def __pos_setter_x(pos_x_, shape_, offset_):
        cur_pos_ = shape_.getWorldPosition()

        shape.setWorldPosition((pos_x_ + offset_, cur_pos_.y))

    cursor_position = Mengine.getCursorPosition()
    __pos_setter_x(cursor_position.x, shape, offset_x)

    # - schedule animator -
    animator_x = AnimatorEasing(shape.setLocalPositionX, shape.getLocalPositionX())

    animator_x.onInitialize()

    system.animators.append(animator_x)

    def __clean_up():
        Mengine.destroyNode(shape)

    with TaskManager.createTaskChain() as tc:
        tc.addTask("TaskSceneLeave", SceneName=current_scene_name)
        tc.addFunction(__clean_up)


def parallax_debug(func):
    def wrapper(*args, **kwargs):
        CHEAT_PARALLAX_DEBUG = DefaultManager.getDefaultBool("CHEAT_PARALLAX_DEBUG", False)

        if CHEAT_PARALLAX_DEBUG:
            animator_sandbox(*args, **kwargs)
        else:
            # print "CHEAT_PARALLAX_DEBUG = OFF"
            func(*args, **kwargs)

    return wrapper


# = main ========================================================================================
class SystemParallaxEffect(System):
    def __init__(self):
        super(SystemParallaxEffect, self).__init__()

        self.animators = []

        self.MousePositionProviderID = None

    def _onRun(self):
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        self.addObserver(Notificator.onSceneLeave, self.__onSceneLeave)

        return True

    @parallax_debug
    def __setupParallax(self, scene_name):
        parallax_data = ParallaxEffectManager.getData(scene_name)
        objects = parallax_data.Objects

        content_resolution = Mengine.getContentResolution()
        content_width = content_resolution.getWidth()

        content_center_x = content_width / 2

        cursor_position = Mengine.getCursorPosition()
        # print "CURSOR POSITION", cursor_position

        for object_name in objects:
            group_name = objects[object_name].group

            object_ = GroupManager.getObject(group_name, object_name)

            parallax_movie_size = float(objects[object_name].ArtResolution)
            parallax_center = parallax_movie_size / 2

            origin = object_.getOrigin()
            object_.setOrigin((parallax_center, origin[1]))

            position = object_.getPosition()
            object_.setPosition((content_center_x, position[1]))

            parallax_effect = float(objects[object_name].parallaxEffect)

            def __pos_setter(pos_, object_, center_, scale_factor_):
                dist = center_ - pos_
                scaled_dist = dist * scale_factor_

                new_pos = center_ + scaled_dist

                position = object_.getPosition()
                object_.setPosition((new_pos, position[1]))

            __pos_setter(cursor_position.x, object_, content_center_x, parallax_effect)

            __functor_pos_setter = Functor(__pos_setter, object_, content_center_x, parallax_effect)

            animation_time = objects[object_name].Time
            animator = AnimatorEasing(__functor_pos_setter, easing=0.05, epsilon=1.0)

            animator.onInitialize()

            self.animators.append(animator)

    def __onSceneInit(self, scene_name):
        if not ParallaxEffectManager.hasScene(scene_name):
            return False

        self.__setupParallax(scene_name)

        self.MousePositionProviderID = Mengine.addMousePositionProvider(None, None, self.__onMousePositionChange)

        return False

    def __onMousePositionChange(self, touch_id, position):
        # print "__onMousePositionChange", position
        for animator in self.animators:
            animator.set_pos(position.x)

    def _clean_up(self):
        for animator in self.animators:
            animator.onFinalize()
        self.animators = []

        if self.MousePositionProviderID is not None:
            Mengine.removeMousePositionProvider(self.MousePositionProviderID)
            self.MousePositionProviderID = None

    def __onSceneLeave(self, scene_name):
        self._clean_up()

        return False

    def _onStop(self):
        self._clean_up()

# = old ======================================================================
# class SystemParallaxEffect(System):
#
#     def __init__(self):
#         super(SystemParallaxEffect, self).__init__()
#         self.MousePositionProviderID = None
#         self.MousePosition = [0,0]
#         self.MousePositionFollower =[0,0]
#         self.param = None
#         self.Object_Positions=[]
#         self.Objects=[]
#         self.ParallaxNumbers=[]
#         self.center=1280.0/2
#         self.affector = None
#         self.ProgressBar_Follower = None
#         self.speed=None
#         self.tc = None
#         self.Scene_name=None
#         pass
#
#     def _onRun(self):
#         self.addObserver(Notificator.onSceneInit, self._Is_Paralax_Needed)
#         self.addObserver(Notificator.onSceneLeave, self._onStop)
#
#         return True
#
#         pass
#
#     def runTaskChain(self):
#         # print "SystemParallaxEffect runTaskChain"
#         self.ProgressBar_Follower = Mengine.createValueFollowerLinear(0.0, self.speed, self.__update)
#         new_value=1.0
#         self.ProgressBar_Follower.setFollow(new_value)
#
#     def __update(self, value,YOO=None,you=None):
#         # print "__update",value,YOO,you
#         self._ParallaxEffect(value)
#         # self.scopeAddLoadingProgress()
#         pass
#
#     def scopeAddLoadingProgress(self):
#         # cur_value = self.ProgressBar_Follower.getFollow()
#         # new_value = self.MousePosition[0]
#         # print "_ParallaxEffect", cur_value,new_value
#         # if cur_value == new_value:
#         #     return
#         #
#         # # self.ProgressBar_Loading.setValue(new_value)
#         # self.ProgressBar_Follower.setFollow(new_value)
#         pass
#
#     def _ParallaxEffect(self,value):
#         # print "_ParallaxEffect",value
#         Parallax=(self.center-value)/self.center
#         for i in range(len(self.Objects)):
#             pos=self.Object_Positions[i]
#             new_pos=(pos.x+(Parallax*self.ParallaxNumbers[i]), pos.y)
#             self.Objects[i].setPosition(new_pos)
#
#     def __sign(self, a):
#         if a<0:
#             return -1
#         elif a>0:
#             return 1
#         else:
#             return 0
#
#     def _Is_Paralax_Needed(self,Scene):
#         # print "SystemParallaxEffect _Is_Paralax_Needed Scene",Scene
#         Scenes = ParallaxEffectManager.getScenes()
#         for elem in Scenes:
#             if elem == Scene:
#                 print "_Is_Paralax_Needed True"
#                 self.Scene_name = elem
#                 self._setup()
#                 return False
#         return False
#
#     def _setup(self):
#         self.param = ParallaxEffectManager.getData(self.Scene_name)
#         self.speed = self.param.CameraSpeed / 100
#         content_size = float(self.param.ScreenResolution)
#
#         for key in self.param.Objects:
#
#             self.Objects.append(GroupManager.getObject(self.param.Objects[key].group, key))
#             self.ParallaxNumbers.append(self.param.Objects[key].parallaxEffect)
#
#             paralax_movie_size =float(self.param.Objects[key].ArtResolution)
#
#             content_center = content_size / 2
#             paralax_center = paralax_movie_size / 2
#
#             diff = paralax_center - content_center
#             node = self.Objects[-1].getEntityNode()
#             pos=node.getWorldPosition()
#             pos.x -= diff
#             self.Objects[-1].setPosition(pos)
#
#             self.Object_Positions.append(pos)
#
#         self.MousePositionProviderID = Mengine.addMousePositionProvider(
#             None, None, None, self.__onMousePositionChange)
#
#         self.runTaskChain()
#         return False
#
#     def __getText(self, movie_But):
#         movie = movie_But.get("Idle")
#         if movie.getEntity().hasMovieText(self.object.getText_ID()) is False:
#             return None
#
#         textField = movie.getEntity().getMovieText(self.object.getText_ID())
#         return textField
#         pass
#
#
#     def __onMousePositionChange(self, touchID, position):
#         # print "mouse", position.x, position.y
#         self.MousePosition[0] = position.x
#         self.MousePosition[1] = position.y
#         new_value=self.MousePosition[0]
#         self.ProgressBar_Follower.setFollow(new_value)
#
#     def _onStop(self, Scene=None):
#         if self.Scene_name==None:
#             return False
#         if self.affector is not None:
#             self._end_affector()
#
#         if self.tc is not None:
#             self.tc.cancel()
#         self.tc = None
#
#         if self.ProgressBar_Follower is not None:
#             Mengine.destroyValueFollower(self.ProgressBar_Follower)
#             self.ProgressBar_Follower = None
#
#         if self.MousePositionProviderID is not None:
#             Mengine.removeMousePositionProvider(self.MousePositionProviderID)
#         self.MousePositionProviderID = None
#         self.MousePosition = [0, 0]
#         self.MousePositionFollower = [0, 0]
#         self.param = None
#         self.Keys = []
#         self.Objects = []
#         self.ParallaxNumbers = []
#         self.center = 1280.0 / 2
#         self.affector = None
#         self.Scene_name = None
#         return False
#     pass
