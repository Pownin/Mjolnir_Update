import bpy
import os

def export_material_names(filepath):
    material_names = [mat.name for mat in bpy.data.materials if mat]
    
    with open(filepath, 'w') as file:
        for name in material_names:
            file.write(name + '\n')
    
    print(f"Exported {len(material_names)} material names to {filepath}")

default_path = os.path.join(bpy.path.abspath('//'), 'material_names.txt')
export_material_names(default_path)