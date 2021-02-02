# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

if "bpy" in locals():
    import importlib
    if "bfu_write_text" in locals():
        importlib.reload(bfu_write_text)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_export_single_alembic_animation" in locals():
        importlib.reload(bfu_export_single_alembic_animation)
    if "bfu_export_single_fbx_action" in locals():
        importlib.reload(bfu_export_single_fbx_action)
    if "bfu_export_single_camera" in locals():
        importlib.reload(bfu_export_single_camera)
    if "bfu_export_single_fbx_nla_anim" in locals():
        importlib.reload(bfu_export_single_fbx_nla_anim)
    if "bfu_export_single_skeletal_mesh" in locals():
        importlib.reload(bfu_export_single_skeletal_mesh)
    if "bfu_export_single_static_mesh" in locals():
        importlib.reload(bfu_export_single_static_mesh)
    if "bfu_export_single_static_mesh_collection" in locals():
        importlib.reload(bfu_export_single_static_mesh_collection)

import bpy
import time
import math

import addon_utils

from . import bfu_write_text
from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from .bfu_utils import *
from . import bfu_export_single_alembic_animation
from .bfu_export_single_alembic_animation import *

from . import bfu_export_single_fbx_action
from .bfu_export_single_fbx_action import *

from . import bfu_export_single_camera
from .bfu_export_single_camera import *

from . import bfu_export_single_fbx_nla_anim
from .bfu_export_single_fbx_nla_anim import *

from . import bfu_export_single_skeletal_mesh
from .bfu_export_single_skeletal_mesh import *

from . import bfu_export_single_static_mesh
from .bfu_export_single_static_mesh import *

from . import bfu_export_single_static_mesh_collection
from .bfu_export_single_static_mesh_collection import *


class ExportSigleObjects():

    def SaveDataForSigneExport():
        pass

    def ResetDataAfterSigneExport():
        pass


def IsValidActionForExport(scene, obj, animType):
    if animType == "Action":
        if scene.anin_export:
            if obj.bfu_export_procedure == 'auto-rig-pro':
                if CheckPluginIsActivated('auto_rig_pro-master'):
                    return True
            else:
                return True
        else:
            False
    elif animType == "Pose":
        if scene.anin_export:
            if obj.bfu_export_procedure == 'auto-rig-pro':
                if CheckPluginIsActivated('auto_rig_pro-master'):
                    return True
            else:
                return True
        else:
            False
    elif animType == "NLA":
        if scene.anin_export:
            if obj.bfu_export_procedure == 'auto-rig-pro':
                return False
            else:
                return True
        else:
            False
    else:
        print("Error in IsValidActionForExport() animType not found: ", animType)
    return False


def IsValidObjectForExport(scene, obj):
    objType = GetAssetType(obj)

    if objType == "Camera":
        return scene.camera_export
    if objType == "StaticMesh":
        return scene.static_export
    if objType == "SkeletalMesh":
        if scene.skeletal_export:
            if obj.bfu_export_procedure == 'auto-rig-pro':
                if CheckPluginIsActivated('auto_rig_pro-master'):
                    return True
            else:
                return True
        else:
            False
    if objType == "Alembic":
        return scene.alembic_export

    return False


def ExportAllAssetByList(targetobjects, targetActionName, targetcollection):
    # Export all objects that need to be exported from a list

    if len(targetobjects) < 1 and len(targetcollection) < 1:
        return

    scene = bpy.context.scene
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    counter = CounterTimer()

    NumberAssetToExport = len(GetFinalAssetToExport())

    def UpdateProgress(time=None):
        update_progress(
            "Export assets",
            len(scene.UnrealExportedAssetsList)/NumberAssetToExport,
            time
        )
    UpdateProgress()

    # Export collections
    if scene.static_collection_export:
        for col in GetCollectionToExport(scene):
            if col in targetcollection:
                # StaticMesh collection
                ExportSingleStaticMeshCollection(
                    scene,
                    GetCollectionExportDir(),
                    GetCollectionExportFileName(col),
                    col
                )
                UpdateProgress()

    # Export assets
    for obj in targetobjects:
        if obj.ExportEnum == "export_recursive":

            # Camera
            if GetAssetType(obj) == "Camera" and IsValidObjectForExport(scene, obj):
                # Save current start/end frame
                UserStartFrame = scene.frame_start
                UserEndFrame = scene.frame_end
                ProcessCameraExport(obj)

                # Resets previous start/end frame
                scene.frame_start = UserStartFrame
                scene.frame_end = UserEndFrame
                UpdateProgress()

            # StaticMesh
            if GetAssetType(obj) == "StaticMesh" and IsValidObjectForExport(scene, obj):
                ExportSingleStaticMesh(
                    scene,
                    GetObjExportDir(obj),
                    GetObjExportFileName(obj),
                    obj
                    )
                if obj.ExportAsLod is False:
                    if (scene.text_AdditionalData and
                            addon_prefs.useGeneratedScripts):
                        ExportSingleAdditionalParameterMesh(
                            GetObjExportDir(obj),
                            GetObjExportFileName(
                                obj,
                                "_AdditionalParameter.ini"
                                ),
                            obj
                            )
                UpdateProgress()

            # SkeletalMesh
            if GetAssetType(obj) == "SkeletalMesh" and IsValidObjectForExport(scene, obj):
                ExportSingleSkeletalMesh(
                    scene,
                    GetObjExportDir(obj),
                    GetObjExportFileName(obj),
                    obj
                    )

                if (scene.text_AdditionalData and
                        addon_prefs.useGeneratedScripts):

                    ExportSingleAdditionalParameterMesh(
                        GetObjExportDir(obj),
                        GetObjExportFileName(obj, "_AdditionalParameter.ini"),
                        obj
                        )
                UpdateProgress()

            # Alembic
            if GetAssetType(obj) == "Alembic" and IsValidObjectForExport(scene, obj):
                ExportSingleAlembicAnimation(
                    scene,
                    GetObjExportDir(obj),
                    GetObjExportFileName(obj, ".abc"),
                    obj
                    )
                UpdateProgress()

            # Action animation
            if GetAssetType(obj) == "SkeletalMesh" and obj.visible_get():
                animExportDir = os.path.join(
                    GetObjExportDir(obj),
                    scene.anim_subfolder_name
                    )
                for action in GetActionToExport(obj):
                    if action.name in targetActionName:
                        animType = GetActionType(action)

                        # Action
                        if animType == "Action" and IsValidActionForExport(scene, obj, animType):
                            # Save current start/end frame
                            UserStartFrame = scene.frame_start
                            UserEndFrame = scene.frame_end
                            ExportSingleFbxAction(
                                scene,
                                animExportDir,
                                GetActionExportFileName(obj, action),
                                obj,
                                action,
                                "Action"
                                )
                            # Resets previous start/end frame
                            scene.frame_start = UserStartFrame
                            scene.frame_end = UserEndFrame
                            UpdateProgress()

                        # pose
                        if animType == "Pose" and IsValidActionForExport(scene, obj, animType):
                            # Save current start/end frame
                            UserStartFrame = scene.frame_start
                            UserEndFrame = scene.frame_end
                            ExportSingleFbxAction(
                                scene,
                                animExportDir,
                                GetActionExportFileName(obj, action),
                                obj,
                                action,
                                "Pose"
                                )
                            # Resets previous start/end frame
                            scene.frame_start = UserStartFrame
                            scene.frame_end = UserEndFrame
                            UpdateProgress()

                # NLA animation
                if IsValidActionForExport(scene, obj, "NLA"):
                    if obj.ExportNLA:
                        scene.frame_end += 1
                        ExportSingleFbxNLAAnim(
                            scene,
                            animExportDir,
                            GetNLAExportFileName(obj),
                            obj
                            )
                        scene.frame_end -= 1

    UpdateProgress(counter.GetTime())


def ExportForUnrealEngine():
    scene = bpy.context.scene
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    MoveToGlobalView()

    MyCurrentDataSave = UserSceneSave()
    MyCurrentDataSave.SaveCurrentScene()

    for object in bpy.data.objects:
        if object.hide_select:
            object.hide_select = False
        if object.hide_viewport:
            object.hide_viewport = False

    for col in bpy.data.collections:
        if col.hide_select:
            col.hide_select = False
        if col.hide_viewport:
            col.hide_viewport = False

    for vlayer in bpy.context.scene.view_layers:
        for childCol in vlayer.layer_collection.children:
            if childCol.exclude:
                childCol.exclude = False
            if childCol.hide_viewport:
                childCol.hide_viewport = False

    SafeModeSet(MyCurrentDataSave.user_active, 'OBJECT')

    if addon_prefs.revertExportPath:
        RemoveFolderTree(bpy.path.abspath(scene.export_static_file_path))
        RemoveFolderTree(bpy.path.abspath(scene.export_skeletal_file_path))
        RemoveFolderTree(bpy.path.abspath(scene.export_alembic_file_path))
        RemoveFolderTree(bpy.path.abspath(scene.export_camera_file_path))
        RemoveFolderTree(bpy.path.abspath(scene.export_other_file_path))

    assetList = []  # Do a simple lit of objects to export
    for Asset in GetFinalAssetToExport():
        if Asset.obj in GetAllobjectsByExportType("export_recursive"):
            if Asset.obj not in assetList:
                assetList.append(Asset.obj)

    ExportAllAssetByList(
        targetobjects=assetList,
        targetActionName=MyCurrentDataSave.action_names,
        targetcollection=MyCurrentDataSave.collection_names,
    )

    MyCurrentDataSave.ResetSelectByName()
    MyCurrentDataSave.ResetSceneAtSave()

    # Clean actions
    for action in bpy.data.actions:
        if action.name not in MyCurrentDataSave.action_names:
            bpy.data.actions.remove(action)
