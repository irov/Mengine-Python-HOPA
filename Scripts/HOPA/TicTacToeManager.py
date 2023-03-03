from Foundation.DatabaseManager import DatabaseManager


class TicTacToeManager(object):
    players_params = {}

    class TicTacToeParams:
        def __init__(self, player_id, player_name):
            self.player_id = player_id
            self.player_name = player_name

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            player_id = record.get("PlayerID")
            player_name = record.get("PlayerName")

            TicTacToeManager.players_params[player_id] = TicTacToeManager.TicTacToeParams(player_id, player_name)

        return True

    @staticmethod
    def getPlayersParams():
        return TicTacToeManager.players_params

    @staticmethod
    def getPlayerParams(player_id):
        if player_id not in ['X', 'O']:
            Trace.log("Manager", 0, "[TicTacToe Manager] {} is not in ['X', 'O']".format(player_id))
            return

        return TicTacToeManager.players_params[player_id]
