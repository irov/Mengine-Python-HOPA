from Foundation.GroupManager import GroupManager
from Foundation.System import System
from HOPA.ZoomManager import ZoomManager


class SystemZoomAfterFrame(System):
    def __init__(self):
        super(SystemZoomAfterFrame, self).__init__()
        self.Ent = None
        self.Prev_Parent = None
        pass

    def _onRun(self):
        self.addObserver(Notificator.onZoomAttachToFrame, self._ZoomAttachToFrame)
        self.addObserver(Notificator.onZoomDeAttachToFrame, self._ZoomDeAttachToFrame)

        return True
        pass

    def _onStop(self):
        pass

    def _ZoomAttachToFrame(self, Ent):
        self.Ent = Ent
        Group = self.Ent.object.getGroup()
        zoomGroupName = self.Ent.object.getGroupName()

        Zoom = ZoomManager.getZoom(zoomGroupName)
        FrameGroupName = Zoom.getFrameGroupName()
        GroupBorder = GroupManager.getGroup(FrameGroupName)
        frameScene = GroupBorder.getScene()
        frameLayer = GroupBorder.getMainLayer()

        frameZoomBorder = self.__getFrameBorder(Group, GroupBorder)
        self.Prev_Parent = frameZoomBorder.getParent()

        self.Ent.addChild(frameZoomBorder)
        frameScene.setLocalPosition((0.0, 0.0))
        frameZoomBorder.setLocalPosition((0.0, 0.0))
        frameLayer.setScale((1.0, 1.0, 1.0))
        return False
        pass

    def _ZoomDeAttachToFrame(self, zoom):
        if (self.Ent == None):
            return False
            pass
        Group = self.Ent.object.getGroup()
        zoomGroupName = self.Ent.object.getGroupName()

        Zoom = ZoomManager.getZoom(zoomGroupName)
        FrameGroupName = Zoom.getFrameGroupName()
        GroupBorder = GroupManager.getGroup(FrameGroupName)

        frameZoomBorder = self.__getFrameBorder(Group, GroupBorder)
        self.Prev_Parent.addChild(frameZoomBorder)
        return False
        pass

    def __getFrameBorder(self, Group, GroupBorder):
        frameScene = Group.getScene()
        SceneName = frameScene.getName()

        po = ZoomManager.calcZoomPointLeft("%s" % SceneName)
        PosSet = (-po[0], -po[1])
        self.Ent.node.setLocalPosition(PosSet)

        frameGroupBorder = GroupBorder.getScene()
        return frameGroupBorder
        pass

    pass
