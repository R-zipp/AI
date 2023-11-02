import bpy

# .blend 파일을 불러옵니다.
# blend_file = 'D:/workspace/Final_Project/FloorplanToBlender3d/Target/floorplan1.blend'
# blend_file = 'D:/workspace/Final_Project/FloorplanToBlender3d/Target/floorplan2.blend'
blend_file = 'floorplan_test.blend'
bpy.ops.wm.open_mainfile(filepath=blend_file)

# 현재 scene을 가져옵니다.
# scene = bpy.context.scene

# obs = []
# for ob in scene.objects:
#     # whatever objects you want to join...
#     if ob.type == 'MESH':
#         obs.append(ob)

# print(obs)
# bpy.ops.object.join(obs)
# bpy.ops.object.select_all(action='DESELECT')
# bpy.ops.object.select_all(action='SELECT')

# bpy.ops.object.join()
# obs = [ob for ob in scene.objects if ob.type == 'MESH']



#Deselect all
bpy.ops.object.select_all(action='DESELECT')

#Mesh objects
MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']

for OBJS in MSH_OBJS:
    #Select all mesh objects
    OBJS.select_set(state=True)

    #Makes one active
    bpy.context.view_layer.objects.active = OBJS

#Joins objects
bpy.ops.object.join()


# .fbx 파일로 내보냅니다.
fbx_file = 'floorplan_test_join.fbx'
bpy.ops.export_scene.fbx(filepath=fbx_file)

# Blender 세션을 종료합니다.
bpy.ops.wm.quit_blender()