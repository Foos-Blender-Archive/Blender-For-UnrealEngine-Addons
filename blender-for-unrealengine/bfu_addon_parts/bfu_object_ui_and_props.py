# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import os
import bpy
import addon_utils
from . import bfu_modular_skeletal_specified_parts_meshs
from .. import bbpl
from .. import bpl
from .. import bfu_export_procedure
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_cached_asset_list
from .. import bfu_export
from .. import bfu_ui
from .. import languages
from .. import bfu_custom_property
from .. import bfu_base_object
from .. import bfu_adv_object
from .. import bfu_base_collection
from .. import bfu_material
from .. import bfu_camera
from .. import bfu_spline
from .. import bfu_vertex_color
from .. import bfu_static_mesh
from .. import bfu_skeletal_mesh
from .. import bfu_lod
from .. import bfu_alembic_animation
from .. import bfu_anim_base
from .. import bfu_anim_action
from .. import bfu_anim_action_adv
from .. import bfu_anim_nla
from .. import bfu_anim_nla_adv
from .. import bfu_groom
from .. import bfu_assets_manager
from .. import bfu_uv_map
from .. import bfu_light_map
from .. import bfu_assets_references
from .. import bfu_collision


class BFU_PT_BlenderForUnrealObject(bpy.types.Panel):
    # Unreal engine export panel

    bl_idname = "BFU_PT_BlenderForUnrealObject"
    bl_label = "Unreal Engine Assets Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"


    bpy.types.Object.bfu_export_global_scale = bpy.props.FloatProperty(
        name="Global scale",
        description="Scale, change is not recommended with SkeletalMesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default=1.0
        )

    bpy.types.Object.bfu_override_procedure_preset = bpy.props.BoolProperty(
        name="Override Export Preset",
        description="If true override the export precedure preset.",
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )

    bpy.types.Object.bfu_export_use_space_transform = bpy.props.BoolProperty(
        name="Use Space Transform",
        default=True,
        )

    bpy.types.Object.bfu_export_axis_forward = bpy.props.EnumProperty(
        name="Axis Forward",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('X', "X Forward", ""),
            ('Y', "Y Forward", ""),
            ('Z', "Z Forward", ""),
            ('-X', "-X Forward", ""),
            ('-Y', "-Y Forward", ""),
            ('-Z', "-Z Forward", ""),
            ],
        default='-Z',
        )

    bpy.types.Object.bfu_export_axis_up = bpy.props.EnumProperty(
        name="Axis Up",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('X', "X Up", ""),
            ('Y', "Y Up", ""),
            ('Z', "Z Up", ""),
            ('-X', "-X Up", ""),
            ('-Y', "-Y Up", ""),
            ('-Z', "-Z Up", ""),
            ],
        default='Y',
        )

    bpy.types.Object.bfu_export_primary_bone_axis = bpy.props.EnumProperty(
        name="Primary Axis Bone",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", ""),
            ],
        default='Y',
        )

    bpy.types.Object.bfu_export_secondary_bone_axis = bpy.props.EnumProperty(
        name="Secondary Axis Bone",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", ""),
            ],
        default='X',
        )

    bpy.types.Object.bfu_export_animation_without_mesh = bpy.props.BoolProperty(
        name="Export animation without mesh",
        description=(
            "If checked, When exporting animation, do not include mesh data in the FBX file."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_mirror_symmetry_right_side_bones = bpy.props.BoolProperty(
        name="Revert direction of symmetry right side bones",
        description=(
            "If checked, The right-side bones will be mirrored for mirroring physic object in UE PhysicAsset Editor."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_use_ue_mannequin_bone_alignment = bpy.props.BoolProperty(
        name="Apply bone alignments similar to UE Mannequin.",
        description=(
            "If checked, similar to the UE Mannequin, the leg bones will be oriented upwards, and the pelvis and feet bone will be aligned facing upwards during export."
        ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
    )

    bpy.types.Object.bfu_move_to_center_for_export = bpy.props.BoolProperty(
        name="Move to center",
        description=(
            "If true use object origin else use scene origin." +
            " | If true the mesh will be moved to the center" +
            " of the scene for export." +
            " (This is used so that the origin of the fbx file" +
            " is the same as the mesh in blender)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_rotate_to_zero_for_export = bpy.props.BoolProperty(
        name="Rotate to zero",
        description=(
            "If true use object rotation else use scene rotation." +
            " | If true the mesh will use zero rotation for export."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )





    bpy.types.Object.bfu_additional_location_for_export = bpy.props.FloatVectorProperty(
        name="Additional location",
        description=(
            "This will add a additional absolute location to the mesh"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        subtype="TRANSLATION",
        default=(0, 0, 0)
        )

    bpy.types.Object.bfu_additional_rotation_for_export = bpy.props.FloatVectorProperty(
        name="Additional rotation",
        description=(
            "This will add a additional absolute rotation to the mesh"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        subtype="EULER",
        default=(0, 0, 0)
        )

    # Scene and global



    class BFU_OT_OpenDocumentationPage(bpy.types.Operator):
        bl_label = "Documentation"
        bl_idname = "object.bfu_open_documentation_page"
        bl_description = "Clic for open documentation page on GitHub"

        def execute(self, context):
            os.system(
                "start \"\" " +
                "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki"
                )
            return {'FINISHED'}



    # Animation :

    class BFU_UL_ActionExportTarget(bpy.types.UIList):
        def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
            action_is_valid = False
            if item.name in bpy.data.actions:
                action_is_valid = True

            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                if action_is_valid:  # If action is valid
                    layout.prop(
                        bpy.data.actions[item.name],
                        "name",
                        text="",
                        emboss=False,
                        icon="ACTION"
                    )
                    layout.prop(item, "use", text="")
                else:
                    dataText = (
                        'Action data named "' + item.name +
                        '" Not Found. Please click on update'
                    )
                    layout.label(text=dataText, icon="ERROR")
            # Not optimized for 'GRID' layout type.
            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
                layout.label(text="", icon_value=icon)

    class BFU_OT_UpdateObjActionListButton(bpy.types.Operator):
        bl_label = "Update action list"
        bl_idname = "object.updateobjactionlist"
        bl_description = "Update action list"

        def execute(self, context):
            def UpdateExportActionList(obj):
                # Update the provisional action list known by the object

                def SetUseFromLast(anim_list, ActionName):
                    for item in anim_list:
                        if item[0] == ActionName:
                            if item[1]:
                                return True
                    return False

                animSave = [["", False]]
                for Anim in obj.bfu_action_asset_list:  # CollectionProperty
                    name = Anim.name
                    use = Anim.use
                    animSave.append([name, use])
                obj.bfu_action_asset_list.clear()
                for action in bpy.data.actions:
                    obj.bfu_action_asset_list.add().name = action.name
                    useFromLast = SetUseFromLast(animSave, action.name)
                    obj.bfu_action_asset_list[action.name].use = useFromLast
            UpdateExportActionList(bpy.context.object)
            return {'FINISHED'}

    class BFU_OT_ShowActionToExport(bpy.types.Operator):
        bl_label = "Show action(s)"
        bl_idname = "object.showobjaction"
        bl_description = (
            "Click to show actions that are" +
            " to be exported with this armature."
            )

        def execute(self, context):
            obj = context.object
            animation_asset_cache = bfu_cached_asset_list.GetAnimationAssetCache(obj)
            animation_asset_cache.UpdateActionCache()
            animation_to_export = animation_asset_cache.GetAnimationAssetList()

            popup_title = "Action list"
            if len(animation_to_export) > 0:
                animationNumber = len(animation_to_export)
                if obj.bfu_anim_nla_use:
                    animationNumber += 1
                popup_title = (
                    str(animationNumber) +
                    ' action(s) found for obj named "'+obj.name+'".'
                    )
            else:
                popup_title = (
                    'No action found for obj named "' +
                    obj.name+'".')

            def draw(self, context: bpy.types.Context):
                col = self.layout.column()

                def addAnimRow(
                        action_name,
                        action_type,
                        frame_start,
                        frame_end):
                    row = col.row()
                    row.label(
                        text="- ["+action_name +
                        "] Frame "+frame_start+" to "+frame_end +
                        " ("+action_type+")"
                        )

                for action in animation_to_export:
                    Frames = bfu_utils.GetDesiredActionStartEndTime(obj, action)
                    frame_start = str(Frames[0])
                    frame_end = str(Frames[1])
                    addAnimRow(action.name, bfu_utils.GetActionType(action), frame_start, frame_end)
                if obj.bfu_anim_nla_use:
                    scene = context.scene
                    addAnimRow(obj.bfu_anim_nla_export_name, "NlAnim", str(scene.frame_start), str(scene.frame_end))

            bpy.context.window_manager.popup_menu(
                draw,
                title=popup_title,
                icon='ACTION'
                )
            return {'FINISHED'}

    class BFU_MT_ObjectGlobalPropertiesPresets(bpy.types.Menu):
        bl_label = 'Global Properties Presets'
        preset_subdir = 'blender-for-unrealengine/global-properties-presets'
        preset_operator = 'script.execute_preset'
        draw = bpy.types.Menu.draw_preset

    from bl_operators.presets import AddPresetBase



    class BFU_OT_AddObjectGlobalPropertiesPreset(AddPresetBase, bpy.types.Operator):
        bl_idname = 'object.add_globalproperties_preset'
        bl_label = 'Add or remove a preset for Global properties'
        bl_description = 'Add or remove a preset for Global properties'
        preset_menu = 'BFU_MT_ObjectGlobalPropertiesPresets'

        def get_object_global_preset_propertys():
            preset_values = [
                'obj.bfu_export_global_scale',
                'obj.bfu_override_procedure_preset',
                'obj.bfu_export_use_space_transform',
                'obj.bfu_export_axis_forward',
                'obj.bfu_export_axis_up',
                'obj.bfu_export_with_meta_data',
                'obj.bfu_export_axis_forward',
                'obj.bfu_export_axis_up',
                'obj.bfu_export_primary_bone_axis',
                'obj.bfu_export_secondary_bone_axis',
                'obj.bfu_export_animation_without_mesh',
                'obj.bfu_mirror_symmetry_right_side_bones',
                'obj.bfu_use_ue_mannequin_bone_alignment',
                'obj.bfu_disable_free_scale_animation',
                'obj.bfu_move_to_center_for_export',
                'obj.bfu_rotate_to_zero_for_export',
                'obj.bfu_additional_location_for_export',
                'obj.bfu_additional_rotation_for_export',
                ]
            preset_values += bfu_base_object.bfu_base_obj_props.get_preset_values()
            preset_values += bfu_adv_object.bfu_adv_obj_props.get_preset_values()
            preset_values += bfu_base_collection.bfu_base_col_props.get_preset_values()
            preset_values += bfu_modular_skeletal_specified_parts_meshs.get_preset_values()
            preset_values += bfu_custom_property.bfu_custom_property_props.get_preset_values()
            preset_values += bfu_material.bfu_material_props.get_preset_values()
            preset_values += bfu_camera.bfu_camera_ui_and_props.get_preset_values()
            preset_values += bfu_spline.bfu_spline_ui_and_props.get_preset_values()
            preset_values += bfu_static_mesh.bfu_static_mesh_props.get_preset_values()
            preset_values += bfu_skeletal_mesh.bfu_skeletal_mesh_props.get_preset_values()
            preset_values += bfu_alembic_animation.bfu_alembic_animation_props.get_preset_values()
            preset_values += bfu_anim_base.bfu_anim_base_props.get_preset_values()
            preset_values += bfu_anim_action.bfu_anim_action_props.get_preset_values()
            preset_values += bfu_anim_action_adv.bfu_anim_action_adv_props.get_preset_values()
            preset_values += bfu_anim_nla.bfu_anim_nla_props.get_preset_values()
            preset_values += bfu_anim_nla_adv.bfu_anim_nla_adv_props.get_preset_values()
            preset_values += bfu_vertex_color.bfu_vertex_color_props.get_preset_values()
            preset_values += bfu_lod.bfu_lod_props.get_preset_values()
            preset_values += bfu_uv_map.bfu_uv_map_props.get_preset_values()
            preset_values += bfu_light_map.bfu_light_map_props.get_preset_values()
            preset_values += bfu_assets_references.bfu_asset_ref_props.get_preset_values()
            preset_values += bfu_collision.bfu_collision_ui_and_props.get_preset_values()
            return preset_values

        # Common variable used for all preset values
        preset_defines = [
                            'obj = bpy.context.object',
                            'col = bpy.context.collection',
                            'scene = bpy.context.scene'
                         ]

        # Properties to store in the preset
        preset_values = get_object_global_preset_propertys()

        # Directory to store the presets
        preset_subdir = 'blender-for-unrealengine/global-properties-presets'



    class BFU_UL_CollectionExportTarget(bpy.types.UIList):

        def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):

            collection_is_valid = False
            if item.name in bpy.data.collections:
                collection_is_valid = True

            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                if collection_is_valid:  # If action is valid
                    layout.prop(
                        bpy.data.collections[item.name],
                        "name",
                        text="",
                        emboss=False,
                        icon="OUTLINER_COLLECTION")
                    layout.prop(item, "use", text="")
                else:
                    dataText = (
                        'Collection named "' +
                        item.name +
                        '" Not Found. Please clic on update')
                    layout.label(text=dataText, icon="ERROR")
            # Not optimised for 'GRID' layout type.
            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
                layout.label(text="", icon_value=icon)

    class BFU_OT_UpdateCollectionButton(bpy.types.Operator):
        bl_label = "Update collection list"
        bl_idname = "object.updatecollectionlist"
        bl_description = "Update collection list"

        def execute(self, context):
            def UpdateExportCollectionList(scene):
                # Update the provisional collection list known by the object

                def SetUseFromLast(col_list, CollectionName):
                    for item in col_list:
                        if item[0] == CollectionName:
                            if item[1]:
                                return True
                    return False

                colSave = [["", False]]
                for col in scene.bfu_collection_asset_list:  # CollectionProperty
                    name = col.name
                    use = col.use
                    colSave.append([name, use])
                scene.bfu_collection_asset_list.clear()
                for col in bpy.data.collections:
                    scene.bfu_collection_asset_list.add().name = col.name
                    useFromLast = SetUseFromLast(colSave, col.name)
                    scene.bfu_collection_asset_list[col.name].use = useFromLast
            UpdateExportCollectionList(context.scene)
            return {'FINISHED'}

    class BFU_OT_ShowCollectionToExport(bpy.types.Operator):
        bl_label = "Show collection(s)"
        bl_idname = "object.showscenecollection"
        bl_description = "Click to show collections to export"

        def execute(self, context):
            scene = context.scene
            collection_asset_cache = bfu_cached_asset_list.GetCollectionAssetCache()
            collection_export_asset_list = collection_asset_cache.GetCollectionAssetList()
            popup_title = "Collection list"
            if len(collection_export_asset_list) > 0:
                popup_title = (
                    str(len(collection_export_asset_list))+' collection(s) to export found.')
            else:
                popup_title = 'No collection to export found.'

            def draw(self, context: bpy.types.Context):
                col = self.layout.column()
                for collection in collection_export_asset_list:
                    row = col.row()
                    row.label(text="- "+collection.name)
            bpy.context.window_manager.popup_menu(
                draw,
                title=popup_title,
                icon='GROUP')
            return {'FINISHED'}

    def draw(self, context: bpy.types.Context):
        
        scene = bpy.context.scene
        obj = bpy.context.object
        addon_prefs = bfu_basics.GetAddonPrefs()
        layout = self.layout
        
        if bpy.app.version >= (4, 2, 0):
            version_str = 'Version '+ str(bbpl.blender_extension.extension_utils.get_package_version())
        else:
            version_str = 'Version '+ bbpl.blender_addon.addon_utils.get_addon_version_str("Unreal Engine Assets Exporter")

        credit_box = layout.box()
        credit_box.label(text=languages.ti('intro'))
        credit_box.label(text=version_str)
        credit_box.operator("object.bfu_open_documentation_page", icon="HELP")

        row = layout.row(align=True)
        row.menu(
            'BFU_MT_ObjectGlobalPropertiesPresets',
            text='Global Properties Presets'
            )
        row.operator(
            'object.add_globalproperties_preset',
            text='',
            icon='ADD'
            )
        row.operator(
            'object.add_globalproperties_preset',
            text='',
            icon='REMOVE'
            ).remove_active = True

        layout.row().prop(scene, "bfu_active_tab", expand=True)
        if scene.bfu_active_tab == "OBJECT":
            layout.row().prop(scene, "bfu_active_object_tab", expand=True)
        if scene.bfu_active_tab == "SCENE":
            layout.row().prop(scene, "bfu_active_scene_tab", expand=True)

        bfu_material.bfu_material_ui.draw_ui_object_collision(layout)
        bfu_vertex_color.bfu_vertex_color_ui.draw_ui_object_collision(layout)


        if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
            
            scene.bfu_object_properties_expanded.draw(layout)
            if scene.bfu_object_properties_expanded.is_expend():

                if obj is None:
                    layout.row().label(text='No selected object.')
                else:

                    AssetType = layout.row()
                    AssetType.prop(obj, 'name', text="", icon='OBJECT_DATA')
                    # Show asset type
                    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_asset_class(obj)
                    if asset_class:
                        asset_type_name = asset_class.get_asset_type_name(obj)
                    else:
                        asset_type_name = "Asset type not found."

                    AssetType.label(text='('+asset_type_name+')')

                    ExportType = layout.column()
                    ExportType.prop(obj, 'bfu_export_type')


                    if obj.bfu_export_type == "export_recursive":

                        folderNameProperty = layout.column()
                        folderNameProperty.prop(obj, 'bfu_export_folder_name', icon='FILE_FOLDER')

                        ProxyProp = layout.column()
                        if bfu_utils.GetExportAsProxy(obj):
                            ProxyProp.label(text="The Armature was detected as a proxy.")
                            proxy_child = bfu_utils.GetExportProxyChild(obj)
                            if proxy_child:
                                ProxyProp.label(text="Proxy child: " + proxy_child.name)
                            else:
                                ProxyProp.label(text="Proxy child not found")

                        if not bfu_utils.GetExportAsProxy(obj):
                            # exportCustomName
                            exportCustomName = layout.row()
                            exportCustomName.prop(obj, "bfu_use_custom_export_name")
                            useCustomName = obj.bfu_use_custom_export_name
                            exportCustomNameText = exportCustomName.column()
                            exportCustomNameText.prop(obj, "bfu_custom_export_name")
                            exportCustomNameText.enabled = useCustomName
                    bfu_alembic_animation.bfu_alembic_animation_ui.draw_general_ui_object(layout, obj)
                    bfu_groom.bfu_groom_ui.draw_general_ui_object(layout, obj)
                    bfu_skeletal_mesh.bfu_skeletal_mesh_ui.draw_general_ui_object(layout, obj)




            


            bfu_alembic_animation.bfu_alembic_animation_ui.draw_ui_object(layout, obj)
            bfu_groom.bfu_groom_ui.draw_ui_object(layout, obj)

            scene.bfu_object_advanced_properties_expanded.draw(layout)
            if scene.bfu_object_advanced_properties_expanded.is_expend():
                if obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        transformProp = layout.column()
                        is_not_alembic_animation = not bfu_alembic_animation.bfu_alembic_animation_utils.is_alembic_animation(obj)
                        is_not_camera = not bfu_camera.bfu_camera_utils.is_camera(obj)
                        if is_not_alembic_animation and is_not_camera:
                            transformProp.prop(obj, "bfu_move_to_center_for_export")
                            transformProp.prop(obj, "bfu_rotate_to_zero_for_export")
                            transformProp.prop(obj, "bfu_additional_location_for_export")
                            transformProp.prop(obj, "bfu_additional_rotation_for_export")
                            
                        transformProp.prop(obj, 'bfu_export_global_scale')
                        if bfu_camera.bfu_camera_utils.is_camera(obj):
                            transformProp.prop(obj, "bfu_additional_location_for_export")

                        AxisProperty = layout.column()
                        
                        AxisProperty.prop(obj, 'bfu_override_procedure_preset')
                        if obj.bfu_override_procedure_preset:
                            AxisProperty.prop(obj, 'bfu_export_use_space_transform')
                            AxisProperty.prop(obj, 'bfu_export_axis_forward')
                            AxisProperty.prop(obj, 'bfu_export_axis_up')
                            bbpl.blender_layout.layout_doc_button.add_doc_page_operator(AxisProperty, text="About axis Transforms", url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Axis-Transforms")
                            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                                BoneAxisProperty = layout.column()
                                BoneAxisProperty.prop(obj, 'bfu_export_primary_bone_axis')
                                BoneAxisProperty.prop(obj, 'bfu_export_secondary_bone_axis')
                        else:
                            box = layout.box()
                            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                                preset = bfu_export_procedure.bfu_skeleton_export_procedure.get_obj_skeleton_procedure_preset(obj)
                            else:
                                preset = bfu_export_procedure.bfu_static_export_procedure.get_obj_static_procedure_preset(obj)
                            var_lines = box.column()
                            for key, value in preset.items():
                                display_key = bpl.utils.format_property_name(key)
                                var_lines.label(text=f"{display_key}: {value}\n")
                        export_data = layout.column()
                        bfu_custom_property.bfu_custom_property_utils.draw_ui_custom_property(export_data, obj)
                        export_data.prop(obj, "bfu_export_with_meta_data")

                            
                else:
                    layout.label(text='(No properties to show.)')


        if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
            if obj is not None:
                if obj.bfu_export_type == "export_recursive" and not obj.bfu_export_as_lod_mesh:

                    scene.bfu_animation_action_properties_expanded.draw(layout)
                    if scene.bfu_animation_action_properties_expanded.is_expend():
                        if (bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj) or
                                bfu_camera.bfu_camera_utils.is_camera(obj) or
                                bfu_alembic_animation.bfu_alembic_animation_utils.is_alembic_animation(obj)):

                            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                                # Action list
                                ActionListProperty = layout.column()
                                ActionListProperty.prop(obj, 'bfu_anim_action_export_enum')
                                if obj.bfu_anim_action_export_enum == "export_specific_list":
                                    ActionListProperty.template_list(
                                        # type and unique id
                                        "BFU_UL_ActionExportTarget", "",
                                        # pointer to the CollectionProperty
                                        obj, "bfu_action_asset_list",
                                        # pointer to the active identifier
                                        obj, "bfu_active_action_asset_list",
                                        maxrows=5,
                                        rows=5
                                    )
                                    ActionListProperty.operator(
                                        "object.updateobjactionlist",
                                        icon='RECOVER_LAST')
                                if obj.bfu_anim_action_export_enum == "export_specific_prefix":
                                    ActionListProperty.prop(obj, 'bfu_prefix_name_to_export')

                            # Action Time
                            if obj.type != "CAMERA" and obj.bfu_skeleton_export_procedure != "auto-rig-pro":
                                ActionTimeProperty = layout.column()
                                ActionTimeProperty.enabled = obj.bfu_anim_action_export_enum != 'dont_export'
                                ActionTimeProperty.prop(obj, 'bfu_anim_action_start_end_time_enum')
                                if obj.bfu_anim_action_start_end_time_enum == "with_customframes":
                                    OfsetTime = ActionTimeProperty.row()
                                    OfsetTime.prop(obj, 'bfu_anim_action_custom_start_frame')
                                    OfsetTime.prop(obj, 'bfu_anim_action_custom_end_frame')
                                if obj.bfu_anim_action_start_end_time_enum != "with_customframes":
                                    OfsetTime = ActionTimeProperty.row()
                                    OfsetTime.prop(obj, 'bfu_anim_action_start_frame_offset')
                                    OfsetTime.prop(obj, 'bfu_anim_action_end_frame_offset')

                            else:
                                layout.label(
                                    text=(
                                        "Note: animation start/end use scene frames" +
                                        " with the camera for the sequencer.")
                                    )

                            # Nomenclature
                            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                                export_anim_naming = layout.column()
                                export_anim_naming.enabled = obj.bfu_anim_action_export_enum != 'dont_export'
                                export_anim_naming.prop(obj, 'bfu_anim_naming_type')
                                if obj.bfu_anim_naming_type == "include_custom_name":
                                    export_anim_naming_text = export_anim_naming.column()
                                    export_anim_naming_text.prop(obj, 'bfu_anim_naming_custom')



                        else:
                            layout.label(
                                text='(This assets is not a SkeletalMesh or Camera)')

                    scene.bfu_animation_action_advanced_properties_expanded.draw(layout)
                    if scene.bfu_animation_action_advanced_properties_expanded.is_expend():

                        if bfu_alembic_animation.bfu_alembic_animation_utils.is_not_alembic_animation(obj):
                            transformProp = layout.column()
                            transformProp.enabled = obj.bfu_anim_action_export_enum != 'dont_export'
                            transformProp.prop(obj, "bfu_move_action_to_center_for_export")
                            transformProp.prop(obj, "bfu_rotate_action_to_zero_for_export")

                    scene.bfu_animation_nla_properties_expanded.draw(layout)
                    if scene.bfu_animation_nla_properties_expanded.is_expend():
                        # NLA
                        if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                            NLAAnim = layout.row()
                            NLAAnim.prop(obj, 'bfu_anim_nla_use')
                            NLAAnimChild = NLAAnim.column()
                            NLAAnimChild.enabled = obj.bfu_anim_nla_use
                            NLAAnimChild.prop(obj, 'bfu_anim_nla_export_name')
                            if obj.bfu_skeleton_export_procedure == "auto-rig-pro":
                                NLAAnim.enabled = False
                                NLAAnimChild.enabled = False

                        # NLA Time
                        if obj.type != "CAMERA" and obj.bfu_skeleton_export_procedure != "auto-rig-pro":
                            NLATimeProperty = layout.column()
                            NLATimeProperty.enabled = obj.bfu_anim_nla_use
                            NLATimeProperty.prop(obj, 'bfu_anim_nla_start_end_time_enum')
                            if obj.bfu_anim_nla_start_end_time_enum == "with_customframes":
                                OfsetTime = NLATimeProperty.row()
                                OfsetTime.prop(obj, 'bfu_anim_nla_custom_start_frame')
                                OfsetTime.prop(obj, 'bfu_anim_nla_custom_end_frame')
                            if obj.bfu_anim_nla_start_end_time_enum != "with_customframes":
                                OfsetTime = NLATimeProperty.row()
                                OfsetTime.prop(obj, 'bfu_anim_nla_start_frame_offset')
                                OfsetTime.prop(obj, 'bfu_anim_nla_end_frame_offset')


                    scene.bfu_animation_nla_advanced_properties_expanded.draw(layout)
                    if scene.bfu_animation_nla_advanced_properties_expanded.is_expend():
                        if bfu_alembic_animation.bfu_alembic_animation_utils.is_not_alembic_animation(obj):
                            transformProp2 = layout.column()
                            transformProp2.enabled = obj.bfu_anim_nla_use
                            transformProp2.prop(obj, "bfu_move_nla_to_center_for_export")
                            transformProp2.prop(obj, "bfu_rotate_nla_to_zero_for_export")


                    scene.bfu_animation_advanced_properties_expanded.draw(layout)
                    if scene.bfu_animation_advanced_properties_expanded.is_expend():
                        # Animation fbx properties
                        if bfu_alembic_animation.bfu_alembic_animation_utils.is_not_alembic_animation(obj):
                            propsFbx = layout.row()
                            if obj.bfu_skeleton_export_procedure != "auto-rig-pro":
                                propsFbx.prop(obj, 'bfu_sample_anim_for_export')
                            propsFbx.prop(obj, 'bfu_simplify_anim_for_export')
                        propsScaleAnimation = layout.row()
                        propsScaleAnimation.prop(obj, "bfu_disable_free_scale_animation")

                    # Armature export action list feedback
                    if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                        layout.label(
                            text='Note: The Action with only one' +
                            ' frame are exported like Pose.')
                        ArmaturePropertyInfo = (
                            layout.row().box().split(factor=0.75)
                            )
                        animation_asset_cache = bfu_cached_asset_list.GetAnimationAssetCache(obj)
                        animation_to_export = animation_asset_cache.GetAnimationAssetList()
                        ActionNum = len(animation_to_export)
                        if obj.bfu_anim_nla_use:
                            ActionNum += 1
                        actionFeedback = (
                            str(ActionNum) +
                            " Animation(s) will be exported with this object.")
                        ArmaturePropertyInfo.label(
                            text=actionFeedback,
                            icon='INFO')
                        ArmaturePropertyInfo.operator("object.showobjaction")
                else:
                    layout.label(text='(No properties to show.)')
            else:
                layout.label(text='(No properties to show.)')

        if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):


            scene.bfu_object_collision_properties_expanded.draw(layout)
            if scene.bfu_object_collision_properties_expanded.is_expend():
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        # StaticMesh prop
                        if bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(obj):
                            if not obj.bfu_export_as_lod_mesh:
                                auto_generate_collision = layout.row()
                                auto_generate_collision.prop(
                                    obj,
                                    'bfu_auto_generate_collision'
                                    )
                                collision_trace_flag = layout.row()
                                collision_trace_flag.prop(
                                    obj,
                                    'bfu_collision_trace_flag'
                                    )
                        # SkeletalMesh prop
                        if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                            if not obj.bfu_export_as_lod_mesh:
                                create_physics_asset = layout.row()
                                create_physics_asset.prop(obj, "bfu_create_physics_asset")
                                enable_skeletal_mesh_per_poly_collision = layout.row()
                                enable_skeletal_mesh_per_poly_collision.prop(obj, 'bfu_enable_skeletal_mesh_per_poly_collision')



            scene.bfu_object_light_map_properties_expanded.draw(layout)
            if scene.bfu_object_light_map_properties_expanded.is_expend():
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        # Light map
                        if bfu_static_mesh.bfu_static_mesh_utils.is_static_mesh(obj):
                            StaticMeshLightMapRes = layout.box()
                            StaticMeshLightMapRes.prop(obj, 'bfu_static_mesh_light_map_mode')
                            if obj.bfu_static_mesh_light_map_mode == "CustomMap":
                                CustomLightMap = StaticMeshLightMapRes.column()
                                CustomLightMap.prop(obj, 'bfu_static_mesh_custom_light_map_res')
                            if obj.bfu_static_mesh_light_map_mode == "SurfaceArea":
                                SurfaceAreaLightMap = StaticMeshLightMapRes.column()
                                SurfaceAreaLightMapButton = SurfaceAreaLightMap.row()
                                SurfaceAreaLightMapButton.operator("object.comput_lightmap", icon='TEXTURE')
                                SurfaceAreaLightMapButton.operator("object.comput_all_lightmap", icon='TEXTURE')
                                SurfaceAreaLightMap.prop(obj, 'bfu_use_static_mesh_light_map_world_scale')
                                SurfaceAreaLightMap.prop(obj, 'bfu_static_mesh_light_map_surface_scale')
                                SurfaceAreaLightMap.prop(obj, 'bfu_static_mesh_light_map_round_power_of_two')
                            if obj.bfu_static_mesh_light_map_mode != "Default":
                                CompuntedLightMap = str(bfu_light_map.bfu_light_map_utils.GetCompuntedLightMap(obj))
                                StaticMeshLightMapRes.label(text='Compunted light map: ' + CompuntedLightMap)
                            bfu_generate_light_map_uvs = layout.row()
                            bfu_generate_light_map_uvs.prop(obj, 'bfu_generate_light_map_uvs')


            scene.bfu_object_uv_map_properties_expanded.draw(layout)
            if scene.bfu_object_uv_map_properties_expanded.is_expend():
                if obj.bfu_export_type == "export_recursive":
                    # Geometry Node Uv
                    bfu_convert_geometry_node_attribute_to_uv = layout.column()
                    convert_geometry_node_attribute_to_uv_use = bfu_convert_geometry_node_attribute_to_uv.row()
                    convert_geometry_node_attribute_to_uv_use.prop(obj, 'bfu_convert_geometry_node_attribute_to_uv')
                    bbpl.blender_layout.layout_doc_button.add_doc_page_operator(convert_geometry_node_attribute_to_uv_use, url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/UV-Maps#geometry-node-uv")
                    bfu_convert_geometry_node_attribute_to_uv_name = bfu_convert_geometry_node_attribute_to_uv.column()
                    bfu_convert_geometry_node_attribute_to_uv_name.prop(obj, 'bfu_convert_geometry_node_attribute_to_uv_name')
                    bfu_convert_geometry_node_attribute_to_uv_name.enabled = obj.bfu_convert_geometry_node_attribute_to_uv

                    # Extreme UV Scale
                    ui_correct_extrem_uv_scale = layout.column()
                    ui_correct_extrem_uv_scale_use = ui_correct_extrem_uv_scale.row()
                    ui_correct_extrem_uv_scale_use.prop(obj, 'bfu_use_correct_extrem_uv_scale')
                    bbpl.blender_layout.layout_doc_button.add_doc_page_operator(ui_correct_extrem_uv_scale_use, url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/UV-Maps#extreme-uv-scale")
                    ui_correct_extrem_uv_scale_options = ui_correct_extrem_uv_scale.column()
                    ui_correct_extrem_uv_scale_options.prop(obj, 'bfu_correct_extrem_uv_scale_step_scale')
                    ui_correct_extrem_uv_scale_options.prop(obj, 'bfu_correct_extrem_uv_scale_use_absolute')
                    ui_correct_extrem_uv_scale_options.enabled = obj.bfu_use_correct_extrem_uv_scale

        if bfu_ui.bfu_ui_utils.DisplayPropertyFilter("SCENE", "GENERAL"):

            scene.bfu_collection_properties_expanded.draw(layout)
            if scene.bfu_collection_properties_expanded.is_expend():
                collectionListProperty = layout.column()
                collectionListProperty.template_list(
                    # type and unique id
                    "BFU_UL_CollectionExportTarget", "",
                    # pointer to the CollectionProperty
                    scene, "bfu_collection_asset_list",
                    # pointer to the active identifier
                    scene, "bfu_active_collection_asset_list",
                    maxrows=5,
                    rows=5
                )
                collectionListProperty.operator(
                    "object.updatecollectionlist",
                    icon='RECOVER_LAST')

                if scene.bfu_active_collection_asset_list < len(scene.bfu_collection_asset_list):
                    col_name = scene.bfu_collection_asset_list[scene.bfu_active_collection_asset_list].name
                    if col_name in bpy.data.collections:
                        col = bpy.data.collections[col_name]
                        col_prop = layout
                        col_prop.prop(col, 'bfu_export_folder_name', icon='FILE_FOLDER')
                        bfu_export_procedure.bfu_export_procedure_ui.draw_collection_export_procedure(layout, col)

                collectionPropertyInfo = layout.row().box().split(factor=0.75)
                collection_asset_cache = bfu_cached_asset_list.GetCollectionAssetCache()
                collection_export_asset_list = collection_asset_cache.GetCollectionAssetList()
                collectionNum = len(collection_export_asset_list)
                collectionFeedback = (
                    str(collectionNum) +
                    " Collection(s) will be exported.")
                collectionPropertyInfo.label(text=collectionFeedback, icon='INFO')
                collectionPropertyInfo.operator("object.showscenecollection")
                layout.label(text='Note: The collection are exported like StaticMesh.')


        bfu_base_object.bfu_base_obj_ui.draw_ui(layout, obj)
        bfu_adv_object.bfu_adv_obj_ui.draw_ui(layout, obj)
        bfu_base_collection.bfu_base_col_ui.draw_ui(layout, obj)
        bfu_static_mesh.bfu_static_mesh_ui.draw_ui_object(layout, obj)
        bfu_skeletal_mesh.bfu_skeletal_mesh_ui.draw_ui_object(layout, obj)
        bfu_camera.bfu_camera_ui_and_props.draw_ui_object_camera(layout, obj)
        bfu_spline.bfu_spline_ui_and_props.draw_ui_object_spline(layout, obj)
        bfu_lod.bfu_lod_ui.draw_ui(layout, obj)
        bfu_uv_map.bfu_uv_map_ui.draw_obj_ui(layout, obj)
        bfu_light_map.bfu_light_map_ui.draw_obj_ui(layout, obj)
        bfu_assets_references.bfu_asset_ref_ui.draw_ui(layout, obj)

        # Animations
        bfu_anim_base.bfu_anim_base_ui.draw_ui(layout, obj)
        bfu_anim_action.bfu_anim_action_ui.draw_ui(layout, obj)
        bfu_anim_action_adv.bfu_anim_action_adv_ui.draw_ui(layout, obj)
        bfu_anim_nla.bfu_anim_nla_ui.draw_ui(layout, obj)
        bfu_anim_nla_adv.bfu_anim_nla_adv_ui.draw_ui(layout, obj)

        





# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_BlenderForUnrealObject,
    BFU_PT_BlenderForUnrealObject.BFU_MT_ObjectGlobalPropertiesPresets,
    BFU_PT_BlenderForUnrealObject.BFU_OT_AddObjectGlobalPropertiesPreset,
    BFU_PT_BlenderForUnrealObject.BFU_OT_OpenDocumentationPage,
    BFU_PT_BlenderForUnrealObject.BFU_UL_ActionExportTarget,
    BFU_PT_BlenderForUnrealObject.BFU_OT_UpdateObjActionListButton,
    BFU_PT_BlenderForUnrealObject.BFU_OT_ShowActionToExport,
    BFU_PT_BlenderForUnrealObject.BFU_UL_CollectionExportTarget,
    BFU_PT_BlenderForUnrealObject.BFU_OT_UpdateCollectionButton,
    BFU_PT_BlenderForUnrealObject.BFU_OT_ShowCollectionToExport,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
