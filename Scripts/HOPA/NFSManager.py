import Trace
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager

class NFSManager(object):
    s_nfs = {}

    class NFSTile(object):
        def __init__(self, groupName, x, y, angle):
            self.groupName = groupName
            self.x = x
            self.y = y
            self.angle = angle
            pass
        pass

    class NFS(object):
        def __init__(self, sceneName, group, obj, tiles, winTile):
            self.sceneName = sceneName
            self.group = group
            self.obj = obj
            self.tiles = tiles

            self.winTile = winTile
            pass
        pass

    @staticmethod
    def loadNFS(name, sceneName, groupName, objectName, module, param):
        Param = Mengine.getParam(param)

        nfs_tiles = []
        for value in Param:
            tile_groupName = value[0].strip()
            tile_x = int(value[1].strip())
            tile_y = int(value[2].strip())
            tile_angle = int(value[3].strip())

            if tile_groupName == "":
                continue

            tile = NFSManager.NFSTile(tile_groupName, tile_x, tile_y, tile_angle)
            nfs_tiles.append(tile)
            pass

        winTile = nfs_tiles[-1]

        around_index = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]

        def __findTile(tiles, i, j):
            for tile in tiles:
                if tile.x == i and tile.y == j:
                    return True
                    pass
                pass

            return False
            pass

        Coach_Grass = DefaultManager.getDefault("NFSGrass", "Coach_Grass")

        grass_tiles = []

        for tile in nfs_tiles:
            for i, j in around_index:
                x = tile.x + i
                y = tile.y + j

                if __findTile(grass_tiles, x, y) is True:
                    continue
                    pass

                if __findTile(nfs_tiles, x, y) is True:
                    continue
                    pass

                tile_grass = NFSManager.NFSTile(Coach_Grass, x, y, 0)
                grass_tiles.append(tile_grass)
                pass
            pass

        nfs_tiles.extend(grass_tiles)

        nfs_group = GroupManager.getGroup(groupName)

        if nfs_group is None:
            Trace.log("NFSManager", 0, "NFSManager.loadNFS: Maybe you forgot to add [%s] in Groups.xls!" % (groupName))
            return
            pass

        if sceneName is None:
            Trace.log("NFSManager", 0, "NFSManager.loadNFS: You forgot to add NFSsceneName!" % (sceneName))
            return
            pass

        nfs_obj = nfs_group.getObject(objectName)
        nfs_obj.onEnigmaInit(name)

        nfs = NFSManager.NFS(sceneName, nfs_group, nfs_obj, nfs_tiles, winTile)

        NFSManager.s_nfs[name] = nfs

        return nfs
        pass

    @staticmethod
    def hasNFS(name):
        return name in NFSManager.s_nfs
        pass

    @staticmethod
    def getNFS(name):
        if NFSManager.hasNFS(name) is False:
            Trace.log("Manager", 0, "NFSManager.getNFS: not found nfs %s" % (name))
            return None
            pass

        nfs = NFSManager.s_nfs[name]

        return nfs
        pass

    @staticmethod
    def getNFSObject(name):
        desc = NFSManager.getNFS(name)

        if desc is None:
            return None
            pass

        return desc.obj
        pass

    @staticmethod
    def getNFSTile(name):
        desc = NFSManager.getNFS(name)

        if desc is None:
            return None
            pass

        return desc.tiles
        pass
    pass