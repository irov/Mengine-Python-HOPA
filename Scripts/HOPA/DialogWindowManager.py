from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class DialogWindowManager(Manager):
    s_presets = {}

    class __Param(object):
        if _DEVELOPMENT is True:
            def __repr__(self):
                return "<{}: {}>".format(self.__class__.__name__, self.__dict__)

    class PresetParams(__Param):
        def __init__(self, record):
            self.id = DialogWindowManager.getRecordValue(record, "PresetID", default=None)
            self.confirm = DialogWindowManager.getRecordValue(record, "ConfirmButtonTextID", default=None)
            self.cancel = DialogWindowManager.getRecordValue(record, "CancelButtonTextID", default=None)
            self.question = DialogWindowManager.getRecordValue(record, "QuestionTextID", default=None)
            self.title = DialogWindowManager.getRecordValue(record, "TitleTextID", default=None)
            self.url_left = DialogWindowManager.getRecordValue(record, "UrlLeftTextID", default=None)
            self.url_right = DialogWindowManager.getRecordValue(record, "UrlRightTextID", default=None)
            self.url_center = DialogWindowManager.getRecordValue(record, "UrlCenterTextID", default=None)
            self.icon_value = DialogWindowManager.getRecordValue(record, "IconValueTextID", default=None)

        def get(self, key, default=None):
            return self.__dict__.get(key, default)

    @staticmethod
    def loadPresets(records):
        def trace(msg):
            Trace.log("System", 0, "DialogWindow got error while load presets: {}".format(msg))

        for i, record in enumerate(records):
            params = DialogWindowManager.PresetParams(record)
            if params.id in DialogWindowManager.s_presets:
                trace("Use only unique names - {!r} already used".format(params.id))

            DialogWindowManager.s_presets[params.id] = params

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        if name == "DialogWindowPresets":
            DialogWindowManager.loadPresets(records)

        return True

    # === Getters ======================================================================================================

    @staticmethod
    def getPresets():
        return DialogWindowManager.s_presets

    @staticmethod
    def getPreset(lookup_id):
        return DialogWindowManager.s_presets.get(lookup_id)

    @staticmethod
    def hasPreset(lookup_id):
        return lookup_id in DialogWindowManager.s_presets
