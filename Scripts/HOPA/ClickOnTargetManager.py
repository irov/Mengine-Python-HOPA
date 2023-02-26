"""
Documentation:
https://wonderland-games.atlassian.net/wiki/spaces/HOG/pages/170754049/ClickOnTarget
"""

from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class ClickOnTargetParam(object):
    def __init__(self, filler, target_fill, target_charge_anim, target_appear_anim, target_disappear_anim, filler_rand_accel_min, filler_rand_accel_max, filler_max_speed, movie_in_group_with_target_mg_slot, target_idle, target_down, target_hit_list, target_miss_list):
        self.filler = filler
        self.target_fill = target_fill

        self.target_charge_anim = target_charge_anim
        self.target_appear_anim = target_appear_anim
        self.target_disappear_anim = target_disappear_anim

        self.filler_rand_accel_min = filler_rand_accel_min
        self.filler_rand_accel_max = filler_rand_accel_max
        self.filler_max_speed = filler_max_speed

        self.movie_in_group_with_target_mg_slot = movie_in_group_with_target_mg_slot

        self.target_idle = target_idle
        self.target_down = target_down
        self.target_hit_list = target_hit_list
        self.target_miss_list = target_miss_list

class ClickOnTargetManager(Manager):
    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	Movie2CursorBoundary	Movie2CursorAim Movie2CursorReady Movie2CursorIdle	
            Movie2TargetIdle	Movie2TargetDown	MissMoviesXlsx [Movie2TargetHit]	
            
            EnigmaName	Movie2Filler	Movie2TargetFill	
            Movie2TargetFill_ChargeAnim	Movie2TargetFill_AppearAnim	Movie2TargetFill_DisappearAnim	
            fFillerRandAccelMin	fFillerRandAccelMax	fFillerMaxSpeed	
            MovieInGroupWithTargetMGSlot	
            Movie2TargetIdle	Movie2TargetDown	MissMoviesXlsx	[Movie2TargetHit]
            '''
            enigma_name = record.get('EnigmaName')

            filler = record.get('Movie2Filler')
            target_fill = record.get('Movie2TargetFill')

            target_charge_anim = record.get('Movie2TargetFill_ChargeAnim')
            target_appear_anim = record.get('Movie2TargetFill_AppearAnim')
            target_disappear_anim = record.get('Movie2TargetFill_DisappearAnim')

            filler_rand_accel_min = float(record.get('fFillerRandAccelMin', 200.0))
            filler_rand_accel_max = float(record.get('fFillerRandAccelMax', 400.0))
            filler_max_speed = float(record.get('fFillerMaxSpeed', 200.0))

            movie_in_group_with_target_mg_slot = record.get('MovieInGroupWithTargetMGSlot')

            target_idle = record.get('Movie2TargetIdle')
            target_down = record.get('Movie2TargetDown')
            target_miss_xlsx = record.get('MissMoviesXlsx')
            target_hit_list = record.get('Movie2TargetHit')

            result = ClickOnTargetManager.addParam(enigma_name, module, filler, target_fill, target_charge_anim, target_appear_anim, target_disappear_anim, filler_rand_accel_min, filler_rand_accel_max, filler_max_speed, movie_in_group_with_target_mg_slot, target_idle, target_down, target_miss_xlsx, target_hit_list)

            if result is False:
                error_msg = "ClickOnTargetManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, filler, target_fill, target_charge_anim, target_appear_anim, target_disappear_anim, filler_rand_accel_min, filler_rand_accel_max, filler_max_speed, movie_in_group_with_target_mg_slot, target_idle, target_down, target_miss_xlsx, target_hit_list):
        if enigma_name in ClickOnTargetManager.s_params:
            error_msg = "ClickOnTargetManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        target_miss_list = list()
        if target_miss_xlsx is not None:
            records = DatabaseManager.getDatabaseRecords(module, target_miss_xlsx)
            if records is None:
                error_msg = "ClickOnTargetManager cant find MissMoviesXlsx database for {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False

            target_miss_list = records[0].get('Movie2TargetMissList')

        param = ClickOnTargetParam(filler, target_fill, target_charge_anim, target_appear_anim, target_disappear_anim, filler_rand_accel_min, filler_rand_accel_max, filler_max_speed, movie_in_group_with_target_mg_slot, target_idle, target_down, target_hit_list, target_miss_list)

        ClickOnTargetManager.s_params[enigma_name] = param

    @staticmethod
    def getParam(enigma_name):
        return ClickOnTargetManager.s_params.get(enigma_name)