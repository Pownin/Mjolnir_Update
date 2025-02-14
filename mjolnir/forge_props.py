# Import necessary modules from Blender and system libraries
import bpy  # Blender's Python API
import sys  # System-specific parameters and functions
import os  # Miscellaneous operating system interfaces
from bpy.props import *  # Property types for defining custom properties
from bpy.types import Scene  # Blender scene type for working with 3D data
from importlib import reload  # Reloads modules for development purposes

# Adding the directory of the current .blend file to the system path
dir = os.path.dirname(bpy.data.filepath)  # Get the directory of the current Blender file
if not dir in sys.path:
    sys.path.append(dir)  # Add directory to the system path if not already present

# Import custom libraries and reload them for changes
import mjolnir.forge_types  # Import Forge-specific types (custom module)
reload(mjolnir.forge_types)  # Reload the module

import mjolnir.halo3  # Import Halo 3-related functions (custom module)
reload(mjolnir.halo3)  # Reload the module

# Import necessary items from custom modules
from mjolnir.halo3 import *
from mjolnir.forge_types import *

'''
*************************************

CLASSES

*************************************
'''

# Define a property group for Forge collection properties
class ForgeCollectionProperties(bpy.types.PropertyGroup):
    # Function to retrieve icons for the collection's UI
    def iconsEnum(self, context):
        icons = bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items.keys()  # Get all available icons
        icoEnum = []  # Create an empty list for icons
        for i in range(0, len(icons)):
            ico = icons[i]
            icoEnum.append((ico, "", ico, ico, i))  # Add the icon to the list
        return icoEnum  # Return the list of icons

    # EnumProperty to select an icon for the collection
    icon: EnumProperty(name="Icon", description="Icon used in menus", items=iconsEnum, default=0)

# Panel to display Forge collection properties in the Blender UI
class ForgeCollectionPanel(bpy.types.Panel):
    bl_label = "Forge Collection"  # Panel label
    bl_idname = 'SCENE_PT_forge_collection'  # Unique ID for the panel
    bl_space_type = 'PROPERTIES'  # Space type: properties editor
    bl_region_type = 'WINDOW'  # Region type: window
    bl_context = 'collection'  # Context: collection (for organizing objects)

    # Draw function to display UI elements in the panel
    def draw(self, context):
        layout = self.layout  # Get the layout for the panel
        layout.use_property_split = True  # Enable split layout
        collectionProps = context.collection.forge  # Get Forge collection properties
        layout.prop(collectionProps, 'icon')  # Add the icon property to the layout

# Define a property group for Forge object properties
class ForgeObjectProperties(bpy.types.PropertyGroup):
    # Function to update the color property of the object
    def UpdateColor(self, context):
        color = self.color
        if color == 'TEAM_COLOR':  # If color is set to team color, use the team color
            color = self.team
        self.colorIndex = colorEnumToNumber[color]  # Convert the color to its corresponding index

    # Function to update the shape of the object
    def UpdateShape(self, context):
        shapeObject = bpy.data.objects.get(self.shapeObject, None)  # Get the shape object by name
        if self.shape == 'NONE':  # If no shape is selected
            if shapeObject != None:  # If a shape object exists, remove it
                bpy.data.objects.remove(shapeObject, do_unlink=True)
            return

        if shapeObject is None:  # If the shape object doesn't exist, create a new one
            shapeObject = bpy.data.objects.new("%s Shape" % self.object, None)  # Create a new empty object
            self.shapeObject = shapeObject.name  # Store the name of the shape object
            collection = context.collection  # Get the current collection
            collection.objects.link(shapeObject)  # Link the new shape object to the collection
            shapeObject.rotation_euler = Euler((0, 0, radians(90)))  # Rotate the shape
            shapeObject.show_instancer_for_viewport = shapeObject.show_instancer_for_render = False  # Hide shape instancer in viewport/render
            shapeObject.instance_type = 'COLLECTION'  # Set instance type to collection
            blenderObject = bpy.data.objects[self.object]  # Get the associated Blender object
            shapeObject.parent = blenderObject  # Set the Blender object as the parent

        # Link the shape object to the appropriate collection based on its type (Box or Cylinder)
        collection = None
        if self.shape == 'BOX':  # If the shape is a box
            collection = bpy.data.collections['Shape Box']  # Link to 'Shape Box' collection
            shapeObject.scale = (self.width, self.length, self.top + self.bottom)  # Set the scale of the box
        elif self.shape == 'CYLINDER':  # If the shape is a cylinder
            collection = bpy.data.collections['Shape Cylinder']  # Link to 'Shape Cylinder' collection
            diameter = self.width * 2  # Calculate the diameter of the cylinder
            shapeObject.scale = (diameter, diameter, self.top + self.bottom)  # Set the scale of the cylinder

        if shapeObject.instance_collection != collection:  # Update the shape's collection if needed
            shapeObject.instance_collection = collection

        shapeObject.location = (0, 0, (self.top - self.bottom) / 2)  # Set the shape's location

    # Function to update the physics mode of the object
    def UpdatePhysics(self, context):
        mode = self.physics
        if mode == 'NORMAL':  # Normal mode (affected by gravity)
            self.variantPlacementFlags[6] = False
            self.variantPlacementFlags[7] = False
        elif mode == 'FIXED':  # Fixed mode (no gravity)
            self.variantPlacementFlags[6] = True
            self.variantPlacementFlags[7] = False
        elif mode == 'PHASED':  # Phased mode (no gravity or collisions)
            self.variantPlacementFlags[6] = False
            self.variantPlacementFlags[7] = True

    # Function to update the multiplayer object type
    def UpdateObjectType(self, context):
        current = self.mpObjectType
        for i, value in enumerate(mp_object_types):  # Find the index of the current multiplayer object type
            if current == value[0]:
                bpy.context.selected_objects[0]['object_type'] = i  # Set the object type property based on index

    # Function to update the definition index of the object
    def UpdateDefinitionIndex(self, context):
        current = self.mpObjectType
        for i, value in enumerate(mp_object_types):  # Find the index of the current multiplayer object type
            if current == value[0]:
                bpy.context.selected_objects[0]['object_type'] = i  # Set the object type property based on index

    # Define various custom properties for Forge objects
    shapeObject: StringProperty()  # Store the name of the shape object
    objectPlacementFlags: EnumProperty(name="Physics", description="Physics mode", default='PHASED',
        items= [
            ('NORMAL', "Normal", "Affected by gravity and movable"),
            ('FIXED', "Fixed", "Unaffected by gravity"),
            ('PHASED', "Phased", "Unaffected by gravity and collisionless"),
        ]
    )
    
    physics: EnumProperty(name="Physics", description="Physics mode", default='PHASED',
        items= [
            ('NORMAL', "Normal", "Affected by gravity and movable"),
            ('FIXED', "Fixed", "Unaffected by gravity"),
            ('PHASED', "Phased", "Unaffected by gravity and collisionless"),
        ],
        update=UpdatePhysics  # Update function when the property changes
    )
    
    # Team, color, and other object-related properties
    team: EnumProperty(name="Team", description="Object team", items=teamEnum, default='NEUTRAL', update=UpdateColor)
    color: EnumProperty(name="Color", description="Object color", items=colorEnum, default='TEAM_COLOR', update=UpdateColor)
    colorIndex: IntProperty(default=8)  # Default color index
    spawnTime: IntProperty(name="Spawn Time", description="Time in seconds before the object spawns or respawns", min=0, max=255)  # Respawn time
    sharedStorage: IntProperty(name="Channel", description="Shared Storage (Channels, Ammo)", default=0)
    gameSpecific: BoolProperty(name="Game Specific", description="Should object exclusively spawn for current game mode")
    placeAtStart: BoolProperty(name="Place At Start", description="Should object spawn at start", default=True)

    # Custom properties for managing placement and variant flags
    Scene.placementFlagsStatus = BoolProperty(default=False)
    placementFlags: BoolVectorProperty(name="Prop name", description="Object Placement Flags", size=10, default=(False,) * 10)

    Scene.variantPlacementFlagStatus = BoolProperty(default=False)
    variantPlacementFlags: BoolVectorProperty(name="Prop name", description="Variant Placement Flags", size=8, default=(False,) * 8)

    # Multiplayer object type and symmetry settings
    mpObjectType: EnumProperty(name="Multiplayer Object Type", description="Shows different forge menu options", items=mp_object_types, default='ORDINARY', update=UpdateObjectType)
    symmetry: EnumProperty(name="Symmetry", description="Game mode symmetry",
        items=[
            ('BOTH', "Both", "Present in symmetric and asymmetric game modes (default)"),
            ('SYMMETRIC', "Symmetric", "Present only in symmetric game modes"),
            ('ASYMMETRIC', "Asymmetric", "Present only in asymmetric game modes"),
        ],
        default='BOTH'
    )
    
    # Shape-related properties (shape type, dimensions)
    shape: EnumProperty(name="Shape", description="Area shape", default='NONE', update=UpdateShape,
        items= [
            ('NONE', "None", ""), 
            ('CYLINDER', "Cylinder", ""), 
            ('BOX', "Box", "")
        ]
    )
    width: FloatProperty(name="Width", description="", unit='LENGTH', min=0, max=60.0, update=UpdateShape)
    length: FloatProperty(name="Length", description="", unit='LENGTH', min=0, max=60.0, update=UpdateShape)
    top: FloatProperty(name="Top", description="Distance to top from center", unit='LENGTH', min=0, max=60.0, update=UpdateShape)
    bottom: FloatProperty(name="Bottom", description="Distance to bottom from center", unit='LENGTH', min=0, max=60.0, update=UpdateShape)

    # Function to convert the current Blender object into a Forge-compatible object
    def ToForgeObject(self, forgeObject, blobj, inst=None):
        forgeObject.team = colorEnumToNumber[self.team]  # Assign the team number based on color enum
        forgeObject.color = colorEnumToNumber[self.color]  # Assign color
        forgeObject.flags = ForgeObjectFlags.HideAtStart*(not self.placeAtStart) + ForgeObjectFlags.GameSpecific*self.gameSpecific + physEnumToFlag[self.physics] + symmetryToFlag[self.symmetry]  # Set flags based on the object's properties
        forgeObject.spawnTime = self.spawnTime  # Set spawn time
        forgeObject.sharedStorage = self.sharedStorage  # Set shared storage (ammo, channels, etc.)
        forgeObject.shape = shapeEnumToNumber[self.shape]  # Convert shape enum to number
        '''forgeObject.shape_data.width = self.width
        forgeObject.shape_data.length = self.length
        forgeObject.shape_data.top = self.top
        forgeObject.shape_data.bottom = self.bottom'''
        m = inst.matrix_world  # Get the transformation matrix of the object
        forgeObject.forward = float3.fromVector(m.col[1])  # Set the forward direction based on matrix
        forgeObject.up = float3.fromVector(m.col[2])  # Set the up direction based on matrix
        forgeObject.position = float3.fromVector(m.col[3])  # Set the position based on matrix
        # print(forgeObject.position)  # Uncomment for debugging
