''' YIfan's repeating code of the paper P.R.L 108,058301(2012)
 'Fast and Accurate Modeling of Molecular Atomization Energies
 with Machine Learning'
'''
from TensorMol import *

b=MSet("gdb9")
b.ReadXYZ("gdb9")
# Load GDB9
print(b.mols[0].coords)


TreatedAtoms = b.AtomTypes()
d=Digester(TreatedAtoms, name_="Coulomb", OType_="Energy")

# Make a coulomb MolDigester which works over the whole molecule.

tset=TensorData(b,d)

tset.BuildTrainMolwise("gdb9_NEQ",TreatedAtoms)
# Make a Tensordata and use it to buildtraining data
'''
#manager=TFManager("gdb9_NEQ_"+dig_)
# Make a TFManager to produce a KRR instance.
# Train.
# Test.
'''
