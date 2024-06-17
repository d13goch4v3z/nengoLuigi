# this file has the same structure as simpleIO_3.py but wwe 
# added couple of extra ensembles and nodes to the network.
# we also added extra probes to the network. 
#
# libs
import os, time, signal, rospy, sys, nengo, scipy, datetime, message_filters, nengo_loihi
import numpy as np 
import matplotlib.pyplot as plt
from nengo_loihi.hardware.allocators import Greedy 

class experiment: 
    def __init__(self, name, **kwargs):
        self.name = name
        self.dt = 0.008
        self.net = self.build()
        self.sim, self.hw, self.board = self.setupHardware(self.net)
        self.i = 0 

    def build(self): 
        net = nengo.Network(label=self.name)

        # structrue of the network 
        # inn (node) -> int (ensemble) -> out (probe)
        with net: 
            nengo_loihi.add_params(net)
            self.sineNode = nengo.Node(lambda t: np.sin(t), label='sineNode')
            self.stepNode05 = nengo.Node(lambda t: 0 if t < 0.3 else 0.5, label='stepNode05')
            self.stepNode07 = nengo.Node(lambda t: 0 if t < 0.3 else 0.7, label='stepNode07')
            self.stepNode09 = nengo.Node(lambda t: 0 if t < 0.3 else 0.9, label='stepNode09')
            self.stepNode05_inv = nengo.Node(lambda t: 0.5 if t < 2.0 else 0, label='stepNode05_inv')
            self.stepNode07_inv = nengo.Node(lambda t: 0.7 if t < 2.0 else 0, label='stepNode07_inv')
            self.stepNode09_inv = nengo.Node(lambda t: 0.9 if t < 2.0 else 0, label='stepNode09_inv')
            # Nodes and Ensembles
            self.test_node = nengo.Ensemble(10, radius=1, dimensions=1, label='test_node')
            self.sineEns = nengo.Ensemble(100, radius=1, dimensions=1, label='sineEns')
            self.step05Ens = nengo.Ensemble(100, radius=1, dimensions=1, label='step05Ens')   
            self.step07Ens = nengo.Ensemble(100, radius=1, dimensions=1, label='step07Ens')
            self.step09Ens = nengo.Ensemble(100, radius=1, dimensions=1, label='step09Ens')
            self.step05Ens_inv = nengo.Ensemble(100, radius=1, dimensions=1, label='step05Ens_inv')   
            self.step07Ens_inv = nengo.Ensemble(100, radius=1, dimensions=1, label='step07Ens_inv')
            self.step09Ens_inv = nengo.Ensemble(100, radius=1, dimensions=1, label='step09Ens_inv')
            # Connections
            nengo.Connection(self.sineNode, self.sineEns, transform=1, label='stepNode_to_stepEns')
            nengo.Connection(self.stepNode05, self.step05Ens, transform=1, label='sineNode05_to_sine05Ens')
            nengo.Connection(self.stepNode07, self.step07Ens, transform=1, label='stepNode07_to_step07Ens')
            nengo.Connection(self.stepNode09, self.step09Ens, transform=1, label='sineNode09_to_sine09Ens')
            nengo.Connection(self.stepNode05_inv, self.step05Ens_inv, transform=1, label='sineNode05_inv_to_sine05Ens_inv')
            nengo.Connection(self.stepNode07_inv, self.step07Ens_inv, transform=1, label='stepNode07_inv_to_step07Ens_inv')
            nengo.Connection(self.stepNode09_inv, self.step09Ens_inv, transform=1, label='sineNode09_inv_to_sine09Ens_inv')

            # Probes
            self.sineEns_Probe = nengo.Probe(self.sineEns, synapse=nengo.synapses.Alpha(0.1), label='sineEns_Probe') 
            self.step05Ens_Probe = nengo.Probe(self.step05Ens, synapse=nengo.synapses.Alpha(0.1), label='step05Ens_Probe')
            self.step07Ens_Probe = nengo.Probe(self.step07Ens, synapse=nengo.synapses.Alpha(0.1), label='step07Ens_Probe')
            self.step09Ens_Probe = nengo.Probe(self.step09Ens, synapse=nengo.synapses.Alpha(0.1), label='step09Ens_Probe')
            self.step05Ens_inv_Probe = nengo.Probe(self.step05Ens_inv, synapse=nengo.synapses.Alpha(0.1), label='step05Ens_inv_Probe')
            self.step07Ens_inv_Probe = nengo.Probe(self.step07Ens_inv, synapse=nengo.synapses.Alpha(0.1), label='step07Ens_inv_Probe')
            self.step09Ens_inv_Probe = nengo.Probe(self.step09Ens_inv, synapse=nengo.synapses.Alpha(0.1), label='step09Ens_inv_Probe')
            
            #net.config[self.int].block_shape = nengo_loihi.BlockShape((1, 10), (10, 10)) # 20 splits of 5 neurons each
            # (20, 5)
            # (10, 10) 10 splits of 10 neurons
            #print(net.config[self.int].block_shape.n_splits)
            #net.config[self.int2].block_shape = nengo_loihi.BlockShape((2, 5), (20, 5))
            # self.out_node1 = nengo.Probe(self.inn)
            # self.out_node2 = nengo.Probe(self.inn_2)

        return net
    
    def setupHardware(self, net): 
        os.environ.update({'KAPOHOBAY': '1'})
        nengo_loihi.set_defaults()
        sim = nengo_loihi.Simulator(net, dt=self.dt, progress_bar=False, target='loihi', hardware_options={"snip_max_spikes_per_step": 300, "n_chips": 2, "allocator": Greedy()}, precompute=True)
        board = sim.sims['loihi'].nxsdk_board
        hw = sim.sims['loihi']
        sim.sims['loihi'].connect()
        self.printProbeLog(sim.sims['loihi'].model)
        return sim, hw, board

    def shutdown(self):
        self.sim.close()
        self.sim.sims['loihi'].close()

    def run(self):
        while self.i < 500:
            self.sim.step()
            self.i += 1
        self.shutdown()
    
    def get_probes(self):
        return self.sineEns_Probe, self.step05Ens_Probe, self.step07Ens_Probe, self.step09Ens_Probe, self.step05Ens_inv_Probe, self.step07Ens_inv_Probe, self.step09Ens_inv_Probe

    def plot(self): 
        data = self.get_probes()
        plt.figure(dpi=200, figsize=(30, 10))

        print('<----Plotting---->')
        print(type(self.sim.data))

        plt.subplot(2, 4, 1)
        plt.scatter(self.sim.trange(), self.sim.data[data[0]])
        plt.title('sineEns_Probe*')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')  # Set y-axis label

        plt.subplot(2, 4, 2)  # 1 row, 2 columns, second plot
        plt.scatter(self.sim.trange(), self.sim.data[data[1]])
        plt.title('step05Ens_Probe*')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')

        plt.subplot(2, 4, 3)  # 1 row, 2 columns, third plot
        plt.scatter(self.sim.trange(), self.sim.data[data[2]])
        plt.title('step07Ens_Probe*')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')

        plt.subplot(2, 4, 4)  # 1 row, 2 columns, fourth plot
        plt.scatter(self.sim.trange(), self.sim.data[data[3]])
        plt.title('step09Ens_Probe*')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')

        plt.subplot(2, 4, 5)  # 1 row, 2 columns, fifth plot
        plt.scatter(self.sim.trange(), self.sim.data[data[4]])
        plt.title('step05Ens_inv_Probe*')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')

        plt.subplot(2, 4, 6)  # 1 row, 2 columns, sixth plot
        plt.scatter(self.sim.trange(), self.sim.data[data[5]])
        plt.title('step07Ens_inv_Probe*')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')

        plt.subplot(2, 4, 7)  # 1 row, 2 columns, seventh plot
        plt.scatter(self.sim.trange(), self.sim.data[data[6]])
        plt.title('step09Ens_inv_Probe*')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')

        plt.tight_layout()  

        directory = os.path.join(os.getcwd(), 'plots')
        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(os.path.join(directory, 'figure.png'))  # Save figure to specific folder



        directory = os.path.join(os.getcwd(), 'plots')
        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(os.path.join(directory, 'figure.png'))  # Save figure to specific folder


    def logger(self, message, filename="logfile.txt", path="/home/cortana/nengo_loihi_debug"):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"logfile_{timestamp}.txt"
        try:
            with open(f"{path}/{filename}", "a") as f:
                f.write(f"{datetime.datetime.now()} - {message}\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")
    def printProbeLog(self, model):
        loihiProbes = model.probes
        # the model is the object that contains the probes 
        # the loihiProbes has atrributes like key, target, synapse. 
        # the target maps to the LoihiBlock. The LoihiBlock might be the one not working?
        #loihiProbes = sim.sims['loihi'].model.probes
        self.logger("<-------------Loihi Probes Information------------>")
        for i, j in enumerate(loihiProbes):
            self.logger(f"Probe Number {i} of {len(loihiProbes) - 1}")
            self.logger(f"Probe: {i}")
            self.logger(f"  is_transformed: {j.is_transformed}")
            self.logger(f"  Key: {j.key}")
            self.logger(f"  Output_size: {j.output_size}")
            self.logger(f"  Reindexing: {j.reindexing}")
            self.logger(f"  Slice: {j.slice}")
            self.logger(f"  Synapse: {j.synapse}")
            self.logger(f"  Target: {j.target}")
            self.logger(f"  Weight_outputs: {j.weight_outputs}")
            self.logger(f"  Weights : {j.weights}")
            
        self.logger("<-------------Model Information------------>")
        attributes = ['__class__', '__delattr__', '__dir__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'add_block', 'add_input', 'add_probe', 'block_comp_map', 'block_shapes', 'blocks', 'build', 'build_callback', 'builder', 'chip2host_params', 'chip2host_receivers', 'config', 'connection_decode_neurons', 'decode_neurons', 'decode_tau', 'decoder_cache', 'default_validation_level', 'dt', 'has_built', 'host', 'host2chip_pes_senders', 'host2chip_senders', 'host_model', 'host_pre', 'inputs', 'intercept_limit', 'label', 'needs_sender', 'nengo_probe_conns', 'nengo_probes', 'node_neurons', 'objs', 'pes_error_scale', 'pes_wgt_exp', 'probes', 'seeded', 'seeds', 'spike_targets', 'split', 'toplevel', 'utilization_summary', 'validation_level', 'vth_nonspiking']
        self.logger("<-------------Object Attributes Information------------>")
        for i, attr in enumerate(attributes):
            self.logger(f"Attribute Number {i} of {len(attributes) - 1}")
            self.logger(f"Attribute: {attr}")
            try:
                value = getattr(model, attr)
                if attr == 'objs': 
                    for i in value:
                        self.logger(i)
                else:
                    self.logger(f"  Value: {value}")
            except AttributeError:
                self.logger("  This attribute does not exist for the object")

        

if __name__ == '__main__':
    e = experiment('test')
    e.run()
    e.plot()
    print('done')
            