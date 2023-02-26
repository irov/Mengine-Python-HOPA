import Trace
from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class FindSimilarChipsForActivateParam(object):
    def __init__(self, chips, places, hand_setup, hand_charged, slots, hand_charged_alpha_enable, hand_charged_alpha_disable, hand_setup_alpha_enable, hand_setup_alpha_disable, movie_use_alpha_enable, movie_use_alpha_disable, chips_prototypes_alpha):
        self.chips = chips
        self.places = places
        self.hand_setup = hand_setup
        self.hand_charged = hand_charged
        self.slots = slots

        self.hand_charged_alpha_enable = hand_charged_alpha_enable
        self.hand_charged_alpha_disable = hand_charged_alpha_disable

        self.hand_setup_alpha_enable = hand_setup_alpha_enable
        self.hand_setup_alpha_disable = hand_setup_alpha_disable

        self.movie_use_alpha_enable = movie_use_alpha_enable
        self.movie_use_alpha_disable = movie_use_alpha_disable

        self.chips_prototypes_alpha = chips_prototypes_alpha

class FindSimilarChipsForActivateManager(Manager):
    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            '''
                EnigmaName	ChipParam	PlaceParam	Movie2_HandSetup	Movie2_HandCharged	Movie2_Slots
                HandChargedAlphaEnable	HandChargedAlphaDisable	
                HandSetupAlphaEnable	HandSetupAlphaDisable	
                MovieUseAlphaEnable	MovieUseAlphaDisable	
                ChipsPrototypesAlpha


            '''
            enigma_name = record.get('EnigmaName')
            chip_param = record.get('ChipParam')
            place_param = record.get('PlaceParam')
            hand_setup = record.get('Movie2_HandSetup')
            hand_charged = record.get('Movie2_HandCharged')
            slots = record.get('Movie2_Slots')

            hand_charged_alpha_enable = record.get('HandChargedAlphaEnable')
            hand_charged_alpha_disable = record.get('HandChargedAlphaDisable')

            hand_setup_alpha_enable = record.get('HandSetupAlphaEnable')
            hand_setup_alpha_disable = record.get('HandSetupAlphaDisable')

            movie_use_alpha_enable = record.get('MovieUseAlphaEnable')
            movie_use_alpha_disable = record.get('MovieUseAlphaDisable')

            chips_prototypes_alpha = record.get('ChipsPrototypesAlpha')

            result = FindSimilarChipsForActivateManager.addParam(enigma_name, module, chip_param, place_param, hand_setup, hand_charged, slots, hand_charged_alpha_enable, hand_charged_alpha_disable, hand_setup_alpha_enable, hand_setup_alpha_disable, movie_use_alpha_enable, movie_use_alpha_disable, chips_prototypes_alpha)

            if result is False:
                error_msg = "FindSimilarChipsForActivateManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(enigma_name, module, chip_param, place_param, hand_setup, hand_charged, slots, hand_charged_alpha_enable, hand_charged_alpha_disable, hand_setup_alpha_enable, hand_setup_alpha_disable, movie_use_alpha_enable, movie_use_alpha_disable, chips_prototypes_alpha):
        if enigma_name in FindSimilarChipsForActivateManager.s_params:
            error_msg = "FindSimilarChipsForActivateManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(module, chip_param)
        chip_dict = {}
        if records is None:
            error_msg = "FindSimilarChipsForActivateManager cant find Chips database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipTypeID	Movie2_ChipPrototype	NumOfChips
            '''
            chip_type_id = record.get('ChipTypeID')
            movie_prototype = record.get('Movie2_ChipPrototype')
            num_of_chips = record.get('NumOfChips')

            chip_dict[chip_type_id] = (movie_prototype, num_of_chips)

        # -------------- Places ----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(module, place_param)
        place_dict = {}
        if records is None:
            error_msg = "FindSimilarChipsForActivateManager cant find Chips database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                PlaceID	Movie2_Idle	Movie2_Fight	Movie2_Death	Movie2_Use	ProgressBarPrototype	SlotProgressBar
                NumOfUses	ChipForUseID
            '''
            place_id = record.get('PlaceID')
            movie_name_idle = record.get('Movie2_Idle')
            movie_name_fight = record.get('Movie2_Fight')
            movie_name_death = record.get('Movie2_Death')
            movie_name_use = record.get('Movie2_Use')
            progress_bar_prototype = record.get('ProgressBarPrototype')
            slot_progress_bar = record.get('SlotProgressBar')

            num_of_uses = record.get('NumOfUses')
            chip_for_use_id = record.get('ChipForUseID')

            place_dict[place_id] = ((movie_name_idle, movie_name_fight, movie_name_death, movie_name_use, progress_bar_prototype, slot_progress_bar), num_of_uses, chip_for_use_id)

        param = FindSimilarChipsForActivateParam(chip_dict, place_dict, hand_setup, hand_charged, slots, hand_charged_alpha_enable, hand_charged_alpha_disable, hand_setup_alpha_enable, hand_setup_alpha_disable, movie_use_alpha_enable, movie_use_alpha_disable, chips_prototypes_alpha)
        FindSimilarChipsForActivateManager.s_params[enigma_name] = param
        return True

    @staticmethod
    def getParam(enigma_name):
        return FindSimilarChipsForActivateManager.s_params.get(enigma_name)