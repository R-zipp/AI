import bpy
import os
import io
import contextlib


class BlendToFBX():
    def __init__(self) -> None:
        pass


    def get_file_name(self, file_name):
        name, extension = file_name.split("/")[-1].split(".")

        return name, extension


    def blend_to_fbx(self, blend_file, fbx_dir):
        name, extension = self.get_file_name(blend_file)

        bpy.ops.wm.open_mainfile(filepath=blend_file)

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

        fbx_file = os.path.join(fbx_dir, f'{name}_join_all.fbx')

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