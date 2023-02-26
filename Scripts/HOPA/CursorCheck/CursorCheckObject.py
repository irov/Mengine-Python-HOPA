from Foundation.ArrowCursorCheck import ArrowCursorCheck

class CursorCheckObject(ArrowCursorCheck):
    def _onCheck(self, obj, Params):
        if "Object" not in Params:
            return False

        return obj == Params["Object"]