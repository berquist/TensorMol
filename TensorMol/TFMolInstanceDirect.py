from __future__ import division
from __future__ import print_function

"""
	These instances work directly on raw coordinate, atomic number data.
	They either generate their own descriptor or physical model.
	They are also simplified relative to the usual MolInstance.
"""

from .TFInstance import *
from .TensorMolData import *
from .TFMolInstance import *
from .ElectrostaticsTF import *


class MolInstance_LJForce(MolInstance_fc_sqdiff_BP):
	"""
	Optimizes a LJ force where pairs of atoms have specific
	Epsilon and Re parameters.
	"""
	def __init__(self, TData_, Name_=None, Trainable_=True):
		"""
		Args:
			TData_: A TensorMolData instance.
			Name_: A name for this instance.
		"""
		self.NetType = "LJForce"
		self.TData = TData_
		self.name = "Mol_"+self.TData.name+"_"+self.TData.dig.name+"_"+self.NetType
		LOGGER.debug("Raised Instance: "+self.name)
		self.train_dir = './networks/'+self.name
		self.MaxNAtoms = TData_.MaxNAtoms
		self.batch_size_output = 4096
		self.inp_pl=None
		self.frce_pl=None
		self.LJe = None
		self.LJr = None
		self.sess = None
		self.forces = None
		self.energies = None
		self.total_loss = None
		self.loss = None
		self.train_op = None
		self.summary_op = None
		self.saver = None
		self.summary_writer = None
		self.dbg1 = None
		self.dbg2 = None
		# Using multidimensional inputs creates all sorts of issues; for the time being only support flat inputs.

	def train_prepare(self,  continue_training =False):
		"""
		Get placeholders, graph and losses in order to begin training.
		Also assigns the desired padding.

		Args:
			continue_training: should read the graph variables from a saved checkpoint.
		"""
		with tf.Graph().as_default():
			self.inp_pl=tf.placeholder(tf.float32, shape=tuple([None,self.MaxNAtoms,4]))
			self.frce_pl = tf.placeholder(tf.float32, shape=tuple([None,self.MaxNAtoms,3])) # Forces.
			self.LJe = tf.Variable(0.1*tf.ones([8,8]),trainable=True)
			self.LJr = tf.Variable(tf.ones([8,8]),trainable=True)
			# These are squared later to keep them positive.
			self.energies, self.forces = self.LJFrc(self.inp_pl)
			self.total_loss, self.loss = self.loss_op(self.forces, self.frce_pl)
			self.train_op = self.training(self.total_loss, PARAMS["learning_rate"], PARAMS["momentum"])
			self.summary_op = tf.summary.merge_all()
			init = tf.global_variables_initializer()
			self.sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
			self.saver = tf.train.Saver()
			self.summary_writer = tf.summary.FileWriter(self.train_dir, self.sess.graph)
			self.sess.run(init)
		return

	def loss_op(self, output, labels):
		"""
		The loss operation of this model is complicated
		Because you have to construct the electrostatic energy moleculewise,
		and the mulitpoles.

		Emats and Qmats are constructed to accerate this process...
		"""
		output = tf.Print(output,[output],"Comp'd",1000,1000)
		labels = tf.Print(labels,[labels],"Desired",1000,1000)
		diff  = tf.subtract(output, labels)
		#tf.Print(diff, [diff], message="This is diff: ",first_n=10000000,summarize=100000000)
		loss = tf.nn.l2_loss(diff)
		tf.add_to_collection('losses', loss)
		return tf.add_n(tf.get_collection('losses'), name='total_loss'), loss

	def LJFrc(self, inp_pl):
		"""
		Compute forces for a batch of molecules
		with the current LJe, and LJr.

		Args:
			inp_pl: placeholder for the NMol X MaxNatom X 4 tensor of Z,x,y,z
		"""
		# separate out the Z from the XYZ.
		inp_shp = tf.shape(inp_pl)
		nmol = inp_shp[0]
		maxnatom = inp_shp[1]
		XYZs = tf.slice(inp_pl,[0,0,1],[-1,-1,-1])
		Zs = tf.cast(tf.reshape(tf.slice(inp_pl,[0,0,0],[-1,-1,1]),[nmol,maxnatom,1]),tf.int32)
		self.LJe = tf.Print(self.LJe,[self.LJe],"LJe",1000,1000)
		self.LJr = tf.Print(self.LJr,[self.LJr],"LJr",1000,1000)
		LJe2 = self.LJe*self.LJe
		LJr2 = self.LJr*self.LJr
		#LJe2 = tf.Print(LJe2,[LJe2],"LJe2",1000,1000)
		#LJr2 = tf.Print(LJr2,[LJr2],"LJr2",1000,1000)
		Ens = LJEnergies(XYZs, Zs, LJe2, LJr2)
		#Ens = tf.Print(Ens,[Ens],"Energies",5000,5000)
		frcs = -1.0*(tf.gradients(Ens, XYZs)[0])
		return Ens, frcs

	def EvalForce(self,m):
		Ins = self.TData.dig.Emb(m,False,False)
		Ins = Ins.reshape(tuple([1]+list(Ins.shape)))
		feeddict = {self.inp_pl:Ins}
		En,Frc = self.sess.run([self.energies, self.forces],feed_dict=feeddict)
		return En,JOULEPERHARTREE*Frc[0] # Returns energies and forces.

	def print_training(self, step, loss, Ncase, duration, Train=True):
		print("step: ", "%7d"%step, "  duration: ", "%.5f"%duration,  "  train loss: ", "%.10f"%(float(loss)/(Ncase)))
		return

	def Prepare(self):
		self.train_prepare()
		return

	def train_step(self, step):
		"""
		Perform a single training step (complete processing of all input), using minibatches of size self.batch_size

		Args:
			step: the index of this step.
		"""
		Ncase_train = len(self.TData.set.mols)
		start_time = time.time()
		train_loss =  0.0
		num_of_mols = 0
		for ministep in range (0, int(Ncase_train/self.batch_size_output)):
			#print ("ministep: ", ministep, " Ncase_train:", Ncase_train, " self.batch_size", self.batch_size)
			batch_data = self.TData.RawBatch()
			if (not np.all(np.isfinite(batch_data[0]))):
				print("Bad Batch...0 ")
			if (not np.all(np.isfinite(batch_data[1]))):
				print("Bad Batch...1 ")
			feeddict={i:d for i,d in zip([self.inp_pl,self.frce_pl],[batch_data[0],batch_data[1]])}
			dump_2, total_loss_value, loss_value = self.sess.run([self.train_op, self.total_loss, self.loss], feed_dict=feeddict)
			train_loss = train_loss + loss_value
			duration = time.time() - start_time
			num_of_mols += self.batch_size_output
			#print ("atom_outputs:", atom_outputs, " mol outputs:", mol_output)
			#print ("atom_outputs shape:", atom_outputs[0].shape, " mol outputs", mol_output.shape)
		#print("train diff:", (mol_output[0]-batch_data[2])[:actual_mols], np.sum(np.square((mol_output[0]-batch_data[2])[:actual_mols])))
		#print ("train_loss:", train_loss, " Ncase_train:", Ncase_train, train_loss/num_of_mols)
		#print ("diff:", mol_output - batch_data[2], " shape:", mol_output.shape)
		self.print_training(step, train_loss, num_of_mols, duration)
		return

	def train(self, mxsteps=10000):
		self.train_prepare()
		LOGGER.info("MolInstance_LJForce.train()")
		test_freq = PARAMS["test_freq"]
		mini_test_loss = float('inf') # some big numbers
		for step in  range (0, mxsteps):
			self.train_step(step)
		self.SaveAndClose()
		return
