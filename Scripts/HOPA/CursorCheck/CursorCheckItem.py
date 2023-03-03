from Foundation.ArrowCursorCheck import ArrowCursorCheck


class CursorCheckItem(ArrowCursorCheck):
    def _onCheck(self, obj, Params):
        if "ItemName" not in Params:
            return False

        return obj.name == Params.get("ItemName")
