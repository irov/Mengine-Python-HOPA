from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class BoneHelpChainManager(object):
    s_chain = []

    class ChainState(object):
        def __init__(self, group, sub_group, movie, button, text):
            self.group = group
            self.sub_group = sub_group
            self.movie = movie
            self.button = button
            self.text = text
            pass

        def __get_object(self, objectName):
            if self.sub_group is not None:
                sub_object = GroupManager.getObject(self.group, self.sub_group)
                _object = sub_object.getObject(objectName)
                pass
            else:
                _object = GroupManager.getObject(self.group, objectName)
                pass
            return _object
            pass

        def getHelpObjects(self):
            movie = self.__get_object(self.movie)
            button = self.__get_object(self.button)
            text = self.__get_object(self.text)
            return (movie, button, text)
            pass

        def getMovieObject(self):
            movie = self.__get_object(self.movie)
            return movie
            pass

        def getTextObject(self):
            text = self.__get_object(self.text)
            return text
            pass

        def getButtonObject(self):
            button = self.__get_object(self.button)
            return button
            pass

    @staticmethod
    def onFinalize():
        BoneHelpChainManager.s_chain = []
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for values in records:
            movie = values.get("Movie")
            button = values.get("Button")
            text = values.get("Text")
            group = values.get("Group")
            sub_group = values.get("SubGroup")
            chain_state = BoneHelpChainManager.ChainState(group, sub_group, movie, button, text)
            BoneHelpChainManager.s_chain.append(chain_state)
            pass
        pass

    @staticmethod
    def getWholeChainAsObjects():
        whole_chain = [chain_state.getHelpObjects() for chain_state in BoneHelpChainManager.s_chain]
        return whole_chain
        pass

    @staticmethod
    def getChainMovies():
        whole_chain = [chain_state.getMovieObject() for chain_state in BoneHelpChainManager.s_chain]
        return whole_chain
        pass

    @staticmethod
    def getChainTexts():
        whole_chain = [chain_state.getTextObject() for chain_state in BoneHelpChainManager.s_chain]
        return whole_chain
        pass

    @staticmethod
    def getChainButtons():
        whole_chain = [chain_state.getButtonObject() for chain_state in BoneHelpChainManager.s_chain]
        return whole_chain
        pass