import Trace
from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class LanguageSelectParam(object):
    slot_format = "slot_{}"

    slot_index_begin = 0

    @staticmethod
    def getSlotFormat(index):
        return LanguageSelectParam.slot_format.format(index)

    def __init__(self, movie_with_slot, button_proto, alias, alias_over, text, text_over, lang):
        self.movie_with_slot = movie_with_slot
        self.button_proto = button_proto
        self.alias = alias
        self.alias_over = alias_over
        self.text = text
        self.text_over = text_over
        self.lang = lang

    def get(self):
        return self.movie_with_slot, self.button_proto, self.alias, self.alias_over, self.text, self.text_over, self.lang

class LanguageSelectManager(Manager):
    s_params = []

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            MovieWithSlot   ButtonPrototype	
            PrototypeTextAlias	PrototypeTextAlias_Over	TextId	TextId_Over	Language
            '''
            MovieWithSlot = str(record.get("MovieWithSlot"))
            ButtonPrototype = str(record.get("ButtonPrototype"))
            PrototypeTextAlias = str(record.get("PrototypeTextAlias"))
            PrototypeTextAlias_Over = str(record.get("PrototypeTextAlias_Over"))
            TextId = str(record.get("TextId"))
            TextId_Over = str(record.get("TextId_Over"))
            Language = str(record.get("Language"))

            LanguageSelectManager.validateText(TextId)
            LanguageSelectManager.validateText(TextId_Over)

            LanguageSelectManager.s_params.append(LanguageSelectParam(MovieWithSlot, ButtonPrototype, PrototypeTextAlias, PrototypeTextAlias_Over, TextId, TextId_Over, Language))

        return True

    @staticmethod
    def validateText(text):
        if not Mengine.existText(text):
            Trace.log("Manager", 0, "TEXT ID %s NOT EXISTS!!!!" % text)
            return False
        return True

    @staticmethod
    def getParams():
        return LanguageSelectManager.s_params