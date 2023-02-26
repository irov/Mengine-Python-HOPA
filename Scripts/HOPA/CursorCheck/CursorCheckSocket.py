from Foundation.ArrowCursorCheck import ArrowCursorCheck

class CursorCheckSocket(ArrowCursorCheck):
    def _onCheck(self, obj, Params):
        if "SocketName" not in Params:
            return False

        return obj.name == Params["SocketName"]