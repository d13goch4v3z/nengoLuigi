# libs
import os, time, signal, rospy, sys, nengo, scipy, datetime, message_filters, nengo_loihi
import numpy as np 
import matplotlib.pyplot as plt

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
            self.inn_2 = nengo.Node(lambda t: 0 if t < 0.5 else 0.5)
            self.inn = nengo.Node(lambda t: np.sin(t))
            
            self.test_node = nengo.Ensemble(100, radius=1, dimensions=1, label='test_ensemble')

            self.int = nengo.Ensemble(100, radius=1, dimensions=1, label='ens')
            self.int2 = nengo.Ensemble(100, radius=1, dimensions=1, label='ens2')    #Order in which ensembles appear affects order of probing
        
            nengo.Connection(self.inn, self.int, transform=1)
            nengo.Connection(self.inn_2, self.int2, transform=1)



            self.out = nengo.Probe(self.int, synapse=nengo.synapses.Alpha(0.1)) 
            self.out2 = nengo.Probe(self.int2, synapse=nengo.synapses.Alpha(0.1))
            self.test_out = nengo.Probe(self.test_node, synapse=nengo.synapses.Alpha(0.1))
            
            # self.out_node1 = nengo.Probe(self.inn)
            # self.out_node2 = nengo.Probe(self.inn_2)

        return net
    
    def setupHardware(self, net): 
        os.environ.update({'KAPOHOBAY': '1'})
        nengo_loihi.set_defaults()
        sim = nengo_loihi.Simulator(net, dt=self.dt, progress_bar=False, target='loihi', hardware_options={"snip_max_spikes_per_step": 300, "n_chips": 2}, precompute=True)
        board = sim.sims['loihi'].nxsdk_board
        hw = sim.sims['loihi']
        sim.sims['loihi'].connect()
        return sim, hw, board
    
    
    def printInformation(self, sim): 
        print("<---------------Utilization Summary--------------->")
        print(nengo_loihi.builder.Model.utilization_summary(sim.model))
        print("<---------------Blocks--------------->")
        loihiBlocks = self.sim.model.blocks
        for block, index in loihiBlocks.items():
            print(f"Block {index}:")
            print(f"  n_neurons: {block.n_neurons}")
            print(f"  label: {block.label}")
            print(f"  axons: {block.axons}")
            print(f"  compartment: {block.compartment}")
            print(f"  named_synapses: {block.named_synapses}")
            print(f"  synapses: {block.synapses}")
            print("\n")
        # # The hardware interface of loihi is located in the sim object. 
        # # The sim object is a dictionary with the keys being the target of the simulator.
        # print(self.sim.sims['loihi'])
        # # Assuming hardware_interface is an instance of HardwareInterface
        print("<---------------Hardware--------------->")
        hardware_interface = self.sim.sims['loihi']

        print(f"board: {hardware_interface.board}")
        print(f"chip2host: {hardware_interface.chip2host}")
        print(f"closed: {hardware_interface.closed}")
        print(f"connected: {hardware_interface.connected}")
        print(f"connection_retries: {hardware_interface.connection_retries}")
        print(f"host2chip: {hardware_interface.host2chip}")
        print(f"model: {hardware_interface.model}")
        print(f"no_snips: {hardware_interface.no_snips}")
        print(f"nxsdk_board: {hardware_interface.nxsdk_board}")
        print(f"seed: {hardware_interface.seed}")
        print(f"snips: {hardware_interface.snips}")
        print(f"use_snips: {hardware_interface.use_snips}")
        nxsdkProbes = []
        for i in hardware_interface.no_snips.probe_map:
            nxsdkProbes.append(hardware_interface.no_snips.probe_map[i][0])
        print(nxsdkProbes)
        # fig = plt.figure(2, figsize=(10, 10))
        # uProbe = nxsdkProbes[0]
        # uProbe.plot()
        # plt.title('uProbe')
        # directory = os.path.join(os.getcwd(), 'plots')
        # if not os.path.exists(directory):
        #     os.makedirs(directory)

        # plt.savefig(os.path.join(directory, 'probe_map.png')) 



    def shutdown(self):
        self.sim.close()
        self.sim.sims['loihi'].close()

    def run(self):
        while self.i < 500:
            self.sim.step()
            self.i += 1
        self.printInformation(self.sim)
        self.shutdown()
    
    def get_probes(self):
        return self.out, self.out2, self.test_out

    def plot(self): 
        data = self.get_probes()
        plt.figure(dpi=200)

        # print(type(self.sim.data[data[0]]))
        # print(np.shape(data)) 
        # print(type(self.sim.data)) # Simulator.Simulationdata
        # print(self.sim.data.keys()) # 22

        plt.subplot(1, 3, 1)
        plt.scatter(self.sim.trange(), self.sim.data[data[0]])
        plt.title('Title 1')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')  # Set y-axis label

        plt.subplot(1, 3, 2)  # 1 row, 2 columns, second plot
        plt.scatter(self.sim.trange(), self.sim.data[data[1]])
        plt.title('Title 2')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')

        plt.subplot(1, 3, 3)  # 1 row, 2 columns, second plot
        plt.scatter(self.sim.trange(), self.sim.data[data[2]])
        plt.title('Title 3')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')

        directory = os.path.join(os.getcwd(), 'plots')
        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(os.path.join(directory, 'figure.png'))  # Save figure to specific folder


if __name__ == '__main__':
    e = experiment('test')
    e.run()
    e.plot()
    print('done')
            