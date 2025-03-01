# Importing necessary modules
from ast import If  # AST (Abstract Syntax Tree) module to parse Python syntax
import bpy  # Blender Python module for 3D operations
import time  # Time module for time-related functions
from os.path import exists  # To check if file paths exist
from ctypes import *  # Ctypes for calling functions from DLLs/shared libraries
from importlib import reload  # Reload to reload imported modules
import binascii  # Convert binary data to ASCII or vice versa
import struct  # To work with C-style structs
import mjolnir.utils  # Utility functions from Mjolnir (custom library)

# Reloading the modules to ensure the latest version of the code is used
import mjolnir.halo3
import mjolnir.forge_types
import mjolnir.forge_props
reload(mjolnir.halo3)  # Reload Halo 3-related functions
reload(mjolnir.forge_types)  # Reload Forge types (game objects)
reload(mjolnir.forge_props)  # Reload Forge props
reload(mjolnir.utils)  # Reload utility functions

# Importing necessary classes/functions from the modules
from mjolnir.forge_types import *
from mjolnir.forge_props import *
from mjolnir.halo3 import *
from mjolnir.utils import *

# Defining global variables
dllPath = bpy.path.abspath("//") + "ForgeBridge.dll"  # Path to the ForgeBridge DLL
mapPalette = 'Sandbox Palette'  # Palette used in the map (e.g., Sandbox)
maxObjectCount = 640  # Maximum allowed objects in Forge
quotas = None  # Placeholder for object quotas

# Function to reload the memory from the Forge DLL
def tryReload():
    forge.ReadMemory()

# Function to display a message box in Blender's UI
def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    # Inner function to draw the layout of the message box
    def draw(self, context):
        self.layout.label(text=message)
    # Call Blender's popup menu to show the message
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

# Function to get the Forge object from an instance, if possible
def tryGetForgeObjectFromInstance(instance):
    object = instance.object  # Get the associated Blender object
    if instance.is_instance and object.is_instancer:
        return object  # Return if the object is an instancer (group of objects)
    elif object.get('isForgeObject', False):  # Check if it's marked as a Forge object
        p = object.parent  # Get the parent of the object
        if p is None or p.instance_type == 'NONE' or p.instance_type == 'COLLECTION': 
            return object  # Return the object if it has no instance or it's part of a collection
    else:
        return None  # Return None if it doesn't meet the criteria

# Function to check if an object should be removed based on bit flags
def checkRemove(val):
    return bool((val >> 5) & 1)  # Check the 5th bit in the value

# Function to import Forge objects from the game into Blender
def importForgeObjects(context, self=None, createCollections=False):
    # Add a custom property 'protected' to Blender objects
    bpy.types.Object.protected = BoolProperty(name = 'protected', default = False)
    if context.scene.name == 'Props':  # Skip import if the scene is 'Props'
        return False
    if not forge.TrySetConnect(True):  # Try to connect to the Forge DLL
        return False

    t0 = time.time()  # Start a timer to measure import time

    forge.ReadMemory()  # Read the memory from the Forge DLL
    forge.FindPointer()  # Find the memory pointer for Forge objects
    mvar = forge.GetH3_MVAR_Ptr().contents  # Get pointer to the MVAR (map variant) structure
    print("Name: %s (by %s)" % (mvar.data.display_name, mvar.data.author.decode()))  # Display map name and author
    print("Description: " + mvar.data.description.decode())  # Display map description
    print("Scenario Objects: " + str(mvar.data.scenario_objects))  # Print number of scenario objects
    quotas = mvar.quotas  # Set object quotas from the MVAR

    # Loop through all variant objects in the map
    for i in range(mvar.data.variant_objects):
        forgeObject = mvar.objects[i]  # Get Forge object
        itemName = "%s (%d, %d, %d)" % (getItemName(forgeObject.definition_index), forgeObject.definition_index, forgeObject.object_index, forgeObject.helper_index)

        # Check if the object is known and not marked for removal
        if getItemName(forgeObject.definition_index) != 'Unknown' and checkRemove(forgeObject.placement) == False:
            itemName = getItemName(forgeObject.definition_index)
        else:
            # Create a new collection in Blender for this object
            collection = bpy.data.collections.new(itemName)
            # bpy.data.scenes['Scene'].collection.children.link(collection)
            blenderObject = bpy.data.objects.new(itemName, None)  # Create a new empty object
            collection.objects.link(blenderObject)  # Link it to the collection
            blenderObject.empty_display_type = 'ARROWS'  # Set display type to arrows
            blenderObject.empty_display_size = 0.5  # Set display size

        # Create a new Blender object for the Forge object
        blenderObject = createForgeObject(context, itemName, i)
        if i <= mvar.data.scenario_objects:  # Protect objects that are part of the scenario
            blenderObject.protected = True

        # Set the placement flags for the Forge object
        for x in range(len(blenderObject.forge.placementFlags)):
            blenderObject.forge.placementFlags[x] = setFlags(forgeObject.placement, x)

        # Set the variant placement flags
        for x in range(len(blenderObject.forge.variantPlacementFlags)):
            blenderObject.forge.variantPlacementFlags[x] = setFlags(forgeObject.mp_placement, x)
        
        # Assign various properties to the Blender object
        blenderObject.forge.sharedStorage = forgeObject.shared_storage
        blenderObject.forge.spawnTime = forgeObject.spawn_time_seconds
        blenderObject.name = blenderObject.name
        blenderObject['placement'] = forgeObject.placement
        blenderObject['reuse_timeout'] = forgeObject.reuse_timeout
        blenderObject['object_index'] = forgeObject.object_index
        blenderObject['helper_index'] = forgeObject.helper_index
        blenderObject['definition_index'] = forgeObject.definition_index
        blenderObject.matrix_world = forgeObject.transform.toMatrix()  # Set the object's transform matrix
        blenderObject['attached_id'] = forgeObject.attached_id
        blenderObject['attached_bsp_index'] = forgeObject.attached_bsp_index
        blenderObject['attached_type'] = forgeObject.attached_type
        blenderObject['attached_source'] = forgeObject.attached_source

        # Assign more properties related to the game engine
        blenderObject['game_engine_flags'] = forgeObject.game_engine_flags
        blenderObject['mp_placement'] = forgeObject.mp_placement
        blenderObject['team'] = forgeObject.team
        blenderObject['shared_storage'] = forgeObject.shared_storage
        blenderObject['spawn_time_seconds'] = forgeObject.spawn_time_seconds
        blenderObject['object_type'] = forgeObject.object_type
        blenderObject['shape'] = forgeObject.shape
        blenderObject['width'] = forgeObject.shape_data.width
        blenderObject['length'] = forgeObject.shape_data.length
        blenderObject['top'] = forgeObject.shape_data.top
        blenderObject['bottom'] = forgeObject.shape_data.bottom

    # Print the number of imported objects and the time taken
    print("Imported %d objects in %.3fs" % (mvar.data.variant_objects, time.time() - t0))
    forge.ClearObjectList()  # Clear the list of objects after import
    return {'FINISHED'}  # Return status

# Function to set flags based on a value and bit position
def setFlags(value, bit):
    return (value >> bit) & 1  # Return the value of the bit at 'bit' position

# Function to get a string enum from a list of options
def getStringEnum(options, val):
    return options.index(val)  # Return the index of the value in the list of options

# Convert a Blender object to a struct for memory writing
def toStruct(obj, m):
    if obj['definition_index'] != -1:  # Check if the object has a valid definition index
        # Prepare a list of fields to be packed into the struct
        fields = [
            getFlagsVal(obj.forge.placementFlags),
            0,
            -1,
            -1,
            obj['definition_index'],
            round(m.col[3][0], 4),  # Round position coordinates
            round(m.col[3][1], 4),
            round(m.col[3][2], 4),
            round(m.col[1][0], 4),  # Round rotation matrix
            round(m.col[1][1], 4),
            round(m.col[1][2], 4),
            round(m.col[2][0], 4),
            round(m.col[2][1], 4),
            round(m.col[2][2], 4),
            -1,
            -1,
            255,
            255,
            1023,  # Set default game engine flags
            getFlagsVal(obj.forge.variantPlacementFlags),
            obj['team'],
            obj.forge.sharedStorage,
            obj.forge.spawnTime,
            obj['object_type'],
            obj['shape'],
            obj['width'],
            obj['length'],
            obj['top'],
            obj['bottom']
        ]
        # Pack the fields into a binary format using struct
        try:
            return struct.Struct('<hhiiifffffffffihBBhBBBBBBffff').pack(*fields)
        except struct.error as e:
            print("Error: " + e)  # Print an error if packing fails
    else:
        return None

# Function to check if the object exceeds the quota limit
def checkQuota(obj):
    index = obj['definition_index']  # Get the object's definition index
    quota = quotas[index]  # Check the object's quota

def skipList(name):
    ignoreList = ["Sandbox", "Waterfall","Environment","Ceiling", "Base Map", "Foundry", "Blackout", "Construct", "Narrows", "Sandtrap", "Valhalla", "Avalanche", "Standoff", "Edge", "Icebox", "Pit", "Citadel", "Longshore", "LastResort", "Epitaph", "Ratsnest", "Ghosttown", "Leaves", "Guardian", "Overhang", "Trees", "Overhang", "Assembly", "Top"]
    return any(name in x for x in ignoreList)

# Function to export Forge objects from Blender back into the game
def exportForgeObjects(self=None):
    #if not forge.TrySetConnect(True):
       # return False

    hitLimit = False
    t0 = time.time()
    i = 0
    for instance in bpy.context.evaluated_depsgraph_get().object_instances:
        if instance.object.name in bpy.context.scene.collection.all_objects and skipList(instance.object.name) is False:
            blenderObject = tryGetForgeObjectFromInstance(instance)
            if blenderObject != None:
                if i >= maxObjectCount: 
                    hitLimit = True
                    continue
                if not hitLimit:
                    forgeObject = forge.GetObjectPtr(i).contents
                    blenderObject.forge.ToForgeObject(forgeObject, blenderObject, instance)
                    b = toStruct(blenderObject, instance.matrix_world)
                    if i in range(2,640):
                        if b != None:
                            if 'Grid' not in instance.object.name and 'Invisible' not in instance.object.name:
                                #'porter' not in instance.object.name and 
                                print("Exporting: "+ instance.object.name)
                                print(binascii.hexlify(b))
                                forge.WriteMemory(binascii.hexlify(b), i-2)

            i += 1
    forge.WriteCount(i)
    ShowMessageBox("Exported %d objects in %.3fs" % (i, time.time() - t0))
    print("Exported %d objects in %.3fs" % (i, time.time() - t0), "Export Success")
    return {'FINISHED'} 

# Function to toggle physics in Forge (e.g., enabling/disabling object physics)
def modPhysics():
    forge.TogglePhysics()

# Main function to initialize the Forge DLL and set it up
def bridgeMain():
    global forge  # Use the global forge variable
    forge = cdll.LoadLibrary(dllPath)  # Load the ForgeBridge DLL
    print("ForgeBridge.dll Version is: %d" % forge.GetDllVersion())  # Print the DLL version
    forge.TrySetConnect.restype = c_bool  # Set the return type for the TrySetConnect function
    forge.GetObjectPtr.restype = POINTER(H3_ForgeObject)  # Set the return type for GetObjectPtr
    forge.GetH3_MVAR_Ptr.restype = POINTER(H3_MVAR)  # Set the return type for GetH3_MVAR_Ptr
    forge.GetH3_MVAR.restype = H3_MVAR  # Set the return type for GetH3_MVAR

    # Call the GetMapName function and print the map name
    forge.GetMapName.restype = c_wchar_p  # Ensure it returns a wide string
    map_name = forge.GetMapName()
    print(f"[INFO] Current Map Name: {map_name}")

    if forge.TrySetConnect(True):  # Try to connect to the Forge DLL
        forge.ReadMemory()  # Read the memory if connection is successful
