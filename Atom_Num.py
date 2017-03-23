from Mol import *
from Util import *
import os, sys, re, random, math, copy, itertools
import numpy as np
import cPickle as pickle
import LinearOperations, DigestMol, Digest, Opt


def EmbAtomwiseErr(mol_,dig_,emb_,Gdatom):
	ins = dig_.TrainDigestMolwise(mol_,MakeOutputs_=False)
	err = np.sqrt(np.sum((ins-emb_)*(ins-emb_)))
	return err

def Atoms_Num(coord_,dig_,emb_,Gdatom,atom_=None):
#Yifan's test about reproduce atom numbers

  if (1):
	def callbk(x_):
		mn = Mol(atom_)
		print "Atom error :",np.sqrt(np.sum((Gdatom-mn.atoms)*(Gdatom-mn.atoms)))
                print(Mol.atoms,".....",Gdatom)
  #all atoms are hydragen at first
  atom_= np.ones(len(Gdatom_), dtype=np.uint8)
  natom=len(atom_)
  YFob=lambda AtomNum: EmbAtomwiseErr(Mol(AtomNum,coord_),dig_,emb_)

  import scipy.optimize

  step=0
  #coords=coord_.reshape(natom*3)
  while (EmbAtomwiseErr(Mol(atom_,coord_),dig_,emb_) > 1.e-5) and (step < 10):
		step += 1
		res=scipy.optimize.minimize(YFob,atom_,method='L-BFGS-B',tol=2*natom,options={"maxiter":5000000,"maxfun":10000000},callback=callbk)
		print "Reversal complete: ", res.message
                for i in range(res.x):
                       if res.x[i]<1:
                          atom_[i]=1
                       elif res.x[i]>8:
                          atom_[i]=8
                       else:
                          atom_[i]=int(res.x[i]) 

  mfit=Mol(atom_,coord)               
  return


#def Yifan_Atoms(mol_, dig_, emb_):







