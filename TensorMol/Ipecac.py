"""
 Ipecac: a syrup which causes vomiting.
 This file contains routines which 'attempt' to reverse embeddings back to the geometry of a molecule.
 Ie: it's the inverse of Digest.py
"""

import os, sys, re, random, math, copy, itertools
import numpy as np
import cPickle as pickle

from .Mol import *
from .Util import *
from . import LinearOperations, DigestMol, Digest, Opt

def EmbAtomwiseErr(mol_,dig_,emb_):
	ins = dig_.TrainDigestMolwise(mol_,MakeOutputs_=False)
	err = np.sqrt(np.sum((ins-emb_)*(ins-emb_)))
	return err

def ReverseAtomwiseEmbedding(dig_, emb_,atoms_=None, guess_=None, GdDistMatrix=None):
	"""
	Args:
		atoms_: a list of element types for which this routine provides coords.
		dig_: a digester
		emb_: the embedding which we will try to construct a mol to match. Because this is atomwise this will actually be a (natom X embedding shape) tensor.
	Returns:
		A best-fit version of a molecule which produces an embedding as close to emb_ as possible.
	"""
	natom = len(atoms_)
	# Construct a random non-clashing guess.
	# this is the tricky step, a random guess probably won't work.
	coords = np.random.rand(natom,3)
	if (guess_==None):
	# This puts natom into a cube of length 1 so correct the density to be roughly 1atom/angstrom.
		coords *= natom
		mfit = Mol(atoms_,coords)
		mfit.WriteXYZfile("./results/", "RevLog")
		# Next optimize with an equilibrium distance matrix which is roughly correct for each type of species...
		mfit.DistMatrix = np.ones((natom,3))
		np.fill_diagonal(mfit.DistMatrix,0.0)
		opt = Optimizer(None)
		opt.OptGoForce(mfit)
		mfit.WriteXYZfile("./results/", "RevLog")
	else:
		coords = guess_
	atoms = np.ones(len(atoms_), dtype=np.uint8)
	# Now shit gets real. Create a function to minimize.
	objective = lambda crds: EmbAtomwiseErr(Mol(atoms,crds.reshape(natom,3)),dig_,emb_)
	if (1):
		def callbk(x_):
			mn = Mol(atoms, x_.reshape(natom,3))
			mn.BuildDistanceMatrix()
			print "Distance error : ", np.sqrt(np.sum((GdDistMatrix-mn.DistMatrix)*(GdDistMatrix-mn.DistMatrix)))
	import scipy.optimize
	step = 0
	while (EmbAtomwiseErr(Mol(atoms,coords),dig_,emb_) > 1.e-5) and (step < 10):
		step += 1
		res=scipy.optimize.minimize(objective,coords.reshape(natom*3),method='L-BFGS-B',tol=0.000001,options={"maxiter":5000000,"maxfun":10000000},callback=callbk)
		print "Reversal complete: ", res.message
		coords = res.x.reshape(natom,3)
		mfit = Mol(atoms, coords)
		atoms = BruteForceAtoms(mfit, dig_, emb_)
	mfit = Mol(atoms, coords)
	return mfit

def BruteForceAtoms(mol_, dig_, emb_):
	print "Searching for best atom fit"
	bestmol = copy.deepcopy(mol_)
	besterr = 100.0
	posib_stoich = [x for x in itertools.product([1,6,7,8], repeat=len(mol_.atoms))]
	for stoich in posib_stoich:
		tmpmol = Mol(np.array(stoich), mol_.coords)
		tmperr = EmbAtomwiseErr(tmpmol,dig_,emb_)
		if tmperr < besterr:
			bestmol = copy.deepcopy(tmpmol)
			besterr = tmperr
			print besterr
	print bestmol.atoms
	return bestmol.atoms
