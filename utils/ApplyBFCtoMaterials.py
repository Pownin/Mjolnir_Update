import bpy

# Loop through all materials in the Blender scene
for mat in bpy.data.materials:
    if mat and mat.use_nodes:  # Ensure material uses nodes
        if hasattr(mat, 'blend_method'):  # Ensure property exists
            mat.use_backface_culling = True  # Enable backface culling
            print(f"Enabled Backface Culling for: {mat.name}")

print("✅ Backface Culling has been applied to all materials!")
