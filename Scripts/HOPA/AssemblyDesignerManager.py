from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class AssemblyDesignerManager(Manager):
    s_params = {}

    class AssemblyDesignerParam(object):
        class __ItemParam(object):
            def __init__(self, item_id, item_type, movie_name_on_set, movie_name_on_shelf, shelf_id):
                self.item_id = item_id
                self.item_type = item_type
                self.movie_name_on_set = movie_name_on_set
                self.movie_name_on_shelf = movie_name_on_shelf
                self.shelf_id = shelf_id

        def __init__(self, enigma_name, shelves_params, item_types_params, finish_sets_params, carcass_movie_name, number_of_sets, number_of_shelves, start_shelf_id, start_set_id):
            self.enigma_name = enigma_name
            self.shelves_params = shelves_params
            self.start_shelf_id = start_shelf_id
            self.start_set_id = start_set_id
            self.finish_sets_params = finish_sets_params
            self.carcass_movie_name = carcass_movie_name
            self.number_of_sets = number_of_sets
            self.number_of_shelves = number_of_shelves

            self.items = {}

            self.__createItems(item_types_params, shelves_params)

        def __createItems(self, item_types_params, shelves_params):
            for item_id, (item_type, movie_name_on_set, movie_name_on_shelf) in item_types_params.iteritems():
                for shelf_id, (_, _, shelf_items) in shelves_params.iteritems():
                    if item_id not in shelf_items:
                        continue
                    self.items[item_id] = self.__ItemParam(item_id, item_type, movie_name_on_set, movie_name_on_shelf, shelf_id)

        def __testsParams(self):
            assert self.enigma_name is not None
            assert self.start_shelf_id is not None
            assert len(self.shelves_params) == self.number_of_shelves
            assert len(self.finish_sets_params) == self.number_of_sets

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            """
            EnigmaName	Shelfs	FinishSets	ItemTypes	CarcassMovieName	StartShelfID    NumberOfSets	NumberOfShelves
            """
            enigma_name = record.get('EnigmaName')
            shelves_db_name = record.get('Shelves')
            finish_sets_db_name = record.get('FinishSets')
            item_types_db_name = record.get('ItemTypes')
            carcass_movie_name = record.get('CarcassMovieName')
            start_shelf_id = record.get('StartShelfID')
            start_set_id = record.get('StartSetID')
            number_of_sets = record.get('NumberOfSets')
            number_of_shelves = record.get('NumberOfShelves')

            result = AssemblyDesignerManager.addParam(enigma_name, module, shelves_db_name, finish_sets_db_name, item_types_db_name, carcass_movie_name, number_of_sets, number_of_shelves, start_shelf_id, start_set_id)
            if result is False:
                error_msg = "ForestMazeManager invalid addParam {}".format(enigma_name)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(enigma_name, module, shelves_db_name, finish_sets_db_name, item_types_db_name, carcass_movie_name, number_of_sets, number_of_shelves, start_shelf_id, start_set_id):
        if enigma_name in AssemblyDesignerManager.s_params:
            error_msg = "AssemblyDesignerManager already have param for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Shelves ---------------------------------------------------------------------------------------

        records = DatabaseManager.getDatabaseRecords(module, shelves_db_name)
        shelves_params = {}

        if records is None:
            error_msg = "AssemblyDesignerManager cant find Shelves database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            """
            ShelfID	[Items]
            """
            shelf_id = record.get('ShelfID')
            movie_name = record.get('MovieName')
            number_of_places = record.get('NumberOfPlaces')
            items = record.get('Items')

            shelves_params[shelf_id] = (movie_name, number_of_places, items)

        # -------------- ItemTypes -------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(module, item_types_db_name)
        item_types_params = {}

        if records is None:
            error_msg = "AssemblyDesignerManager cant find Shelves database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            """
            ItemID	ItemType MovieNameOnSet	MovieNameOnShelf
            """
            item_id = record.get('ItemID')
            item_type = record.get('ItemType')
            movie_name_on_set = record.get('MovieNameOnSet')
            movie_name_on_shelf = record.get('MovieNameOnShelf')

            item_types_params[item_id] = (item_type, movie_name_on_set, movie_name_on_shelf)

        # -------------- FinishSets ------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(module, finish_sets_db_name)
        finish_sets_params = {}

        if records is None:
            error_msg = "AssemblyDesignerManager cant find Shelves database for {}".format(enigma_name)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            """
            SetID	Type1	Type2	Type3	Type4	Type6
            """
            set_id = record.pop('SetID')
            set_name_not_complete_text_id = record.pop('SetNameNotCompleteTextID')
            set_name_complete_text_id = record.pop('SetNameCompleteTextID')

            finish_sets_params[set_id] = (record, set_name_not_complete_text_id, set_name_complete_text_id)

        AssemblyDesignerManager.s_params[enigma_name] = AssemblyDesignerManager.AssemblyDesignerParam(enigma_name, shelves_params, item_types_params, finish_sets_params, carcass_movie_name, number_of_sets, number_of_shelves, start_shelf_id, start_set_id)

        return True

    @staticmethod
    def getParams(enigma_name):
        assembly_designer_param = AssemblyDesignerManager.s_params.get(enigma_name, None)
        if assembly_designer_param is None:
            Trace.log("Manager", 0, "AssemblyDesignerManager has not param for enigma {}".format(enigma_name))

        return assembly_designer_param