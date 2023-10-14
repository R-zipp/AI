import bpy

# .blend 파일을 불러옵니다.
blend_file = 'floorplan1.blend'
bpy.ops.wm.open_mainfile(filepath=blend_file)

# .fbx 파일로 내보냅니다.
fbx_file = 'floorplan.fbx'
bpy.ops.export_scene.fbx(filepath=fbx_file)

# Blender 세션을 종료합니다.
bpy.ops.wm.quit_blender()