import bpy, blf, enum, time
from bpy.types import Operator
from bpy.props import *
from mathutils import *
from ctypes import *
from math import *

# Function to create an array modifier for duplicating objects
# The type parameter defines the kind of array (e.g., OBJECT, CONST, CURVE)
# count sets the number of duplicates, offset specifies the distance between them,
# and rotation defines the rotational offset for each duplicate. curveLen is used for CURVE type.
def arrayModifier(context, type, count=3, offset=(1,0,0), rotation=(0,0,0), curveLen=5):
    # Get the active object and its location
    sourceObject = context.active_object
    loc = sourceObject.location
    size = 1

    # Check if the object is part of a collection for instancing
    collection = sourceObject.instance_collection
    if collection != None:
        name = collection.name
        # Loop through objects in the collection to find the largest dimension (y-axis)
        for instanced_object in collection.objects:
            s = instanced_object.dimensions.y
            if s > size: size = s
    else: 
        name = sourceObject.name

    # Add a new plane object at the source object's location to serve as the array holder
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=loc, size=1)
    arrayObject = masterParent = context.object
    arrayObject.name = "%s Array" % name  # Name the array based on the source object
    arrayObject.instance_type = 'FACES'
    arrayObject.show_instancer_for_viewport = arrayObject.show_instancer_for_render = False
    arrayObject.select_set(True)

    # Add an Array modifier to the newly created array object
    bpy.ops.object.modifier_add(type='ARRAY')
    modifier = arrayObject.modifiers["Array"]
    modifier.show_on_cage = True
    modifier.use_relative_offset = False  # Disable relative offset to use constant/object offset

    # If the array type is not 'CONST', create a parent object to hold the array
    if type != 'CONST':
        parentObject = masterParent = bpy.data.objects.new("%s Array Holder" % name, None)
        context.collection.objects.link(parentObject)  # Link the holder to the collection
        parentObject.location = loc
        parentObject.empty_display_size = 2
        arrayObject.parent = parentObject  # Set parent to the array holder
        arrayObject.location = (0,0,0)  # Set the array holder's location

    # If the type is 'OBJECT', create an empty object for offset and rotation
    if type == 'OBJECT':
        offsetObj = bpy.data.objects.new("%s Array Offset" % name, None)
        context.collection.objects.link(offsetObj)  # Link the offset object to the collection
        offsetObj.empty_display_size = size  # Set its size
        offsetObj.location = offset  # Set the offset position
        offsetObj.rotation_euler = rotation  # Apply rotation offset
        offsetObj.parent = parentObject  # Set it as the child of the array holder
        offsetObj.select_set(True)

        # Configure the modifier to use the object offset method
        modifier.use_constant_offset = False
        modifier.use_object_offset = True
        modifier.offset_object = offsetObj

    # If the array type is not 'OBJECT', use constant offset instead
    else:
        modifier.use_constant_offset = True
        modifier.constant_offset_displace = offset

    # If the array type is 'CURVE', add a curve to follow for the array
    if type == 'CURVE':
        bpy.ops.object.modifier_add(type='CURVE')  # Add a curve modifier
        curveModifier = arrayObject.modifiers["Curve"]
        curveModifier.show_on_cage = curveModifier.show_in_editmode = True
        
        # Create a new Bezier curve and configure it
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=False, align='WORLD', location=(0,0,0), radius=curveLen)
        curve = bpy.context.object
        curve.name = "%s Curve" % name  # Name the curve based on the source object
        curve.parent = parentObject  # Set the parent to the array holder
        curve.select_set(True)
        curveData = curve.data
        curveData.twist_mode = 'Z_UP'  # Set the curve's twist mode to Z-up
        curveData.use_deform_bounds = curve.show_in_front = True  # Enable deformation along bounds

        # Configure the array modifier to fit along the curve
        modifier.fit_type = 'FIT_CURVE'
        modifier.curve = curve
        curveModifier.object = curve

        arrayObject.select_set(True)
    else:
        modifier.count = count  # Set the number of duplicates for non-curve arrays

    # Set the rotation of the parent object to match the source object
    masterParent.rotation_euler = sourceObject.rotation_euler

    # Set the source object to be the child of the array object and reset its transformations
    sourceObject.parent = arrayObject
    sourceObject.location = (0,0,0)
    sourceObject.rotation_euler = (0,0,0)
    sourceObject.display_type = 'BOUNDS'
    sourceObject.select_set(True)

    # If the type is not 'CONST', also select the parent object
    if type != 'CONST': 
        parentObject.select_set(True)
