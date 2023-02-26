from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager

from ExtrasManager import ExtrasManager

class Extras(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addActionActivate(Type, "CurrentLayer", Update=Extras._updateLayers)
        Type.addAction(Type, "OpenedExtraNames", Append=Extras._appendNextExtra)
        pass

    def __init__(self):
        super(Extras, self).__init__()
        self.extras = {}
        pass

    def _appendNextExtra(self, id, extraName):
        # print ("Append new extra -->", extraName)
        # print ("Append new extra id -->", id)
        pass

    def _updateLayers(self, newLayer):
        if newLayer is None:
            return
            pass
        pass

    def _onPreparation(self):
        super(Extras, self)._onPreparation()
        self.extras = ExtrasManager.getExtras()
        pass

    def _onActivate(self):
        extrasCount = len(self.extras)
        extras = self.extras.itervalues()
        extrasKeys = self.extras.iterkeys()

        TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName=self.CurrentLayer, Value=True)

        with TaskManager.createTaskChain(Name="Extras", Group=self.object, Repeat=True) as tc:
            with tc.addRaceTask(extrasCount) as (tc_buttons):
                for tc_button, name, extra in zip(tc_buttons, extrasKeys, extras):
                    buttonName = extra.getButtonName()
                    layerName = extra.getGroupName()
                    objectName = extra.getObjectName()
                    entityType = extra.getEntityType()

                    tc_button.addTask("TaskButtonClick", ButtonName=buttonName)
                    tc_button.addTask("TaskScope", Scope=self.update, Args=(layerName, objectName, entityType, name))
                    pass
                pass
            pass
        pass

    def update(self, scope, groupName, objectName, entityType, name):
        if entityType == "Enigma":
            entityObject = GroupManager.getObject(groupName, objectName)

            scope.addTask("TaskSetParam", Object=entityObject, Param="EntityName", Value=name)
            pass

        if self.CurrentLayer != groupName:
            scope.addTask("TaskSceneLayerGroupEnable", LayerName=self.CurrentLayer, Value=False)
            scope.addTask("TaskSceneLayerGroupEnable", LayerName=groupName, Value=True)
            scope.addTask("TaskSetParam", Object=self.object, Param="CurrentLayer", Value=groupName)
            pass
        pass

    def _onDeactivate(self):
        if TaskManager.existTaskChain("Extras"):
            TaskManager.cancelTaskChain("Extras")
            pass

        self.extras = {}
        pass
    pass