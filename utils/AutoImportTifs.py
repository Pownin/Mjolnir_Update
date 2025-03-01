import bpy
import os
import re

def find_texture_file(root_folder, base_material_name):
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower() == base_material_name.lower() + ".tif":
                return os.path.join(dirpath, filename)
    return None

def get_base_material_name(material_name):
    return re.sub(r'\.\d+$', '', material_name)

def apply_textures_from_folder(texture_folder):
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                mat = slot.material
                if mat and mat.name:
                    base_material_name = get_base_material_name(mat.name)
                    texture_path = find_texture_file(texture_folder, base_material_name)
                    
                    if texture_path:
                        if not mat.node_tree:
                            mat.use_nodes = True
                        
                        nodes = mat.node_tree.nodes
                        links = mat.node_tree.links
                        
                        for node in nodes:
                            if node.type == 'TEX_IMAGE':
                                nodes.remove(node)
                        
                        # Create new image texture node
                        tex_node = nodes.new(type='ShaderNodeTexImage')
                        tex_node.image = bpy.data.images.load(texture_path)
                        
                        bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                        if bsdf:
                            links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
                        
                        print(f"Applied texture: {texture_path} to material: {mat.name}")
                    else:
                        print(f"Texture file not found for material: {mat.name}")

# folder path
texture_folder = "E:\Map&Block Models\Foundry\Shaders"
apply_textures_from_folder(texture_folder)