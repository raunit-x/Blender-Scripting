import trimesh
import bpy
import pickle as pkl
import numpy as np

MESH_PROP_FACES_FL = '/Users/raunitdalal/Desktop/Blender Scripts/3D_Plotting/basicModel_m_lbs_10_207_0_v1.0.0.pkl'
with open(MESH_PROP_FACES_FL, 'rb') as f:
    sampling = pkl.load(f)
