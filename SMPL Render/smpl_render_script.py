import bpy
import mathutils
import random
import os
import math


def import_object(filepath):
    bpy.ops.import_scene.fbx(filepath=filepath)


def add_camera(name):
    cam = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam)
    cam_obj.location = (random.randint(1, 10), random.randint(1, 10), random.randint(1, 10))
    bpy.context.scene.collection.objects.link(cam_obj)
    return cam_obj


def point_to(camera_obj, point):
    loc_camera = camera_obj.location
    direction = point - loc_camera 
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera_obj.rotation_euler = rot_quat.to_euler() 


def move_to_random(obj):
    obj.location = (random.randint(-10, 10), random.randint(-10, 10), random.randint(-10mov, 10))


def rotate_object(obj):
    obj.rotation_euler = (random.random() * math.pi * 2, random.random() * math.pi * 2, random.random() * math.pi * 2)

def move_and_point(cam_obj, point):
    move_to_random(cam_obj)
    point_to(cam_obj, point)
    
    
def clean_up():
    for o in bpy.context.scene.objects:
        if o.name == 'group_m_mosh_cmu88':
            o.select_set(True)
        else:
            o.select_set(False)
    bpy.ops.object.delete()


def render_result(output_path):
    scene = bpy.context.scene
    scene.camera = bpy.data.objects['Camera']
    bpy.context.scene.render.filepath = os.path.join(output_path, 'render_python.png')
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    render_path = '/Users/raunitdalal/Desktop'
    object_path = '/Users/raunitdalal/Downloads/SMPL_sample_animations/mosh_cmu_8806_f_lbs_10_207_0_v1.0.2.fbx'
    import_object(object_path)
    clean_up()
    rotate_object(bpy.data.objects['m_mosh_cmu88'])
    cam_obj = add_camera('Camera')
    obj_location = bpy.data.objects['m_mosh_cmu88'].location
    point_to(cam_obj, obj_location)
    render_result(render_path)
    move_and_point(cam_obj, obj_location)
    render_result(render_path)
