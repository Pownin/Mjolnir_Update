import bpy

bl_info = {
    "name": "Forge Object Duplicate",
    "author": "Exhibit",
    "version": (0, 1)
}

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


class OBJECT_OT_CustomOp(bpy.types.Operator):
    """Forge Object Duplicate. Shift+D"""
    bl_idname = "object.simple_operator"
    bl_label = "Forge Dupe"

    def execute(self, context):
        duplicate()
        return {'FINISHED'}


addon_keymaps = []

def is_set(x, n):
    return x & 2 ** n != 0 

def clear_bit(value, bit):
    return value & ~(1<<bit)

def setBit(n, bitIndex):
    bitMask = 1 << bitIndex
    return n | bitMask
        
def getIndex():
    objectCount = 0
    for instance in bpy.context.evaluated_depsgraph_get().object_instances:
        if tryGetForgeObjectFromInstance(instance) != None: 
            objectCount += 1
    return int(objectCount)+1

def duplicate():
    print("Duplicating {count} objects".format(count = len(bpy.context.selected_objects)))
    for obj in bpy.context.selected_objects:
        copiedObject = obj.copy()
        if copiedObject.forge.placementFlags[3] == True:
            copiedObject.forge.placementFlags[3] = False # is scenario
            copiedObject.forge.placementFlags[1] = True # is edited
            
        newIndex = getIndex()
        type = obj.name[obj.name.rindex('- ')+2:]
        newName = str(newIndex) + ' - ' + type
        copiedObject.name = newName
        obj.select_set(False)
        bpy.context.collection.objects.link(copiedObject)
        bpy.context.view_layer.objects.active = copiedObject
    
def register():
    bpy.utils.register_class(OBJECT_OT_CustomOp)
    
    # Add the hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(OBJECT_OT_CustomOp.bl_idname, type='E', value='PRESS', shift=True)
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_CustomOp)
    
    # Remove the hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
