import bpy,blf
from importlib import reload
import json
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.types import Scene

from mjolnir.forge_props import *
from mjolnir.forge_types import *
from mjolnir.modifiers import *

import mjolnir.bridge
reload(mjolnir.bridge)
from mjolnir.bridge import *
import mjolnir.prefabs

mapPalette = 'Props'
maxObjectCount = 640
persistence = bpy.app.driver_namespace


'''
*************************************

TEMP FUNCTIONS FOR TESTING

*************************************
'''

def tryGetForgeObjectFromInstance(instance):
    object = instance.object
    if instance.is_instance:
        if object.is_instancer: 
            return object
    elif object.get('isForgeObject',False):
        p = object.parent
        if p is None or p.instance_type == 'NONE' or p.instance_type == 'COLLECTION': 
            return object
    else:
        return None

def pollForgePanel(self, context):
    if context.object is None: 
        return False
    return context.object.get('isForgeObject', False)
'''
*************************************

ICON / OBJECT / COLLECTION BUILDING

*************************************
'''
iconDict = {}

def fillIconDict(collection):
    global iconDict
    for child in collection.children:
        if len(child.objects) > 0:
            if iconDict.get(child, None) is None: 
                iconDict[child] = child.forge.icon
        else: 
            fillIconDict(child)

def getCollectionEnums(collection, list):
    global iconDict
    for child in collection.children:
        if len(child.objects) > 0:
            list.append((child.name, child.name, "", iconDict.get(child, 'NONE'), len(list)))
        else: getCollectionEnums(child, list)
    return list

def genObjectTypesEnum(self, context): 
    return getCollectionEnums(bpy.data.collections[mapPalette], [])

def findReplacements(self, context):
    faulksmash = []
    prefab = []
    for obj in bpy.context.selected_objects:
        if obj.forge.placementFlags[3] == False:
            prefab.append(obj)
        else:
            faulksmash.append(obj)
    for obj in prefab:
        match = None
        for d in faulksmash:
            if d['definition_index'] == obj['definition_index'] and match is None:
                faulksmash.remove(d)
                match = d
                match.location = obj.location
                match.rotation_euler = obj.rotation_euler
        if match is not None:
            bpy.data.objects.remove(obj, do_unlink=True)

def ExportPrefab(filepath):
    print('Export')
    prefab = {
        "components": []
    }
    for obj in bpy.context.selected_objects:
        p = obj.location
        r = obj.rotation_euler
        obj.forge.placementFlags[3] = False
        component = {
            'placement': getFlagsVal(obj.forge.placementFlags),
            "reuse_timeout": 0,
            "object_index": -1,
            "helper_object_index": -1,
            "definition_index": obj['definition_index'],
            'position': [p[0], p[1], p[2]],
            'rotation': [r[0], r[1], r[2]],
            'e_scenario_game_engine': 1023,
            'mp_placement':getFlagsVal(obj.forge.variantPlacementFlags),
            'team': obj['team'],
            'shared_storage': obj['shared_storage'],
            'spawn_time':obj['spawn_time_seconds'],
            'object_type': obj['object_type']
        }
        prefab["components"].append(component)
    # Writing to sample.json
    with open(filepath, "w") as outfile:
        json.dump(prefab, outfile)

def ImportPrefab(filepath):
    objectCount = 0
    for instance in bpy.context.evaluated_depsgraph_get().object_instances:
        if tryGetForgeObjectFromInstance(instance) != None: 
            objectCount += 1

    with open(filepath, 'r') as openfile:
        json_object = json.load(openfile)
        count = 1
        for obj in json_object["components"]:
            itemName = "%s (%d, %d, %d)" % (getItemName(obj['definition_index']),obj['definition_index'], -1, -1)
            if getItemName(obj['definition_index']) != 'Unknown':
                itemName = getItemName(obj['definition_index'])

            blenderObject = createForgeObject(bpy.context, itemName, objectCount+count)

            for x in range(len(blenderObject.forge.placementFlags)):
                blenderObject.forge.placementFlags[x] = setFlags(obj['placement'], x)
                if x == 3:
                    blenderObject.forge.placementFlags[x] = False

            for x in range(len(blenderObject.forge.variantPlacementFlags)):
                blenderObject.forge.variantPlacementFlags[x] = setFlags(obj['mp_placement'], x)

            blenderObject.name = blenderObject.name
            blenderObject['placement'] = obj['placement']
            blenderObject['reuse_timeout'] = 0
            blenderObject['object_index'] = -1
            blenderObject['helper_index'] = -1
            blenderObject['definition_index'] = obj['definition_index']
            p = obj['position']
            blenderObject.location = (p[0], p[1], p[2])
            r = obj['rotation']
            blenderObject.rotation_euler = (r[0], r[1], r[2])

            blenderObject['attached_id'] = -1
            blenderObject['attached_bsp_index'] = 65535
            blenderObject['attached_type'] = 255
            blenderObject['attached_source'] = 255

            blenderObject['game_engine_flags'] = obj['e_scenario_game_engine']
            blenderObject['mp_placement'] = obj['mp_placement']
            blenderObject['team'] = obj['team']
            blenderObject['shared_storage'] = obj['shared_storage']
            blenderObject['spawn_time_seconds'] = obj['spawn_time']
            blenderObject['object_type'] = obj['object_type']
            blenderObject['shape'] = 0
            blenderObject['width'] = 0
            blenderObject['length'] = 0
            blenderObject['top'] = 0
            blenderObject['bottom'] = 0
            bpy.context.view_layer.objects.active = blenderObject
            count+=1

    print('Imported: '+str(count))

def clearObjects(context):
    print("Doesn't do anything")
    '''for obj in bpy.context.scene.objects:
        if obj['isForgeObject'] == True:
            if obj.protected:
                obj.protected = False
            bpy.data.objects.remove(obj)'''

def physicsMod():
    forge.TogglePhysics()

'''
*************************************

CLASSES

*************************************
'''

class ClearObjects(Operator):
    bl_idname = 'forge.clear'
    bl_label = 'Clear Button'
 
    def execute(self, context):
        clearObjects(context)
        return {"FINISHED"}

class ReplaceButton(Operator):
    bl_idname = 'forge.replace'
    bl_label = 'Optimize Selected'
 
    def execute(self, context):
        findReplacements(self, context)
        return {"FINISHED"}

class ExportButton(Operator):
    bl_idname = 'forge.refresh'
    bl_label = 'Refresh Button'
 
    def execute(self, context):
        exportForgeObjects()
        return {"FINISHED"}

class ImportButton(Operator):
    bl_idname = 'forge.imp'
    bl_label = 'Reload Button'
 
    def execute(self, context):
        importForgeObjects(bpy.context)
        return {"FINISHED"}

class ObjectArray(Operator):
    bl_idname = 'array.object'
    bl_label = 'Object Array'
 
    def execute(self, context):
        o = bpy.context
        arrayModifier(o,'OBJECT')
        return {"FINISHED"}

class ConstArray(Operator):
    bl_idname = 'array.const'
    bl_label = 'Linear Array'
 
    def execute(self, context):
        o = bpy.context
        arrayModifier(o,'CONST')
        return {"FINISHED"}

class TogglePhysics(Operator):
    bl_idname = 'mod.physics'
    bl_label = 'Toggle Physics'
 
    def execute(self, context):
        modPhysics()
        return {"FINISHED"}

class MakePrefab(Operator, ExportHelper):
    bl_idname = 'forge.prefab'
    bl_label = 'Export Prefab'
    bl_options = {'PRESET', 'UNDO'}
 
    filename_ext = '.json'
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
 
    def execute(self, context):
        ExportPrefab(self.filepath)
        return {"FINISHED"}

class ImportPrefabs(Operator, ImportHelper):
    bl_idname = 'forge.add'
    bl_label = 'Import Prefab'
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = '.json'
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
 
    def execute(self, context):
        ImportPrefab(self.filepath)
        return {"FINISHED"}

class DebugPanel(bpy.types.Panel):
    bl_idname = "panel.DebugPanel"
    bl_label = "Mjolnir Controls"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_category = "Tools"
    bl_category = "MJOLNIR"
 
    def draw(self, context):
        layout = self.layout

        layout.label(text="Commands")
        layout.operator("array.object", text="Object Array")
        layout.operator("array.const", text="Constant Array")
        layout.operator("forge.prefab", text="Make Prefab")
        layout.operator("forge.add", text="Load Prefab")
        layout.operator("forge.replace", text="Optimize Selected")

        layout.separator()
        layout.label(text="In-game Functions")
        layout.operator("forge.imp", text="Import Objects from Forge")
        layout.operator("forge.refresh", text="Export Objects to Forge")
        layout.operator("forge.refresh_scene", text="Refresh Objects")

        layout.separator()
        layout.label(text="Mods")
        layout.operator("mod.physics", text="Toggle Physics")

        layout.separator()
        layout.label(text="Misc")
        layout.operator("view3d.walk_navigation", text="Walk Navigation")

class ImportForgeObjects(Operator):
    bl_idname = "forge.import"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Forge Objects"
    bl_options = {'REGISTER', 'UNDO'}

    additive: BoolProperty(name="Additive", description="Add the forge objects to the existing scene loaded in Blender", default=True)

    def execute(self, context):
        if not self.additive:
            for o in context.scene.objects:
                if o.get('isForgeObject', False):
                    bpy.data.objects.remove(o, do_unlink=True)
        importForgeObjects(bpy.context)
        return {'FINISHED'}

class ExportForgeObjects(Operator):
    bl_idname = 'forge.export'
    bl_label = "Export Forge Objects"

    def execute(self, context):
        exportForgeObjects()
        return {'FINISHED'}

class ConvertForge(Operator):
    bl_idname = 'object.convert_forge'
    bl_label = "Convert Forge Object"

    isForgeObject: BoolProperty()

    def execute(self, context):
        for obj in context.selected_objects: 
            obj['isForgeObject'] = self.isForgeObject
        return {'FINISHED'}

class AddForgeObject(Operator):
    bl_idname = 'forge.add_object'
    bl_label = "Forge Object..."
    bl_property = 'objectType'

    #objectType: EnumProperty(name="Object Type", items=genObjectTypesEnum)
    
    def invoke(self, context, event):
        fillIconDict(bpy.data.collections[mapPalette])
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        blenderObject = createForgeObject(context, self.objectType)
        blenderObject.location = context.scene.cursor.location
        for obj in bpy.context.selected_objects: 
            obj.select_set(False)
        blenderObject.select_set(True)
        context.view_layer.objects.active = blenderObject
        
        bpy.ops.ed.undo_push()
        return {'FINISHED'}

class AddForgeObjectMenu(bpy.types.Menu):
    bl_label = "Forge Object"
    bl_idname = 'VIEW3D_MT_add_forge_object'

    def draw(self, context):
        try: 
            children = context.forgeColl.children
        except: 
            return

        layout = self.layout
        for child in children:
            name = child.name
            if len(child.objects) > 0:
                layout.operator_context = 'EXEC_DEFAULT'
                op = layout.operator(AddForgeObject.bl_idname, text=name, icon=child.forge.icon)
                op.objectType = name
            elif len(child.children) > 0:
                self.layout.context_pointer_set('forgeColl',child)
                layout.menu(self.__class__.bl_idname, text=name, icon=child.forge.icon)


'''
*************************************

DRAW MJOLNIR PANELS

*************************************
'''
def drawFlagDropdown(layout, context, data):
    row = layout.row()
    icon = 'TRIA_DOWN' if context.scene[data['status_name']] else 'TRIA_RIGHT'
    row.prop(context.scene, data['status_name'], icon=icon, icon_only=True)
    row.label(text=data['label'])
    
    if context.scene[data['status_name']]:
        box = layout.box()
        column = box.column(align=True)
        for idx, x in enumerate(data['flags']):
            row = column.row(align=True)
            row.label(text = x)
            row.prop(context.object.forge, data['prop'], index = idx, text = '')

def drawForgeObjectProperties(self, context, region):
    layout = self.layout
    properties = [
        "physics",
        "mpObjectType",
        "spawnTime",
        "sharedStorage"
    ]
    obj = context.object

    layout.prop(obj, 'location')
    layout.prop(obj, 'rotation_euler', text="Rotation")    
    layout.prop(obj, 'instance_collection', text="Object Type")

    forgeProperties = obj.forge

    for property in properties:
        column = layout.column(align=True)
        column.prop(forgeProperties, property)

    flagsDropdowns = [
        {
            'prop': 'placementFlags',
            'status_name': 'placementFlagsStatus',
            'label': 'Object Placement Flags:',
            'flags': e_variant_object_placement_flags
        },
        {
            'prop': 'variantPlacementFlags',
            'status_name': 'variantPlacementFlagStatus',
            'label': 'Variant Placement Flags:',
            'flags': e_variant_placement_flags
        }
    ]

    for dropdown in flagsDropdowns:
        drawFlagDropdown(layout, context, dropdown)

    '''shape = forgeProperties.shape
    isBox = shape == 'BOX'
    column = layout.column(align=True)
    column.prop(forgeProperties, 'shape')
    column2 = column.column(align=True)
    column2.enabled = shape != 'NONE'
    column2.prop(forgeProperties, 'width', text=('Width' if isBox else 'Radius'))
    if isBox: 
        column2.prop(forgeProperties, 'length')

    column2.prop(forgeProperties, 'top')
    column2.prop(forgeProperties, 'bottom')'''

# BOTTOM LEFT ITEM COUNTER
def drawForgeObjectOverlay():
    for area in bpy.context.screen.areas:
        if area.type != 'VIEW_3D': continue
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                if not space.overlay.show_overlays: return
                break
    
    objectCount = 0
    for instance in bpy.context.evaluated_depsgraph_get().object_instances:
        if tryGetForgeObjectFromInstance(instance) != None: 
            objectCount += 1
    
    font_id = 0
    blf.position(font_id, 15, 15, 0)  # Position the text in the bottom-left corner
    blf.size(font_id, 11)  # Set the font size (two arguments)

    if objectCount > maxObjectCount:
        # TEXT BECOMES RED IF ABOVE LIMIT
        blf.color(font_id, 1, 0, 0, 1)  # Red color if the object count exceeds the max limit
    elif objectCount > 500:
        # TEXT BECOMES YELLOW IF NEARING LIMIT
        blf.color(font_id, 1, 0.5, 0, 1)  # Yellow color if nearing the limit
    else: 
        # TEXT IS WHITE BY DEFAULT
        blf.color(font_id, 0, 1, 0.1, 1)  # Default greenish-white color

    # Display object count out of maxObjectCount
    blf.draw(font_id, "%d / %d" % (objectCount, maxObjectCount))



'''
*************************************

FORGE OBJECT PANEL CLASSES

*************************************
'''

class ForgeObjectPanel(bpy.types.Panel):
    bl_label = "Forge Properties"
    bl_idname = 'SCENE_PT_forge_object'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {"DEFAULT_CLOSED"}
    
    @classmethod
    def poll(self, context):
        return pollForgePanel(self, context)

    def draw(self, context):
        drawForgeObjectProperties(self, context, 'WINDOW')

class ForgeObjectPanel_Sidebar(bpy.types.Panel):
    bl_label = "Forge Properties"
    bl_idname = 'SCENE_PT_forge_object_sidebar'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Forge'
    bl_context = 'objectmode'

    @classmethod
    def poll(self, context): 
        return pollForgePanel(self, context)
        
    def draw(self, context): 
        drawForgeObjectProperties(self, context, 'UI')


class ForgeCollectionPanel(bpy.types.Panel):
    bl_label = "Forge Collection"
    bl_idname = 'SCENE_PT_forge_collection'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'collection'
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        collectionProps = context.collection.forge
        layout.prop(collectionProps, 'icon')

'''
*************************************

MENU SETUP FUNCTIONS

*************************************
'''

def convertForgeMenuItem(self, context):
    isForge = context.active_object.get('isForgeObject', False)
    if isForge: 
        op = self.layout.operator(ConvertForge.bl_idname, icon='REMOVE', text="Convert To Blender Object")
    else: 
        op = self.layout.operator(ConvertForge.bl_idname, icon='ADD', text="Convert To Forge Object")
        
    op.isForgeObject = not isForge

def addForgeObjectMenuItem(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator(AddForgeObject.bl_idname, icon='ADD')
    layout.context_pointer_set('forgeColl', bpy.data.collections[mapPalette])
    layout.menu(AddForgeObjectMenu.bl_idname)

class RefreshScene(Operator):
    bl_idname = 'forge.refresh_scene'
    bl_label = 'Refresh Scene'
 
    def execute(self, context):
        # Get the map model name based on the blend file
        map_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]

        # Delete all objects except the map model
        for obj in bpy.data.objects:
            # Check if the object name is not the map model
            if obj.name != map_name and obj.get('isForgeObject', False):
                bpy.data.objects.remove(obj, do_unlink=True)

        # Import the Forge objects again
        importForgeObjects(bpy.context)
        self.report({'INFO'}, f"Scene refreshed, excluding map model '{map_name}'")
        return {'FINISHED'}
    
class WalkNavigation(Operator):
    bl_idname = "view3d.walk_navigation"
    bl_label = "Walk Navigation"

    def execute(self, context):
        # Trigger Blender's built-in walk navigation
        bpy.ops.view3d.walk('INVOKE_DEFAULT')
        return {'FINISHED'}

classes = [
    ClearObjects,
    DebugPanel,
    ExportButton,
    ImportButton,
    ObjectArray,
    ConstArray,
    MakePrefab,
    ImportPrefabs,
    ForgeObjectProperties,
    ForgeCollectionProperties,
    ImportForgeObjects,
    ExportForgeObjects, 
    AddForgeObject, 
    ConvertForge,   
    AddForgeObjectMenu,
    ForgeObjectPanel,
    ForgeObjectPanel_Sidebar,
    TogglePhysics,
    ReplaceButton,
    RefreshScene,
    WalkNavigation

]

object_menus = [
    convertForgeMenuItem
]

add_menus = [
    #addForgeObjectMenuItem
]

'''
*************************************

REGISTRATION FUNCTIONS

*************************************
'''
# "registerDrawEvent" STORES UI CREATION EVENTS IN PERSISTENCE TO BE DESTROYED USING "unregister_menus"

def registerDrawEvent(event, item):
    id = event.bl_rna.name
    handles = persistence.get(id, [])
    event.append(item)
    handles.append(item)
    persistence[id] = handles

# "removeDrawEvents" TRIGGERS THE EVENT REMOVAL FROM PERSISTENCE
def removeDrawEvents(event):
    for item in persistence.get(event.bl_rna.name,[]):
        try: 
            event.remove(item)
        except:
            pass

# REGISTERS ALL THE CLASSES FROM THE "classes" LIST
def register_classes():
    for new_class in classes: 
        bpy.utils.register_class(new_class)

def unregister_classes():
    for new_class in classes:
        try:
            bpy.utils.unregister_class(new_class)
        except:
            pass

def register_menu(menus, type):
    for menu in menus:
        registerDrawEvent(type, menu)

def ensure_forge_scene_properties():
    """Ensure the required Forge properties exist in the Blender scene."""
    scene = bpy.context.scene

    if "placementFlagsStatus" not in scene.keys():
        scene["placementFlagsStatus"] = False

    if "variantPlacementFlagStatus" not in scene.keys():
        scene["variantPlacementFlagStatus"] = False

    print("✅ Forge scene properties registered!")


def register_menus():
    ensure_forge_scene_properties() 

    register_classes()
    
    register_menu(object_menus, bpy.types.VIEW3D_MT_object_context_menu)
    
    register_menu(add_menus, bpy.types.VIEW3D_MT_add)
    
    bpy.types.Object.forge = bpy.props.PointerProperty(type=ForgeObjectProperties)
    bpy.types.Collection.forge = bpy.props.PointerProperty(type=ForgeCollectionProperties)

    persistence['forgeObjectsOverlay_handle'] = bpy.types.SpaceView3D.draw_handler_add(drawForgeObjectOverlay, (), 'WINDOW', 'POST_PIXEL')


def unregister_menus():
    unregister_classes()
    undraw_types = [
        bpy.types.VIEW3D_MT_object_context_menu,
        bpy.types.VIEW3D_MT_add,
        bpy.types.TOPBAR_MT_file_import,
        bpy.types.TOPBAR_MT_file_export
    ]
    for type in undraw_types:
        removeDrawEvents(type)

    bpy.types.SpaceView3D.draw_handler_remove(persistence['forgeObjectsOverlay_handle'], 'WINDOW')



'''


registerDrawEvent(bpy.types.TOPBAR_MT_file_import, importForgeMenu)
registerDrawEvent(bpy.types.TOPBAR_MT_file_export, exportForgeMenu)
def importForgeMenu(self, context): 
    self.layout.operator(ImportForgeObjects.bl_idname, text="Forge Objects", icon='ANTIALIASED')

def exportForgeMenu(self, context): 
    self.layout.operator(ExportForgeObjects.bl_idname, text="Export Forge Objects", icon='ANTIALIASED')

def convertForgeMenuItem(self, context):
    isForge = context.active_object.get('isForgeObject', False)
    if isForge: 
        op = self.layout.operator(ConvertForge.bl_idname, icon='REMOVE', text="Convert To Blender Object")
    else: 
        op = self.layout.operator(ConvertForge.bl_idname, icon='ADD', text="Convert To Forge Object")
        
    op.isForgeObject = not isForge
    

'''