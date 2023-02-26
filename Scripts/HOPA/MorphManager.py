from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager

class MorphManager(Manager):
    s_morphs = []

    class __Param(object):
        if _DEVELOPMENT is True:
            def __repr__(self):
                return "<{}: {}>".format(self.__class__.__name__, self.__dict__)

    class MorphParams(__Param):
        def __init__(self, record):
            self._correct_record = False

            self.id = MorphManager.getRecordValue(record, "MorphID")

            self.group_name = MorphManager.getRecordValue(record, "GroupName")
            movie_name = MorphManager.getRecordValue(record, "MorphMovieName")
            self.state_movies = {"Idle": movie_name + "_Idle", "Pick": movie_name + "_Pick"}
            self.parent_movie_name = MorphManager.getRecordValue(record, "ParentMovieName")
            self.slot_name = MorphManager.getRecordValue(record, "SlotName")

            self.settings = MorphManager.MorphSettings(record)

            self.__checkRecord()  # if self.hasCorrectRecord() is True:  #     if _DEVELOPMENT is True:  #         Trace.msg("MorphManager successfully load [{}] morph {!r} in {!r} with params: {}".format(  #             self.id, movie_name, self.group_name, self.settings.__dict__))

        def __checkRecord(self):
            error_msg = "MorphManager checkRecord [{}] find error: ".format(self.id)

            def trace(msg):
                Trace.log("Manager", 0, msg)

            for key, val in self.__dict__.items():
                if val is None:
                    trace(error_msg + "{} not configured".format(key))
                    return False

            if GroupManager.hasGroup(self.group_name) is False:
                trace(error_msg + "group {!r} not found".format(self.group_name))
                return False
            group = GroupManager.getGroup(self.group_name)

            if isinstance(group, GroupManager.EmptyGroup):
                # EmptyGroup in 99% means CE group
                if _DEVELOPMENT is True:
                    Trace.msg("MorphManager checkRecord [{}] find, that group {!r} is EmptyGroup".format(self.id, self.group_name))
                return False

            error_msg += "[{}] not found ".format(self.group_name)

            for state, movie_name in self.state_movies.items():
                if group.hasObject(movie_name) is False:
                    trace(error_msg + "morph movie {!r} (for state {})".format(movie_name, state))
                    return False

            if group.hasObject(self.parent_movie_name) is False:
                trace(error_msg + "parent movie {!r}".format(self.parent_movie_name))
                return False

            self._correct_record = True
            return True

        def hasCorrectRecord(self):
            return self._correct_record

    class MorphSettings(__Param):
        def __init__(self, record):
            self.anim_delay = MorphManager.getRecordValue(record, "AnimDelay", default=5) * 1000.0
            pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for record in records:
            morph_param = MorphManager.MorphParams(record)
            if morph_param.hasCorrectRecord() is False:
                continue
            MorphManager.s_morphs.append(morph_param)

        return True
    # ---

    @staticmethod
    def getAllMorphs():
        """ return list with registered MorphManager.Morph """
        return MorphManager.s_morphs

    @staticmethod
    def getMorphById(morph_id):
        """ return None or MorphManager.Morph (morph params) """
        found_morphs = filter(lambda morph: morph.id == morph_id, MorphManager.s_morphs)
        if len(found_morphs) == 0:
            return None
        return found_morphs[0]

    @staticmethod
    def getMorphByGroup(group_name):
        """ return list with found MorphManager.Morph (morph all params) """
        found_morphs = filter(lambda morph: morph.group_name == group_name, MorphManager.s_morphs)
        return found_morphs

    @staticmethod
    def getMorphSettings(morph_id):
        """ return None or MorphManager.MorphSettings (morph fx params) """
        morph = MorphManager.getMorphById(morph_id)
        if morph is not None:
            return morph.settings
        return None