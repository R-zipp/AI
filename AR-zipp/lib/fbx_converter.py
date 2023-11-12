import bpy
import os
import io
import contextlib

import lib.const as const


class BlendToFBX():
    def __init__(self) -> None:
        self.default_path = const.TEXTURE_FILE_PATH


    def texture_loader(self, texture_name):
        
        texture_list = os.listdir(os.path.join(self.default_path, texture_name))
        
        texture_paths = {}
        for texture in texture_list:
            if 'Albedo' in texture:
                texture_paths['albedo'] = f'{self.default_path}{texture_name}/{texture}'
            if 'ao' in texture:
                texture_paths['ao'] = f'{self.default_path}{texture_name}/{texture}'
            if 'displacement' in texture:
                texture_paths['displacement'] = f'{self.default_path}{texture_name}/{texture}'
            if 'normal' in texture:
                texture_paths['normal'] = f'{self.default_path}{texture_name}/{texture}'
            if 'roughness' in texture:
                texture_paths['roughness'] = f'{self.default_path}{texture_name}/{texture}'
        
        return texture_paths


    def create_white_material(self, material_name="WhiteMaterial"):
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)  # RGBA 값 (흰색)
        return mat


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


    def scale_change(self, obj):
        # Reset the scale
        obj.scale = (1, 1, 1)

        # Apply the scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Apply new dimensions
        new_dimensions = [obj.dimensions.x*self.size_multiplier, obj.dimensions.y*self.size_multiplier, self.desired_height]
        obj.dimensions = new_dimensions
        
    
    def triangulate_object(self, obj):
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        
    def postprocessing(self, obj):
        # Auto UV Mapping
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        
    def blend_to_fbx(self, blend_file, fbx_dir, texture_name=None, size_multiplier=1, desired_height=1):
        self.size_multiplier = size_multiplier
        self.desired_height = desired_height

        os.makedirs(fbx_dir, exist_ok=True)
        name, extension = blend_file.split("/")[-1].split(".")

        bpy.ops.wm.open_mainfile(filepath=blend_file)
        bpy.ops.object.select_all(action='DESELECT')

        if texture_name:
            texture_paths = self.texture_loader(texture_name)
            detailed_material = self.create_detailed_material(texture_paths, tiling_factor=(0.1, 0.1))
        else:
            detailed_material = self.create_white_material()
        
        # Mesh objects
        MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']

        for OBJS in MSH_OBJS:
            OBJS.select_set(state=True)
            bpy.context.view_layer.objects.active = OBJS

            if 'Wall' in OBJS.name and 'Box' in OBJS.name:
                self.apply_shared_material(OBJS, detailed_material)

        # Joins objects
        bpy.ops.object.join()

        # Get the current active object
        obj = bpy.context.object

        self.scale_change(obj)
        
        self.postprocessing(obj)

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