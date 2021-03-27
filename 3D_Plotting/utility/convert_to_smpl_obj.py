import trimesh
import numpy as np


files = [1089]
faces = np.load('/Users/raunitdalal/Desktop/faces.npy')

for f in files:
    loc = f'/Users/raunitdalal/Desktop/Blender Scripts/3D_Plotting/folders/{"%.6d" % f}/verts_{"%.6d" % f}.npy'
    verts = np.load(loc)
    mesh = trimesh.Trimesh(vertices=verts, faces=faces)
    out_dir = f'/Users/raunitdalal/Desktop/Blender Scripts/3D_Plotting/folders/{"%.6d" % f}/'
    trimesh.exchange.export.export_mesh(mesh, out_dir + f'object_{"%.6d" % f}.obj')
