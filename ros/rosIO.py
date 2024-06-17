# Diego Chavez Arana
# self note if I have problems finding libraries try to mess with the LD_LIBRARY_PATH
# or the KAPOHOBAY variable
# or try executing the python script using sudo su
# or try to source the terminal with /opt/ros/noetic/setup.bash
# or try to make the build.sh executable with chmod +x build.sh
# or try to put the shebang line in the build.sh file

from nxsdk.arch.n2a.n2board import N2Board
from nxsdk.graph.processes.phase_enums import Phase
import matplotlib.pyplot as plt
import os, subprocess
import matplotlib as mpl
haveDisplay = "DISPLAY" in os.environ
if not haveDisplay:
    mpl.use('Agg')
os.environ['KAPOHOBAY'] = '1'



class lui: 
    def __init__(self):
        print("Initializing...")
    

    def setupNetwork(self): 
        # instantiate the board, (boardId, numChips, numCoresPerChip, numNeuronsPerCore)
        boardId = 1
        numChips = 1
        numCoresPerChip = [10]
        numSynapsesPerCore = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        board = N2Board(boardId, numChips, numCoresPerChip, numSynapsesPerCore)
        # obatin the cores object 
        n2Cores = board.n2Chips[0].n2CoresAsList
        # configure a core to be driven by a bias
        n2Cores[0].cxProfileCfg[0].configure(decayV=int(1/16*2**12))
        n2Cores[0].cxMetaState[0].configure(phase0=2) # 2 allows the compartment to be driven by a bias state
        n2Cores[0].vthProfileCfg[0].staticCfg.configure(vth=1000) #numerical threshold mantissa is vth*(2^6) = 1000*2^6 = 64000
        n2Cores[0].numUpdates.configure(numUpdates=1)
        n2Cores[0].cxCfg[0].configure(bias=100, biasExp=6, vthProfile=0, cxProfile=0) # configure bias and mantissa exponent bias*(2^6) = 6400

        for coreId, n2Core in enumerate(n2Cores[1:]):
            n2Core.numUpdates.configure(numUpdates=1)
            n2Core.vthProfileCfg[0].staticCfg.configure(vth=1000*(coreId+1))
            n2Core.synapses[0].CIdx = 0 #each core has diffrent synapses
            n2Core.synapses[0].Wgt = 64 
            n2Core.synapses[0].synFmtId = 1
            n2Core.synapseFmt[1].wgtExp = 0
            n2Core.synapseFmt[1].wgtBits = 7
            n2Core.synapseFmt[1].numSynapses = 63
            n2Core.synapseFmt[1].cIdxOffset = 0
            n2Core.synapseFmt[1].cIdxMult = 0
            n2Core.synapseFmt[1].idxBits = 1
            n2Core.synapseFmt[1].fanoutType = 2
            n2Core.synapseFmt[1].compression = 0

            n2Core.synapseMap[0].synapsePtr = 0
            n2Core.synapseMap[0].synapseLen = 1
            n2Core.synapseMap[0].discreteMapEntry.configure()

            n2Cores[0].createDiscreteAxon(srcCxId=0,
                                      dstChipId=0,
                                      dstCoreId=n2Core.id,
                                      dstSynMapId=0)
            
        # create host snip 
        pubSubProcess = board.createSnip(phase=Phase.HOST_CONCURRENT_EXECUTION, library=self.lib)
        cFilePath = os.path.dirname(os.path.realpath(__file__)) + "/runmgmt.c"
        includeDir = os.path.dirname(os.path.realpath(__file__))
        funcName = "run_mgmt"
        guardName = "do_run_mgmt"
        embeddedProcess = board.createSnip(phase=Phase.EMBEDDED_MGMT, cFilePath=cFilePath, includeDir=includeDir, funcName=funcName, guardName=guardName)
        
        inputChannel = board.createChannel(b'input', "int", 1000000)
        inputChannel.connect(pubSubProcess, embeddedProcess)
        feedbackChannel = board.createChannel(b'feedback', "int", 1000000)
        feedbackChannel.connect(embeddedProcess, pubSubProcess)

        self.board = board
    
    def generateProbes(self): 
        mon = self.board.monitor
        n2Cores = self.board.n2Chips[0].n2CoresAsList
        for n2Core in n2Cores:
            yield (mon.probe(n2Core.cxState, [0], 'u')[0],
               mon.probe(n2Core.cxState, [0], 'v')[0],
               mon.probe(n2Core.cxState, [0], 'spike')[0])
    
    def run(self):
        self.board.run(100)
        self.board.disconnect()

    def buildSharedLibrary(self):
        lib = os.path.dirname(os.path.realpath(__file__)) + "/build/librosIOsnip.so"
        build_script = "{}/build.sh".format(os.path.dirname(os.path.realpath(__file__)))
        subprocess.run([build_script], check=True, shell=True, executable="/bin/bash")
        self.lib = lib



if __name__ == "__main__":
    lui = lui()
    lui.buildSharedLibrary()
    lui.setupNetwork()
    output = list(lui.generateProbes())
    lui.run()


    
    fig = plt.figure(1001, figsize=(15, 10))
    figIndex = iter(range(1, 13))


    for coreId, probes in enumerate(output):
        # Since there are no incoming spikes and noise is disabled by default, u
        # remains constant at 0 for source core
        plt.subplot(4, 3, coreId+1)
        probes[0].plot()
        plt.title('%d: u' % coreId)

        # v increases due to the bias current.  The concave nature of the curve
        # when the voltage is increasing is due to the decay constant.  Upon
        # reaching the threshold of 64000, the compartment spikes and resets
        # to 0. Since there is no refractory period, the voltage immediate
        # begins to increase again.
        plt.subplot(4, 3, coreId+1)
        probes[1].plot()
        plt.title('%d: v' % coreId)

        plt.subplot(4, 3, coreId+1)
        probes[2].plot()
        plt.title('%d: spike' % coreId)
        plt.tight_layout()

    if haveDisplay:
        plt.show()
    else:
        fileName = "tutorial_19_fig1001.png"
        print("No display available, saving to file " + fileName + ".")
        fig.savefig(fileName)


