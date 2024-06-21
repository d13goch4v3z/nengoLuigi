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



class compartment: 
    def __init__(self):
        pass
    def experiment1(self):
        """
        """
        ### INITIALIZE THE BOARD
        ## boardId is just an identifier number for the board
        ## numChips is the number of chips utilized in the board
        ## numCoresPerChip is a list of the number of cores per chip: 
        # [#cores_for_chip_1, #cores_for_chip_2]
        ## numSynapsesPerCore is a list of lists of the number of synapses per core
        # [[synapses_4_core_1_in_chip_1, synapses_4_core_2_in_chip_1], [synapses_4_core_1_in_chip_2]]
        boardId = 1 
        numChips = 1
        numCoresPerChip = [1]
        numSynapsesPerCore = [[1]]
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
        board.n2Chips[0].n2Cores[0].cxProfileCfg[0].configure(decayV=int(1/16*2**12))
        board.n2Chips[0].n2Cores[0].cxMetaState[0].configure(phase0=2)
        board.n2Chips[0].n2Cores[0].vthProfileCfg[0].staticCfg.configure(vth=1000)
        board.n2Chips[0].n2Cores[0].numUpdates.configure(numUpdates=1)
        board.n2Chips[0].n2Cores[0].cxCfg[0].configure(bias=100, biasExp=6, vthProfile=0, cxProfile=0)

        """
        in this case we configured a board with 2 chips and 3 cores. 
        in the first chip we configured two cores with 5 and 1 synapses respectively.
        in the second chip we configured one core with 1 synapse.
        """
        probes = []
        toProbe = ['u', 'v']
        probes.append(board.monitor.probe(board.n2Chips[0].n2Cores[0].cxState, [0], toProbe[0])[0])
        probes.append(board.monitor.probe(board.n2Chips[0].n2Cores[0].cxState, [0], toProbe[1])[0])
        return board, probes
    
    def runExperiment(self, board, probes):
        ## run the experiment
        board.run(100)
        board.disconnect()
        ## plot the results
        fig = plt.figure(1001)
        plt.subplot(1, 2, 1)
        probes[0].plot()
        plt.title('u')

        plt.subplot(1, 2, 2)
        probes[1].plot()  
        plt.title('v')

        plt.tight_layout()
        
        file_path = os.path.join(os.getcwd(), 'experiment1.png')
        print("saving figure to: ", file_path)
        fig.savefig(file_path, dpi=200)
        


class experiment_2: 
    def __init__(self): 
        pass
    def setupNetwork(self): 
        boardId = 1 
        numChips = 1
        numCoresPerChip = [1]
        numSynapsesPerCore = [[5]]
        board = N2Board(boardId, numChips, numCoresPerChip, numSynapsesPerCore)

        """
        set up a compartment with a bias
        """
        board.n2Chips[0].n2Cores[0].cxProfileCfg[0].configure(decayV=int(1/16*2**12), decayU=int(1/10*2**12))
        board.n2Chips[0].n2Cores[0].cxMetaState[0].configure(phase0=2)
        board.n2Chips[0].n2Cores[0].vthProfileCfg[0].staticCfg.configure(vth=10) # 10*(2^6)=640
        board.n2Chips[0].n2Cores[0].numUpdates.configure(numUpdates=1)
        board.n2Chips[0].n2Cores[0].cxCfg[0].configure(bias=1, biasExp=6, vthProfile=0, cxProfile=0) # 1*(2^6)=64
        
        """
        connections
        """
        # to connect a compartment to another compartment
        
        targetCoreId = 4
        targetAxonId = 0
        targetChipId = board.n2Chips[0].n2Cores[0].parent.id
        board.n2Chips[0].n2Cores[0].createDiscreteAxon(0, targetChipId, targetCoreId, targetAxonId)
        
        targetSynapsePtr = 0
        tagretSynapseLen = 2
        board.n2Chips[0].n2Cores[0].synapseMap[targetAxonId].synapsePtr = targetSynapsePtr
        board.n2Chips[0].n2Cores[0].synapseMap[targetAxonId].synapseLen = tagretSynapseLen
        board.n2Chips[0].n2Cores[0].synapseMap[targetAxonId].discreteMapEntry.configure()
        
        # setup the types of synapses 
        board.n2Chips[0].n2Cores[0].synapses[0].CIdx = 1
        board.n2Chips[0].n2Cores[0].synapses[0].Wgt = 4
        board.n2Chips[0].n2Cores[0].synapses[0].synFmtId = 1

        board.n2Chips[0].n2Cores[0].synapses[1].CIdx = 2
        board.n2Chips[0].n2Cores[0].synapses[1].Wgt = -4
        board.n2Chips[0].n2Cores[0].synapses[1].synFmtId = 1

        board.n2Chips[0].n2Cores[0].synapseFmt[1].wgtExp = 0 
        board.n2Chips[0].n2Cores[0].synapseFmt[1].wgtBits = 7
        board.n2Chips[0].n2Cores[0].synapseFmt[1].numSynapses = 63
        board.n2Chips[0].n2Cores[0].synapseFmt[1].idxBits = 1
        board.n2Chips[0].n2Cores[0].synapseFmt[1].compression = 1
        board.n2Chips[0].n2Cores[0].synapseFmt[1].fanoutType = 1

        probes = []
        uProbe = board.monitor.probe(board.n2Chips[0].n2Cores[0].cxState, [0, 1, 2], 'u')
        vProbe = board.monitor.probe(board.n2Chips[0].n2Cores[0].cxState, [0, 1, 2], 'v')        
        probes.append(uProbe)
        probes.append(vProbe)



        return board, probes
    
    def runExperiment(self, board, probes):
        ## run the experiment
        board.run(40)
        board.disconnect()
        print(probes)
        fig = plt.figure(figsize=(10, 5))
        k = 1 
        for j in range(0, 3): 
            plt.subplot(3, 2, k)
            probes[0][j].plot()
            plt.title('u'+str(j))
            k += 1 

            plt.subplot(3, 2, k)
            probes[1][j].plot()
            plt.title('v'+str(j))
            k += 1
        
        plt.tight_layout()
        
        file_path = os.path.join(os.getcwd(), 'experiment2.png')
        print("saving figure to: ", file_path)
        fig.savefig(file_path, dpi = 200)
        

        

if __name__ == "__main__":
    e2 = experiment_2()
    board, probes = e2.setupNetwork()
    e2.runExperiment(board, probes)
    print("done")