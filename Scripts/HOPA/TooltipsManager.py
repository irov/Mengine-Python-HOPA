from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class TooltipsManager(Manager):
    s_data = {}
    s_data_by_id = {}

    class Param(object):
        def __init__(self, transition_to_text_id):
            self.transition_to_text_id = transition_to_text_id

        def getTextID(self):
            return self.transition_to_text_id

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            tooltip_id = record.get("TooltipID")
            resource_name = record.get("Resource_Name")
            transition_to_text_id = record.get("NameID")
            new_param = TooltipsManager.Param(transition_to_text_id)

            TooltipsManager.s_data[resource_name] = new_param
            TooltipsManager.s_data_by_id[tooltip_id] = new_param

        return True

    @staticmethod
    def getTooltipByID(tooltip_id):
        return TooltipsManager.s_data_by_id.get(tooltip_id)

    @staticmethod
    def getParam(socket_name):
        return TooltipsManager.s_data.get(socket_name, None)

    @staticmethod
    def getTransitionSocketSceneNameTo(socket_name):
        param = TooltipsManager.getParam(socket_name)

        if not param:
            return None

        text_id = param.getTextID()

        return text_id

    @staticmethod
    def getTooltipTextIDByResourceName(resource_name):
        param = TooltipsManager.getParam(resource_name)
        if param is None:
            return None

        return param.getTextID()
