import os
from os.path import exists
import bpy
from mathutils import Euler
import math

os.system('cls')

# Location to all JMS files
jms_directory = 'D:\\Program Files x86\\Steam\\steamapps\\common\\H3EK\\sandbox\\'

# get list of all files in directory
file_list = sorted(os.listdir(jms_directory))

def checkName(name):
    if name.endswith('.jms') and '_physics' not in name:
        return True
    return False

# Get a list of files ending in 'jms' and not the phmo
obj_list = [item for item in file_list if checkName(item)]

# Collapses all the newly created collections so it's cleaner to look at
def toggle_collapse(context, state):
    area = next(a for a in context.screen.areas if a.type == 'OUTLINER')
    bpy.ops.outliner.show_hierarchy({'area': area}, 'INVOKE_DEFAULT')
    for i in range(state):
        bpy.ops.outliner.expanded_toggle({'area': area})
    area.tag_redraw()

def importJMS(file):
    old_objs = set(bpy.context.scene.objects)
    file_path = os.path.join(jms_directory, file)
    bpy.ops.import_scene.jms(filepath = file_path)
    return set(bpy.context.scene.objects) - old_objs

def getFixedName(name):
    s_name = name.split('_')
    capitalized = []
    for s in s_name:
        capitalized.append(s.capitalize())
    return ' '.join(capitalized)

def linkObject(collection,obj):
    obj.rotation_euler = Euler((0,0,math.radians(90)), 'XYZ')
    collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)

def grouping(objs,n, physics = False):
    n = getFixedName(n)
    collection = bpy.data.collections.get(n)
    parent = bpy.data.collections.get(n)

    if collection is None:
        collection = bpy.context.blend_data.collections.new(name=n)
        bpy.context.collection.children.link(collection)

    if physics != False:
        p_name = 'p_'+n
        collection = bpy.context.blend_data.collections.new(name=p_name)
        
    for o in objs:
        if o.type == 'ARMATURE':
            for child in o.children:
                if child.name.startswith('#') != True:
                    linkObject(collection,child)

        elif o.parent == None and child.name.startswith('#') != True:
            linkObject(collection,o)

    bpy.context.scene.collection.objects.unlink(o)
    
    if physics == True:
        collection.hide_viewport = True
        parent.children.link(collection)

    
count = 0
# loop through the strings in obj_list and add the files to the scene
for item in filtered:
    new_objects = importJMS(item)
    grouping(new_objects, item.replace('.jms',''))

    # Check if phmo file exists
    if exists(os.path.join(jms_directory, item.replace('.jms', '_physics.jms'))):
        item = item.replace('.jms', '_physics.jms')
        new_objects = importJMS(item)
        grouping(new_objects, item.replace('.jms',''), True)

    print('Imported: '+ item +' | '+ str(count) + ' of ' + str(len(filtered)))
    count+=1


bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)
toggle_collapse(bpy.context, 2)