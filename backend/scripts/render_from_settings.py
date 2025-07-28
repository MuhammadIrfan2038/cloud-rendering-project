import bpy
import os
import sys

# Ambil argumen CLI setelah -- (biasanya path output)
output_dir = sys.argv[-1]


# Siapkan folder output
os.makedirs(output_dir, exist_ok=True)

# Ambil setting dari scene
scene = bpy.context.scene
frame_start = scene.frame_start
frame_end = scene.frame_end
image_format = scene.render.image_settings.file_format  # Misal: PNG, JPEG

# Logging untuk debug
print("📦 Output dir:", scene.render.filepath)
print("🖼️ Format:", image_format)
print("🎞️ Frame range:", frame_start, "-", frame_end)

# Pastikan Blender menyimpan ke direktori yang kita inginkan
bpy.context.scene.render.filepath = os.path.join(output_dir, "frame_")

# Jalankan render animation (dari frame_start sampai frame_end)
bpy.ops.render.render(animation=True)
