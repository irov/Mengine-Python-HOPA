from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.TaskAlias import TaskAlias


class AliasRemoveItemAttach(MixinItem, TaskAlias):
    def _onParams(self, params):
        super(AliasRemoveItemAttach, self)._onParams(params)
        self.SiblingNode = None

    def _onCheck(self):
        if ArrowManager.emptyArrowAttach() is True:
            return False

        arrowItem = ArrowManager.getArrowAttach()

        if arrowItem is not self.Item:
            return False

        return True

    def _onGenerate(self, source):
        source.addTask("TaskRemoveArrowAttach")
        source.addTask("TaskFanItemInNone", FanItem=self.Item)
        source.addFunction(self._saveItemEntityNodeSibling)
        source.addTask("TaskObjectReturn", Object=self.Item)
        source.addFunction(self._returnItemNearSiblingNode)

    def _saveItemEntityNodeSibling(self):
        entity_node = self.Item.getEntityNode()

        if entity_node is None:
            return

        self.SiblingNode = entity_node.getSiblingNext()

    def _returnItemNearSiblingNode(self):
        if self.SiblingNode is None:
            return

        entity_node = self.Item.getEntityNode()
        if entity_node is None:
            return

        parent = self.Item.getParent()
        if parent is None:
            return

        parent_entity = parent.entity
        if parent_entity is None:
            return

        if self.SiblingNode.hasParent() is False:
            return

        sibling_parent = self.SiblingNode.getParent()
        if sibling_parent != parent_entity:
            entity_node.removeFromParent()
            sibling_parent.addChild(entity_node)
            sibling_parent.addChildAfter(entity_node, self.SiblingNode)
            return

        parent_entity.addChildAfter(entity_node, self.SiblingNode)
