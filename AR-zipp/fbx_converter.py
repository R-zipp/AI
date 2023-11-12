import bpy
import os
import io
import contextlib


class BlendToFBX():
    def __init__(self) -> None:
        pass


    def create_detailed_material(self, texture_paths, material_name="DetailedMaterial", tiling_factor=(2, 2)):
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        bsdf = nodes.get('Principled BSDF')

        for texture_type, path in texture_paths.items():
            tex_image = nodes.new('ShaderNodeTexImage')
            tex_image.image = bpy.data.images.load(path)

            mapping = nodes.new('ShaderNodeMapping')
            mapping.vector_type = 'TEXTURE'
            mapping.inputs['Scale'].default_value = (tiling_factor[0], tiling_factor[1], 1)

            texCoord = nodes.new('ShaderNodeTexCoord')

            links = mat.node_tree.links
            links.new(texCoord.outputs['UV'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])

            if texture_type == 'albedo':
                links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
            elif texture_type == 'ao':
                # AO는 별도의 처리가 필요할 수 있습니다
                pass
            elif texture_type == 'displacement':
                material_output = nodes.get('Material Output')
                disp_node = nodes.new('ShaderNodeDisplacement')
                links.new(tex_image.outputs['Color'], disp_node.inputs['Height'])
                links.new(disp_node.outputs['Displacement'], material_output.inputs['Displacement'])
            elif texture_type == 'normal':
                normal_map = nodes.new('ShaderNodeNormalMap')
                links.new(tex_image.outputs['Color'], normal_map.inputs['Color'])
                links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
            elif texture_type == 'roughness':
                links.new(tex_image.outputs['Color'], bsdf.inputs['Roughness'])

        return mat



    def apply_shared_material(self, obj, shared_material):
        if obj.data.materials:
            obj.data.materials[0] = shared_material
        else:
            obj.data.materials.append(shared_material)


    def blend_to_fbx(self, blend_file, fbx_dir, size_multiplier=1, desired_height=1):

        os.makedirs(fbx_dir, exist_ok=True)
        name, extension = blend_file.split("/")[-1].split(".")

        bpy.ops.wm.open_mainfile(filepath=blend_file)
        bpy.ops.object.select_all(action='DESELECT')

        texture_paths = {
                        'albedo': 'D:/workspace/Final_Project/AR-zipp/texture/plaster_damaged_xevjddns/xevjddns_8K_Albedo.jpg',
                        'ao': 'D:/workspace/Final_Project/AR-zipp/texture/plaster_damaged_xevjddns/xevjddns_8K_AO.jpg',
                        'displacement': 'D:/workspace/Final_Project/AR-zipp/texture/plaster_damaged_xevjddns/xevjddns_8K_Displacement.jpg',
                        'normal': 'D:/workspace/Final_Project/AR-zipp/texture/plaster_damaged_xevjddns/xevjddns_8K_Normal.jpg',
                        'roughness': 'D:/workspace/Final_Project/AR-zipp/texture/plaster_damaged_xevjddns/xevjddns_8K_Roughness.jpg'
                        }
        detailed_material = self.create_detailed_material(texture_paths, tiling_factor=(0.1, 0.1))
        
        # Mesh objects
        MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']

        for OBJS in MSH_OBJS:
            OBJS.select_set(state=True)
            bpy.context.view_layer.objects.active = OBJS

            if 'Wall' in OBJS.name and 'Box' in OBJS.name:
                print(OBJS.name)
                self.apply_shared_material(OBJS, detailed_material)

        # Joins objects
        bpy.ops.object.join()

        # Get the current active object
        obj = bpy.context.object

        # Reset the scale
        obj.scale = (1, 1, 1)

        # Apply the scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Apply new dimensions
        new_dimensions = [obj.dimensions.x*size_multiplier, obj.dimensions.y*size_multiplier, desired_height]
        obj.dimensions = new_dimensions
        
        # Auto UV Mapping
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')

        # add triangulate 
        self.triangulate_object(obj)

        fbx_file = os.path.join(fbx_dir, f'{name}_s{size_multiplier}_h{desired_height}.fbx')

        with contextlib.redirect_stdout(io.StringIO()):
            bpy.ops.export_scene.fbx(
                                        filepath=fbx_file,
                                        axis_forward='-Z',
                                        axis_up='Y',
                                        use_selection=False,
                                        global_scale=1.0,
                                        apply_unit_scale=True,
                                        bake_space_transform=False,
                                        object_types={'MESH', 'ARMATURE'},
                                        use_mesh_modifiers=True,
                                        mesh_smooth_type='FACE',
                                        path_mode='COPY',
                                        embed_textures=True
                                    )

        bpy.ops.wm.quit_blender()

        return fbx_file




if __name__ == '__main__':
    blend_file = 'statics/blend_file/floorplan30.blend'
    fbx_dir = 'statics/fbx_file'

    converter = BlendToFBX()
    converter.blend_to_fbx(blend_file, fbx_dir)