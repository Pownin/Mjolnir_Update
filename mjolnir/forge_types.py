# Importing necessary modules from Blender, math libraries, and ctypes for C-style structures
import bpy, blf, enum  # Blender, Blender Font Drawing, Enum for creating enumerations
from bpy.props import *  # Importing property types to define custom properties for Blender objects
from mathutils import *  # Math utilities for 3D vectors, matrices, etc.
from ctypes import *  # Ctypes for defining C-style structures and accessing DLLs
from math import *  # Basic math functions

# Function to invert a dictionary (swap keys and values)
def inverseDict(dict):
    invDict = {}  # Create an empty dictionary
    for key, val in dict.items():  # Loop through the dictionary items
        if val not in invDict: 
            invDict[val] = key  # Swap the key and value
    return invDict  # Return the inverted dictionary

'''
*************************************

CORE CLASSES

*************************************
'''

# Class to represent a 3D vector with x, y, z components
class float3(Structure):
    _fields_ = [ 
        ('x', c_float),  # X component of the vector
        ('y', c_float),  # Y component of the vector
        ('z', c_float)   # Z component of the vector
    ]
    
    # Cross product with another vector
    def cross(self, other): 
        return float3(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)

    # Convert from a mathutils.Vector to float3
    def fromVector(vec):
        return float3(vec.x, vec.y, vec.z)

    # Convert this float3 to a mathutils.Vector
    def toVector(self): 
        return Vector((self.x, self.y, self.z))

    # String representation of the float3
    def __str__(self): 
        return "(%.2f, %.2f, %.2f)" % (self.x, self.y, self.z)

# Class to represent a transform with position, forward, and up vectors
class Transform(Structure):
    _fields_ = [
        ('position', float3),  # Position vector
        ('forward', float3),   # Forward direction vector
        ('up', float3)         # Up direction vector
    ]
    
    # String representation of the transform
    def __str__(self):
        return "%s %s %s" % (self.position, self.forward, self.up)

    # Convert the transform to a 4x4 matrix for use in Blender
    def toMatrix(self):
        fwd = self.forward  # Forward direction
        up = self.up        # Up direction
        right = fwd.cross(up)  # Calculate the right vector using the cross product
        pos = self.position  # Position vector
        # Return a 4x4 transformation matrix
        return Matrix(((right.x, fwd.x, up.x, pos.x),
                       (right.y, fwd.y, up.y, pos.y),
                       (right.z, fwd.z, up.z, pos.z),
                       (0, 0, 0, 1)))

# Class to represent a range with minimum and maximum values
class Range(Structure):
    _fields_ = [ 
        ('min', c_float),  # Minimum value
        ('max', c_float)   # Maximum value
    ]
    
    # String representation of the range
    def __str__(self): 
        return "(%.2f, %.2f)" % (self.min, self.max)

# Class to represent bounds in 3D space (ranges in x, y, z directions)
class Bounds(Structure):
    _fields_ = [
        ('x', Range),  # Range along the x-axis
        ('y', Range),  # Range along the y-axis
        ('z', Range)   # Range along the z-axis
    ]
    
    # String representation of the bounds
    def __str__(self):
        return "(%s, %s, %s)" % (self.x, self.y, self.z)

'''
*************************************

CLASSES

*************************************
'''

# Class to represent shape data for an object (dimensions)
class ShapeData(Structure):
    _fields_ = [
        ('width', c_float),   # Width of the shape
        ('length', c_float),  # Length of the shape
        ('top', c_float),     # Distance from the center to the top
        ('bottom', c_float)   # Distance from the center to the bottom
    ]

# Enum class to represent different physics flags for a Forge object
class ForgeObjectFlags(enum.IntFlag):
    PhysicsNormal = 0b00000000  # Normal physics (affected by gravity)
    PhysicsFixed  = 0b01000000  # Fixed physics (no gravity)
    PhysicsPhased = 0b11000000  # Phased physics (no gravity or collision)
    PhysicsMask   = 0b11000000  # Mask to filter physics flags
    GameSpecific  = 0b00100000  # Object specific to a game mode
    Asymmetric    = 0b00001000  # Asymmetric object (for asymmetric game modes)
    Symmetric     = 0b00000100  # Symmetric object (for symmetric game modes)
    SymmetryMask  = 0b00001100  # Mask to filter symmetry flags
    HideAtStart   = 0b00000010  # Hide object at the start of the game

# Class to represent object quota limits in the game
class Quota(Structure):
    _fields_ = [
        ('object_definition_index', c_int),  # Index of the object's definition
        ('min_count', c_ubyte),  # Minimum allowed count
        ('max_count', c_ubyte),  # Maximum allowed count
        ('count', c_ubyte),      # Current count
        ('max_allowed', c_ubyte),  # Maximum allowed in the game
        ('price', c_float),      # Price of the object (game-specific)
    ]

# Enum to represent the different games in MCC (Master Chief Collection)
class MCC_Game(enum.Enum):
    NoGame = 0     # No game selected
    HaloReach = 1  # Halo: Reach game
    Halo3 = 2      # Halo 3 game

# Enum class to represent different placement flags for Forge objects
class PlacementFlags(enum.IntFlag):
    OCCUPIED_SLOT = 1  # Object is occupying a slot
    OBJECT_EDITED = 2  # Object has been edited
    NEVER_CREATED_SCENARIO_OBJECT = 4  # Scenario object never created
    SCENARIO_OBJECT_BIT = 8  # Flag for scenario objects
    PLACEMENT_CREATE_AT_REST_BIT = 16  # Create object at rest
    SCENARIO_OBJECT_REMOVED = 32  # Scenario object was removed
    OBJECT_SUSPENDED = 64  # Object is suspended
    OBJECT_CANDY_MONITORED = 128  # Object is candy-monitored
    SPAWNS_ATTACHED = 256  # Object spawns attached
    HARD_ATTACHMENT = 512  # Object has a hard attachment

'''
*************************************

ENUMS

*************************************
'''

# Dictionary to map color numbers to color names
colorNumberToEnum = { 
    0: 'RED',
    1: 'BLUE',
    2: 'GREEN',
    3: 'ORANGE',
    4: 'PURPLE',
    5: 'YELLOW',
    6: 'BROWN',
    7: 'PINK',
    8: 'NEUTRAL',
    255: 'TEAM_COLOR'
}

# Dictionary to map physics flags to their names
physicsFlags = {
    ForgeObjectFlags.PhysicsNormal: 'NORMAL',  # Normal physics
    ForgeObjectFlags.PhysicsFixed: 'FIXED',    # Fixed physics
    ForgeObjectFlags.PhysicsPhased: 'PHASED'   # Phased physics
}

# Dictionary to map symmetry flags to their names
symmetryFlags = {
    ForgeObjectFlags.Symmetric: 'SYMMETRIC',  # Symmetric
    ForgeObjectFlags.Asymmetric: 'ASYMMETRIC',  # Asymmetric
    ForgeObjectFlags.Symmetric + ForgeObjectFlags.Asymmetric: 'BOTH'  # Both symmetric and asymmetric
}

# Dictionary to map shape numbers to shape names
shapeNumberToEnum = { 
    0: 'NONE',      # No shape
    1: 'SPHERE',    # Sphere shape
    2: 'CYLINDER',  # Cylinder shape
    3: 'BOX'        # Box shape
}

# Enum to represent team colors and their names/icons in Blender's UI
teamEnum = [
    ('RED', "Red", "", 'SEQUENCE_COLOR_01', 0),
    ('BLUE', "Blue", "", 'SEQUENCE_COLOR_05', 1),
    ('GREEN', "Green", "", 'SEQUENCE_COLOR_04', 2),
    ('ORANGE', "Orange", "", 'SEQUENCE_COLOR_02', 3),
    ('PURPLE', "Purple", "", 'SEQUENCE_COLOR_06', 4),
    ('YELLOW', "Yellow", "", 'SEQUENCE_COLOR_03', 5),
    ('BROWN', "Brown", "", 'SEQUENCE_COLOR_08', 6),
    ('PINK', "Pink", "", 'SEQUENCE_COLOR_07', 7),
    ('NEUTRAL', "Neutral", "", 'SEQUENCE_COLOR_09', 9)
]

# Enum to represent color options including 'Team Color'
colorEnum = teamEnum + [('TEAM_COLOR', "Team", "", 'COMMUNITY', 10)]

# Tuple to represent teleporter types
teleporterTypes = (12, 13, 14)  # Teleporter types (in-game object types)

# Invert the color, physics, symmetry, and shape dictionaries for reverse lookups
colorEnumToNumber = inverseDict(colorNumberToEnum)
physEnumToFlag = inverseDict(physicsFlags)
symmetryToFlag = inverseDict(symmetryFlags)
colorEnumToNumber = inverseDict(colorNumberToEnum)
shapeEnumToNumber = inverseDict(shapeNumberToEnum)
