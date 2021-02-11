'''
This file renders an assembly of the 2D image, the skeleton, the uncoloured 3D mesh and the coloured 3D mesh of the subject

To run in blender
Enter this in the python console
filename = "./Blender/assembly.py"
exec(compile(open(filename).read(), filename, 'exec'))
OR
You can also use blender from the command line

Run the following command in terminal to execute this:
blender --python ./assembly.py -- img_id
where img_id is the input image ID of the subject

NOTE: Wherever you give addresses, give full address in case of files running blender

BLENDER VERSION: 2.79
'''

import bpy
import random
import numpy as np
import bmesh
import sys
import os

from bpy import context, data, ops
import math
from mathutils import Euler, Matrix, Quaternion, Vector

source_dir = '/Users/raunitdalal/Downloads/Blender_3D_plot_gen/'
###############################
##Deleting all previous experiments' objects

bpy.ops.object.select_all(action='SELECT')
bpy.data.objects['Camera'].select = False
# bpy.data.objects['Lamp'].select = False

bpy.ops.object.delete()

# Create new lamp datablock
lamp_data = bpy.data.lamps.new(name="Lamp", type='HEMI')
# lamp_data.energy *= 5
# Create new object with our lamp datablock
lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)

bpy.context.scene.objects.link(lamp_object)

img_id = 1

### Select or add the dataset you are using
dataset = '_sample'

#################################
##Fixing the camera's position
cam = bpy.data.objects['Camera']
cam.data.type = 'PERSP'
cam.location = (8.90836, -5.66768, 2.87374)  ## when displaying skeleton, uncoloured mesh and colored mesh
# cam.location = (6.55316, -5.36825, 2.63625)## when displaying any 2 of the above 3
cam.rotation_euler = (
    71.5 / 180 * np.pi, 0, 46.7 / 180 * np.pi)  ## when displaying skeleton, uncoloured mesh and colored mesh
# cam.rotation_euler = (71.5/180*np.pi, 0, 46.7/180*np.pi)## when displaying any 2 of the above 3


#########################             SKELETON             ###############################

NUM_JOINTS = 17

# ##### MOST REALISTIC: [(SMOOTH_ENABLE, True),  (USE_SPHERE_JOINTS, False)]
# ###      SECOND BEST: [(SMOOTH_ENABLE, True),   (USE_SPHERE_JOINTS, True)]
# #              CRUDE: [(SMOOTH_ENABLE, False),  (USE_SPHERE_JOINTS, True)]


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

TRANS = (0, 0, 0)  ### x,y,z
ROT_EULER = (0, 45, 90)  ### euler angles in rads


def add_sphere_at(centre, radius):
    # bpy.ops.surface.primitive_nurbs_surface_sphere_add(radius=radius, location=centre)
    bpy.ops.mesh.primitive_uv_sphere_add(location=centre, size=radius)
    bpy.context.object.active_material = smat


def add_cylinder_between(pt1, pt2, r):
    x1 = pt1[0]
    y1 = pt1[1]
    z1 = pt1[2]

    x2 = pt2[0]
    y2 = pt2[1]
    z2 = pt2[2]

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

    phi = math.atan2(dy, dx)
    theta = math.acos(dz / dist)

    bpy.context.object.rotation_euler[1] = theta
    bpy.context.object.rotation_euler[2] = phi


def create_custom_mesh(pt1, pt2, pt3, objname):
    # Define arrays for holding data
    myvertex = []
    myfaces = []

    # Create all Vertices

    # vertex 0
    mypoint = [pt1]
    myvertex.extend(mypoint)

    # vertex 1
    mypoint = [pt2]
    myvertex.extend(mypoint)

    # vertex 2
    mypoint = [pt3]
    myvertex.extend(mypoint)

    # vertex 3
    # mypoint = [(1.0, 1.0, 0.0)]
    # myvertex.extend(mypoint)

    # -------------------------------------
    # Create all Faces
    # -------------------------------------
    myface = [(0, 1, 2)]
    myfaces.extend(myface)

    mymesh = bpy.data.meshes.new(objname)

    myobject = bpy.data.objects.new(objname, mymesh)

    bpy.context.scene.objects.link(myobject)

    # Generate mesh data
    mymesh.from_pydata(myvertex, [], myfaces)
    # Calculate the edges
    mymesh.update(calc_edges=True)

    return myobject


####


edges = [0,
         0, 1, 2, 3,
         1, 5, 6, 1,
         0, 9, 10, 11,
         0, 13, 14, 15]

clrs_sid = np.array([[175, 25, 240],  # 1
                     [25, 128, 128], [75, 180, 80], [170, 170, 70], [60, 128, 210],  # 5
                     [200, 130, 0], [180, 30, 145], [255, 128, 50], [240, 50, 128],  # 9
                     [200, 20, 110], [0, 0, 255], [128, 128, 0], [0, 128, 255],  # 13
                     [0, 255, 0], [255, 0, 128], [128, 255, 0], [255, 0, 0]])  # 17

# joints = np.load('../Sample/joints_%.5d' % img_id + dataset + '.npy')  # # add "full" address of joints file here
joints = np.load(os.path.join(source_dir, 'Sample_store/joints_%.5d' % img_id + dataset + '.npy'))

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

for n in range(len(edges)):
    cmat = bpy.data.materials.new('cylMat' + str(n))
    cmat.diffuse_color = clrs_sid[n] / 255.0
    cmat.use_shadeless = True

    p1 = edges[n]
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

##changing skeleton location and orientation
skeleton.location = (1.6, -1, 0)

skeleton.rotation_euler[0] = -np.pi / 2
if dataset == '_surr':
    skeleton.rotation_euler[2] = np.pi / 4
elif dataset == '_lsp':
    skeleton.rotation_euler[2] = np.pi / 3
else:
    skeleton.rotation_euler[2] = np.pi / 3

#############################################################################################################################
##importing the 2d image as plane

## Enter the name of the image file
img_name = 'image_sample_%.5d.jpg' % img_id

# Add "full" address for image folder as directory
filename = os.path.join(source_dir, 'Sample_store', img_name)
bpy.ops.import_image.to_plane(files=[{"name": filename}])
img = bpy.context.object

##Bringing it to the center of the grid
bpy.ops.object.location_clear(clear_delta=False)

##Scaling the image plane
bpy.ops.transform.resize(value=(2, 2, 2), constraint_axis=(False, False, False), constraint_orientation='GLOBAL',
                         mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

##Moving the center of the image to the center of the grid
bpy.ops.object.location_clear(clear_delta=False)

###Moving the plane to a fixed position
# deselecting all objects and then selecting only our 2d image
bpy.ops.object.select_all(action='DESELECT')
img.select = True

##changing the location
img.location = (0, -1, 1)
img.rotation_euler = (np.pi / 2, 0, np.pi / 2)
img.active_material.use_shadeless = True
# imat = bpy.data.materials.new('imageMat')
# imat.use_shadeless = True
# img.active_material = imat


################################################################################################################################
##Importing the first grid plane
bpy.ops.mesh.primitive_grid_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
    True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
    False, False, False))
grid = bpy.context.object

nmat = bpy.data.materials.new('gridMat')

nmat.type = 'WIRE'
nmat.diffuse_color = (0, 0, 0)
nmat.use_shadeless = True

grid.active_material = nmat
bpy.ops.transform.rotate(value=np.pi / 2, axis=(0, 0, 1), constraint_axis=(False, False, True),
                         constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                         proportional_edit_falloff='SMOOTH', proportional_size=1)
grid.location = (1, -1, 0)
grid.dimensions = (2, 2, 0)
grid.rotation_euler = (0, 0, 0)

################################################################################################################################
##Importing the second grid plane
bpy.ops.mesh.primitive_grid_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
    True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
    False, False, False))
grid1 = bpy.context.object

grid1.active_material = nmat
bpy.ops.transform.rotate(value=np.pi / 2, axis=(0, 0, 1), constraint_axis=(False, False, True),
                         constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                         proportional_edit_falloff='SMOOTH', proportional_size=1)
grid1.location = (3, -1, 0)
grid1.dimensions = (2, 2, 0)
grid1.rotation_euler = (0, 0, 0)
bpy.ops.object.select_all(action='DESELECT')

################################################################################################################################
##Importing the third grid plane
bpy.ops.mesh.primitive_grid_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(
    True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
    False, False, False))
grid2 = bpy.context.object

grid2.active_material = nmat
bpy.ops.transform.rotate(value=np.pi / 2, axis=(0, 0, 1), constraint_axis=(False, False, True),
                         constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED',
                         proportional_edit_falloff='SMOOTH', proportional_size=1)
grid2.location = (5, -1, 0)
grid2.dimensions = (2, 2, 0)
grid2.rotation_euler = (0, 0, 0)
bpy.ops.object.select_all(action='DESELECT')

#########################             PLAIN MESH             ###############################
##Importing the human mesh

## Add the "full" location of the human mesh here
file_loc = os.path.join(source_dir, "Sample_store/human_mesh_%.5d" % img_id + dataset + ".obj")
# bpy.ops.import_scene.obj(filepath=file_loc)
# human_obj = bpy.context.selected_objects[0]
# human_name = human_obj.name
# bpy.ops.object.select_all(action='DESELECT')
# human_obj = bpy.data.objects[human_name]
# human_obj.select = True
#
# human_mesh = human_obj.data
#
# bm = bmesh.new()
# bm.from_mesh(human_mesh)
#
min_x = min_y = min_z = 5
max_x = max_y = max_z = -5
#
# for v in bm.verts:
#     if v.co.x < min_x:
#         min_x = v.co.x
#
#     if v.co.y < min_y:
#         min_y = v.co.y
#
#     if v.co.z < min_z:
#         min_z = v.co.z
#
#     if v.co.x > max_x:
#         max_x = v.co.x
#
#     if v.co.y > max_y:
#         max_y = v.co.y
#
#     if v.co.z > max_z:
#         max_z = v.co.z
#
height = max_y - min_y
new_height = (200 / 224 * 2)
scale = new_height / height
# centre_x = (max_x + min_x) / 2
print(scale)
#
# bm.free()
#
# # Changing the loaction and orientation of the mesh
# human_obj.scale = (scale, scale, scale)
# human_obj.location = (3.2, -1 - centre_x, max_y)
# skeleton.location = (1.6, -1 - centre_x, -min_y)
# skeleton.dimensions = human_obj.dimensions * scale
#
# human_obj.rotation_euler[0] = -np.pi / 2
# if dataset == '_surr':
#     human_obj.rotation_euler[2] = np.pi / 4
# else:
#     human_obj.rotation_euler[2] = np.pi / 3

#########################             COLOURED MESH             ###############################
##Importing the human mesh

bpy.ops.import_scene.obj(filepath=file_loc)
color_obj = bpy.context.selected_objects[0]
human_name = color_obj.name
bpy.ops.object.select_all(action='DESELECT')
color_obj = bpy.data.objects[human_name]
color_obj.select = True
color_obj.scale = (scale, scale, scale)

human_mesh = color_obj.data

bm = bmesh.new()
bm.from_mesh(human_mesh)

min_x = min_y = min_z = 5
max_x = max_y = max_z = -5

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
scale = new_height / height
centre_x = (max_x + min_x) / 2
print(scale)

bm.free()

# Changing the location and orientation of the mesh
color_obj.scale = (scale, scale, scale)
color_obj.location = (3.2, -1 - centre_x, max_y)
skeleton.location = (1.6, -1 - centre_x, -min_y)
skeleton.dimensions = color_obj.dimensions * scale

color_obj.rotation_euler[0] = -np.pi / 2
if dataset == '_surr':
    color_obj.rotation_euler[2] = np.pi / 4
else:
    color_obj.rotation_euler[2] = np.pi / 3

#######################################################################
####increasing number of vertices of the human mesh using subdivision surface modifiers
print('before subdivision\n' + str(len(human_mesh.vertices)))
bpy.context.scene.objects.active = bpy.data.objects[human_name]
ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide()
ops.object.mode_set(mode='OBJECT')
print('after subdivision\n' + str(len(human_mesh.vertices)))

#######################################################################
####Coloring the entire mesh one vertex at a time

my_object = color_obj.data

# Add "full" address of the color file here
clr_path = os.path.join(source_dir, 'Sample_store', 'highres_clr_picked_%.5d' % img_id + dataset + '_out.npy')
clr = np.load(clr_path)

color_map_collection = my_object.vertex_colors
if len(color_map_collection) == 0:
    color_map_collection.new()

"""
let us assume for sake of brevity that there is now 
a vertex color map called  'Col'    
"""

color_map = color_map_collection['Col']

# or you could avoid using the vertex color map name
# color_map = color_map_collection.active

i = 0
for poly in my_object.polygons:
    for idx in poly.loop_indices:
        vert_index = my_object.loops[idx].vertex_index
        rgb = clr[vert_index]
        color_map.data[i].color = rgb
        i += 1
print('Number of vertices: ' + str(i))

meshMat = bpy.data.materials.new('colourMeshMat')
color_obj.active_material = meshMat
meshMat.use_shadeless = True
meshMat.use_vertex_color_paint = True

# set to vertex paint mode to see the result
color_obj.select = True
bpy.ops.object.mode_set(mode='VERTEX_PAINT')

bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
# bpy.context.scene.render.alpha_mode = 'SKY'

bpy.context.scene.render.resolution_percentage = 100

## Render and save
destination_path = '/Users/raunitdalal/Desktop'
bpy.context.scene.render.filepath = os.path.join(destination_path, 'grid_plots_' + str(img_id) + dataset + ".png")
bpy.ops.render.render(write_still=True)

## Quit blender directly
# bpy.ops.wm.quit_blender()


## load the vertices color file
