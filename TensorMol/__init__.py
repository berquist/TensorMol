"""Code Conventions and Style Guide:

- USE HARD TABS. configure whatever editor you are using to use hard tabs.
- UseCapitalizationToSeparateWords in names.
- Prefer long interperable words to ambiguous abbreviations.
- Avoid_the_underscore to separate words which takes longer to type than a cap.
- The underscore is a good way to denote a function argument.
- Keep functions to fewer than 5 parameters
- Keep files and classes to < 2000 lines.
- Keep classes to < 20 member variables.
- Keep loops to a depth < 6
- Use functional programming constructs whenever possible.
- Use docstrings, you asshole and use Args: and Returns:
- Commit your changes once a day at least.
- Use np.array rather than python list whenever possible.
- It's NOT okay to put default parameters in __init__() and change them all the time instead add them to TMPARAMS.py so they become logged parameters attached to results.
- import TensorMol as tm; works as desired, don't mess that up.

Violators are subject to having their code and reproductive fitness mocked publically in comments.
"""

from .PhysicalData import *
from .Util import *
from .Mol import *
from .Sets import *
from .MolFrag import *
from .Opt import *
from .Neb import *
from .Digest import *
from .DigestMol import *
from .TensorData import *
from .TensorMolData import *
from .TensorMolDataEE import *
from .TFInstance import *
from .TFMolInstance import *
from .TFMolInstanceDirect import *
from .TFManage import *
from .TFMolManage import *
from .Ipecac import *
from .EmbOpt import *
from .Basis import *
from .DIIS import *
from .BFGS import *
from .Neb import *
from .SimpleMD import *
from .ElectrostaticsTF import *
from .Electrostatics import *
from .LinearOperations import *
from .AbInitio import *

from . import *
from . import AbInitio
from . import Basis
from . import BFGS
from . import DigestMol
from . import Digest
from . import DIIS
from . import Electrostatics
from . import ElectrostaticsTF
from . import EmbOpt
from . import Grids
from . import Ipecac
from . import LinearOperations
from . import MBEData
from . import MBE_Opt
from . import MBE
from . import MolFrag
from . import MolGraph
from . import Mol
from . import Neb
from . import NN_MBE
from . import Opt
from . import PhysicalData
from . import PickleTM
from . import QuasiNewtonTools
from . import Sets
from . import SimpleMD
from . import TensorData
from . import TensorMolDataEE
from . import TensorMolData
from . import TFInstance
from . import TFManage
from . import TFMolInstanceDirect
from . import TFMolInstanceEE
from . import TFMolInstance
from . import TFMolManage
from . import TFMolManageQ
from . import TMParams
from . import Transformer
from . import Util
