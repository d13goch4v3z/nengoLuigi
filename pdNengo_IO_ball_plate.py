import os, time, signal, sys, nengo, scipy, datetime, nengo_loihi
import numpy as np 
import matplotlib.pyplot as plt
from nengo_loihi.hardware.allocators import Greedy 
import usb.core, usb.util

class touchscreen(): 
    def __init__(self, idVendor = 0x04d8, idProduct = 0x0c02):
        print("<--- Touchscreen Initialization --->")
        dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        ep_in = dev[0].interfaces()[0].endpoints()[0]
        ep_out = dev[0].interfaces()[0].endpoints()[1]
        intf = dev[0].interfaces()[0].bInterfaceNumber
        dev.reset()

        if dev is None: 
            raise ValueError('Device not found')
        else: 
            print("<--- Touchscreen Found --->")
        
        if dev.is_kernel_driver_active(intf):
            dev.detach_kernel_driver(intf)
            usb.util.claim_interface(dev, intf)
        
        self.dev = dev
        self.ep_in = ep_in
        self.ep_out = ep_out

        self.recordingX = np.array([])
        self.recordingY = np.array([])

    def __call__(self, t):
        touchScreenInput = self.obtainData()
        self.recordingX = np.append(self.recordingX, touchScreenInput[0])
        self.recordingY = np.append(self.recordingY, touchScreenInput[1])
        return [touchScreenInput[0], touchScreenInput[1]]

    def obtainData(self):
        try: 
            data = self.dev.read(self.ep_in.bEndpointAddress, self.ep_in.wMaxPacketSize)
            return [np.round((data[2]*255 + data[1]-293)/3925, 8) , np.round((data[4]*255 + data[3] - 194)/3935, 8)]
        except usb.core.USBError as e: 
            if e.args == ('Operation timed out',): 
                return None
    
class loihi():
    def __init__(self, name, **kwargs):
        self.touch = touchscreen()
        self.name = name
        self.dt = 0.005 #0.008 #TODO changing the dt parameter will strongly affect the derivative of the signal.
        self.net = self.build()
        self.sim, self.hw, self.board = self.setupHardware(self.net)
        self.i = 0


    
    def build(self): 
        net = nengo.Network(label=self.name)
        with net: 
            dTransform = 10
            synapseV = 0.01
            xDesired = 0
            yDesired = 0

            nengo_loihi.add_params(net)
            self.inputNode = nengo.Node(self.touch.__call__, label='input', size_out=2)

            self.dummyEns = nengo.Ensemble(1, radius=1, dimensions=1, label='dummy')
            self.inputEnsX = nengo.Ensemble(300, radius=2, dimensions=1, label='inputEnsX')
            self.inputEnsY = nengo.Ensemble(300, radius=2, dimensions=1, label='inputEnsY')
            self.errorEnsX = nengo.Ensemble(300, radius=1, dimensions=1, label='errorEnsX')
            self.errorEnsY = nengo.Ensemble(300, radius=1, dimensions=1, label='errorEnsY')
            self.derivativeEnsX = nengo.Ensemble(400, radius=2, dimensions=1, label='derivativeEnsX')
            self.derivativeEnsY = nengo.Ensemble(400, radius=2, dimensions=1, label='derivativeEnsY')
            self.delayEnsX = nengo.Ensemble(300, radius=2, dimensions=1, label='delayEnsX')
            self.delayEnsY = nengo.Ensemble(300, radius=2, dimensions=1, label='delayEnsY')

            self.xDesNode = nengo.Node(xDesired, label='xDesired')
            self.yDesNode = nengo.Node(yDesired, label='yDesired')

            nengo.Connection(self.inputNode[0], self.inputEnsX, transform=1, label='inputNodeX_to_inputEnsX', synapse=0.01)
            nengo.Connection(self.inputNode[1], self.inputEnsY, transform=1, label='inputNodeY_to_inputEnsY', synapse=0.01)

            nengo.Connection(self.xDesired, self.errorEnsX, transform=1, label='xDesired_to_errorEnsX')
            nengo.Connection(self.xDesNode, self.errorEnsX, transform=-1, label='xDesiredNode_to_errorEnsX')
            nengo.Connection(self.yDesired, self.errorEnsY, transform=1, label='yDesired_to_errorEnsY')
            nengo.Connection(self.yDesNode, self.errorEnsY, transform=-1, label='yDesiredNode_to_errorEnsY')

            nengo.Connection(self.errorEnsX, self.derivativeEnsX, transform=10, synapse=0.1, label='inputEnsX_to_derivativeEnsX')
            nengo.Connection(self.errorEnsX, self.delayEnsX, transform=1, synapse=0.1, label='inputEnsX_to_delayEnsX')
            nengo.Connection(self.delayEnsX, self.derivativeEnsX, transform=-10, synapse=0.1, label='delayEnsX_to_derivativeEnsX')

            nengo.Connection(self.errorEnsY, self.derivativeEnsY, transform=10, synapse=0.1, label='inputEnsY_to_derivativeEnsY')
            nengo.Connection(self.errorEnsY, self.delayEnsY, transform=1, synapse=0.1, label='inputEnsX_to_delayEnsY')
            nengo.Connection(self.delayEnsY, self.derivativeEnsY, transform=-10, synapse=0.1, label='delayEnsX_to_derivativeEnsY')

            self.inputProbeX = nengo.Probe(self.inputEnsX, synapse=nengo.synapses.Alpha(0.05), label='inputProbeX') # 0.05 - 0.1 Alpha is the best
            self.inputProbeY = nengo.Probe(self.inputEnsY, synapse=nengo.synapses.Alpha(0.05), label='inputProbeY') # 
            self.derivativeProbeX = nengo.Probe(self.derivativeEnsX, synapse=nengo.synapses.Alpha(0.1), label='derivativeProbeX') # 0.05 - 0.1 Alpha is the best
            self.derivativeProbeY = nengo.Probe(self.derivativeEnsY, synapse=nengo.synapses.Alpha(0.1), label='derivativeProbeY')
            # nengo.synapses.Alpha(0.1)
            return net
    def get_probes(self):
        return [self.inputProbeX, self.inputProbeY, self.derivativeProbeX, self.derivativeProbeY]
    def setupHardware(self, net):
        os.environ.update({'KAPOHOBAY': '1'})
        nengo_loihi.set_defaults()
        sim = nengo_loihi.Simulator(net, dt=self.dt, progress_bar=False, target='loihi', hardware_options={"snip_max_spikes_per_step": 500, "n_chips": 2, "allocator": Greedy()}, precompute=True)
        board = sim.sims['loihi'].nxsdk_board
        hw = sim.sims['loihi']
        sim.sims['loihi'].connect()
        self.printProbeLog(sim.sims['loihi'].model)
        return sim, hw, board
    
    def run(self):
        while self.i < 500:
            self.sim.step()
            # Create a touchscreen object
            
            self.i += 1
        self.shutdown()
    
    def shutdown(self):
        self.sim.close()
        self.sim.sims['loihi'].close()

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
    def plot(self): 
        data = self.get_probes()
        plt.figure(dpi=200, figsize=(30, 10))

        print('<----Plotting---->')
        print(type(self.sim.data))

        plt.subplot(2, 3, 1)
        plt.scatter(self.sim.trange(), self.sim.data[data[0]])
        plt.title('readingXLui')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')  # Set y-axis label

        plt.subplot(2, 3, 2)
        plt.scatter(self.sim.trange(), self.sim.data[data[1]])
        plt.title('readingYLui')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')  # Set y-axis label

        plt.subplot(2, 3, 3)
        plt.scatter(np.arange(0, len(self.touch.recordingX)), self.touch.recordingX)
        plt.title('readingXTouch')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')  # Set y-axis label

        plt.subplot(2, 3, 6)
        plt.scatter(np.arange(0, len(self.touch.recordingY)), self.touch.recordingY)
        plt.title('readingYTouch')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')  # Set y-axis label

        plt.subplot(2, 3, 4)
        plt.scatter(self.sim.trange(), self.sim.data[data[2]])
        plt.title('derivativeX')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')  # Set y-axis label

        plt.subplot(2, 3, 5)
        plt.scatter(self.sim.trange(), self.sim.data[data[3]])
        plt.title('derivativeY')  # Set title
        plt.xlabel('X-Axis Label')  # Set x-axis label
        plt.ylabel('Y-Axis Label')  # Set y-axis label

        plt.tight_layout()  

        directory = os.path.join(os.getcwd(), 'plots')
        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(os.path.join(directory, 'figure.png'))  # Save figure to specific folder



        directory = os.path.join(os.getcwd(), 'plots')
        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(os.path.join(directory, 'figure.png'))  # Save figure to specific folder

            
if __name__ == '__main__':
    lui = loihi('ball_plate')
    lui.run()
    lui.plot()
    print('Done!')