from Foundation.DatabaseManager import DatabaseManager


class ProgrammatorManager(object):
    # Temporary storage
    carrier_slot = "Carrier"
    hand_slot = "Item"
    s_objects = {}

    class Data(object):
        def __init__(self):
            pass

        def set(self, dictinaryData):
            self.__dict__.update(dictinaryData)
            pass

        def __repr__(self):
            return repr(self.__dict__)
            pass

    @staticmethod
    def onFinalize():
        ProgrammatorManager.s_objects = {}
        pass

    @staticmethod
    def loadGames(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for values in records:
            objectName = values.get("Name")
            if objectName == "":
                continue
            collectionName = values.get("Collection")
            ProgrammatorManager.load(collectionName, objectName)
            pass
        pass

    @staticmethod
    def load(module, param, EnigmaName):
        records = DatabaseManager.getDatabaseRecords(module, param)

        monkey_movies = [values.get("ItemMovie") for values in records if values.get("ItemMovie") is not None]
        buttons = [values.get("Button") for values in records if values.get("Button") is not None]
        task_movies = [values.get("TaskMovie") for values in records if values.get("TaskMovie") is not None]
        hands = [values.get("HandMovie") for values in records if values.get("HandMovie") is not None]
        win_order = [values.get("WinOrder") for values in records if values.get("WinOrder") is not None]
        container_slots = [values.get("ContainerSlots") for values in records if values.get("ContainerSlots") is not None]
        final_container = [values.get("FinalSlots") for values in records if values.get("FinalSlots") is not None]
        wheel_up = [values.get("WheelUpMovie") for values in records if values.get("WheelUpMovie") is not None]
        wheel_down = [values.get("WheelDownMovie") for values in records if values.get("WheelDownMovie") is not None]
        tap_slots = [values.get("TapSlots") for values in records if values.get("TapSlots") is not None]
        moves_r = [values.get("MovesRight") for values in records if values.get("MovesRight") is not None]
        moves_l = [values.get("MovesLeft") for values in records if values.get("MovesLeft") is not None]
        pretty_dict = dict(
            monkey_movies=monkey_movies,
            buttons=buttons,
            task_movies=task_movies,
            hands=hands,
            win_order=win_order,
            container_slots=container_slots,
            final_container=final_container,
            wheel_up=wheel_up,
            wheel_down=wheel_down,
            tap_slots=tap_slots,
            moves_r=moves_r,
            moves_l=moves_l
        )
        data = ProgrammatorManager.Data()
        ProgrammatorManager.s_objects[EnigmaName] = data
        data.set(pretty_dict)
        pass

    @staticmethod
    def getGameData(EnigmaName):
        if EnigmaName not in ProgrammatorManager.s_objects:
            Trace.log("Manager", 0, "Cant find %s" % EnigmaName)
            return
            pass
        data = ProgrammatorManager.s_objects[EnigmaName]
        return data
        pass

    #    monkey_movies = ["Movie_Monkey_1",
    #                     "Movie_Monkey_2",
    #                     "Movie_Monkey_3"]
    #
    #
    #
    #    buttons = [ "Button_Right",
    #                 "Button_Left",
    #                 "Button_Up",
    #                 "Button_Down",]
    #
    #
    #
    #    task_movies = [ "Movie_Task_Right",
    #                    "Movie_Task_Left",
    #                    "Movie_Task_Up",
    #                    "Movie_Task_Down",]
    #
    #
    #
    #    hands = [ "Movie_Hand_Top_U",
    #             "Movie_Hand_Top_D",
    #             "Movie_Hand_Bot_U",
    #             "Movie_Hand_Bot_D",
    #             "Movie_Hand_Final_U",
    #             "Movie_Hand_Final_D",
    #                 ]
    #
    #
    #    win_order = ["Movie_Monkey_1",
    #                 "Movie_Monkey_2",
    #                 "Movie_Monkey_3"]
    #
    #
    #
    #    container_slots = [
    #        ("Top_1", "Bot_1"),
    #        ("Top_2", "Bot_2"),
    #        ("Top_3", "Bot_3"),]
    #
    #    final_container = ["Bot_4", "Top_4", "Top_41" ]

    #    wheel_up = ["Movie_WheelUp1", "Movie_WheelUp2", "Movie_WheelUp3"]
    #    wheel_down = ["Movie_WheelDown1", "Movie_WheelDown2", "Movie_WheelDown3"]
    #
    #
    #    tap_slots = [
    #        "Task_1",
    #        "Task_2",
    #        "Task_3",
    #        "Task_4",
    #        "Task_5",
    #        "Task_6"]
    #
    #    moves_r = ["Movie_Right1_2", "Movie_Right2_3", "Movie_Right3_4"]
    #    moves_l  = [ "Movie_Left2_1",  "Movie_Left3_2", "Movie_Left4_3"]

    pass
