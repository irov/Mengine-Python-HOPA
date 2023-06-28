from Foundation.DefaultManager import DefaultManager
from Foundation.Entities.MovieVirtualArea.VirtualArea import VirtualArea
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.Utils import SimpleLogger
from HOPA.SemaphoreManager import SemaphoreManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


_Log = SimpleLogger("SystemCameraManipulation")


class DebugHUD(object):
    def __init__(self):
        self.observers = []
        self.dev_hud = {}
        self.scale = 0.6

    def onRun(self):
        self.observers.append(Notification.addObserver(Notificator.onSceneInit, self.onSceneInit))

    def onStop(self):
        for dev_hud_node in self.dev_hud.values():
            dev_hud_node.removeFromParent()
            Mengine.destroyNode(dev_hud_node)
        self.dev_hud = {}

        for observer in self.observers:
            Notification.removeObserver(observer)
        self.observers = []

    # utils

    def __createDevHUD(self):
        self.dev_hud = {
            # "mouse_pos_0": None,
            # "mouse_pos_1": None,
            # "mouse_move_0": None,
            # "mouse_move_1": None,
            # "mouse_wheel": None,
            "on_drag": None,
            "drag_status": None,
            "on_drag_move": None,
            "on_scale": None,
            "block": None,
            "global_block": None,
        }

        font_name = "IUWindowText" if Mengine.hasFont("IUWindowText") else "__CONSOLE_FONT__"

        for key in self.dev_hud:
            dev_hud_el = Mengine.createNode("TextField")
            dev_hud_el.setTextId("__ID_TEXT_CONSOLE")
            dev_hud_el.setFontName(font_name)
            dev_hud_el.setHorizontalLeftAlign()
            dev_hud_el.setVerticalCenterAlign()
            dev_hud_el.setScale((self.scale, self.scale, 1))
            dev_hud_el.enable()

            self.dev_hud[key] = dev_hud_el

    # observers

    def onSceneInit(self, scene_name):
        # preparation

        scene = SceneManager.getCurrentScene()
        if scene is None:
            return False

        layer = SceneManager.getLayerScene("BlockInput") or scene.getMainLayer()
        if layer is None:
            return False
        layerSize = layer.getSize()

        zoomOpenGroupName = ZoomManager.getZoomOpenGroupName()

        # node handle

        if len(self.dev_hud) == 0:
            self.__createDevHUD()

        for i, (key, dev_hud_node) in enumerate(self.dev_hud.items()):
            dev_hud_node.removeFromParent()
            layer.addChild(dev_hud_node)

            dev_hud_node.setTextFormatArgs("")

            textPosition = Mengine.vec3f(layerSize.x * 0.03, layerSize.y // 3 + i * layerSize.y * 0.03, 0.0)
            if zoomOpenGroupName is not None:
                dev_hud_node.setWorldPosition(textPosition)
            else:
                dev_hud_node.setLocalPosition(textPosition)

        return False

    def update(self, key, text):
        if key not in self.dev_hud:
            return
        self.dev_hud[key].setTextFormatArgs(text)

    # input handlers

    def onMouseWheel(self, _x, _y, scale, cur_scale=0.0):
        """ _x, _y are relative coords: x=1 right, y=1 bottom, x=0 left, y=0 top """
        if "mouse_wheel" in self.dev_hud:
            self.dev_hud["mouse_wheel"].setTextFormatArgs("wheel: {} [{}]".format(scale, cur_scale))

    def onMouseMove(self, touchId, x, y, dx, dy):
        mouse_move_id = "mouse_move_{}".format(touchId)
        mouse_pos_id = "mouse_pos_{}".format(touchId)

        if mouse_move_id in self.dev_hud:
            self.dev_hud[mouse_move_id].setTextFormatArgs("[{}] move: ({}, {})".format(touchId, dx, dy))
        if mouse_pos_id in self.dev_hud:
            self.dev_hud[mouse_pos_id].setTextFormatArgs("[{}] pos: ({}, {})".format(touchId, x, y))


class DebugCameraGizmo(object):
    MIN_SCALE = None
    MAX_SCALE = None
    SCALE_FACTOR = 0.05
    MAX_STEP = 50.0  # px, float

    def __init__(self):
        self.observers = []
        self.enable = False
        self.mouse_wheel_id = None

        self.camera = None
        self.viewport = None

        self.camera_pos = None
        self.camera_dir = None

        self.dbg = True

    def onRun(self):
        self.camera_pos = Mengine.vec2f(0, 0)
        self.camera_dir = Mengine.vec3f(0, 0, 1)
        self.mouse_wheel_id = Mengine.addMouseWheelHandler(self.onMouseWheel)

        self.observers.append(Notification.addObserver(Notificator.onSceneInit, self._onSceneInit))
        self.observers.append(Notification.addObserver(Notificator.onSceneInit, self._onSceneInit))

        self.enable = True

    def onStop(self):
        if self.mouse_wheel_id is not None:
            Mengine.removeGlobalHandler(self.mouse_wheel_id)
            self.mouse_wheel_id = None

        for observer in self.observers:
            Notification.removeObserver(observer)
        self.observers = None

        if self.camera is not None:
            self.camera.setCameraPosition((0.0, 0.0, 0.0))
            self.camera.setScale((1.0, 1.0, 1.0))
        self.camera = None
        self.viewport = None

        self.camera_pos = None
        self.camera_dir = None

        self.enable = False

    def onMouseWheel(self, event):
        if self.enable is False:
            Trace.msg_err("{} not enable".format(self.__class__.__name__))
            return False

        self.move_and_scale(event)  # self.test_rotate(event)

    def test_rotate(self, event):
        step = 0.5
        step_vec = Mengine.vec3f(0, event.scroll * step, 1)

        direction = self.camera_dir + step_vec
        print(direction)

        self.camera.setCameraDirection(direction)
        self.camera_dir = direction

    def move_and_scale(self, event):
        # scale params
        scale = event.scroll * self.SCALE_FACTOR
        cur_scale = self.camera.getScale()
        next_scale = cur_scale.x + scale if (cur_scale.x + scale) > 1 else 1

        # position params
        content_resolution = Mengine.getContentResolution()
        resolution = Mengine.vec2f(content_resolution.getWidth(), content_resolution.getHeight())
        half_res = Mengine.vec2f(resolution.x * 0.5, resolution.y * 0.5)
        screen_pos = Mengine.vec2f(event.x * resolution.x, event.y * resolution.x)

        # point = Mengine.vec2f(
        #     (screen_pos.x - resolution.x * 0.5) / next_scale,
        #     (screen_pos.y - resolution.y * 0.5) / next_scale
        # )

        def adjust(val, _min, _max):
            if val > _max:
                return _max
            if val < _min:
                return _min
            return val

        # our new position
        this_pos = Mengine.vec2f(
            (screen_pos.x - half_res.x) / next_scale,
            (screen_pos.y - half_res.y) / next_scale
        )

        # check distance. If > max_step, then move from last point to new by max_step units
        step = self.MAX_STEP / next_scale  # step decrease proportionally scale param
        vec = Mengine.vec2f(self.camera_pos.x - this_pos.x, self.camera_pos.y - this_pos.y)
        vec_len = self.getEuclideanDistance(vec, Mengine.vec2f(0, 0))
        direction = vec / self.getEuclideanDistance(vec, Mengine.vec2f(0, 0),to_vec=True) if vec_len != 0 else Mengine.vec2f(0, 0)
        dist = self.getEuclideanDistance(self.camera_pos, this_pos)
        if dist > step:
            step_vec = direction * Mengine.vec2f(step, step)
            print("DIRECTION VECTOR:    ", direction, "  !! ADJUSTED STEP:", dist, ">", step, ":", step_vec)
            # move from last point to new by max_step units in mouse position direction
            this_pos = self.camera_pos - step_vec
        else:
            print("DIRECTION VECTOR:    ", direction, "   ", dist)

        # adjust new position by our borders
        new_pos = Mengine.vec2f(
            adjust(this_pos.x, -half_res.x, half_res.x),
            adjust(this_pos.y, -half_res.y, half_res.y)
        )

        # change pos
        self.set_position(new_pos)

        # scale camera
        self.set_scale(next_scale)

    # camera:

    def set_position(self, vec3f_pos):
        if self.camera is None:
            Trace.msg_err("Camera is NONE")
            return False
        if vec3f_pos == self.camera_pos:
            return True
        self.camera.setCameraPosition(vec3f_pos)
        print(":::  ", self.camera_pos, "->", vec3f_pos)
        self.camera_pos = vec3f_pos
        return True

    def set_scale(self, scale):
        if isinstance(scale, (int, float)):
            self.camera.setScale((scale, scale, scale))
        elif isinstance(scale, Mengine.vec3f):
            self.camera.setScale(scale)
        else:
            Trace.log("System", 0, "Wrong scale type {!r} {}. Must be Mengine.vec3f or numeric".format(scale, type(scale)))

    # utils:

    @staticmethod
    def getEuclideanDistance(vec1, vec2, to_vec=False):
        dist = ((vec1.x - vec2.x) ** 2 + (vec1.y - vec2.y) ** 2) ** 0.5
        if to_vec is True:
            return Mengine.vec2f(dist, dist)
        return dist

    # observers:

    def _onSceneInit(self, scene_name):
        self.camera = Mengine.getDefaultSceneRenderCamera2D()
        self.viewport = Mengine.getDefaultRenderViewport2D()
        return False

    def _onSceneDeactivate(self, scene_name):
        self.camera = None
        self.viewport = None
        return False


class SystemCameraManipulation(System):

    def __init__(self):
        super(SystemCameraManipulation, self).__init__()

        # dev input handlers:
        self.move_handler_id = None
        self.button_handler_id = None
        self.wheel_handler_id = None

        # VirtualArea
        self.virtual_area = None

        # block params
        self._blocked_hotspot = False
        self._global_blocked_hotspot = False
        self._blocked_enigmas = []

        self.root = None
        self.camera = None
        self.hotspot = None
        self.viewport = None

        self.bounds = None

        self._touch_ids = []

    def _onParams(self, params):
        self.bounds = {"begin": None, "end": None}
        self.dev_hud = DebugHUD()  # debug hud
        self.debug_camera_gizmo = DebugCameraGizmo()

    def _onSave(self):
        save = {
            "blocked_hotspot": self._blocked_hotspot,
            "global_blocked_hotspot": self._global_blocked_hotspot,
            "blocked_enigmas": self._blocked_enigmas,
        }
        return save

    def _onLoad(self, save):
        if save is None:
            save = {}

        self._blocked_hotspot = save.get("blocked_hotspot", False)
        self._global_blocked_hotspot = save.get("global_blocked_hotspot", False)
        self._blocked_enigmas = save.get("blocked_enigmas", [])

    def _onRun(self):
        if Mengine.hasTouchpad() is False:
            return True

        if _DEVELOPMENT and DefaultManager.getDefaultBool("DebugTouchpadVirtualAreaHUD", False):
            self.move_handler_id = Mengine.addMouseMoveHandler(self._onMouseMove)
            self.button_handler_id = Mengine.addMouseButtonHandler(self._onMouseButton)
            self.wheel_handler_id = Mengine.addMouseWheelHandler(self._onMouseWheel)

            self.dev_hud.onRun()
        # self.debug_camera_gizmo.onRun()

        self.addObserver(Notificator.onHintActionStart, self._cbResetZoom)
        self.addObserver(Notificator.onHintActionEnd, self._onZoomUnblock)

        self.addObserver(Notificator.onZoomInit, self._onZoomBlock)
        self.addObserver(Notificator.onZoomLeave, self._onZoomUnblock)

        # enigma blocker
        self.addObserver(Notificator.onEnigmaPlay, self._cbEnigmaActivate)
        self.addObserver(Notificator.onEnigmaDeactivate, self._cbEnigmaDeactivate)
        self.addObserver(Notificator.onEnigmaComplete, self._cbEnigmaComplete)

        # virtual area

        self.addObserver(Notificator.onSceneActivate, self._onScenePreparation)
        self.addObserver(Notificator.onSceneDeactivate, self._onSceneDeactivate)

        return True

    def _onStop(self):
        if Mengine.hasTouchpad() is False:
            return

        if self.move_handler_id:
            Mengine.removeGlobalHandler(self.move_handler_id)
        if self.button_handler_id:
            Mengine.removeGlobalHandler(self.button_handler_id)
        if self.wheel_handler_id:
            Mengine.removeGlobalHandler(self.wheel_handler_id)

        self.finalizeVirtualArea()

        if _DEVELOPMENT:
            self.dev_hud.onStop()  # self.debug_camera_gizmo.onStop()

    def _onScenePreparation(self, scene_name):
        if scene_name is None or scene_name == "CutScene":
            return False

        if SceneManager.isGameScene(scene_name) is False:
            return False

        self.initVirtualArea()

        return False

    def _onSceneDeactivate(self, scene_name):
        if scene_name is None:
            return False

        self.finalizeVirtualArea()

        return False

    # virtual area

    def get_bounds_viewport(self):
        target = self.virtual_area._target
        return target.get_bounds_viewport()

    def initVirtualArea(self):
        if self.virtual_area is not None:
            Trace.log("System", 0, "initVirtualArea failed: it is already created!")
            return False

        default_render_viewport = Mengine.getDefaultRenderViewport2D()
        default_viewport = default_render_viewport.getViewport()
        self.bounds["begin"] = default_viewport.begin
        self.bounds["end"] = default_viewport.end

        if self.createHotspot() is False:
            return False

        if _DESKTOP is True:  # run on PC
            scale_factor = DefaultManager.getDefaultFloat("DesktopScaleFactor", 0.05)
        else:
            scale_factor = DefaultManager.getDefaultFloat("TouchpadScaleFactor", 0.005)

        self.virtual_area = VirtualArea()
        self.virtual_area.onInitialize(
            dragging_mode='free',
            disable_drag_if_invalid=False,
            enable_scale=DefaultManager.getDefaultBool("TouchpadEnableScale", True),
            max_scale=DefaultManager.getDefaultFloat("TouchpadMaxScale", 2.0),
            scale_factor=scale_factor,
            allow_out_of_bounds=False
        )

        hotspot = self.hotspot

        self.virtual_area.setup_viewport(hotspot)
        self.virtual_area.init_handlers(hotspot)

        scene = SceneManager.getCurrentScene()
        layer = scene.getMainLayer()

        scene.node.addChildFront(self.virtual_area._root)

        # FIX DESCR: I don't know why, but when we do it - it calls onDeactivate for GameArea - bugs, bugs, bugs...
        # layer.removeFromParent()

        self.virtual_area.add_node(layer)

        self.virtual_area.on_touch += self._on_touch
        self.virtual_area.on_drag_start += self._on_drag_start
        self.virtual_area.on_drag_end += self._on_drag_end
        self.virtual_area.on_scale += self._on_scale
        self.virtual_area.on_drag += self._on_drag

        self.virtual_area.set_content_size(0, 0, self.bounds["end"].x, self.bounds["end"].y)

        if self.isBlocked() is True:
            self.setEnableHotspot(False)

        return True

    def finalizeVirtualArea(self):
        if self.virtual_area is None:
            return True

        self.virtual_area.onFinalize()
        self.virtual_area = None
        self.destroyHotspot()
        return True

    def createHotspot(self):
        if self.hotspot is not None:
            Trace.log("System", 0, "createHotspot failed: it is already created!")
            return False

        scene = SceneManager.getCurrentScene()
        layer = scene.getMainLayer()

        hotspot = Mengine.createNode("HotSpotPolygon")

        hotspot.setName("VirtualAreaSocket")
        polygon = [
            (self.bounds["begin"].x, self.bounds["begin"].y),
            (self.bounds["end"].x, self.bounds["begin"].y),
            (self.bounds["end"].x, self.bounds["end"].y),
            (self.bounds["begin"].x, self.bounds["end"].y)
        ]
        hotspot.setPolygon(polygon)
        hotspot.setDefaultHandle(False)
        layer.addChild(hotspot)

        hotspot.enable()

        self.hotspot = hotspot

        return True

    def isBlocked(self):
        return self._blocked_hotspot is True or self._global_blocked_hotspot is True

    def setBlockHotspot(self, value, _global=False):
        """ enable block for setEnableHotspot
            (if global - unblock won't work while global block true)
        """

        if _global is True:
            self._global_blocked_hotspot = bool(value)
            self.dev_hud.update("global_block", "global_block: {}".format(value))

        if value is True:
            self.setEnableHotspot(False)
            self._blocked_hotspot = True
        elif value is False and self._global_blocked_hotspot is False:
            # if global block is enable - you can't unblock hotspot
            self._blocked_hotspot = False
            self.setEnableHotspot(True)

        self.dev_hud.update("block", "block: {}".format(self._blocked_hotspot))

    def setEnigmaBlock(self, value, enigma_name):
        """ blocks hotspot if this enigma is activated (if value=True)
            or removes auto enigma block is value=False """
        if value is True and enigma_name not in self._blocked_enigmas:
            self._blocked_enigmas.append(enigma_name)
        elif value is False and enigma_name in self._blocked_enigmas:
            self._blocked_enigmas.remove(enigma_name)

    def setEnableHotspot(self, value):
        """ toggle enable hotspot (actually feature to scale)
            if now blocked_hotspot is True - do nothing
        """
        if self.hotspot is None:
            return

        if value is True and self.isBlocked() is False:
            self.hotspot.enable()
        elif value is False:
            self.hotspot.disable()

    def destroyHotspot(self):
        if self.hotspot is None:
            Trace.log("System", 0, "destroyHotspot failed: it is already destroyed!")
            return False

        self.hotspot.removeFromParent()
        Mengine.destroyNode(self.hotspot)
        self.hotspot = None

        return True

    # utils:

    def _resetFreezeHOG(self):
        semaphore = SemaphoreManager.getSemaphore("SkipFreezeHOGCounter")
        semaphore.setValue(True)

    def _on_touch(self, touch_id):
        if touch_id not in self._touch_ids:
            self._touch_ids.append(touch_id)
        if len(self._touch_ids) >= 2:
            ZoomManager.setBlockOpen(True)
            self._resetFreezeHOG()

    def _on_drag_start(self, *args, **kwargs):
        # print "$$$ _on_drag_start"
        ZoomManager.setBlockOpen(True)
        self.dev_hud.update("drag_status", "drag status: True")
        self._resetFreezeHOG()

    def _on_drag_end(self, *args, **kwargs):
        # print "$$$ _on_drag_end"
        ZoomManager.setBlockOpen(False)
        self._touch_ids = []
        self.dev_hud.update("drag_status", "drag status: False")

    def _on_drag(self, x, y):
        bounds = self.virtual_area._target._bounds
        begin, end = bounds['begin'], bounds['end']

        self.dev_hud.update("on_drag", "drag: {}".format((x, y)))
        self.dev_hud.update("on_drag_move", "bounds: {}, {}".format((begin.x, begin.y), (end.x, end.y)))

    def _on_scale(self, scale_factor):
        self.dev_hud.update("on_scale", "scale: {}".format(scale_factor))
        self._resetFreezeHOG()

    def resetZoom(self):
        self.virtual_area.set_scale(1.0)
        return True

    # observers:

    def _cbResetZoom(self, *args):
        self.resetZoom()

        return False

    def _onZoomBlock(self, *args):
        self.setEnableHotspot(False)
        self.resetZoom()

        return False

    def _onZoomUnblock(self, *args):
        self.setEnableHotspot(True)

        return False

    def _cbEnigmaActivate(self, enigma):
        enigma_name = enigma.getParam("EnigmaName")
        if enigma_name not in self._blocked_enigmas:
            return False

        self.setBlockHotspot(True)

        return False

    def _cbEnigmaDeactivate(self, enigma):
        enigma_name = enigma.getParam("EnigmaName")
        if enigma_name not in self._blocked_enigmas:
            return False

        self.setBlockHotspot(False)

        return False

    def _cbEnigmaComplete(self, enigma):
        enigma_name = enigma.getParam("EnigmaName")
        if enigma_name not in self._blocked_enigmas:
            return False

        self.setEnigmaBlock(False, enigma_name)
        self.setBlockHotspot(False)

        return False

    # input handlers:

    def _onMouseWheel(self, event):
        scale_factor = self.virtual_area._target._scale_factor if self.virtual_area else None
        self.dev_hud.onMouseWheel(event.x, event.y, event.scroll, scale_factor)

        # print "WHEEL --- [{}] ({}, {}) ".format(direction, rel_x, rel_y)

    def _onMouseMove(self, event):
        self.dev_hud.onMouseMove(event.touchId, event.x, event.y, event.dx, event.dy)

        # print "MOVE --- <{}> ({}, {}) [{}, {}]".format(touchId, x, y, dx, dy)

    def _onMouseButton(self, event):
        print("BUTTON --- <{}> ({}, {}) btn={} | [down={}, press={}]".format(
            event.touchId, event.x, event.y, event.button, event.isDown, event.isPressed)
        )
