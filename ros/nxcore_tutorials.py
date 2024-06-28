# This is a compressed script to explain nxcore in a concise
# and structured matter 
# prepared by: diego chavez
from nxsdk.arch.n2a.n2board import N2Board
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
haveDisplay = "DISPLAY" in os.environ
if not haveDisplay:
    mpl.use('Agg')
os.environ['KAPOHOBAY'] = '1'
os.chdir("/home/cortana/nengo_loihi_debug/ros/nxcore")
print(os.getcwd())

class experiment_1: 
    def __init__(self):
        pass
    def experiment1(self):
        #### Experiment 1 aims to explain the distribution of the loihi board compartments
        #### and how to probe these compartments
        ### INITIALIZE THE BOARD
        ## boardId is just an identifier number for the board
        ## numChips is the number of chips utilized in the board
        ## numCoresPerChip is a list of the number of cores per chip: 
        # [#cores_for_chip_1, #cores_for_chip_2]
        ## numSynapsesPerCore is a list of lists of the number of synapses per core
        # [[synapses_4_core_1_in_chip_1, synapses_4_core_2_in_chip_1], [synapses_4_core_1_in_chip_2]]
        boardId = 1 
        numChips = 2
        numCoresPerChip = [2, 1]
        numSynapsesPerCore = [[5, 1], [1]]
        board = N2Board(boardId, numChips, numCoresPerChip, numSynapsesPerCore)

        ## configure a compartment in the board 
        # this can be done by addressing the specific compartment in the board object
        # board.n2Chips[chip_id].n2Cores[core_id].
        # These are the paramters you can modify 
        # - 'axonCfg', 'axonMap', 'axons', 'channels', 'clear'
        # - 'createChannel', 'createDirectAxon', 'createDiscreteAxon', 'createInputGenerator', 'createOutputConsumer'
        # - 'createPop16Axon', 'createPop32Axon', 'createProcess', 'createRuntimeManager', 'createSnip'
        # - 'cxCfg', 'cxMetaState', 'cxProfileCfg', 'cxState', 'dendriteAccum'
        # - 'dendriteAccumCfg', 'dendriteRandom', 'dendriteSharedCfg', 'dendriteTimeState', 'embeddedProcesses'
        # - 'executor', 'fetch', 'fetchDynamic', 'fetchStatic', 'getAddress'
        # - 'hostProcesses', 'id', 'initCore', 'inputGenerators', 'logger'
        # - 'monitor', 'nodeSets', 'numUpdates', 'nxGraphs', 'nxmonitor'
        # - 'optimumCoreAssignment', 'outputAxon', 'outputConsumers', 'parent', 'push'
        # - 'rewardTrace', 'runtimeManagers', 'somaRandom', 'somaState', 'somaTraceCfg'
        # - 'stdpCfg', 'stdpEpochCount', 'stdpPostCfg', 'stdpPostRandom', 'stdpPostState'
        # - 'stdpPreCfg', 'stdpPreProfileCfg', 'stdpPreRandom', 'stdpProfileCfg', 'stdpUcodeMem'
        # - 'synapseFmt', 'synapseMap', 'synapseMem', 'synapseRepackRandom', 'synapses'
        # - 'sync', 'timeState', 'vthProfileCfg'
        
        ### CONFIGURE THE COMPARTMENT 
        # There are couple of parameters that need to be configured as a minimum for the 
        # compartment to work. 
        # 1. Voltage decay and current decay 
        # 2. The cxMetaState for a specific compartment is selected as phaseK where
        # K is the phase number, and K = mod(i, 4). phaseK = 2 allows the compartment to 
        # be driven by a bias current. 
        # 3. The voltage threshold vthProfileCfg is defined as the vth*(2^6)
        # 4. NumUpdates controls how many compartment groups will be services (4 per group). 
        #   numUpdates = 4i - 1, i is the number of compartments (i in range from 1 to 256). 
        #   It is how many compartments and axons update core. 
        # 5. Compartment Pointers
        #   bias -> bias*(2^biasExp)
        #   vthProfile = 0 (vthProfileCfg)
        #   cxProfile = 0 (cxProfileCfg)
        board.n2Chips[0].n2Cores[0].cxProfileCfg[0].configure(decayV=int(1/16*2**12), decayU = int(1/16*2**12))
        board.n2Chips[0].n2Cores[0].cxMetaState[0].configure(phase0=2)
        board.n2Chips[0].n2Cores[0].vthProfileCfg[0].staticCfg.configure(vth=10)
        board.n2Chips[0].n2Cores[0].numUpdates.configure(numUpdates=1)
        board.n2Chips[0].n2Cores[0].cxCfg[0].configure(bias=100, biasExp=6, vthProfile=0, cxProfile=0)

        return board

    def runExperiment1(self, board):
        mon = board.monitor
        uProbe = mon.probe(board.n2Chips[0].n2Cores[0].cxState, [0, 1, 2, 3, 4, 5], 'u')
        vProbe = mon.probe(board.n2Chips[0].n2Cores[0].cxState, [0, 1, 2, 3, 4, 5], 'v')

        board.run(30)
        board.disconnect()
        
        fig = plt.figure(1002)
        k = 1 
        for j in range(0, 5): 
            plt.subplot(5, 1, k)
            uProbe[j].plot()
            plt.title('u'+str(j))
            k += 1
        filename = "experiment1"
        fig.savefig(filename + ".png", dpi=200)
        

class experiment_2: 
    def __init__(self):
        pass
    def experiment2(self): 
        #### Experiment 2 configures compartments with a bias current 
        #### and connects to another one to show the functionality of excitatory and 
        #### inhibitory synapses
        boardId = 1
        numChips = 1
        numCoresPerChip = [1]
        numSynapsesPerCore = [[5]]
        board = N2Board(boardId, numChips, numCoresPerChip, numSynapsesPerCore) # in this case we only have one core with 10 compartments configured 

        n2Core = board.n2Chips[0].n2Cores[0] # obtain the only core with 5 compartments. 

        n2Core.cxProfileCfg[0].configure(decayV=int(1/16*2**12), decayU = int(1/10*2**12))
        n2Core.cxMetaState[0].configure(phase0=2)
        n2Core.vthProfileCfg[0].staticCfg.configure(vth=10)
        n2Core.numUpdates.configure(numUpdates=1)
        n2Core.cxCfg[0].configure(bias=1, biasExp=6, vthProfile=0, cxProfile=0)

        # output synapses
        # create discrete axon
        srcCxId = 0
        dstChipId = board.n2Chips[0].n2Cores[0].parent.id
        dstCoreId = board.n2Chips[0].n2Cores[0].id
        dstSynMapId = 0
        n2Core.createDiscreteAxon(srcCxId, dstChipId, dstCoreId, dstSynMapId)
        
        # input axon 
        # to create the input axon we create a index with target
        targetSynapsePtr = 0
        targetSynapseLen = 2
        board.n2Chips[0].n2Cores[0].synapseMap[dstSynMapId].synapsePtr = targetSynapsePtr
        board.n2Chips[0].n2Cores[0].synapseMap[dstSynMapId].synapseLen = targetSynapseLen
        board.n2Chips[0].n2Cores[0].synapseMap[dstSynMapId].discreteMapEntry.configure()



        board.n2Chips[0].n2Cores[0].synapseFmt[1].wgtExp = 0 # this one configures the excitaotry and inhibitory synapses to have a weight exponent of 0
        board.n2Chips[0].n2Cores[0].synapseFmt[1].wgtBits = 7 # this one configures the weight bits to be 7 that maps to 8 bits 
        board.n2Chips[0].n2Cores[0].synapseFmt[1].numSynapses = 63 # 63 asks the compiler to figure out map synapses 
        board.n2Chips[0].n2Cores[0].synapseFmt[1].idxBits = 1 
        board.n2Chips[0].n2Cores[0].synapseFmt[1].compression = 3 
        board.n2Chips[0].n2Cores[0].synapseFmt[1].fanoutType = 1

        n2Core.synapses[0].CIdx = 1
        n2Core.synapses[0].Wgt = 4
        n2Core.synapses[0].synFmtId = 1

        n2Core.synapses[1].CIdx = 2
        n2Core.synapses[1].Wgt = -4
        n2Core.synapses[1].synFmtId = 1

        # 
        # 0 - > 2 

        return board 
    def runExperiment2(self, board):
        mon = board.monitor
        uProbe = mon.probe(board.n2Chips[0].n2Cores[0].cxState, [0, 1, 2], 'u') # 1024 nodes, baseId 4096
        vProbe = mon.probe(board.n2Chips[0].n2Cores[0].cxState, [0, 1, 2], 'v')

        board.run(30)
        board.disconnect()
        
        fig = plt.figure(1002, figsize=(10, 20))
        k = 1 
        for j in range(0, 3): 
            plt.subplot(3, 1, k)
            uProbe[j].plot()
            plt.title('u'+str(j))
            k += 1
        filename = "experiment2uProbe"
        fig.savefig(filename + ".png", dpi=200)    

        fig = plt.figure(1003, figsize=(10, 20))
        k = 1 
        for j in range(0, 3): 
            plt.subplot(3, 1, k)
            vProbe[j].plot()
            plt.title('v'+str(j))
            k += 1
        filename = "experiment2vProbe"
        fig.savefig(filename + ".png", dpi=200) 


class experiment_3: 
    def __init__(self):
        pass
    def experiment3(self): 
        #### experiment 3
        ### in this experiment will connect multiles cores with one synapse between each other
        boardId = 1 
        numChips = 1
        numCoresPerChip = [4]
        numSynapsesPerCore = [[1, 1, 1, 1]] # each core will have one synapse
        board = N2Board(boardId, numChips, numCoresPerChip, numSynapsesPerCore)
        board.n2Chips[0].n2Cores[0].cxProfileCfg[0].configure(decayV=int(1/16*2**12)) # voltage decay will happen when the compartment reaches a voltage threshold
        board.n2Chips[0].n2Cores[0].cxMetaState[0].configure(phase0=2)
        board.n2Chips[0].n2Cores[0].vthProfileCfg[0].staticCfg.configure(vth=1000)
        board.n2Chips[0].n2Cores[0].numUpdates.configure(numUpdates=1)
        board.n2Chips[0].n2Cores[0].cxCfg[0].configure(bias=100, biasExp=6, vthProfile=0, cxProfile=0)

        n2Cores = board.n2Chips[0].n2CoresAsList
        for i, j in enumerate(n2Cores[1:]):
            j.numUpdates.configure(numUpdates=1)
            j.vthProfileCfg[0].staticCfg.configure(vth=1000*(i+1)) # each core has a compartment
            j.synapses[0].CIdx = 0
            j.synapses[0].Wgt = 64 
            j.synapses[0].synFmtId = 1

            # configure synapse format ID
            j.synapseFmt[1].wgtExp = 0
            j.synapseFmt[1].wgtBits = 7
            j.synapseFmt[1].numSynapses = 63
            j.synapseFmt[1].cIdxOffset = 0
            j.synapseFmt[1].cIdxMult = 0
            j.synapseFmt[1].idxBits = 1
            j.synapseFmt[1].fanoutType = 2
            j.synapseFmt[1].compression = 0

            # synapse map 
            j.synapseMap[0].synapsePtr = 0
            j.synapseMap[0].synapseLen = 1 # len(synapses)
            j.synapseMap[0].discreteMapEntry.configure()

            j.createDiscreteAxon(srcCxId=0, 
                                    dstChipId=0, 
                                    dstCoreId=j.id, 
                                    dstSynMapId=0)  
            
        return board, board.n2Chips[0].n2CoresAsList
    
    def genProbes(self, cores, mon):
        for n2Core in cores: 
            yield(mon.probe(n2Core.cxState, [0], 'u')[0], 
                  mon.probe(n2Core.cxState, [0], 'v')[0], 
                  mon.probe(n2Core.cxState, [0], 'spike')[0])
            
    def runExperiment3(self, board):
        board.run(100)
        board.disconnect()
    
    def plot(self, probes): 
        fig = plt.figure(1001)
        figIndex = iter(range(1, 13))
        for coreId, (uProbe, vProbe, spikeProbe) in enumerate(
            zip(probes[0], probes[1], probes[2])):
            # Since there are no incoming spikes and noise is disabled by default, u
            # remains constant at 0 for source core
            plt.subplot(4, 3, next(figIndex))
            uProbe.plot()
            plt.title('%d: u' % coreId)

            # v increases due to the bias current.  The concave nature of the curve
            # when the voltage is increasing is due to the decay constant.  Upon
            # reaching the threshold of 64000, the compartment spikes and resets
            # to 0. Since there is no refractory period, the voltage immediate
            # begins to increase again.
            plt.subplot(4, 3, next(figIndex))
            vProbe.plot()
            plt.title('%d: v' % coreId)

            plt.subplot(4, 3, next(figIndex))
            spikeProbe.plot()
            plt.title('%d: spike' % coreId)
        filename = "experiment3Probe"
        fig.savefig(filename + ".png", dpi=200) 
    

if __name__ == "__main__":
    exp2 = experiment_2()
    board = exp2.experiment2()
    exp2.runExperiment2(board)
    
    # (uProbes, vProbes, spikeProbes) = zip(*list(exp3.genProbes(cores, board.monitor)))
    # exp3.runExperiment3(board)
    # exp3.plot((uProbes, vProbes, spikeProbes))
