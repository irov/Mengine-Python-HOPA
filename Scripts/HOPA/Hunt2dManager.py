from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class Hunt2Param(object):
    def __init__(self, trace_points_number, group_name, preys_move_speed_default_value, bullet_move_speed_default_value, delay_on_finish_trace_point_default_value, alpha_time, trace, b_hunter_hand_alpha_in_on_first_play):
        self.trace_points_number = trace_points_number
        self.group_name = group_name
        self.preys_move_speed_default_value = preys_move_speed_default_value
        self.bullet_move_speed_default_value = bullet_move_speed_default_value
        self.delay_on_finish_trace_point_default_value = delay_on_finish_trace_point_default_value
        self.alpha_time = alpha_time
        self.trace = trace
        self.b_hunter_hand_alpha_in_on_first_play = b_hunter_hand_alpha_in_on_first_play

class Hunt2dManager(Manager):
    s_hunt2d_games = {}

    class Hunt2dParam(object):
        def __init__(self):
            pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            '''
                EnigmaName GroupName    TracePointsNumber    PreysMoveSpeedDefaultValue  BulletMoveSpeedDefaultValue
                DelayOnFinishTracePointDefaultValue [Trace]
            '''
            enigma_name = record.get('EnigmaName')
            group_name = record.get('GroupName')
            trace_points_number = record.get('TracePointsNumber')
            preys_move_speed_default_value = record.get('PreysMoveSpeedDefaultValue')
            bullet_move_speed_default_value = record.get('BulletMoveSpeedDefaultValue')
            delay_on_finish_trace_point_default_value = record.get('DelayOnFinishTracePointDefaultValue')
            alpha_time = record.get('alphaTime')
            trace = record.get('Trace')
            b_hunter_hand_alpha_in_on_first_play = bool(record.get('bHunterHandAlphaInOnFirstPlay', False))

            Hunt2dManager.s_hunt2d_games[enigma_name] = Hunt2Param(trace_points_number, group_name, preys_move_speed_default_value, bullet_move_speed_default_value, delay_on_finish_trace_point_default_value, alpha_time, trace, b_hunter_hand_alpha_in_on_first_play)

        return True

    @staticmethod
    def getParam(enigma_name):
        return Hunt2dManager.s_hunt2d_games.get(enigma_name, None)