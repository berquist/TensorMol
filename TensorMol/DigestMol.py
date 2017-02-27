"""
 Calculate an embeeding for a molecule, such as coulomb matrix
 Todo: Should inherit from Digest.py (which needs cleanup)
"""

from Mol import *
from Util import *

class MolDigester:
    def __init__(self, eles_, name_="Coulomb", OType_="FragEnergy", SensRadius_=6):
    	self.name = name_
    	self.OType = OType_
    	self.lshape = None  # output is just the energy
    	self.eshape = None
    	self.SensRadius = SensRadius_
    	self.eles = eles_
        self.MeanNorm=0.0
    	self.StdNorm=1.0
    	self.neles = len(eles_) # Consistent list of atoms in the order they are treated.
    	self.ngrid = 5 #this is a shitty parameter if we go with anything other than RDF and should be replaced.
    	self.nsym = self.neles+(self.neles+1)*self.neles  # channel of sym functions

    def AssignNormalization(self,mn,sn):
    	self.MeanNorm=mn
    	self.StdNorm=sn
    	return

    def make_sym(self, mol):
    	zeta=[]
    	eta1=[]
    	eta2=[]
    	Rs=[]
    	eles = list(set(list(mol.atoms)))
    	SYM = []
    	for i in range (0, self.ngrid):
    		zeta.append(1.5**i)    # set some value for zeta, eta, Rs
    		eta1.append(0.008*(2**i))
    		eta2.append(0.002*(2**i))
    		Rs.append(i*self.SensRadius/float(self.ngrid))
    	for i in range (0, mol.NAtoms()):
    		sym =  MolEmb.Make_Sym(mol.coords, (mol.coords[i]).reshape((1,-1)), mol.atoms.astype(np.uint8), self.eles.astype(np.uint8), i, self.SensRadius, zeta, eta1, eta2, Rs)
    		sym = np.asarray(sym[0], dtype=np.float32)
    		sym = sym.reshape((self.nsym*sym.shape[1] *  sym.shape[2]))
    		#print "sym", sym
    		SYM.append(sym)
    	SYM =  np.asarray(SYM)
    	print "mol.atoms", mol.atoms, "SYM", SYM
    	SYM_deri = np.zeros((SYM.shape[0], SYM.shape[1])) # debug, it will take some work to implement to derivative of sym func.
    	return SYM, SYM_deri

    def make_cm_bp(self, mol):
    	CM_BP = []
    	ngrids = 10
    	for i in range (0, mol.NAtoms()):
    		cm_bp = MolEmb.Make_CM(mol.coords, (mol.coords[i]).reshape((1,-1)), mol.atoms.astype(np.uint8), self.eles.astype(np.uint8), self.SensRadius, ngrids, i,  0.0 )
    		#print "before: ", cm_bp, len(cm_bp)
    		cm_bp = np.asarray(cm_bp[0], dtype=np.float32)
    		cm_bp.flatten()
    		#print "SHAPE", cm_bp.shape
    		#cm_bp = cm_bp.reshape(-1)
    		#cm_bp = cm_bp[np.nonzero(cm_bp)] #Kun: what were you trying to do here...
    		CM_BP.append(cm_bp)
    	CM_BP = np.array(CM_BP)[0,:,:]
    	CM_BP_deri = np.zeros((CM_BP.shape[0], CM_BP.shape[1])) # debug, it will take some work to implement to derivative of coloumb_bp func.
    	return 	CM_BP, CM_BP_deri

    def make_gauinv(self, mol):
    	""" This is a totally inefficient way of doing this
    		MolEmb should loop atoms. """
    	GauInv = []
    	for i in range (0, mol.NAtoms()):
    		gauinv = MolEmb.Make_Inv(mol.coords, (mol.coords[i]).reshape((1,-1)), mol.atoms.astype(np.uint8),self.SensRadius, i)
    		gauinv = np.asarray(gauinv[0], dtype = np.float32 )
    		gauinv = gauinv.reshape(-1)
    		GauInv.append(gauinv)
    	GauInv = np.asarray(GauInv)
    	GauInv_deri = np.zeros((GauInv.shape[0], GauInv.shape[1]))
    	return GauInv, GauInv_deri

    def make_cm(self, mol_):
    	natoms  = mol_.NAtoms()
    	CM=np.zeros((natoms, natoms))
    	deri_CM = np.zeros((natoms, natoms, 6))
    	xyz = (mol_.coords).copy()
    	#ele = (mol_.atoms).copy()
    	ele = np.zeros(natoms)  # for eebug
    	ele.fill(1.0)   # for debug, set ele value to 1
    	code = """
    	double dist = 0.0;
    	double deri[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    	for (int j=0; j < natoms; j++) {
    		for (int k=0; k<natoms; k++) {
    			if (k==j) {
    				dist=1.0;
    				deri[0] =0.0;
    				deri[1] =0.0;
    				deri[2] =0.0;
    				deri[3] =0.0;
    				deri[4] =0.0;
    				deri[5] =0.0;
    			}
    			else {
    				dist=sqrt(pow(xyz[j*3+0]-xyz[k*3+0],2) + pow(xyz[j*3+1]-xyz[k*3+1],2) + pow(xyz[j*3+2]-xyz[k*3+2],2));
    				deri[0] = -(xyz[j*3+0]-xyz[k*3+0])/(dist*dist*dist);
    				deri[1] = -(xyz[j*3+1]-xyz[k*3+1])/(dist*dist*dist);
    				deri[2] = -(xyz[j*3+2]-xyz[k*3+2])/(dist*dist*dist);
    				deri[3] = -deri[0];
    				deri[4] = -deri[1];
    				deri[5] = -deri[2];
    			}
    			CM[natoms*j+k]= ele[j]*ele[k]/dist;
    			deri_CM[natoms*j*6+k*6+0]=ele[j]*ele[k]*deri[0];
    			deri_CM[natoms*j*6+k*6+1]=ele[j]*ele[k]*deri[1];
    			deri_CM[natoms*j*6+k*6+2]=ele[j]*ele[k]*deri[2];
    			deri_CM[natoms*j*6+k*6+3]=ele[j]*ele[k]*deri[3];
    			deri_CM[natoms*j*6+k*6+4]=ele[j]*ele[k]*deri[4];
    			deri_CM[natoms*j*6+k*6+5]=ele[j]*ele[k]*deri[5];
    		}

    	}

    	"""
    	res = inline(code, ['CM','natoms','xyz','ele', 'deri_CM'],headers=['<math.h>','<iostream>'], compiler='gcc')
    	return CM, deri_CM

    def GetUpTri(self, CM):
    	CM = CM[np.triu_indices(CM.shape[0], 1)].copy() ##for debug purpose, ignore the diagnoal element
    	#index = np.array([2,3,4,6,7,8,9,10,11]) # for debug, ignore the AA, BB block, only remain AB
    	#CM = CM[index].copy()  # for debug
    	return  CM  #for debug purpose, ignore the diagnoal element

    def EvalDigest(self, mol_):
    	return self.Emb(mol_,False)

    def Emb(self, mol_, MakeOutputs=True, MakeGradients=False):
    	"""
    	Generates various molecular embeddings.
    	If the embedding has BP on the end it comes out atomwise and includes all atoms in the molecule.
    	Args:
    		mol_: a Molecule to be digested
    		MakeOutputs: generates outputs according to self.OType.
    		MakeGradients: generates outputs according to self.OType.
    	Returns:
    		Output embeddings, and possibly labels and gradients.
    	Todo:
    		Hook up the gradients.
    	"""
    	Ins=None
    	Grads=None
    	Outs=None
    	if (self.name == "Coulomb"):
    		CM, deri_CM = self.make_cm(mol_)
    		Ins = self.GetUpTri(CM)
    	elif(self.name == "Coulomb_BP"):
    		Ins, deri_CM_BP =  self.make_cm_bp(mol_)
    		Ins = Ins.reshape([Ins.shape[0],-1])
    	elif(self.name == "SymFunc"):
    		Ins, SYM_deri = self.make_sym(mol_)
    	elif(self.name == "GauInv_BP"):
    		Ins =  MolEmb.Make_Inv(PARAMS, mol_.coords, mol_.atoms, -1);
    	elif(self.name == "GauSH_BP"):
            # Here I have to add options to octahedrally average SH
    		Ins =  MolEmb.Make_SH(PARAMS, mol_.coords, mol_.atoms, -1);
    	else:
    		raise Exception("Unknown MolDigester Type.", self.name)

    	if (self.eshape == None):
    		self.eshape=Ins.shape[1:] # The first dimension is atoms. eshape is per-atom.
    	if (MakeOutputs):
            if (self.OType == "Energy"):
            	Outs = np.array([mol_.properties["energy"]])
            elif (self.OType == "AtomizationEnergy"):
                Outs = np.array([mol_.properties["atomization"]])
            elif (self.OType == "FragEnergy"):
            	Outs = np.array([mol_.frag_mbe_energy])
            elif (self.OType == "GoEnergy"):
            	Outs = np.array([mol_.GoEnergy()])
            else:
            	raise Exception("Unknown Output Type... "+self.OType)

            if (self.lshape == None):
            	self.lshape=Outs.shape
            if (MakeGradients):
            	return Ins, Grads, Outs
            else:
            	return Ins, Outs
    	else:
    		 return Ins

    def TrainDigest(self, mol_):
    	"""
    	Returns list of inputs and outputs for a molecule.
    	Uses self.Emb() uses Mol to get the Desired output type (Energy,Force,Probability etc.)
    	Args:
    		mol_: a molecule to be digested
    	"""
    	return self.Emb(mol_,True,False)

    def unscld(self,a):
        return (a*self.StdNorm+self.MeanNorm)

    def EvaluateTestOutputs(self, desired, predicted, nmols_=100):
        LOGGER.info("desired.shape "+str(desired.shape)+" predicted.shape "+str(predicted.shape)+" nmols "+str(nmols_))
        LOGGER.info("Evaluating, "+str(len(desired))+" predictions... ")
        if (self.OType=="GoEnergy" or self.OType == "Energy" or self.OType == "AtomizationEnergy"):
            predicted=predicted.flatten()[:nmols_]
            desired=desired.flatten()[:nmols_]
            LOGGER.info( "NCases: "+str(len(desired))+"Mean Norm and Std"+str(self.MeanNorm)+" "+str(self.StdNorm))
            #LOGGER.info( "Mean Energy "+str(self.unscld(desired)))
            #LOGGER.info( "Mean Predicted Energy "+str(self.unscld(predicted)))
            for i in range(min(50,nmols_)):
                LOGGER.info( "Desired: "+str(i)+" "+str(self.unscld(desired[i]))+" Predicted "+str(self.unscld(predicted[i])))
            LOGGER.info("MAE "+str(np.average(np.abs(self.unscld(desired)-self.unscld(predicted)))))
            LOGGER.info("STD "+str(np.std(self.unscld(desired-predicted))))
        else:
        	raise Exception("Unknown Digester Output Type.")
        return

    def Print(self):
    	print "Digest name: ", self.name
