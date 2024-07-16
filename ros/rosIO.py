# Diego Chavez Arana
# self note if I have problems finding libraries try to mess with the LD_LIBRARY_PATH
# or the KAPOHOBAY variable
# or try executing the python script using sudo su
# or try to source the terminal with /opt/ros/noetic/setup.bash
# or try to make the build.sh executable with chmod +x build.sh
# or try to put the shebang line in the build.sh file
# or try to export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ros/noetic/lib

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
        numCoresPerChip = [1]
        numCompartmentsPerCore = [[100]]
        board = N2Board(boardId, numChips, numCoresPerChip, numCompartmentsPerCore)
        # obatin the cores object 
        n2Core = board.n2Chips[0].n2Cores[0]
        n2Core.cxProfileCfg[0].configure(decayV=int(1/16*2**12))
        n2Core.vthProfileCfg[0].staticCfg.configure(vth=10)
        n2Core.numUpdates.configure(numUpdates=1)
        for i, j in enumerate(n2Core.synapses):
            n2Core.cxCfg[i].configure(vthProfile = 0, cxProfile = 0)
           
        # checklist to configure the cores
        # for i, j in enumerate(n2Cores):
        #     j.cxProfileCfg[0].configure(decayV=int(1/16*2**12))
        #     j.cxMetaState[0].configure(phase0=2)
        #     j.vthProfileCfg[0].staticCfg.configure(vth=10)
        #     j.numUpdates.configure(numUpdates=1)
        #     j.cxCfg[0].configure(bias = 0, biasExp = 6, vthProfile = 0, cxProfile = 0)
        #     j.synapses[0].CIdx = 0
        #     j.synapses[0].Wgt = 64
        #     j.synapses[0].synFmtId = 1

        #     j.synapseFmt[1].wgtExp = 0
        #     j.synapseFmt[1].wgtExp = 0
        #     j.synapseFmt[1].wgtBits = 7
        #     j.synapseFmt[1].numSynapses = 63
        #     j.synapseFmt[1].cIdxOffset = 0
        #     j.synapseFmt[1].cIdxMult = 0
        #     j.synapseFmt[1].idxBits = 1
        #     j.synapseFmt[1].fanoutType = 2
        #     j.synapseFmt[1].compression = 0

        #     j.synapseMap[0].synapsePtr = 0
        #     j.synapseMap[0].synapseLen = 1 # len(synapses)
        #     j.synapseMap[0].discreteMapEntry.configure()
            
        #     # j.createDiscreteAxon(srcCxId=0, 
        #     #                         dstChipId=0, 
        #     #                         dstCoreId=j.id, 
        #     #                         dstSynMapId=0) 

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
        n2Core = self.board.n2Chips[0].n2Cores[0]
        numbers = list(range(100))
        sProbe = mon.probe(n2Core.cxState, numbers, 'spike')[0]
        # for i in n2Core.synapses:
        #     mon.probe()
        # # for n2Core in n2Cores:
        # #     yield (mon.probe(n2Core.cxState, [0], 'u')[0],
        # #        mon.probe(n2Core.cxState, [0], 'v')[0],
        # #        mon.probe(n2Core.cxState, [0], 'spike')[0])
        return sProbe
    
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
    sProbe = lui.generateProbes()
    lui.run()


    
    fig = plt.figure(1001, figsize=(15, 10))
    figIndex = iter(range(1, 100))
    for i, j in enumerate(sProbe):
        plt.subplot(10, 10, i+1)
        j.plot()
        plt.title('Spike:' + str(i+1))
        plt.tight_layout()

    # for coreId, probes in enumerate(output):
    #     # Since there are no incoming spikes and noise is disabled by default, u
    #     # remains constant at 0 for source core
    #     # plt.subplot(4, 3, coreId+1)
    #     # probes[0].plot()
    #     # plt.title('%d: u' % coreId)

    #     # # v increases due to the bias current.  The concave nature of the curve
    #     # # when the voltage is increasing is due to the decay constant.  Upon
    #     # # reaching the threshold of 64000, the compartment spikes and resets
    #     # # to 0. Since there is no refractory period, the voltage immediate
    #     # # begins to increase again.
    #     # plt.subplot(4, 3, coreId+1)
    #     # probes[1].plot()
    #     # plt.title('%d: v' % coreId)

    #     plt.subplot(10, 10, coreId+1)
    #     probes[2].plot()
    #     plt.title('%d: spike' % coreId)
    #     plt.tight_layout()

    if haveDisplay:
        plt.show()
    else:
        fileName = "/home/cortana/nengo_loihi_debug/plots/tutorial_19_fig1001.png"
        print("No display available, saving to file " + fileName + ".")
        fig.savefig(fileName)


