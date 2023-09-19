from HOPA.ChangeScreenOnClickManager import BoardCell


class Cell(object):
    def __init__(self):
        self.type = None
        self.params = None
        self.env = None

    def setup(self, value):
        simple_types = [BoardCell.Passage, BoardCell.Wall, BoardCell.Start, BoardCell.Finish]

        for simple_type in simple_types:
            if value == simple_type:
                self.type = simple_type
                self.params = None
                return True

        for gate_type in [BoardCell.Gate, BoardCell.Lever]:
            if value[0] == gate_type:
                self.type = gate_type
                target_number = value[1:]
                self.params = {"target": int(target_number)}
                return True

        Trace.log("Entity", 0, "ChangeScreenOnClick unknown cell type {!r}".format(value))

        self.type = BoardCell.Wall
        self.params = None
        return False

    def equalTo(self, board_type):
        return self.type == board_type

    def isEmpty(self):
        return self.type is None

    def __repr__(self):
        return str(self.type)
