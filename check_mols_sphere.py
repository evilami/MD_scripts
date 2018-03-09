#!/Users/yuzhang/anaconda/envs/py3/bin/python
import mdtraj as md
import matplotlib.pyplot as plt
import numpy as np

import calc_common as comm

traj_name, traj0, topology = comm.load_traj()
para = comm.load_para()
res_targ, res_name = comm.select_groups(traj0)
massind, chargeind = comm.load_atomic(res_targ, topology, para)

center = (4.48300466, 4.48300138, 4.48199593)

res_targ = np.array(res_targ)
if comm.args.v:
    print('The center is located at', center)
    print('Radius:', comm.args.exb)
    print('Cut off distance from surface:', comm.args.cutoff)
    print('Final molecules are writing to file %s...' %"mol_remain.txt")

chunk_size = 100
for chunk_index, traj in enumerate(md.iterload(traj_name, chunk_size, top= 'begin.gro')):
    for sub_ind, frame in enumerate(traj):
        mol_rem = [[] for _ in res_targ]
        temp = [[] for _ in res_targ]
        xyz_com = comm.calc_xyz_com(res_targ, frame, topology, para)
        temp = []
        for resid in range(len(res_targ)):
            dist2 = np.sum((xyz_com[resid]-center)**2, axis = 1)
            temp.append(res_targ[resid][dist2 <= (comm.args.exb+comm.args.cutoff)**2])
        res_targ = np.array(temp)
        if comm.args.v and sub_ind%10 == 9: 
            print('Molecules remained:', [len(i) for i in res_targ], end = ", ")
            print('Reading chunk', chunk_index+1, 'and frame',chunk_index*chunk_size+sub_ind+1)
    if chunk_index == 0:
        break

np.savetxt('mol_remain.txt', res_targ, fmt = '%s')
outfile = open('mol_remain.txt', 'w')
for res in res_targ:
    for item in res:
        outfile.write('%d\t' %item)
    outfile.write('\n')
outfile.close()
