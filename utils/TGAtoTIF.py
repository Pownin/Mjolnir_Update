import os
from PIL import Image

input_folder = r"D:\\SteamLibrary\\steamapps\\common\\Extracted bitmaps"  # Change to your TGA directory
output_folder = r"D:\\SteamLibrary\\steamapps\\common\\Extracted bitmaps\\Tifs"  # Change to where you want TIFs saved

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".tga"):
        tga_path = os.path.join(input_folder, filename)
        tif_path = os.path.join(output_folder, filename.replace(".tga", ".tif"))

        try:
            with Image.open(tga_path) as img:
                img.save(tif_path, format="TIFF", compression="tiff_lzw")
            print(f"Converted: {filename} -> {tif_path}")

        except Exception as e:
            print(f"Failed to convert {filename}: {e}")

print("✅ Conversion complete!")
