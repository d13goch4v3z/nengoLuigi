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
        

if __name__ == "__main__":
    c = compartment()
    c.experiment1()
    print("done")