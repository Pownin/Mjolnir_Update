import bpy
from ctypes import *
import sys
import os
from importlib import import_module, reload

dir = os.path.dirname(bpy.data.filepath)
if dir not in sys.path:
    sys.path.append(dir)

import mjolnir.forge_types
reload(mjolnir.forge_types)
from mjolnir.forge_types import *

# Dynamically detect the map name from the Blender file name
map_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0].lower()

def load_map_items(map_name):
    """Load the corresponding item list based on the map name."""
    try:
        module_name = f"mjolnir.Items{map_name.capitalize()}"
        items_module = import_module(module_name)
        reload(items_module)
        items_dict_name = f"{map_name}Items"
        return getattr(items_module, items_dict_name, {})
    except (ImportError, AttributeError) as e:
        print(f"[ERROR] Failed to load items for '{map_name}': {e}")
        return {}

# Load items based on the current map name
mapItems = load_map_items(map_name)
print(f"[INFO] Loaded items for map '{map_name}': {mapItems}")

'''
*************************************

CLASSES

*************************************
'''

class H3_SaveGame(Structure):
    _pack_ = 1
    _fields_ = [
        ('unique_id', c_ulonglong),
        ('display_name', c_wchar * 16),
        ('description', c_char * 128),
        ('author', c_char * 16),
        ('e_saved_game_file_type', c_uint),
        ('author_is_xuid_online', c_ubyte),
        ('pad0', c_ubyte * 3),
        ('author_xuid', c_ubyte * 8),
        ('byte_size', c_ulonglong),
        ('date', c_ulonglong),
        ('length_seconds', c_int),
        ('e_campaign_id', c_int),
        ('e_map_id', c_int),
        ('e_game_engine_type', c_int),
        ('e_campaign_difficulty_level', c_int),
        ('hopper_id', c_short),
        ('pad', c_short),
        ('game_id', c_ulonglong),
        ('map_variant_version', c_short),
        ('scenario_objects', c_short),
        ('variant_objects', c_short),
        ('quotas', c_short),
        ('e_map_id_2', c_int),
        ('bounds', Bounds),
        ('e_scenario_game_engine', c_int),
        ('max_budget', c_float),
        ('spent_budget', c_float),
        ('showing_helpers', c_short),
        ('built_in', c_short),
        ('original_map_signature_hash', c_uint),
    ]

class H3_ForgeObject(Structure):
    _fields_ = [
        ('placement', c_ushort),
        ('reuse_timeout', c_ushort),
        ('object_index', c_int),
        ('helper_index', c_int),
        ('definition_index', c_int),
        ('transform', Transform),
        ('attached_id', c_int),
        ('attached_bsp_index', c_ushort),
        ('attached_type', c_ubyte),
        ('attached_source', c_ubyte),
        ('game_engine_flags', c_ubyte),
        ('scenario', c_ubyte),
        ('mp_placement', c_ubyte),
        ('team', c_ubyte),
        ('shared_storage', c_ubyte),
        ('spawn_time_seconds', c_ubyte),
        ('object_type', c_ubyte),
        ('shape', c_ubyte),
        ('shape_data', ShapeData)
    ]
    def __str__(self): 
        return f"{self.definition_index} {self.transform}"


class H3_MVAR(Structure):
    _pack_ = 1
    _fields_ = [
        ('data', H3_SaveGame),
        ('objects', H3_ForgeObject * 640),
        ('object_type_start_index', c_short * 14),
        ('quotas', Quota * 256),
        ('gamestate_indices', c_int * 80)
    ]

e_variant_object_placement_flags = [
    'Occupied Slot' ,
    'Object Edited' ,
    'Never Created Scenario Object' ,
    'Scenario Object Bit' ,
    'Placement Create At Rest Bit' ,
    'Scenario Object Removed' ,
    'Object Suspended' ,
    'Object Candy Monitored' ,
    'Spawns Attached' ,
    'Hard Attachment'
]

e_variant_placement_flags = [
    'Unique Spawn Bit',
    'Not Initially Placed Bit',
    'Symmetric Placement',
    'Asymmetric Placement',
    'Timer Starts On Death',
    'Timer Starts On Disturbance',
    'Object Fixed',
    'Object Phased'
]

mp_object_types = [
    ('ORDINARY', 'Ordinary ',''),
    ('WEAPON', 'Weapon',''),
    ('GRENADE', 'Grenade',''),
    ('PROJECTILE', 'Projectile',''),
    ('POWERUP', 'Powerup',''),
    ('EQUIPMENT', 'Equipment',''),
    ('LIGHTVEHICLE', 'Light Land Vehicle',''),
    ('HEAVYVEHICLE', 'Heavy Land Vehicle',''),
    ('FLYINGVEHICLE', 'Flying Vehicle',''),
    ('2WAY', 'Teleporter 2Way',''),
    ('SENDER', 'Teleporter Sender',''),
    ('RECEIVER', 'Teleporter Receiver',''),
    ('SPAWNLOCATION', 'Player Spawn Location',''),
    ('RESPAWNZONE', 'Player Respawn Zone',''),
    ('ODDBALLSPAWN', 'Oddball Spawn Location',''),
    ('FLAGSPAWN', 'Ctf Flag Spawn Location',''),
    ('TARGETSPAWN', 'Target Spawn Location',''),
    ('FLAGRETURN', 'Ctf Flag Return Area',''),
    ('KOTHHILL', 'Koth Hill Area',''),
    ('INFECTIONSAFEAREA', 'Infection Safe Area',''),
    ('TERRITORY', 'Territory Area',''),
    ('VIPAREA', 'Vip Influence Area',''),
    ('VIPDESTINATION', 'Vip Destination Zone',''),
    ('JUGGERNAUTDESTINATION', 'Juggernaut Destination Zone','')
]

'''
*************************************

FUNCTIONS

*************************************
'''

def createForgeObject(context, itemName, i=None, data=None):
    """Create a forge object with a name based on its index."""
    name = itemName if i is None else f"{i} - {itemName}"
    blenderObject = bpy.data.objects.new(name, data)
    context.collection.objects.link(blenderObject)
    blenderObject['isForgeObject'] = True
    blenderObject.forge.object = blenderObject.name
    if itemName in bpy.data.collections:
        blenderObject.instance_collection = bpy.data.collections[itemName]
        blenderObject.instance_type = 'COLLECTION'
        blenderObject.empty_display_size = 0.0001
    else:
        blenderObject.empty_display_type = 'ARROWS'
        blenderObject.empty_display_size = 0.5
    return blenderObject


def getItemName(index):
    """Retrieve item name from the dynamically loaded map items."""
    item_name = mapItems.get(index, 'Unknown')
    if item_name == 'Unknown':
        print(f"[INFO] Index {index} not found in items list.")
    return item_name
