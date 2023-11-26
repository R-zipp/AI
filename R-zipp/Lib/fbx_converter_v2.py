import bpy
import os
import io
import contextlib

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
        # texture_list_low = [name.lower() for name in texture_list]
        
        texture_paths = {}
        for texture in texture_list:
            if 'albedo' in texture:
                texture_paths['albedo'] = f'{self.default_path}{texture_name}/{texture}'
            if 'ao' in texture:
                texture_paths['ao'] = f'{self.default_path}{texture_name}/{texture}'
            if 'displacement' in texture:
                texture_paths['displacement'] = f'{self.default_path}{texture_name}/{texture}'
            if 'normal' in texture:
                texture_paths['normal'] = f'{self.default_path}{texture_name}/{texture}'
            if 'roughness' in texture:
                texture_paths['roughness'] = f'{self.default_path}{texture_name}/{texture}'
            if 'glossiness' in texture:
                texture_paths['glossiness'] = f'{self.default_path}{texture_name}/{texture}'
            if 'bump' in texture:
                texture_paths['bumpmap'] = f'{self.default_path}{texture_name}/{texture}'
            if 'metalness' in texture:
                texture_paths['metalness'] = f'{self.default_path}{texture_name}/{texture}'
            if 'reflection' in texture:
                texture_paths['reflection'] = f'{self.default_path}{texture_name}/{texture}'

        return texture_paths


    def create_detailed_material(self, texture_paths, material_name="DetailedMaterial"):
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        bsdf = nodes.get('Principled BSDF')

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
                mix_node = nodes.new('ShaderNodeMixRGB')
                mix_node.blend_type = 'MULTIPLY'
                links.new(tex_image.outputs['Color'], mix_node.inputs[1])

                # Check if there is a link to the Base Color input
                base_color_links = bsdf.inputs['Base Color'].links
                if base_color_links:
                    base_color_link = base_color_links[0]  # Get the first link
                    links.new(base_color_link.from_socket, mix_node.inputs[2])
                    links.new(mix_node.outputs[0], bsdf.inputs['Base Color'])
                else:
                    # If no base color link, connect AO directly to Base Color
                    links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])

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

            elif texture_type == 'glossiness':
                invert_node = nodes.new('ShaderNodeInvert')
                links.new(tex_image.outputs['Color'], invert_node.inputs['Color'])
                links.new(invert_node.outputs['Color'], bsdf.inputs['Roughness'])

            elif texture_type == 'bump':
                bump_node = nodes.new('ShaderNodeBump')
                links.new(tex_image.outputs['Color'], bump_node.inputs['Height'])
                links.new(bump_node.outputs['Normal'], bsdf.inputs['Normal'])

            elif texture_type == 'metalness':
                links.new(tex_image.outputs['Color'], bsdf.inputs['Metallic'])
                
            elif texture_type == 'reflection':
                reflection_map = nodes.new('ShaderNodeTexImage')
                reflection_map.image = bpy.data.images.load(path)
                links.new(reflection_map.outputs['Color'], bsdf.inputs['Specular'])

        return mat


    def create_white_material(self, material_name="WhiteMaterial"):
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.7, 0.7)  # RGBA 값 (흰색)
        return mat
    
        
    def make_texture(self, texture_name):
        if texture_name:
            texture_paths = self.texture_loader(texture_name)
            detailed_material = self.create_detailed_material(texture_paths)

        else:
            detailed_material = self.create_white_material()
            # detailed_material_rotated = self.create_white_material()
        white_material = self.create_white_material()
        
        return detailed_material, white_material
    
    
    def apply_shared_material(self, obj, shared_material):
        if obj.data.materials:
            obj.data.materials[0] = shared_material
        else:
            obj.data.materials.append(shared_material)
            
            
    def apply_texture(self, mesh_objs):
        for OBJS in mesh_objs:
            OBJS.select_set(state=True)
            bpy.context.view_layer.objects.active = OBJS

            if 'Wall' in OBJS.name and 'Box' in OBJS.name:
                if OBJS.data.materials:
                    OBJS.data.materials[0] = self.detailed_material
                else:
                    OBJS.data.materials.append(self.detailed_material)
                self.apply_shared_material(OBJS, self.detailed_material)
            if 'VertWalls' in OBJS.name:
                self.apply_shared_material(OBJS, self.white_material)
    
    
    def scale_change(self, obj):
        obj.scale = (1, 1, 1)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        new_dimensions = [obj.dimensions.x*self.size_multiplier, obj.dimensions.y*self.size_multiplier, self.desired_height]
        obj.dimensions = new_dimensions
        
    
    def make_UV_projection(self):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.cube_project()
        bpy.ops.object.mode_set(mode='OBJECT')

    
    def triangulate_object(self, obj):
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        
    def export_file(self, export_type='fbx'):
        if export_type == 'fbx':
            file_name = os.path.join(fbx_dir, f'{self.name}_s{self.size_multiplier}_h{self.desired_height}_{self.texture_name}.fbx')
            with contextlib.redirect_stdout(io.StringIO()):
                bpy.ops.export_scene.fbx(
                                            filepath=file_name,
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
        elif export_type == 'glb':
            file_name = os.path.join(fbx_dir, f'{self.name}_s{self.size_multiplier}_h{self.desired_height}_{self.texture_name}.glb')
            with contextlib.redirect_stdout(io.StringIO()):
                bpy.ops.export_scene.gltf(
                                            filepath=file_name,
                                            export_format='GLB',
                                            export_apply=True,
                                        )
        elif export_type == 'glb':
            file_name = os.path.join(fbx_dir, f'{self.name}_s{self.size_multiplier}_h{self.desired_height}_{self.texture_name}.gltf')
            with contextlib.redirect_stdout(io.StringIO()):
                bpy.ops.export_scene.gltf(
                                            filepath=file_name,
                                            export_format='GLTF_SEPARATE',  # 'GLTF_SEPARATE' or 'GLTF_EMBEDDED', 'GLB'
                                            export_apply=True,
                                        )
        else:
            raise Exception('export file type err. file type is only fbx, glb and gltf')
        
        return file_name
    
    
    def blend_to_fbx(self, blend_file, fbx_dir, texture_name=None, size_multiplier=1):
        self.size_multiplier = size_multiplier
        self.texture_name = texture_name
        
        os.makedirs(fbx_dir, exist_ok=True)
        self.name, self.extension = blend_file.split("/")[-1].split(".")

        # Load blend file
        bpy.ops.wm.open_mainfile(filepath=blend_file)
        bpy.ops.object.select_all(action='DESELECT')
        
        # Get all mesh
        MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']
        
        # Make texture
        self.detailed_material, self.white_material = self.make_texture(self.texture_name)
        
        # Apply texture
        self.apply_texture(MSH_OBJS)
        
        # Joins all objects
        bpy.ops.object.join()
        
        # Get the current active object
        obj = bpy.context.object
        
        # Move to origin
        obj.location = (0, 0, 0)
        
        # Chage object size
        self.scale_change(obj)

        # Make UV
        self.make_UV_projection()
        
        # add triangulate 
        self.triangulate_object(obj)
        
        # Export file
        file_name = self.export_file(export_type='fbx')
        
        # Quit blender
        bpy.ops.wm.quit_blender()
        
        return file_name


if __name__ == '__main__':
    converter = BlendToFBX()
    
    blend_path = os.environ.get('BLEND_PATH', 'default')
    size_multiplier = os.environ.get('SIZE_MULTIPLIER', 'default')
    wallpaper_no = os.environ.get('WALLPAPER_NO', '2')
    
    wallpaper_list = const.WALLPAPER_LIST
    
    fbx_dir = const.FBX_DIRECTORY
    
    fbx_file_path = converter.blend_to_fbx(
                                            blend_path, 
                                            fbx_dir, 
                                            texture_name=wallpaper_list[wallpaper_no], 
                                            size_multiplier=float(size_multiplier), 
                                            ).replace('\\', '/')
    print(f'result : {fbx_file_path}')