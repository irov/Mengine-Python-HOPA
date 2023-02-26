from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

SPELLS_UI_DEMON_NAME = 'SpellsUI'  # const for SpellsUI
SPELL_AMULET_TYPE = 'amulet'  # const for SpellAmulet

class SpellUIParam(object):
    def __init__(self, movie2_spell_slots, socket_name):
        self.movie2_spell_slots = movie2_spell_slots
        self.socket_name = socket_name

class SpellUIButtonsParam(object):
    def __init__(self, is_unlocked, spell_type, slot_name, movie2_spell_button_idle, movie2_spell_button_ready, movie2_spell_button_use, movie2_spell_button_locked, movie2_spell_button_update, mind_use_less_spell, spell_use_quest):
        self.is_unlocked = is_unlocked  # locked or unlocked by default
        self.spell_type = spell_type
        self.slot_name = slot_name

        self.movie2_spell_button_idle = movie2_spell_button_idle
        self.movie2_spell_button_ready = movie2_spell_button_ready
        self.movie2_spell_button_use = movie2_spell_button_use
        self.movie2_spell_button_locked = movie2_spell_button_locked
        self.movie2_spell_button_update = movie2_spell_button_update

        self.mind_use_less_spell = mind_use_less_spell

        self.spell_use_quest = spell_use_quest

class SpellDemonParam(object):
    def __init__(self, spell_type, spell_demon_name):
        self.spell_type = spell_type
        self.spell_demon_name = spell_demon_name

class SpellAmuletParam(object):
    def __init__(self, movie2_amulet_idle, movie2_amulet_hide, movie2_amulet_open, movie2button_amulet_hint, text_alias_power_locked, text_alias_power_description, socket_name, play_hide_amulet_after_use_bool, hide_amulet_on_zoom_bool, hint_text_alpha_time, hint_text_show_time, amulet_use_alpha_time):
        self.movie2_amulet_idle = movie2_amulet_idle
        self.movie2_amulet_hide = movie2_amulet_hide
        self.movie2_amulet_open = movie2_amulet_open

        self.movie2button_amulet_hint = movie2button_amulet_hint

        self.text_alias_power_locked = text_alias_power_locked
        self.text_alias_power_description = text_alias_power_description

        self.socket_name = socket_name

        self.play_hide_amulet_after_use_bool = play_hide_amulet_after_use_bool
        self.hide_amulet_on_zoom_bool = hide_amulet_on_zoom_bool

        self.hint_text_alpha_time = hint_text_alpha_time
        self.hint_text_show_time = hint_text_show_time

        self.amulet_use_alpha_time = amulet_use_alpha_time

class SpellAmuletStoneParam(object):
    def __init__(self, is_unlocked, power_type, movie2_power_stone_prototype_appear, movie2_power_stone_prototype_idle, movie2_power_stone_prototype_ready, movie2_power_stone_select, movie2_power_stone_info_type, movie2_power_stone_locked_info_prototype, amulet_stone_slot_name, amulet_info_slot_name, text_id_for_alias_power_locked, text_id_for_alias_power_description, movie2_power_stone_aim_prototype, movie2_power_stone_fail_prototype, mind_add_stone, movie2_power_aim_first_submovie,
        movie2_power_aim_second_submovie, movie2_power_aim_third_submovie):
        self.is_unlocked = is_unlocked  # unlocked or locked by default
        self.power_type = power_type

        self.movie2_power_stone_prototype_appear = movie2_power_stone_prototype_appear
        self.movie2_power_stone_prototype_idle = movie2_power_stone_prototype_idle
        self.movie2_power_stone_prototype_ready = movie2_power_stone_prototype_ready
        self.movie2_power_stone_select = movie2_power_stone_select
        self.movie2_power_stone_info_type = movie2_power_stone_info_type
        self.movie2_power_stone_locked_info_prototype = movie2_power_stone_locked_info_prototype

        self.amulet_stone_slot_name = amulet_stone_slot_name
        self.amulet_info_slot_name = amulet_info_slot_name

        self.text_id_for_alias_power_locked = text_id_for_alias_power_locked
        self.text_id_for_alias_power_description = text_id_for_alias_power_description

        self.movie2_power_stone_aim_prototype = movie2_power_stone_aim_prototype
        self.movie2_power_stone_fail_prototype = movie2_power_stone_fail_prototype

        self.mind_add_stone = mind_add_stone
        self.movie2_power_aim_first_submovie = movie2_power_aim_first_submovie
        self.movie2_power_aim_second_submovie = movie2_power_aim_second_submovie
        self.movie2_power_aim_third_submovie = movie2_power_aim_third_submovie

class SpellAmuletPowerParam(object):
    def __init__(self, is_unblocked, power_name, power_type, mind_power_can_use, mind_power_blocked, mind_power_unblocked, mind_power_wrong_stone):
        self.is_unblocked = is_unblocked  # is blocked or unblocked by default
        self.power_name = power_name
        self.power_type = power_type

        self.mind_power_can_use = mind_power_can_use
        self.mind_power_blocked = mind_power_blocked
        self.mind_power_unblocked = mind_power_unblocked
        self.mind_power_wrong_stone = mind_power_wrong_stone

class SpellAmuletPowerDefaultMinds(object):
    def __init__(self, mind_power_can_use, mind_power_blocked, mind_power_unblocked, mind_power_wrong_stone):
        self.mind_power_can_use = mind_power_can_use
        self.mind_power_blocked = mind_power_blocked
        self.mind_power_unblocked = mind_power_unblocked
        self.mind_power_wrong_stone = mind_power_wrong_stone

class SpellUIRuneParam(object):
    def __init__(self, b_start_enable_state, rune_type, movie2_rune_idle, movie2_rune_ready, movie2_rune_appear):
        self.b_start_enable_state = b_start_enable_state
        self.rune_type = rune_type
        self.movie2_rune_idle = movie2_rune_idle
        self.movie2_rune_ready = movie2_rune_ready
        self.movie2_rune_appear = movie2_rune_appear

class SpellsManager(Manager):
    s_spells_ui_param = None
    s_spells_ui_buttons_params = dict()
    s_spells_demons_params = dict()
    s_spells_ui_runes_params = dict()

    s_spell_amulet_param = None
    s_spell_amulet_stones_params = dict()
    s_spell_amulet_powers_params = dict()
    s_spell_amulet_powers_default_minds = dict()

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            """
            Spells_UI.xlsx:
            Movie2_SpellSlots	SocketName

            Spells_UI_Buttons.xlsx:
            bIsUnlockedByDefault
            SpellType	SlotName	Movie2_SpellButton_IDLE	Movie2_SpellButton_READY	
            Movie2_SpellButton_USE	Movie2_SpellButton_LOCKED	Movie2_SpellButton_UPDATE	
            Mind_UseLessSpell	SpellUseQuest

            Spells_Demons.xlsx:
            SpellType SpellDemonName

            SpellAmulet.xlsx:
            Movie2_Amulet_IDLE	Movie2_Amulet_HIDE	Movie2_Amulet_OPEN	Movie2Button_AmuletHint	
            TextAliasPowerLocked	TextAliasPowerDescription	SocketName	
            PlayHideAmuletAfterUse	HideAmuletOnZoom	
            HintTextAlphaTime	HintTextShowTime    AmuletUseAlphaTime

            SpellAmulet_Stones.xlsx:
            bIsUnlockedByDefault
            PowerType	Movie2_PowerStonePrototype_APPEAR	Movie2_PowerStonePrototype_IDLE	
            Movie2_PowerStonePrototype_SELECT	Movie2_PowerAimPrototype	Movie2_PowerFailPrototype	
            Movie2_PowerStoneInfoPrototype	Movie2_PowerStoneLockedInfoPrototype	
            AmuletStoneSlotName	AmuletInfoSlotName	TextIDForAliasPowerLocked	
            TextIDForAliasPowerDescription	Mind_AddStone

            SpellAmulet_Powers.xlsx:
            bIsUnblockedByDefault
            PowerName	PowerType	Mind_PowerCanUse	Mind_PowerBlocked	Mind_PowerUnblocked	Mind_PowerWrongStone

            Spells_UI_Runes.xlsx:
            bStartEnableState	RuneType	Movie2_Rune_IDLE	Movie2_Rune_READY	Movie2_Rune_APPEAR

            """

            spell_slots = record.get('Movie2_SpellSlots')
            movie2_spell_button_idle = record.get('Movie2_SpellButton_IDLE')
            movie2_amulet_idle = record.get('Movie2_Amulet_IDLE')
            movie2_power_stone_prototype_appear = record.get('Movie2_PowerStonePrototype_APPEAR')
            power_name = record.get('PowerName')
            spell_demon_name = record.get('SpellDemonName')
            rune_type = record.get('RuneType')

            if spell_slots is not None:
                SpellsManager.__loadSpellsUIParam(record)
            elif movie2_spell_button_idle is not None:
                SpellsManager.__loadSpellsUIButtonsParams(record)
            elif movie2_amulet_idle is not None:
                SpellsManager.__loadSpellAmuletParam(record)
            elif movie2_power_stone_prototype_appear is not None:
                SpellsManager.__loadSpellAmuletStoneParam(record)
            elif power_name is not None:
                SpellsManager.__loadSpellAmuletPowerParam(record)
                SpellsManager.__loadSpellAmuletPowerDefaultMinds(record)
            elif spell_demon_name is not None:
                SpellsManager.__loadSpellsDemonsParam(record)
            elif rune_type is not None:
                SpellsManager.__loadSpellsUIRunesParam(record)

        return True

    @staticmethod
    def __loadSpellsUIRunesParam(record):
        """
        :param record:
            bStartEnableState	RuneType	Movie2_Rune_IDLE
            Movie2_Rune_READY	Movie2_Rune_APPEAR

        :return:
        """
        b_start_enable_state = bool(record.get('bStartEnableState', False))
        rune_type = record.get('RuneType')
        movie2_rune_idle = record.get('Movie2_Rune_IDLE')
        movie2_rune_ready = record.get('Movie2_Rune_READY')
        movie2_rune_appear = record.get('Movie2_Rune_APPEAR')

        SpellsManager.s_spells_ui_runes_params[rune_type] = SpellUIRuneParam(b_start_enable_state, rune_type, movie2_rune_idle, movie2_rune_ready, movie2_rune_appear)

    @staticmethod
    def __loadSpellsDemonsParam(record):
        """
        :param record: SpellType SpellDemonName
        :return:
        """
        spell_type = record.get('SpellType')
        spell_demon_name = record.get('SpellDemonName')

        SpellsManager.s_spells_demons_params[spell_type] = SpellDemonParam(spell_type, spell_demon_name)

    @staticmethod
    def __loadSpellsUIParam(record):
        """
        :param record: Movie2_SpellSlots	SocketName
        :return:
        """
        movie2_spell_slots = record.get('Movie2_SpellSlots')
        socket_name = record.get('SocketName')
        SpellsManager.s_spells_ui_param = SpellUIParam(movie2_spell_slots, socket_name)

    @staticmethod
    def __loadSpellsUIButtonsParams(record):
        """
        :param record:
            bIsUnlockedByDefault
            SpellType	SlotName	Movie2_SpellButton_IDLE	Movie2_SpellButton_READY
            Movie2_SpellButton_USE	Movie2_SpellButton_LOCKED	Movie2_SpellButton_UPDATE
            Mind_UseLessSpell	SpellUseQuest

        :return:
        """
        bIsUnlockedByDefault = bool(record.get('bIsUnlockedByDefault', False))
        spell_type = record.get('SpellType')
        slot_name = record.get('SlotName')
        movie2_spell_button_idle = record.get('Movie2_SpellButton_IDLE')
        movie2_spell_button_ready = record.get('Movie2_SpellButton_READY')
        movie2_spell_button_use = record.get('Movie2_SpellButton_USE')
        movie2_spell_button_locked = record.get('Movie2_SpellButton_LOCKED')
        movie2_spell_button_update = record.get('Movie2_SpellButton_UPDATE')
        mind_use_less_spell = record.get('Mind_UseLessSpell')
        spell_use_quest = record.get('SpellUseQuest')

        SpellsManager.s_spells_ui_buttons_params[spell_type] = SpellUIButtonsParam(bIsUnlockedByDefault, spell_type, slot_name, movie2_spell_button_idle, movie2_spell_button_ready, movie2_spell_button_use, movie2_spell_button_locked, movie2_spell_button_update, mind_use_less_spell, spell_use_quest)

    @staticmethod
    def __loadSpellAmuletParam(record):
        """
        :param record: Movie2_Amulet_IDLE	Movie2_Amulet_HIDE	Movie2_Amulet_OPEN	Movie2Button_AmuletHint
                        TextAliasPowerLocked	TextAliasPowerDescription	SocketName
                        PlayHideAmuletAfterUse	HideAmuletOnZoom
                        HintTextAlphaTime	HintTextShowTime AmuletUseAlphaTime
        :return:
        """
        movie2_amulet_idle = record.get('Movie2_Amulet_IDLE')
        movie2_amulet_hide = record.get('Movie2_Amulet_HIDE')
        movie2_amulet_open = record.get('Movie2_Amulet_OPEN')
        movie2_button_amulet_hint = record.get('Movie2Button_AmuletHint')
        text_alias_power_locked = record.get('TextAliasPowerLocked')
        text_alias_power_description = record.get('TextAliasPowerDescription')
        socket_name = record.get('SocketName')
        play_hide_amulet_after_use = bool(record.get('PlayHideAmuletAfterUse'))
        hide_amulet_on_zoom = bool(record.get('HideAmuletOnZoom'))
        hint_text_alpha_time = record.get('HintTextAlphaTime')
        hint_text_show_time = record.get('HintTextShowTime')
        amulet_use_alpha_time = record.get('AmuletUseAlphaTime')

        SpellsManager.s_spell_amulet_param = SpellAmuletParam(movie2_amulet_idle, movie2_amulet_hide, movie2_amulet_open, movie2_button_amulet_hint, text_alias_power_locked, text_alias_power_description, socket_name, play_hide_amulet_after_use, hide_amulet_on_zoom, hint_text_alpha_time, hint_text_show_time, amulet_use_alpha_time)

    @staticmethod
    def __loadSpellAmuletStoneParam(record):
        """
        :param record:
            bIsUnlockedByDefault
            PowerType	Movie2_PowerStonePrototype_APPEAR	Movie2_PowerStonePrototype_IDLE
            Movie2_PowerStonePrototype_SELECT	Movie2_PowerAimPrototype	Movie2_PowerFailPrototype
            Movie2_PowerStoneInfoPrototype	Movie2_PowerStoneLockedInfoPrototype
            AmuletStoneSlotName	AmuletInfoSlotName	TextIDForAliasPowerLocked
            TextIDForAliasPowerDescription	Mind_AddStone

        :return:
        """
        bIsUnlockedByDefault = bool(record.get('bIsUnlockedByDefault', False))
        power_type = record.get('PowerType')
        movie2_power_stone_prototype_appear = record.get('Movie2_PowerStonePrototype_APPEAR')
        movie2_power_stone_prototype_idle = record.get('Movie2_PowerStonePrototype_IDLE')
        movie2_power_stone_prototype_ready = record.get('Movie2_PowerStonePrototype_READY')
        movie2_power_aim_prototype = record.get('Movie2_PowerAimPrototype')
        movie2_power_fail_prototype = record.get('Movie2_PowerFailPrototype')
        movie2_power_stone_prototype_select = record.get('Movie2_PowerStonePrototype_SELECT')
        movie2_power_stone_info_prototype = record.get('Movie2_PowerStoneInfoPrototype')
        movie2_power_stone_locked_prototype = record.get('Movie2_PowerStoneLockedInfoPrototype')
        amulet_stone_slot_name = record.get('AmuletStoneSlotName')
        amulet_info_slot_name = record.get('AmuletInfoSlotName')
        text_id_for_alias_power_locked = record.get('TextIDForAliasPowerLocked')
        text_id_for_alias_power_description = record.get('TextIDForAliasPowerDescription')
        mind_add_stone = record.get('Mind_AddStone')
        movie2_power_aim_first_submovie = record.get('Movie2_PowerAimFirstSubmovie')
        movie2_power_aim_second_submovie = record.get('Movie2_PowerAimSecondSubmovie')
        movie2_power_aim_third_submovie = record.get('Movie2_PowerAimThirdSubmovie')

        SpellsManager.s_spell_amulet_stones_params[power_type] = SpellAmuletStoneParam(bIsUnlockedByDefault, power_type, movie2_power_stone_prototype_appear, movie2_power_stone_prototype_idle, movie2_power_stone_prototype_ready, movie2_power_stone_prototype_select, movie2_power_stone_info_prototype, movie2_power_stone_locked_prototype, amulet_stone_slot_name, amulet_info_slot_name, text_id_for_alias_power_locked, text_id_for_alias_power_description, movie2_power_aim_prototype, movie2_power_fail_prototype,
            mind_add_stone, movie2_power_aim_first_submovie, movie2_power_aim_second_submovie, movie2_power_aim_third_submovie)

    @staticmethod
    def __loadSpellAmuletPowerParam(record):
        """
        :param record:
        bIsUnblockedByDefault
        PowerName	PowerType	Mind_PowerCanUse
        Mind_PowerBlocked	Mind_PowerUnblocked	Mind_PowerWrongStone

        :return:
        """
        bIsUnblockedByDefault = bool(record.get('bIsUnblockedByDefault', False))
        power_name = record.get('PowerName')
        power_type = record.get('PowerType')
        mind_power_can_use = record.get('Mind_PowerCanUse')
        mind_power_blocked = record.get('Mind_PowerBlocked')
        mind_power_unblocked = record.get('Mind_PowerUnblocked')
        mind_power_wrong_stone = record.get('Mind_PowerWrongStone')

        SpellsManager.s_spell_amulet_powers_params[power_name] = SpellAmuletPowerParam(bIsUnblockedByDefault, power_name, power_type, mind_power_can_use, mind_power_blocked, mind_power_unblocked, mind_power_wrong_stone)

    @staticmethod
    def __loadSpellAmuletPowerDefaultMinds(record):
        mind_power_can_use = record.get('Mind_PowerCanUse')
        mind_power_blocked = record.get('Mind_PowerBlocked')
        mind_power_unblocked = record.get('Mind_PowerUnblocked')
        mind_power_wrong_stone = record.get('Mind_PowerWrongStone')

        SpellsManager.s_spell_amulet_powers_default_minds = SpellAmuletPowerDefaultMinds(mind_power_can_use, mind_power_blocked, mind_power_unblocked, mind_power_wrong_stone)

    @staticmethod
    def getSpellAmuletPowerDefaultMinds():
        return SpellsManager.s_spell_amulet_powers_default_minds

    @staticmethod
    def getSpellsUIRunesParams():
        return SpellsManager.s_spells_ui_runes_params

    @staticmethod
    def getSpellsUIRuneParam(rune_type):
        return SpellsManager.s_spells_ui_runes_params.get(rune_type)

    @staticmethod
    def getSpellsUIParam():
        return SpellsManager.s_spells_ui_param

    @staticmethod
    def getSpellsUIButtonsParams():
        return SpellsManager.s_spells_ui_buttons_params

    @staticmethod
    def getSpellsUIButtonParam(spell_type):
        return SpellsManager.s_spells_ui_buttons_params.get(spell_type)

    @staticmethod
    def getSpellAmuletParam():
        return SpellsManager.s_spell_amulet_param

    @staticmethod
    def getSpellAmuletStonesParams():
        return SpellsManager.s_spell_amulet_stones_params

    @staticmethod
    def getSpellAmuletStoneParam(power_type):
        return SpellsManager.s_spell_amulet_stones_params.get(power_type)

    @staticmethod
    def getSpellAmuletPowersParams():
        return SpellsManager.s_spell_amulet_powers_params

    @staticmethod
    def getSpellAmuletPowerParam(power_name):
        return SpellsManager.s_spell_amulet_powers_params.get(power_name)

    @staticmethod
    def getSpellsDemonsParams():
        return SpellsManager.s_spells_demons_params

    @staticmethod
    def getSpellsDemonParam(spell_type):
        return SpellsManager.s_spells_demons_params.get(spell_type)

    @staticmethod
    def getSpellUsePowerQuest():
        return SpellsManager.getSpellsUIButtonParam(SPELL_AMULET_TYPE).spell_use_quest