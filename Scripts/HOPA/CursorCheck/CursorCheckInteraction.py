from Foundation.ArrowCursorCheck import ArrowCursorCheck


class CursorCheckInteraction(ArrowCursorCheck):
    def _onCheck(self, obj, Params):
        if "InteractionName" not in Params:
            return False

        return obj.name == Params["InteractionName"]
