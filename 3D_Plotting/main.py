'''
This file renders an assembly of the 2D image, the skeleton, the uncoloured 3D mesh and the coloured 3D mesh of the subject

To run in blender
Enter this in the python console
filename = '/Users/raunitdalal/Desktop/Blender Scripts/3D_Plotting/main.py'
exec(compile(open(filename).read(), filename, 'exec'))

translate_cam(cam, human_mesh.location)
turn_60(cam, human_mesh.location)
turn_60(cam, human_mesh.location, True)
OR
You can also use blender from the command line

Run the following command in terminal to execute this:
blender --python ./assembly.py -- img_id
where img_id is the input image ID of the subject

NOTE: Wherever you give addresses, give full address in case of files running blender

BLENDER VERSION: 2.79
ids = []
'''

import bpy
import random
import numpy as np
import bmesh
import sys
import os
import addon_utils

from bpy import context, data, ops
import math
from mathutils import Euler, Matrix, Quaternion, Vector

files = [44, 51, 53, 76, 80, 82, 188, 382, 781, 781418, 1112, 1589, 3336, 17371, 17374, 1731164]
img_id = files[16]
source_dir = r'/Users/raunitdalal/Desktop/Blender Scripts/3D_Plotting/folders/%.6d' % img_id


def smpl24_to_17j_adv(pose_smpl):
    ### hip altitude increase and widen
    alt_f = 0.8
    wide_f = 8.0

    pelvis = pose_smpl[0].copy()
    r_hip = pose_smpl[2].copy()
    l_hip = pose_smpl[1].copy()

    ## alt inc
    r_p_dir = pelvis - r_hip
    l_p_dir = pelvis - l_hip

    mag_rp = np.linalg.norm(r_p_dir)
    r_p_dir /= mag_rp
    mag_lp = np.linalg.norm(l_p_dir)
    l_p_dir /= mag_lp

    r_hip = r_hip + (r_p_dir * mag_rp * alt_f)
    l_hip = l_hip + (l_p_dir * mag_lp * alt_f)

    ## widen
    hip_ctr = (r_hip + l_hip) / 2.0
    r_dir = r_hip - hip_ctr
    l_dir = l_hip - hip_ctr

    # unit directions
    mag = np.linalg.norm(r_dir)
    r_dir /= mag
    l_dir /= np.linalg.norm(l_dir)

    r_hip = r_hip + (r_dir * mag * wide_f)
    l_hip = l_hip + (l_dir * mag * wide_f)

    # place back
    pose_smpl[2] = r_hip
    pose_smpl[1] = l_hip

    ### neck to head raise  with tilt towards nose
    alt_f = 0.7

    head = pose_smpl[15].copy()
    neck = pose_smpl[12].copy()

    ## alt inc
    n_h_dir = head - neck

    mag_nh = np.linalg.norm(n_h_dir)
    n_h_dir /= mag_nh

    head = head + (n_h_dir * mag_nh * alt_f)

    # place back
    pose_smpl[15] = head

    ##
    ### remove wrist
    pose_smpl = pose_smpl[:-2]

    ### remove extra def spine
    pose_smpl = np.delete(pose_smpl, 3, 0)  ## 3
    pose_smpl = np.delete(pose_smpl, 5, 0)  ## 6
    pose_smpl = np.delete(pose_smpl, 7, 0)  ## 9
    ### remove torso
    pose_smpl = np.delete(pose_smpl, 10, 0)  ## 10
    pose_smpl = np.delete(pose_smpl, 10, 0)  ## 11

    return pose_smpl


###############################
def select_or_deselect(action='SELECT'):
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except Exception as e1:
        print (e1)
    bpy.ops.object.select_all(action=action)


# #Deleting all previous experiments' objects
select_or_deselect()  # Select all the objects
bpy.data.objects['Camera'].select = False
# bpy.data.objects['Lamp'].select = False

bpy.ops.object.delete()

# Create new lamp datablock
lamp_data = bpy.data.lamps.new(name="Lamp", type='HEMI')
# lamp_data.energy *= 5
# Create new object with our lamp datablock
lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)

bpy.context.scene.objects.link(lamp_object)

# ## Select or add the dataset you are using
dataset = ''

#################################
# #Fixing the camera's position when displaying skeleton, uncoloured mesh and colored mesh
cam = bpy.data.objects['Camera']
cam.data.type = 'PERSP'
cam.location = (8.90836, -5.66768, 2.87374)  # display all
# cam.location = (6.55316, -5.36825, 2.63625) # # when displaying any 2 of the above 3
cam.rotation_euler = (71.5 / 180 * np.pi, 0, 46.7 / 180 * np.pi)  # display all
# cam.rotation_euler = (71.5/180*np.pi, 0, 46.7/180*np.pi)## when displaying any 2 of the above 3


# ########################             SKELETON             ###############################

NUM_JOINTS = 17

# ##### MOST REALISTIC: [(SMOOTH_ENABLE, True), (USE_SPHERE_JOINTS, False)]
# ###      SECOND BEST: [(SMOOTH_ENABLE, True),  (USE_SPHERE_JOINTS, True)]
# #              CRUDE: [(SMOOTH_ENABLE, False), (USE_SPHERE_JOINTS, True)]


###
SMOOTH_ENABLE = True
USE_SPHERE_JOINTS = True

# ## resolution params
if SMOOTH_ENABLE:
    CYL_R = 0.035 * 2
    SPH_R = 0.05 * 2
    SMOOTH_FACTOR = -0.322
else:
    CYL_R = 0.035 * 2
    SPH_R = 0.025 * 2

THICKNESS = 0.24

TRANS = (0, 0, 0)  # ## x,y,z
ROT_EULER = (0, 45, 90)  # ## euler angles in rads


def add_sphere_at(centre, radius):
    bpy.ops.mesh.primitive_uv_sphere_add(location=centre, size=radius)
    bpy.context.object.active_material = smat


def add_cylinder_between(point1, point2, r):
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    dist = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=r,
        depth=dist,
        location=(dx / 2 + x1, dy / 2 + y1, dz / 2 + z1)
    )

    bpy.context.object.active_material = cmat
    if not dist:
        print('Division by zero!')
        return
    phi = math.atan2(dy, dx)
    theta = math.acos(dz / dist)

    bpy.context.object.rotation_euler[1] = theta
    bpy.context.object.rotation_euler[2] = phi


def create_custom_mesh(point1, point2, point3, obj_name):
    # Define arrays for holding data
    my_vertices = [point1, point2, point3]
    my_faces = [(0, 1, 2)]
    # Create all Faces
    # -------------------------------------
    # my_face = [(0, 1, 2)]
    # my_faces.extend(my_face)

    my_mesh = bpy.data.meshes.new(obj_name)
    curr_object = bpy.data.objects.new(obj_name, my_mesh)
    bpy.context.scene.objects.link(curr_object)

    my_mesh.from_pydata(my_vertices, [], my_faces)  # Generate mesh data
    my_mesh.update(calc_edges=True)  # Calculate the edges

    return curr_object


####


edges_17 = [0,
            0, 0, 1, 2,
            3, 4, 5, 6,
            0, 9, 9, 9,
            11, 12, 13, 14]

edges = [0,  #####for smpl joints
         0, 0, 0,
         1, 2, 3, 4,
         5, 6, 7, 8,
         9, 9, 9,
         12, 12, 12,
         16, 17, 18, 19, 20, 21
         ]
# edges = edges[::-1]

clrs_sid = np.array([[175, 25, 240],  # 1
                     [25, 128, 128], [75, 180, 80], [170, 170, 70], [60, 128, 210],  # 5
                     [200, 130, 0], [180, 30, 145], [255, 128, 50], [240, 50, 128],  # 9
                     [200, 20, 110], [0, 0, 255], [128, 128, 0], [0, 128, 255],  # 13
                     [0, 255, 0], [255, 0, 128], [128, 255, 0], [255, 0, 0]])  # 17
clrs_sid = clrs_sid[::-1]
# clrs_sid = np.array(
#     [[0, 0, 255], [0, 255, 0], [255, 0, 0], [255, 0, 255], [0, 255, 255], [255, 255, 0], [127, 127, 0], [0, 127, 0],
#      [100, 0, 100],
#      [255, 0, 255], [0, 255, 0], [0, 0, 255], [255, 255, 0], [127, 127, 0], [100, 0, 100], [175, 100, 195],
#      [0, 0, 255], [0, 255, 0], [255, 0, 0], [255, 0, 255], [0, 255, 255], [255, 255, 0], [127, 127, 0], [0, 127, 0],
#      [100, 0, 100],
#      [255, 0, 255], [0, 255, 0], [0, 0, 255], [255, 255, 0], [127, 127, 0], [100, 0, 100], [175, 100, 195]])

# joints = np.load('../Sample/joints_%.5d' % img_id + dataset + '.npy')  # # add "full" address of joints file here
joints = np.load(os.path.join(source_dir, 'j3d_%.6d' % img_id + dataset + '.npy'))
joints = smpl24_to_17j_adv(joints)

anno_xyz = np.copy(joints) * 0.3  # # get xyz of all joints

anno_xyz = np.transpose(anno_xyz, (1, 0))

print (anno_xyz.shape)

# This is doing nothing: subtracting 0.0 from all the values
anno_xyz[0, :] -= anno_xyz[0, 0]
anno_xyz[1, :] -= anno_xyz[1, 0]
anno_xyz[2, :] -= anno_xyz[2, 0]

anno_xyz /= 10

anno_xyz[:, 16] -= [0.3, 0, 0]

if USE_SPHERE_JOINTS:
    smat = bpy.data.materials.new('sphereMat')
    smat.diffuse_color = (0, 0, 0)
    smat.use_shadeless = True

    for p in range(NUM_JOINTS):
        centre = (anno_xyz[0, p], anno_xyz[1, p], anno_xyz[2, p])
        bpy.ops.mesh.primitive_uv_sphere_add(location=centre, size=SPH_R)
        bpy.context.object.active_material = smat
        if not p:
            hip = bpy.context.object

for n in range(len(edges_17)):
    cmat = bpy.data.materials.new('cylMat' + str(n))
    cmat.diffuse_color = clrs_sid[n] / 255.0
    cmat.use_shadeless = True

    p1 = edges_17[n]
    p2 = n

    pt1 = (anno_xyz[0, p1], anno_xyz[1, p1], anno_xyz[2, p1])
    pt2 = (anno_xyz[0, p2], anno_xyz[1, p2], anno_xyz[2, p2])

    add_cylinder_between(pt1, pt2, r=CYL_R)

bpy.ops.object.select_all(action='DESELECT')
bpy.context.scene.objects.active = hip

bpy.ops.object.select_all(action='SELECT')
bpy.data.objects['Camera'].select = False
bpy.data.objects['Lamp'].select = False

bpy.ops.object.join()
skeleton = bpy.context.object

# #changing skeleton location and orientation
skeleton.location = (1.6, -1, 0)

# skeleton.rotation_euler[0] = -np.pi / 2
# if dataset == '_surr':
#     skeleton.rotation_euler[2] = np.pi / 4
# elif dataset == '_lsp':
#     skeleton.rotation_euler[2] = np.pi / 3
# else:
#     skeleton.rotation_euler[2] = np.pi / 3

# #####################################################################################################################
# ########################             IMPORTING THE 2D IMAGE AS A PLANE             ###############################

# # Enter the name of the image file
img_name = 'img_%.6d.png' % img_id

# Add "full" address for image folder as directory
img_filename = os.path.join(source_dir, img_name)
print(img_filename)

# Enable "Import-Export: Import images as planes" in Add-ons
addon_utils.enable('io_import_images_as_planes', default_set=True, persistent=False, handle_error=None)
bpy.ops.import_image.to_plane(files=[{"name": img_filename}])

img = bpy.context.object

# #Bringing it to the center of the grid
bpy.ops.object.location_clear(clear_delta=False)

# #Scaling the image plane
bpy.ops.transform.resize(value=(2, 2, 2), constraint_axis=(False, False, False), constraint_orientation='GLOBAL',
                         mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

# #Moving the center of the image to the center of the grid
bpy.ops.object.location_clear(clear_delta=False)

# ##Moving the plane to a fixed position
# deselecting all objects and then selecting only our 2d image
bpy.ops.object.select_all(action='DESELECT')
img.select = True

# #changing the location
img.location = (0, -1, 1)
img.rotation_euler = (np.pi / 2, 0, np.pi / 2)
img.active_material.use_shadeless = True


######################################################################################################################
# ######################              IMPORT THE GRID PLANES              ########################

def add_grid_plane(location, mat):
    bpy.ops.mesh.primitive_grid_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
        True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
        False, False, False, False))
    grid = bpy.context.object
    grid.active_material = mat
    bpy.ops.transform.rotate(value=np.pi / 2, axis=(0, 0, 1), constraint_axis=(False, False, True),
                             constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                             proportional_edit_falloff='SMOOTH', proportional_size=1)
    grid.location = location
    grid.dimensions = (2, 2, 0)
    grid.rotation_euler = (0, 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    return grid


nmat = bpy.data.materials.new('gridMat')
nmat.type = 'WIRE'
nmat.diffuse_color = (0, 0, 0)
nmat.use_shadeless = True

grid1 = add_grid_plane((1, -1, 0), nmat)  # import the first grid plane
grid2 = add_grid_plane((3, -1, 0), nmat)  # import the second grid plane
grid3 = add_grid_plane((5, -1, 0), nmat)  # import the third grid plane

# ########################             PLAIN MESH             ###############################
# #Importing the human mesh

# # Add the "full" location of the human mesh here
file_loc = os.path.join(source_dir, "object_%.6d" % img_id + dataset + ".obj")
min_x = min_y = min_z = 5
max_x = max_y = max_z = -5
height = max_y - min_y
new_height = (200 / 224 * 2)
scale = 0.0029761904761904765
print(scale)

# ########################             COLOURED MESH             ###############################
# #Importing the human mesh

bpy.ops.import_scene.obj(filepath=file_loc)
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
color_obj = bpy.context.selected_objects[0]
human_name = color_obj.name
bpy.ops.object.select_all(action='DESELECT')
color_obj = bpy.data.objects[human_name]
color_obj.select = True
color_obj.scale = (scale, scale, scale)

human_mesh = color_obj.data

bm = bmesh.new()
bm.from_mesh(human_mesh)

for v in bm.verts:
    if v.co.x < min_x:
        min_x = v.co.x

    if v.co.y < min_y:
        min_y = v.co.y

    if v.co.z < min_z:
        min_z = v.co.z

    if v.co.x > max_x:
        max_x = v.co.x

    if v.co.y > max_y:
        max_y = v.co.y

    if v.co.z > max_z:
        max_z = v.co.z

height = max_y - min_y
new_height = (200 / 224 * 2)
print (new_height)
scale = new_height / height
centre_x = (max_x + min_x) / 2
print(scale)

bm.free()

# Changing the location and orientation of the mesh
color_obj.scale = (scale, scale, scale)
# color_obj.location = (3.2, -0.766037106513977, max_y * scale)
# skeleton.location = (1.6, -0.8160370588302612, max_y * scale)
color_obj.location = (3.2, -1 - centre_x * scale, max_y * scale)
skeleton.location = (1.6, -1 - centre_x * scale, max_y * scale)
skeleton.dimensions = color_obj.dimensions * scale

# color_obj.rotation_euler[0] = -np.pi / 2
# if dataset == '_surr':
#     color_obj.rotation_euler[2] = np.pi / 4
# else:
#     color_obj.rotation_euler[2] = np.pi / 3

# color_obj.rotation_euler = (-np.pi / 2, 0, np.pi / 2)

# 3D mesh view
color_obj.rotation_euler = (-1.5854706764221191, 0, 1.618557333946228)
skeleton.rotation_euler = (-1.5854706764221191, 0, 1.618557333946228)

# ### ADD THE COLOR TO THE MESH

# load the vertex color segmentations map
# color_vertex_map = np.load(os.path.join(
#     source_dir, 'HighResColorPicker/vtx_clr_smpl_proj_final_part_segmentations.npy'
# ))

# create a dummy color array for all the segments
# rgb_vertex_colors = [(random.random(), random.random(), random.random()) for i in range(color_vertex_map.max() + 1)]

#######################################################################
# ###Coloring the entire mesh one vertex at a time

my_object = color_obj.data

# Add "full" address of the color file here


color_map_collection = my_object.vertex_colors
if not len(color_map_collection):
    color_map_collection.new()
color_map = color_map_collection['Col']

counter = 0
for poly in my_object.polygons:
    for idx in poly.loop_indices:
        vert_index = my_object.loops[idx].vertex_index
        color_map.data[counter].color = (1.0, 0.6, 0.6)
        counter += 1

print('# VERTICES BEFORE SUBDIVISION: ' + str(len(human_mesh.vertices)))

SUBDIVIDE = True  # set to True if you want to subdivide the mesh from 6890 -> 27554 vertices

if SUBDIVIDE:
    bpy.context.scene.objects.active = bpy.data.objects[human_name]
    ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide()
    ops.object.mode_set(mode='OBJECT')
    print('# VERTICES AFTER SUBDIVISION: ' + str(len(human_mesh.vertices)))

meshMat = bpy.data.materials.new('colourMeshMat')
color_obj.active_material = meshMat
meshMat.use_shadeless = False
meshMat.use_vertex_color_paint = True

# set to vertex paint mode to see the result
color_obj.select = True
bpy.ops.object.mode_set(mode='VERTEX_PAINT')

bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

bpy.context.scene.render.resolution_percentage = 100


# # Render and save
def save_render(path, name=""):
    bpy.context.scene.render.filepath = os.path.join(path, 'grid_plots_%.6d' % img_id + name + ".png")
    bpy.ops.render.render(write_still=True)


destination_path = '/Users/raunitdalal/Desktop/Outputs/%.6d' % img_id
try:
    os.mkdir(destination_path)
except Exception as e:
    print(e)


# save_render(destination_path)


def translate_cam(camera_obj, point):
    camera_obj.location = (point[0] + 8, point[1], point[-1])
    look_at(camera_obj, point)
    save_render(destination_path, '-front')


def turn_60(camera_obj, point, neg=False):
    mag = (camera_obj.location[0] ** 2 + camera_obj.location[1] ** 2) ** 0.5
    camera_obj.location = (
        mag * np.sin(np.pi / 3), mag * np.cos(np.pi / 3) * (-1 if neg else 1),
        camera_obj.location[-1])
    print (camera_obj.location.magnitude)
    look_at(camera_obj, point)
    save_render(destination_path, ('-' if neg else '+') + '60')


# positioning the camera towards a particular location
def look_at(camera_obj, point):
    camera_location = camera_obj.location
    direction = point - camera_location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera_obj.rotation_euler = rot_quat.to_euler()


def generate_sphere_coordinates(radius):
    def generate_mod_1_numbers():
        x, y, z = random.uniform(-1, 1), random.uniform(-1, 1), random.random()
        mag = (x ** 2 + y ** 2 + z ** 2) ** 0.5
        return x / mag, y / mag, z / mag

    x1, y1, z1 = generate_mod_1_numbers()
    return x1 * radius, y1 * radius, z1 * radius


def change_camera_position(camera_obj, loc=None):
    if not loc:
        camera_obj.location = generate_sphere_coordinates(camera_obj.location.magnitude)
    else:
        camera_obj.location = loc


human_mesh = bpy.data.objects['object_%.6d' % img_id]
cam = bpy.data.objects['Camera']
save_render(destination_path)
# select_or_deselect()
# bpy.data.objects['Camera'].select = False
# bpy.data.objects['Lamp'].select = False
# bpy.data.objects['object_%.6d' % img_id].select = False
# bpy.ops.object.delete()
# translate_cam(cam, human_mesh.location)
# turn_60(cam, human_mesh.location, True)
# turn_60(cam, human_mesh.location)


# def create_human_mesh_vertex_groups(human_mesh_obj):
#     bpy.ops.object.mode_set(mode='OBJECT')
#     color_vertex_reverse_map = {i: [] for i in range(color_vertex_map.max() + 1)}
#     for i, val in enumerate(color_vertex_map):
#         color_vertex_reverse_map[val].append(i)
#     for i in range(color_vertex_map.max() + 1):
#         new_vertex_group = human_mesh_obj.vertex_groups.new(name='vertex_group_' + str(i))
#         new_vertex_group.add(color_vertex_reverse_map[i], 1.0, 'ADD')


# def make_material_mapping(human_mesh_obj):
#     material_mapping = {}
#     for i, val in enumerate(human_mesh_obj.vertex_groups):
#         mat = bpy.data.materials.new('vertex_group_' + str(i))
#         mat.diffuse_color = random.random(), random.random(), random.random()
#         mat.use_shadeless = True
#         human_mesh_obj.data.materials.append(mat)
#         material_mapping[val.name] = mat
#     return material_mapping
#
#
# def assign_materials_to_vertex_groups(human_mesh_obj):
#     make_material_mapping(human_mesh_obj)
#     help_dict = {}
#     for polygon in human_mesh_obj.data.polygons:
#         poly_vertex_groups = [g.group for v in polygon.vertices for g in human_mesh_obj.data.vertices[v].groups]
#         counts = [poly_vertex_groups.count(i) for i in poly_vertex_groups]
#         mode = poly_vertex_groups[counts.index(max(counts))]
#         group_name = human_mesh_obj.vertex_groups[mode].name
#         help_dict[group_name] = help_dict.get(group_name, 0) + 1
#         polygon.material_index = human_mesh_obj.material_slots.find(group_name)
#     print(help_dict)

#
# create_human_mesh_vertex_groups(human_obj)
# assign_materials_to_vertex_groups(human_obj)

# for idx in range(5):
#     change_camera_position(cam)
#     look_at(cam, human_obj.location)
#     save_render(destination_path, str(idx))
