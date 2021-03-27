import sys
import os

import numpy as np

import trimesh


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


out_DIR = "./"

MESH_PROP_FACES_FL = './assets/smpl_sampling.pkl'
with open(os.path.join(os.path.dirname(__file__), MESH_PROP_FACES_FL), 'rb') as f:
    sampling = pkl.load(f)

M = sampling['meshes']

faces_np = M[0]['f'].astype(np.int32)

verts = np.load("verts.npy")
mesh = trimesh.Trimesh(vertices=verts, faces=faces_np)
trimesh.exchange.export.export_mesh(mesh, out_DIR + "object_" + str(img_id) + ".obj")

j17_test = smpl24_to_17j_adv(src_gt_j3d[instance_id])
print ("TEST::", j17_test.shape)
np.save(out_DIR + "17_j3d_" + str(img_id) + '_' + dataset + "_out.npy", j17_test)

#############
SMPL_24_limb_parents = [0,  #####for smpl joints
                        0, 0, 0,
                        1, 2, 3, 4,
                        5, 6, 7, 8,
                        9, 9, 9,
                        12, 12, 12,
                        16, 17, 18, 19, 20, 21
                        ]

SMPL_24_colors = np.array(
    [[0, 0, 255], [0, 255, 0], [255, 0, 0], [255, 0, 255], [0, 255, 255], [255, 255, 0], [127, 127, 0], [0, 127, 0],
     [100, 0, 100],
     [255, 0, 255], [0, 255, 0], [0, 0, 255], [255, 255, 0], [127, 127, 0], [100, 0, 100], [175, 100, 195],
     [0, 0, 255], [0, 255, 0], [255, 0, 0], [255, 0, 255], [0, 255, 255], [255, 255, 0], [127, 127, 0], [0, 127, 0],
     [100, 0, 100],
     [255, 0, 255], [0, 255, 0], [0, 0, 255], [255, 255, 0], [127, 127, 0], [100, 0, 100], [175, 100, 195]])
