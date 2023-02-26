import Trace
from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class TileParam(object):
    def __init__(self, id_, movie_proto, pos, rot_time, start_rot, finish_rot, rot_step, tiles_to_rotate):
        self.id = id_
        self.movie_proto = movie_proto
        self.pos = pos
        self.rot_time = rot_time
        self.start_rot = start_rot
        self.finish_rot = finish_rot
        self.rot_step = rot_step
        self.tiles_to_rotate = tiles_to_rotate

class RotateTilesWhichRotateEachOtherParam(object):
    def __init__(self, tiles):
        self.tiles = tiles

class RotateTilesWhichRotateEachOtherManager(Manager):
    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName  TileParam
            '''

            enigma_name = record.get('EnigmaName')
            tile_param = record.get('TileParam')

            result = RotateTilesWhichRotateEachOtherManager.addParam(enigma_name, module, tile_param)
            if result is False:
                error_msg = "RotateTilesWhichRotateEachOtherManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(enigma_name, module, tile_param):
        tiles = list()

        if enigma_name in RotateTilesWhichRotateEachOtherManager.s_params:
            error_msg = "RotateTilesWhichRotateEachOtherManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(module, tile_param)
        if records is None:
            error_msg = "RotateTilesWhichRotateEachOtherManager cant find TileParam database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            TileId	TileMovie2Prototype	Position    RotateTime	StartRotation	FinishRotation	Rotator	[TilesToRotate]
            '''
            tile_id = record.get('TileId')
            tile_movie2_prototype = record.get('TileMovie2Prototype')
            position = record.get('Position', '0.0, 0.0')
            position = tuple([float(i) for i in position.split(",")])

            rotate_time = float(record.get('RotateTime', 500.0))

            start_rotation = float(record.get('StartRotation'))
            finish_rotation = float(record.get('FinishRotation'))

            rotator = float(record.get('Rotator'))

            tiles_to_rotate = record.get('TilesToRotate')

            temp = []

            if tiles_to_rotate is not None:
                for data in tiles_to_rotate:
                    data = data.split(",")
                    temp.append((int(data[0]), float(data[1])))

            tiles_to_rotate = temp

            tiles.append(TileParam(tile_id, tile_movie2_prototype, position, rotate_time, start_rotation, finish_rotation, rotator, tiles_to_rotate))

        param = RotateTilesWhichRotateEachOtherParam(tiles)

        RotateTilesWhichRotateEachOtherManager.s_params[enigma_name] = param

    @staticmethod
    def getParam(enigma_name):
        return RotateTilesWhichRotateEachOtherManager.s_params.get(enigma_name)