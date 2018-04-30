#!/Users/yuzhang/anaconda3/bin/python

import itertools
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--length', type = int, default = 2, help = 'Alkyl chain length')
parser.add_argument('-n', '--name', default = 'TEA', help = 'name of the molecule')
parser.add_argument('-o', '--output', default = 'TAA.itp', help = 'name of the output file')

try:
    __IPYTHON__
    args = parser.parse_args([])
except NameError:
    args = parser.parse_args()

class Atom(object):
    index = 0
    cgroup = 0
    def __init__(self, atomname):
        '''Initialize an atom with a unique index and empty neighbor list and no charge group'''
        self.name = atomname
        Atom.index += 1
        self.index = Atom.index
        self.neighbors = []
        self.cgroup = None
    def assign_cgroup(self, n = None):
        if n is None:
            Atom.cgroup += 1
            self.cgroup = Atom.cgroup
        else:
            self.cgroup = n
    def add_neighbor(self, other):
        '''Add neighbor to an atom'''
        self.neighbors.append(other.index)
        other.neighbors.append(self.index)
    def add_neighbors(self, iterator):
        '''Add neighbors from an iterator object'''
        for item in iterator:
            self.add_neighbor(item)
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
    def __lt__(self, other):
        return self.index < other.index
    @staticmethod
    def clear_index():
        '''Clean the atom index'''
        Atom.index = 0
        Atom.cgroup = 0

class TAA(object):
    '''Tetraalkylammonium'''
    def __init__(self, name = 'TAA'):
        '''Initialize an molecule with an N atom'''
        self.name = name
        self.atoms = {}
        self.root = Atom('N3')
        self.root.assign_cgroup()
        self.add_atom(self.root)
        self.bonds = []
        self.angles = []
        self.dihedrals = []
    def get_number(self):
        '''Return the '''
        return len(self.atoms)
    def add_atom(self, atom):
        self.atoms[atom.index] = atom
    def add_bond(self, atom1, atom2):
        atom1.add_neighbor(atom2)
        self.bonds.append((min(atom1.index, atom2.index), max(atom1.index, atom2.index)))
    def add_alkyl(self, n = 2):
        for rep in range(4):
            prev = self.root
            for i in range(n):
                if i == 0:
                    Cname = 'C1'
                    Hname = 'H1'
                else:
                    Hname = 'HC'
                    if i == 1:
                        Cname = 'C2'
                    elif i == n-1:
                        Cname = 'CT'
                    else:
                        Cname = 'CS'
                C = Atom(Cname)
                C.assign_cgroup()
                self.add_atom(C)
                self.add_bond(prev, C)
                prev = C
                for j in range(2):
                    H = Atom(Hname)
                    self.add_atom(H)
                    self.add_bond(C, H)
                    H.assign_cgroup(C.cgroup)
            H = Atom('HC')
            self.add_atom(H)
            self.add_bond(C, H)
            H.assign_cgroup(C.cgroup)
        self.add_angles()
        self.add_dihedrals()
    def add_angles(self):
        for i in range(1, self.get_number()+1):
            center = self.atoms[i]
            if len(center.neighbors) > 1:
                for index1, index2 in itertools.combinations(center.neighbors, 2):
                    self.angles.append((min(index1, index2), center.index, max(index1, index2)))
                    
    def add_dihedrals(self):
        '''Only proper dihedrals are needed for this series of compounds. Add dihedrals according to the
        bond information.
        '''
        for bond in self.bonds:
            for i, j in itertools.product(self.atoms[bond[0]].neighbors, self.atoms[bond[1]].neighbors):
                if i != bond[1] and j != bond[0] and i != j: # avoid triangle loop like cyclopropane
                    self.dihedrals.append((i, bond[0], bond[1], j))
    def write_itp(self, para, filename = 'TAA.itp'):
        '''write all atoms to an itp file'''
        myfile = open(filename, 'w')
        myfile.write('[ moleculetype ]\n')
        myfile.write('%s\t3\n' %self.name)
        
        myfile.write('[ atoms ]\n')
        for i in range(1, self.get_number()+1):
            atomname = self.atoms[i].name
            myfile.write('%5d%5s%5d%5s%5s%5d%12.4f%12.4f\n' %(i, atomname, 1, self.name, atomname[0]+str(i),
                                        self.atoms[i].cgroup, para[atomname][0], para[atomname][1]))
        
        myfile.write('[ bonds ]\n')
        for bond in self.bonds:
            myfile.write('%5d%5d%5d\n' %(bond+(1,)))
        
        myfile.write('[ angles ]\n')
        for angle in self.angles:
            myfile.write('%5d%5d%5d%5d\n' %(angle+(1,)))
            
        myfile.write('[ dihedrals ]\n')
        for dih in self.dihedrals:
            myfile.write('%5d%5d%5d%5d%5d\n' %(dih+(1,)))
        myfile.close()
        
## main ##
para = {'N3': (0.12, 14.007),
        'C1': (-0.17, 12.011),
        'H1': (0.13, 1.008),
        'C2': (0.01, 12.011),
        'CS': (-0.12, 12.011),
        'CT': (-0.18, 12.011),
        'HC': (0.06, 1.008)
       }

Atom.clear_index()
TEA = TAA(args.name)
TEA.add_alkyl(args.length)
TEA.write_itp(para, args.output)
