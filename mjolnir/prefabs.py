import bpy
from importlib import reload
from mjolnir.utils import *
import mjolnir.halo3
reload(mjolnir.utils)
reload(mjolnir.halo3)
from mjolnir.utils import *
from mjolnir.halo3 import *

import json

def setFlags(value, bit):
    return (value>>bit) & 1

def ExportPrefab():
    print('Export')
    prefab = {
        "components": []
    }
    for obj in bpy.context.selected_objects:
        print(getFlagsVal(obj.forge.placementFlags))
        p = obj.location
        r = obj.rotation_euler
        component = {
            'placement': getFlagsVal(obj.forge.placementFlags),
            'definition_index': obj['definition_index'],
            'mp_placement':getFlagsVal(obj.forge.variantPlacementFlags),
            'spawn_time':obj['spawn_time_seconds'],
            'position': [p[0], p[1], p[2]],
            'rotation': [r[0], r[1], r[2]]
        }
        prefab["components"].append(component)
    # Writing to sample.json
    with open("./sample.json", "w") as outfile:
        json.dump(prefab, outfile)

def ImportPrefab():
    with open('./sample.json', 'r') as openfile:
        json_object = json.load(openfile)
        for obj in json_object["components"]:
            itemName = "%s (%d, %d, %d)" % (getItemName(obj['definition_index']),obj['definition_index'], -1, -1)
            if getItemName(obj['definition_index']) != 'Unknown':
                itemName = getItemName(obj['definition_index'])

            blenderObject = createForgeObject(bpy.context, itemName)

            for x in range(len(blenderObject.forge.placementFlags)):
                blenderObject.forge.placementFlags[x] = setFlags(obj['placement'], x)

            for x in range(len(blenderObject.forge.variantPlacementFlags)):
                blenderObject.forge.variantPlacementFlags[x] = setFlags(obj['mp_placement'], x)

            blenderObject.name = blenderObject.name

            blenderObject['spawn_time_seconds'] = obj['spawn_time']
            p = obj['position']
            blenderObject.location = (p[0], p[1], p[2])
            r = obj['rotation']
            blenderObject.rotation_euler = (r[0], r[1], r[2])
            bpy.context.view_layer.objects.active = blenderObject