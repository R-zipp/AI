import bpy
import os
import io
import math
import contextlib
from mathutils import Vector

import sys
current_script_path = os.path.realpath(__file__)
current_directory = os.path.dirname(current_script_path)
sys.path.append(current_directory)

import const


class BlendToFBX():
    def __init__(self) -> None:
        self.default_path = const.TEXTURE_FILE_PATH
        self.desired_height = const.DESIRED_HEIGHT
        self.tiling_factor = const.TILING_FACTOR


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


    def create_detailed_material(self, texture_paths, material_name="DetailedMaterial"):
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        bsdf = nodes.get('Principled BSDF')

        mapping_nodes = {}
        for texture_type, path in texture_paths.items():
            tex_image = nodes.new('ShaderNodeTexImage')
            tex_image.image = bpy.data.images.load(path)

            mapping = nodes.new('ShaderNodeMapping')
            mapping.vector_type = 'TEXTURE'
            mapping.inputs['Scale'].default_value = (self.tiling_factor[0], self.tiling_factor[1], 1)

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
                
            mapping_nodes[texture_type] = mapping

        return mat, mapping_nodes


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
        
    
    def is_horizontal(self, obj):
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        
        width = max(bbox, key=lambda v: v.x).x - min(bbox, key=lambda v: v.x).x
        height = max(bbox, key=lambda v: v.y).y - min(bbox, key=lambda v: v.y).y
        depth = max(bbox, key=lambda v: v.z).z - min(bbox, key=lambda v: v.z).z
        # print(f'width : {width}, height : {height}, depth : {depth}')
        
        return max([width, height]) > depth

    
    def create_rotated_material(self, base_material, rotation_angle):
        # 기본 재질 복제
        rotated_material = base_material.copy()
        rotated_material.name = base_material.name + "_rotated"

        # 모든 mapping 노드를 회전
        for node in rotated_material.node_tree.nodes:
            if node.type == 'MAPPING':
                node.inputs['Rotation'].default_value[2] = rotation_angle

        return rotated_material
    
    
    def postprocessing(self, obj):
        # Auto UV Mapping
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')
    
    
    def blend_to_fbx(self, blend_file, fbx_dir, texture_name=None, size_multiplier=1):
        self.size_multiplier = size_multiplier

        os.makedirs(fbx_dir, exist_ok=True)
        name, extension = blend_file.split("/")[-1].split(".")

        bpy.ops.wm.open_mainfile(filepath=blend_file)
        bpy.ops.object.select_all(action='DESELECT')

        if texture_name:
            texture_paths = self.texture_loader(texture_name)
            detailed_material, mapping_nodes = self.create_detailed_material(texture_paths)
            detailed_material_rotated = self.create_rotated_material(detailed_material, math.radians(90))
        else:
            detailed_material = self.create_white_material()
            mapping_nodes = {}
        white_material = self.create_white_material()

        # Mesh objects
        MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']

        for OBJS in MSH_OBJS:
            OBJS.select_set(state=True)
            bpy.context.view_layer.objects.active = OBJS

            if 'Wall' in OBJS.name and 'Box' in OBJS.name:
                # self.apply_shared_material(OBJS, detailed_material)
                if self.is_horizontal(OBJS):
                    self.apply_shared_material(OBJS, detailed_material_rotated)
                else:
                    self.apply_shared_material(OBJS, detailed_material)
            if 'VertWalls' in OBJS.name:
                self.apply_shared_material(OBJS, white_material)

        # Joins objects
        bpy.ops.object.join()

        # Get the current active object
        obj = bpy.context.object

        self.scale_change(obj)
        
        self.postprocessing(obj)

        # add triangulate 
        self.triangulate_object(obj)

        fbx_file = os.path.join(fbx_dir, f'{name}_s{size_multiplier}_h{self.desired_height}_{texture_name}.fbx')
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
    converter = BlendToFBX()
    
    blend_path = os.environ.get('BLEND_PATH', 'default')
    size_multiplier = os.environ.get('SIZE_MULTIPLIER', 'default')
    
    fbx_dir = const.FBX_DIRECTORY
    fbx_file_path = converter.blend_to_fbx(
                                            blend_path, 
                                            fbx_dir, 
                                            texture_name='plaster_2K', 
                                            size_multiplier=float(size_multiplier), 
                                            ).replace('\\', '/')
    print(fbx_file_path)