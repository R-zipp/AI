import bpy
import os
import io
import contextlib


class BlendToFBX():
    def __init__(self) -> None:
        pass


    def blend_to_fbx(self, blend_file, fbx_dir, size_multiplier=1, desired_height=1):
        os.makedirs(fbx_dir, exist_ok=True)
        name, extension = blend_file.split("/")[-1].split(".")

        bpy.ops.wm.open_mainfile(filepath=blend_file)

        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')

        # Mesh objects
        MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']

        for OBJS in MSH_OBJS:
            #Select all mesh objects
            OBJS.select_set(state=True)

            #Makes one active
            bpy.context.view_layer.objects.active = OBJS

        # Joins objects
        bpy.ops.object.join()
        
        # Get the current active object
        obj = bpy.context.object
        
        # Reset the scale
        obj.scale = (1, 1, 1)

        # Apply the scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        
        new_dimensions = [obj.dimensions.x*size_multiplier, obj.dimensions.y*size_multiplier, desired_height]
        obj.dimensions = new_dimensions
        
        # print(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)

        fbx_file = os.path.join(fbx_dir, f'{name}_s{size_multiplier}_h{desired_height}.fbx')

        fake_stdout = io.StringIO()
        with contextlib.redirect_stdout(fake_stdout):
            print("이 메시지는 보이지 않습니다.")
            bpy.ops.export_scene.fbx(filepath=fbx_file)

        bpy.ops.wm.quit_blender()

        return fbx_file





if __name__ == '__main__':
    blend_file = 'statics/blend_file/floorplan30.blend'
    fbx_dir = 'statics/fbx_file'

    converter = BlendToFBX()
    converter.blend_to_fbx(blend_file, fbx_dir)