bl_info = {
    "name": "Batch Import JMS",
    "author": "Exhibit",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import multiple JMS files",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}


import bpy
import os

from bpy_extras.io_utils import ImportHelper

from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )


class ImportMultipleJMS(bpy.types.Operator, ImportHelper):
    """Batch Import JMS"""
    bl_idname = "import_scene.multiple_jms"
    bl_label = "Import multiple JMS's"
    bl_options = {'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".jms"

    filter_glob = StringProperty(
            default="*.jms",
            options={'HIDDEN'},
            )

    # Selected files
    files: CollectionProperty(type=bpy.types.PropertyGroup)


    def draw(self, context):
        layout = self.layout


    def execute(self, context):

        # get the folder
        folder = (os.path.dirname(self.filepath))

        # iterate through the selected files
        for i in self.files:

            # generate full path to file
            path_to_file = (os.path.join(folder, i.name))

            bpy.ops.import_scene.jms(filepath = path_to_file)

        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportMultipleJMS.bl_idname, text="Bulk .jms Importer")


def register():
    bpy.utils.register_class(ImportMultipleJMS)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportMultipleJMS)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.import_scene.multiple_jms('INVOKE_DEFAULT')
