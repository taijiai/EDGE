import pickle
import os
import numpy as np
import bpy
from SmplObject import SmplObjects
from scipy.spatial.transform import Rotation as R
from math import radians

class S2F:
    def __init__(self):
        self.scene = bpy.context.scene
        self.load_scene()
        self.data = self.get_data()


    def get_motion_files(self, directory="motions/"):
        pkl_list = []
        for filename in os.listdir(directory):
            if filename.endswith(".pkl"):
                pkl_list += os.path.join(directory, filename),
        return pkl_list

    def cleanup_cube(self):
        bpy.data.objects["Cube"].select_set(True)
        bpy.ops.object.delete()

    def load_scene(self, fbx_path="ybot.fbx"):
        self.cleanup_cube()
        existing_objects = list(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=fbx_path, global_scale=0.85) #TODO: scale to what?
        # print(list(bpy.data.objects))
        # loop
        # for obj in bpy.data.objects:
        #     if obj not in existing_objects:
        #         count = 0
        #         if obj.name.startswith("Alpha"):
        #             # print(f"{obj.name} {obj.location[0]} {obj.location[1]} {obj.location[2]}")
        #             print(f"obj.type {obj.type}")
        #             print(obj.vertex_groups.items)
        # print(bpy.data.collections["Collection"].all_objects)
        self.parent = self.scene.objects["smpl"]
        self.view_joints_surfaces()

    def view_joints_surfaces(self):
        print(f"{self.parent.name} {self.parent.rotation_euler} {self.parent.rotation_quaternion} {self.parent.location[0]} {self.parent.location[1]} {self.parent.location[2]} {self.parent.type} {self.parent.animation_data} {[g.name for g in self.parent.vertex_groups]}")
        for chd in self.parent.children:
            print("--view_joints_surfaces")
            print(f"{chd.name} {chd.rotation_euler} {chd.rotation_quaternion} {chd.location[0]} {chd.location[1]} {chd.location[2]} {chd.type} {chd.animation_data} {[g.name for g in chd.vertex_groups]}")
            if chd.animation_data != None:
                print(f"found {chd.name}")
        print(dir(self.parent.children[0]))

    def config_render(self):
        self.scene.render.image_settings.file_format = "FFMPEG"
        self.scene.render.ffmpeg.format = 'MPEG4'
        self.scene.render.ffmpeg.codec = "H264"
        self.scene.render.fps = 30
        self.scene.frame_start = 1
        self.scene.frame_end = 90#0
        self.scene.render.filepath = "output"

    def render(self):
        """
        ['__doc__', '__module__', '__slots__', 'bake', 'bake_bias', 'bake_margin', 'bake_margin_type', 'bake_samples', 'bake_type', 'bake_user_scale', 'bl_rna', 'border_max_x', 'border_max_y', 'border_min_x', 'border_min_y', 'dither_intensity', 'engine', 'ffmpeg', 'file_extension', 'filepath', 'film_transparent', 'filter_size', 'fps', 'fps_base', 'frame_map_new', 'frame_map_old', 'frame_path', 'hair_subdiv', 'hair_type', 'has_multiple_engines', 'image_settings', 'is_movie_format', 'line_thickness', 'line_thickness_mode', 'metadata_input', 'motion_blur_shutter', 'motion_blur_shutter_curve', 'pixel_aspect_x', 'pixel_aspect_y', 'preview_pixel_size', 'resolution_percentage', 'resolution_x', 'resolution_y', 'rna_type', 'sequencer_gl_preview', 'simplify_child_particles', 'simplify_child_particles_render', 'simplify_gpencil', 'simplify_gpencil_antialiasing', 'simplify_gpencil_modifier', 'simplify_gpencil_onplay', 'simplify_gpencil_shader_fx', 'simplify_gpencil_tint', 'simplify_gpencil_view_fill', 'simplify_shadows', 'simplify_shadows_render', 'simplify_subdivision', 'simplify_subdivision_render', 'simplify_volumes', 'stamp_background', 'stamp_font_size', 'stamp_foreground', 'stamp_note_text', 'stereo_views', 'threads', 'threads_mode', 'use_bake_clear', 'use_bake_lores_mesh', 'use_bake_multires', 'use_bake_selected_to_active', 'use_bake_user_scale', 'use_border', 'use_compositing', 'use_crop_to_border', 'use_file_extension', 'use_freestyle', 'use_high_quality_normals', 'use_lock_interface', 'use_motion_blur', 'use_multiview', 'use_overwrite', 'use_persistent_data', 'use_placeholder', 'use_render_cache', 'use_sequencer', 'use_sequencer_override_scene_strip', 'use_simplify', 'use_single_layer', 'use_spherical_stereo', 'use_stamp', 'use_stamp_camera', 'use_stamp_date', 'use_stamp_filename', 'use_stamp_frame', 'use_stamp_frame_range', 'use_stamp_hostname', 'use_stamp_labels', 'use_stamp_lens', 'use_stamp_marker', 'use_stamp_memory', 'use_stamp_note', 'use_stamp_render_time', 'use_stamp_scene', 'use_stamp_sequencer_strip', 'use_stamp_time', 'views', 'views_format']
        """
        self.config_render()
        self.animate()

        bpy.ops.render.render(write_still=False, animation=True) # Render a sequence of images

    def animate(self):
        # parent = self.scene.objects["smpl"]
        self.animate_helper5(self.parent)

    def find_node(self, joint: str):
        nodes = []
        for node in self.parent.children:
            for vertex in node.vertex_groups:
                if vertex.name == joint:
                    nodes += node,
        return nodes

    def animate_helper7(self, obj):
        if obj == None:
            obj = self.parent
        obj.animation_data_create()
        obj.animation_data.action = bpy.data.actions.new(name="MyAction")
        fcu_z = obj.animation_data.action.fcurves.new(data_path="rotation_euler.X", index=2)
        fcu_z.keyframe_points.add(2)
        fcu_z.keyframe_points[0].co = 1.0, 0.0
        fcu_z.keyframe_points[1].co = 20.0, -1.0
        print(f"--created curve {obj.animation_data.action.fcurves}")

    def write_curve(self, curve, mdata):
        curve.keyframe_points.add(mdata.shape[0])
        print(f"--curve {dir(curve)}")
        for i in range(mdata.shape[0]):
            curve.keyframe_points[i].co = i, mdata[i]#[curve.array_index]

    def animate_helper5(self, obj):
        obj.animation_data_create()
        obj.animation_data.action = bpy.data.actions.new(name="MyAction")
        names = SmplObjects.joints
        smpl_poses = self.data["smpl_poses"]
        rotation = R.from_quat(np.array([-0.7071068, 0, 0, 0.7071068]))  # -90 degrees about the x axis
        for idx, name in enumerate(names):
            nodes = self.find_node(name)
            rotvec = smpl_poses[:, idx * 3: idx * 3 + 3]
            # if root, rotate
            if name == "m_avg_Pelvis":
                rotvec = (rotation * R.from_rotvec(rotvec)).as_rotvec()
            euler = R.from_rotvec(rotvec).as_euler("xyz", degrees=True)
            nodes[0].animation_data_create()
            nodes[0].animation_data.action = bpy.data.actions.new(name=f"action_{nodes[0].name}")
            fcu_x = nodes[0].animation_data.action.fcurves.new(data_path="location", index=0)
            fcu_y = nodes[0].animation_data.action.fcurves.new(data_path="location", index=1)
            fcu_z = nodes[0].animation_data.action.fcurves.new(data_path="location", index=2)
            self.write_curve(fcu_x, euler[:, 0])
            self.write_curve(fcu_y, euler[:, 1])
            self.write_curve(fcu_z, euler[:, 2])
            if idx >= 90:
                break

    def animate_helper4(self, obj):
        obj.animation_data_create()
        obj.animation_data.action = bpy.data.actions.new(name="MyAction")
        fcu_z = obj.animation_data.action.fcurves.new(data_path="location", index=2)
        fcu_z.keyframe_points.add(2)
        fcu_z.keyframe_points[0].co = 1.0, 0.0
        fcu_z.keyframe_points[1].co = 20.0, -1.0
        print(f"--created curve {obj.animation_data.action.fcurves}")

    def animate_helper3(self, obj):
        # Simple keyframe_insert to move the obj on the Y axis
        # https://docs.blender.org/api/current/info_quickstart.html#animation
        obj.location[1] = 0.0
        obj.keyframe_insert(data_path="location", frame=1.0, index=1)
        obj.location[1] = -1.0
        obj.keyframe_insert(data_path="location", frame=20.0, index=1)

    def animate_helper6(self, obj):
        if obj == None:
            obj = self.parent
        smpl_poses = self.data["smpl_poses"]
        join_names = SmplObjects.joints
        rotation = R.from_quat(np.array([-0.7071068, 0, 0, 0.7071068]))  # -90 degrees about the x axis
        for idx, name in enumerate(join_names):
            node = self.find_node(name)
            rotvec = smpl_poses[:, idx * 3: idx * 3 + 3]
            if name == "m_avg_Pelvis":
                rotvec = (rotation * R.from_rotvec(rotvec)).as_rotvec()
            euler = R.from_rotvec(rotvec).as_euler("xyz", degrees=True)
            print("node")
            print(dir(node)) #to_curve
        print("rotation_quaternion") #<Quaternion (w=1.0000, x=0.0000, y=0.0000, z=0.0000)> <Vector (0.0000, 1.0000, 0.0000)>
        print(obj.rotation_quaternion)
        obj.rotation_quaternion = rotation.as_quat()
        print(obj.rotation_quaternion)
        # print(obj.rotation_euler) #<Euler (x=1.5708, y=-0.0000, z=0.0000), order='XYZ'>
        # self.scene.frame_current = 1
        # obj.keyframe_insert(type='Rotation')
        # self.scene.scene.frame_current = 100
        # obj.rotation_euler = (1.0, 0.0, 0.0)
        # obj.keyframe_insert(type='Rotation')
        # self.parent.rotation_quaternion()
        # for i in range(self.scene.frame_start + 1, self.scene.frame_end + 1):
        #     self.scene.frame_set(i)
        #     print(obj.rotation_quaternion)
        #     # obj.keyframe_insert(data_path="rotation_euler")

    def animate_helper2(self, obj):
        if obj == None:
            obj = self.parent
        for i in range(self.scene.frame_start + 1, self.scene.frame_end + 1):
            self.scene.frame_set(i)
            print("rotation_euler")
            print(dir(obj.rotation_euler))
            obj.rotation_euler[0] += radians(18)
            obj.rotation_euler[1] += 0
            obj.rotation_euler[2] += 0
            obj.keyframe_insert(data_path="rotation_euler")

    def animate_helper1(self):
        for i in range(self.scene.frame_start + 1, self.scene.frame_end + 1):
            self.scene.frame_set(i)
            self.parent.location.z += 0.1
            self.parent.keyframe_insert(data_path="location")
            # bpy.ops.anim.keyframe_insert(type='Location')


    def get_data(self):
        # TODO: support more than 1 file
        with open(self.get_motion_files()[0], "rb") as f:
            data = pickle.load(f, encoding="latin-1")
            print(data.keys())
            # ['smpl_poses', 'body_pose', 'smpl_trans', 'transl', 'full_pose'] (900, 3)
            if "smpl_trans" in data:
                print("smpl_trans.shape: " + str(data["smpl_trans"].shape))
                print(data["smpl_trans"])
            return data


if __name__ == '__main__':
    s2f = S2F()
    s2f.render()
    """
   body_pose
   [[ 1.6808077e+00 -9.4238855e-03  1.0747937e-01 ...  8.7879150e-04
   1.4689305e-03  3.6160867e-03]
 [ 1.6868165e+00 -2.0410564e-02  1.1174689e-01 ...  9.0403826e-04
   1.4890584e-03  3.5225973e-03]
 [ 1.6918999e+00 -2.3354549e-02  1.1579980e-01 ...  9.8592078e-04
   1.5063480e-03  3.3678326e-03]
 ...
 [ 1.2732774e+00  9.3227834e-01  1.1523142e+00 ... -1.0611537e-03
  -7.9213531e-04  3.7451130e-03]
 [ 1.2851262e+00  9.3849111e-01  1.1411197e+00 ... -8.9188979e-04
  -7.1188208e-04  3.7625816e-03]
 [ 1.2872528e+00  9.5708907e-01  1.1349887e+00 ... -7.6165679e-04
  -5.0462713e-04  3.8183068e-03]]
  
  
  [[ 1.6808077e+00 -9.4238855e-03  1.0747937e-01 ...  8.7879150e-04
   1.4689305e-03  3.6160867e-03]
 [ 1.6868165e+00 -2.0410564e-02  1.1174689e-01 ...  9.0403826e-04
   1.4890584e-03  3.5225973e-03]
 [ 1.6918999e+00 -2.3354549e-02  1.1579980e-01 ...  9.8592078e-04
   1.5063480e-03  3.3678326e-03]
 ...
 [ 1.2732774e+00  9.3227834e-01  1.1523142e+00 ... -1.0611537e-03
  -7.9213531e-04  3.7451130e-03]
 [ 1.2851262e+00  9.3849111e-01  1.1411197e+00 ... -8.9188979e-04
  -7.1188208e-04  3.7625816e-03]
 [ 1.2872528e+00  9.5708907e-01  1.1349887e+00 ... -7.6165679e-04
  -5.0462713e-04  3.8183068e-03]]
  
   """