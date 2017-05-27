#
# Optimization algorithms
#

from .Mol import *
from .Sets import *
from .TFMolManage import *

class NN_MBE:
	def __init__(self,tfm_=None):
		self.nn_mbe = dict()
		if tfm_ != None:
			for order in tfm_:
				print tfm_[order]
				self.nn_mbe[order] = TFMolManage(tfm_[order], None, False)
		return


	def NN_Energy(self, mol):
		mol.Generate_All_MBE_term(atom_group=3, cutoff=6, center_atom=0)  # one needs to change the variable here
		nn_energy = 0.0
		for i in range (1, mol.mbe_order+1):
			nn_energy += self.nn_mbe[i].Eval_Mol(mol)
		mol.Set_MBE_Force()
		mol.nn_energy = nn_energy
		print "coords of mol:", mol.coords
		print "force of mol:", mol.properties["mbe_deri"]
		print "energy of mol:", nn_energy
		return


class NN_MBE_BF:
        def __init__(self,tfm_=None, dipole_tfm_=None):
		self.mbe_order = PARAMS["MBE_ORDER"]
                self.nn_mbe = tfm_
		self.nn_dipole_mbe = dipole_tfm_
                return

        def NN_Energy(self, mol):
		s = MSet()
		for order in range (1, self.mbe_order+1):
			s.mols += mol.mbe_frags[order]
		energies =  np.asarray(self.nn_mbe.Eval_BPEnergy(s))
		print "energies:", energies
		pointer = 0
		for order in range (1, self.mbe_order+1):
			mol.frag_energy_sum[order] = np.sum(energies[pointer:pointer+len(mol.mbe_frags[order])])
			pointer += len(mol.mbe_frags[order])
		mol.MBE_Energy()
                return

	def NN_Dipole(self, mol):
                s = MSet()
                for order in range (1, self.mbe_order+1):
                        s.mols += mol.mbe_frags[order]
                dipoles, charges =  self.nn_dipole_mbe.Eval_BPDipole_2(s)
                #print "dipole:", dipoles
                pointer = 0
                for order in range (1, self.mbe_order+1):
                        mol.frag_dipole_sum[order] = np.sum(dipoles[pointer:pointer+len(mol.mbe_frags[order])], axis=0)
                        pointer += len(mol.mbe_frags[order])
		#print "mol.frag_dipole_sum[order] ", mol.frag_dipole_sum
		mol.MBE_Dipole()
                return
