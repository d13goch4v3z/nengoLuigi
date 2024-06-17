/*
INTEL CORPORATION CONFIDENTIAL AND PROPRIETARY
Copyright © 2018-2021 Intel Corporation.

The source code contained or described herein and all documents
related to the source code ("Material") are owned by Intel Corporation
or its suppliers or licensors.  Title to the Material remains with
Intel Corporation or its suppliers and licensors.  The Material may
contain trade secrets and proprietary and confidential information of
Intel Corporation and its suppliers and licensors, and is protected by
worldwide copyright and trade secret laws and treaty provisions.  No
part of the Material may be used, copied, reproduced, modified,
published, uploaded, posted, transmitted, distributed, or disclosed in
any way without Intel's prior express written permission.  No license
under any patent, copyright, trade secret or other intellectual
property right is granted to or conferred upon you by disclosure or
delivery of the Materials, either expressly, by implication,
inducement, estoppel or otherwise. Any license under such intellectual
property rights must be express and approved by Intel in writing.
Unless otherwise agreed by Intel in writing, you may not remove or
alter this notice or any other notice embedded in Materials by Intel
or Intel's suppliers or licensors in any way.

*/

#ifndef NXSDK_H
#define NXSDK_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

// TODO: Duplicated from chipconfig.h
#ifndef IO_X
#define IO_X       4
#endif
#define IO_XYP     (IO_X<<7 | 1)
#define BRIDGE_XYP (IO_X<<7 | 3)

typedef struct __attribute__((packed)) {
    uint32_t num_updates : 9,
             num_stdp    :12,
                         :11;
} UpdateCfg;

typedef struct __attribute__((packed)) {
    uint32_t Time   :10,
             T      : 6,
             Tepoch : 6,
                    :10;
} TimeState;

typedef struct __attribute__((packed)) {
    uint32_t FirstLearningIndex :13,
             NumRewardAxons     : 4,
                                :15;
} StdpCfg;

typedef struct __attribute__((packed)) {
    uint32_t WgtLimitMant : 4,
             WgtLimitExp  : 4,
             WgtExp       : 4,
             DiscMaxWgt   : 1,
             LearningCfg  : 2,
             TagBits      : 2,
             DlyBits      : 3,
             WgtBits      : 3,
             ReuseSynData : 1,
             NumSynapses  : 6,
             CIdxOffset   : 4,
             CIdxMult     : 4,
             SkipBits     : 2,
             IdxBits      : 3,
             SynType      : 1,
             FanoutType   : 2,
             Compression  : 3,
             StdpProfile  : 4,
             IgnoreDly    : 1,
                          :10;
} SynFormat;

typedef struct __attribute__((packed)) {
    uint32_t UpdateOnXspike      : 1,
             UpdateOnX1          : 1,
             UpdateOnX2          : 1,
             UpdateOnRewardSpike : 1,
             UpdateOnReward      : 1,
             UpdateAlways        : 1,
             RewardAxon          : 4,
             NumTraceHist        : 3,
             NumTraces           : 1,
             StdpProfile         : 4,
                                 :14;
} StdpPreProfileCfg;

typedef struct __attribute__((packed)) {
    uint32_t SpikeLevelFrac  : 8,
             SpikeLevelInt   : 7,
             Lambda          : 8,
             RandomThreshold : 8,
             Decay0          : 8,
             Decay1          : 8,
             Decay2          : 8,
             Decay3          : 8,
             Decay4          : 8,
             Decay5          : 8,
                             :17;
} TraceCfg;

typedef struct __attribute__((packed)) {
    TraceCfg trace;
    uint32_t padding;
} TraceCfgWithPad;

typedef struct __attribute__((packed)) {
    uint32_t UCodePtr    : 4,
             DecimateExp : 3,
             NumProducts : 3,
             RequireY    : 1,
             UsesXepoch  : 1,
                         :20;
} StdpProfileCfg;

typedef struct __attribute__((packed)) {
    uint32_t Random0 :32,
             Random1 :32,
             Random2 :32,
             Time    : 1,
                     :31;
} TraceRandom;

typedef struct __attribute__((packed)) {
    uint32_t DelayBits: 4,
                      :28;
} DendriteAccumCfg;

typedef struct __attribute__((packed)) {
    uint32_t Gaussian         : 1,
             NoiseExp0        : 6,
             NoiseExp1        : 6,
             NoiseMantOffset0 : 3,
             NoiseMantOffset1 : 3,
             NoiseAtDendOrVm  : 1,
             RefractInhibited : 1,
             DisableInhibited : 1,
             NegVmLimit       : 5,
             PosVmLimit       : 3,
             DmOffsets        : 1,
             DsOffset         : 1;
} SharedCfg;

typedef struct __attribute__((packed)) {
    uint32_t Tepoch         : 6,
             T              : 6,
                            :20;
} DendTimeState;

typedef struct __attribute__((packed)) {
    uint32_t Beta              : 4,
             Amin              : 7,
             Amax              : 7,
             EnableHomeostasis : 1,
                               :13;
} VthProfileDynamicCfg;

typedef struct __attribute__((packed)) {
    uint32_t Vth               :17,
             UseSomaVth        : 1,
             EnableHomeostasis : 1,
                               :13;
} VthProfileStaticCfg;

typedef union {
    VthProfileDynamicCfg vthProfileDynamicCfg;
    VthProfileStaticCfg vthProfileStaticCfg;
} VthProfileCfg;

typedef struct __attribute__((packed)) {
    uint32_t bAP_Action      : 2,
             bAP_Src         : 4,
             ThreshOp        : 2,
             JoinOp          : 3,
             StackOut        : 2,
             StackIn         : 2,
             EnableNoise     : 1,
             EnableAxonDelay : 1,
             RefractDelay    : 6,
             Decay_v         :12,
             Decay_u         :12,
                             :17;
} CxProfileCfg;

typedef struct __attribute__((packed)) {
    uint32_t Phase0  : 3,
             SomaOp0 : 2,
             Phase1  : 3,
             SomaOp1 : 2,
             Phase2  : 3,
             SomaOp2 : 2,
             Phase3  : 3,
             SomaOp3 : 2,
                     :12;
} MetaState;

typedef struct __attribute__((packed)) {
    uint32_t BiasExp    : 3,
             Bias       :13,
             VthProfile : 3,
             CxProfile  : 5,
                        : 8;
} CxCfg;

typedef struct __attribute__((packed)) {
    uint32_t Ptr        :12,
             Len        :10,
             Atom       :10;
} AxonMapEntry;

typedef struct __attribute__((packed)) {
    int32_t  V :24,
             U :24,
               :16;
} CxState;

typedef struct __attribute__((packed)) {
    uint32_t AxonDelay   : 8,
             Vth         :17,
             A           : 7,
             Tprev       : 6,
             SpikeQueue0 : 6,
             SpikeQueue1 : 6,
             SpikeQueue2 : 6,
             SpikeQueue3 : 6,
                         : 2;
} SomaState;

typedef struct __attribute__((packed)) {
    uint32_t X1                : 7,
             Tspike1           : 6,
             TraceCfgSelect    : 2,
             X2                : 7,
             Tspike2           : 6,
             StdpPreProfileCfg : 4;
} PreTraceEntry1;

typedef struct __attribute__((packed)) {
    uint32_t X1                : 7,
             Tspike            : 6,
             TraceCfgSelect1   : 2,
             X2                : 7,
                               : 4,
             TraceCfgSelect2   : 2,
             StdpPreProfileCfg : 4;
} PreTraceEntry2;

typedef struct __attribute__((packed)) {
    uint32_t Ptr             :14,
             Len             : 8,
             CxBase          :10;
} DiscreteMapEntry;

typedef struct __attribute__((packed)) {
    uint32_t Ptr             :14,
             Len             : 7,
             CxBase          : 8,
             AtomBits        : 3;
} Pop16MapEntry;

typedef union {
    PreTraceEntry1   preTraceEntry1;
    PreTraceEntry2   preTraceEntry2;
    DiscreteMapEntry discreteMapEntry;
    Pop16MapEntry    pop16MapEntry;
} SynapseMapEntry;

typedef struct __attribute__((packed)) {
    uint32_t R              : 7,
             Tspike         : 6,
             TraceCfgSelect : 2,
             RewardValue    : 8,
             RewardValid    : 1,
             Rsgn           : 1,
             Rsvd           : 7;
} RewardTraceEntry;

typedef struct __attribute__((packed)) {
    uint32_t Yspike0      : 7,
             Yspike1      : 7,
             Yspike2      : 7,
             Yepoch0      : 7,
             Yepoch1      : 7,
             Yepoch2      : 7,
             Tspike       : 6,
             TraceProfile : 2,
             StdpProfile  : 4,
                          :10;
} PostTraceEntry;

typedef struct __attribute__((packed)) {
    uint32_t accum : 16,
                   : 16;
} DendriteAccumEntry;

typedef struct __attribute__((packed)) {
    uint32_t CoreId        :12,
                           : 2,
             Fixed_0       : 5,
             AxonId        :10,
             Fixed_1       : 1,
             SpikeType     : 2;
} AxonCfgPop16;

typedef struct __attribute__((packed)) {
    uint32_t CoreId        :12,
                           : 2,
             AxonId        :13,
                           : 1,
             Fixed_1       : 2,
             SpikeType     : 2;
} AxonCfgDiscrete;

typedef struct __attribute__((packed)) {
    uint32_t CoreId        :12,
                           : 2,
             SynMemListLen :12,
                           : 2,
             Fixed_1       : 2,
             SpikeType     : 2;
} AxonCfgDirectWord0;

typedef struct __attribute__((packed)) {
    uint32_t SynMemListPtr :14,
             ValidPayload  : 1,
             Fixed_1       : 1,
             Payload0      : 8,
             Payload1      : 8;
} AxonCfgDirectWord1;

typedef struct __attribute__((packed)) {
    uint32_t CoreId        :12,
                           : 2,
             AxonId        :12,
                           : 2,
             Fixed_1       : 2,
             SpikeType     : 2;
} AxonCfgPop32Word0;

typedef struct __attribute__((packed)) {
    uint32_t Fixed_0       :10,
                           : 3,
             ValidPayload  : 1,
             Fixed_1       : 2,
             Payload0      : 8,
             Payload1      : 8;
} AxonCfgPop32Word1;

typedef struct __attribute__((packed)) {
    uint32_t CoreId        :12,
                           : 2,
             ChipId        :14,
                           : 2,
             SpikeType     : 2;
} AxonCfgRemote;

typedef struct __attribute__((packed)) {
  uint32_t CoreId        :12,
                         : 2,
           AxonId        :13,
                         : 1,
           Fixed_1       : 2,
           SpikeType     : 2;
} AxonCfgRelayWord0;

typedef struct __attribute__((packed)) {
  uint32_t atom   :10,
           ChipId :14,
           core_p :2,
           core_y :3,
           core_x :3;
} AxonCfgRelayWord1;

typedef union {
    AxonCfgPop16       pop16;
    AxonCfgDiscrete    discrete;
    AxonCfgDirectWord0 direct_0;
    AxonCfgDirectWord1 direct_1;
    AxonCfgPop32Word0  pop32_0;
    AxonCfgPop32Word1  pop32_1;
    AxonCfgRemote      remote;
    AxonCfgRelayWord0  relay_0;
    AxonCfgRelayWord1  relay_1;
} AxonCfg;

#define AXON_CFG_POP16(coreId, axonId) (AxonCfgPop16) \
    { .CoreId        = coreId.id, \
      .Fixed_0       = 0, \
      .AxonId        = axonId, \
      .Fixed_1       = 1, \
      .SpikeType     = 0 }

#define AXON_CFG_DISCRETE(coreId, axonId) (AxonCfgDiscrete) \
    { .CoreId        = coreId.id, \
      .AxonId        = axonId, \
      .Fixed_1       = 1, \
      .SpikeType     = 0 }

#define AXON_CFG_DIRECT_WORD0(coreId, synMemListLen) (AxonCfgDirectWord0) \
    { .CoreId        = coreId.id, \
      .SynMemListLen = synMemListLen, \
      .Fixed_1       = 1, \
      .SpikeType     = 2 }

#define AXON_CFG_DIRECT_WORD1(synMemListPtr, validPayload, payload0, payload1) (AxonCfgDirectWord1) \
    { .SynMemListPtr = synMemListPtr, \
      .ValidPayload  = validPayload, \
      .Fixed_1       = 1, \
      .Payload0      = payload0, \
      .Payload1      = payload1 }

#define AXON_CFG_POP32_WORD0(coreId, axonId) (AxonCfgPop32Word0) \
    { .CoreId        = coreId.id, \
      .AxonId        = axonId, \
      .Fixed_1       = 1, \
      .SpikeType     = 2 }

#define AXON_CFG_POP32_WORD1(validPayload, payload0, payload1) (AxonCfgPop32Word1) \
    { .Fixed_0       = 0, \
      .ValidPayload  = validPayload, \
      .Fixed_1       = 1, \
      .Payload0      = payload0, \
      .Payload1      = payload1 }

#define AXON_CFG_REMOTE(chipId) (AxonCfgRemote)  \
    { .CoreId       = BRIDGE_XYP, \
      .ChipId       = chipId.id, \
      .SpikeType    = 1 }

#define AXON_CFG_RELAY_WORD0(axonId) (AxonCfgRelayWord0) \
  { .CoreId    = BRIDGE_XYP, \
    .AxonId    = axonId, \
    .Fixed_1   = 1, \
    .SpikeType = 3 }

#define AXON_CFG_RELAY_WORD1(chipId, coreId, Atom) (AxonCfgRelayWord1) \
  { .atom   = Atom, \
    .ChipId = chipId.id, \
    .core_p = coreId.p, \
    .core_y = coreId.y, \
    .core_x = coreId.x }

#define PAD_INTERNAL2(from,to,line)  uint32_t __pad ## line [to-from]
#define PAD_INTERNAL1(from,to,line)  PAD_INTERNAL2(from,to,line)
#define PAD(from,to)  PAD_INTERNAL1(from,to,__LINE__)

typedef struct __attribute__((packed)) {
    UpdateCfg          num_updates;
    TimeState          time;
    uint32_t           reserved0;
    uint32_t           ecc_err;
    uint32_t           reserved1;
    int32_t            reserved2;                         PAD(0x0006,0x0010);
    uint32_t           reserved3[16];                    PAD(0x0020,0x0030);
    uint32_t           reserved4[16];                        PAD(0x0040,0x0080);
    StdpCfg            stdp_cfg;                          PAD(0x0081,0x0082);
    uint32_t           stdp_epoch_count;                  PAD(0x0083,0x0100);
    SynFormat          synapse_fmt[16];
    uint32_t           synapse_repack_random;             PAD(0x0121,0x0130);
    StdpPreProfileCfg  stdp_pre_profile_cfg[16];
    TraceCfgWithPad    stdp_pre_cfg[3];                   PAD(0x014c,0x0150);
    TraceCfgWithPad    stdp_post_cfg[4];
    StdpProfileCfg     stdp_profile_cfg[16];              PAD(0x0170,0x0180);
    uint32_t           stdp_ucode_mem[16];                PAD(0x0190,0x01a0);
    TraceRandom        stdp_pre_random;
    TraceRandom        stdp_post_random;                  PAD(0x01a8,0x01e0);
    DendriteAccumCfg   dendrite_accum_cfg;                PAD(0x01e1,0x0200);
    SharedCfg          dendrite_shared_cfg;
    DendTimeState      dendrite_time_state;
    uint32_t           dendrite_random[2];
    TraceRandom        soma_random;
    TraceCfgWithPad    soma_trace_cfg;                    PAD(0x020c,0x0220);
    VthProfileCfg      vth_profile_cfg[8];                PAD(0x0228,0x0240);
    CxProfileCfg       cx_profile_cfg[32];                PAD(0x0280,0x0400);
    MetaState          cx_meta_state[256];                PAD(0x0500,0x0800);
    CxCfg              cx_cfg[1024];
    AxonMapEntry       axon_map[1024];
    CxState            cx_state[1024];
    SomaState          soma_state[1024];
    AxonCfg            axon_cfg[4096];
    SynapseMapEntry    synapse_map[4096];
    RewardTraceEntry   reward_trace[4];                   PAD(0x4004,0x4800);
    PostTraceEntry     stdp_post_state[1024];             PAD(0x5000,0x6000);
    DendriteAccumEntry dendrite_accum[8192];
    uint64_t           synapse_mem[16384];
} volatile NeuronCore;

typedef struct __attribute__((packed)) {
  union {
    volatile uint8_t spike[4][1024];
  };
} SpikeCountWrap;

typedef struct __attribute__((packed)) {
  union {
    volatile uint32_t spike[4][256];
  };
} SpikeDataWrap;

#define LOIHI_BASE       ((volatile void *)     0x0)
#define LMT_SCM_BASE ((volatile void *) 0x20000)
#define SCM_BASE         LMT_SCM_BASE
#define SPIKE_COUNT (((volatile SpikeCountWrap *) (SCM_BASE+0xF000))->spike)
#define SPIKE_DATA  (((volatile SpikeDataWrap  *) (SCM_BASE+0xE000))->spike)
#define SYNC_REG         ((volatile uint32_t *) 0x37000)
#define MAX_USER_DATA 1024
#define W_MESH_ADDR 20
#define W_MESH_XYP  12
#define MASK_MESH_ADDR (~(~0<<W_MESH_ADDR))
#define MASK_MESH_XYP  (~(~0<<W_MESH_XYP))
#define TICKS_PER_MICROSECOND 400L
#define MAX_BLOCKS  10

typedef struct __attribute__((packed)) {
  union {
    struct { uint16_t p:2, y:5, x:5; };
    uint16_t id:12;
  };
} CoreId;

typedef struct __attribute__((packed)) {
  union {
    struct { uint16_t z:3, y:4, x:7; };
    uint16_t id:14;
  };
} ChipId;

typedef struct runState {
    unsigned int time_step;
    unsigned int total_steps;
    unsigned int epoch;
    unsigned int cmd;
    uint8_t userData[MAX_USER_DATA];
} runState;

typedef struct snnOptions {
    bool debug;
    bool remote_relay;
    uint32_t dvs;
    int32_t epoch;
    uint32_t chips;
    uint8_t numBlocks;
    ChipId spikeBlock[MAX_BLOCKS];
} snnOptions;

typedef struct runFunctions {
    void (*nx_init_network)(runState *);
    void (*nx_init_network_opts)(runState *,snnOptions *,int);
    void (*nx_run_spiking)(runState *);
    void (*nx_run_pre_learn_mgmt)(runState *);
    void (*nx_run_mgmt)(runState *);
    void (*nx_run_remote_mgmt)(runState *);
    int (*nx_do_spiking)(runState *);
    int (*nx_do_pre_learn_mgmt)(runState *);
    int (*nx_do_mgmt)(runState *);
    int (*nx_do_remote_mgmt)(runState *);
    void (*nx_run_user_cmds)(runState *);
    int (*nx_do_quit)(runState*);
} runFunctions;

typedef struct {
  uint16_t pad;       // pad to 16B
  ChipId   chip;      // remote chip
  CoreId   core;      // remote core
  uint16_t recv_axon; // axon index used for flow control on receiving core
  uint16_t send_axon; // axon index used for flow control on sending   core
  uint16_t size;      // message size in bytes
  uint16_t buf;       // address offset of receive buffer relative to SCM_BASE
  uint8_t  buf_max;   // buffer size in messages
  uint8_t  buf_idx;   // head or tail index in buffer
} CspPort;

typedef CspPort CspRecvPort;
typedef CspPort CspSendPort;
CoreId nx_my_coreid();
CoreId nx_coreid_host();
ChipId nx_chipid_host();
ChipId nx_nth_chipid(uint16_t chip);
ChipId nx_chipid(uint8_t X, uint8_t Y, uint8_t Z);
CoreId nx_nth_coreid(uint16_t core);
CoreId nx_nth_cpu_coreid(uint8_t n);
#define nx_coreid_lmt nx_nth_cpu_coreid
void nx_flush_core(CoreId core);
void nx_flush(void *ptr);
void nx_join_barrier_sync();
void nx_run_network(runState *, runFunctions *);
void nx_send_remote_event(uint16_t time, ChipId chip, CoreId core, uint16_t axon);
void nx_send_discrete_spike(uint16_t time, CoreId core, uint16_t axon);
void nx_send_pop16_spike(uint16_t time, CoreId core, uint16_t dstFip, uint16_t srcAtom, uint16_t atomBits);
void nx_send_pop32_spike(uint16_t time, CoreId core, uint16_t dstFip, uint16_t srcAtom, bool validPayload, uint8_t payload0, uint8_t payload1);
void nx_send_remote_long_event(uint16_t time, ChipId chip, CoreId core, uint64_t axon);

void nx_init_network(runState *s);
uint8_t csp_probe_recv(CspRecvPort *port);
void execute_read_regs_command();
void csp_create_recv_port(ChipId chip, CoreId core, CspRecvPort *port, uint16_t size, uint8_t max);
void csp_create_send_port(ChipId chip, CoreId core, CspSendPort *port);
void nx_command_handler(runState *, runFunctions *, CspRecvPort *recvp, CspSendPort *sendp, snnOptions *opts);
void nx_snn_parse_args(int argc, char **argv, snnOptions *opts);
void nx_init_network_opts(runState *s, snnOptions *opts, bool lmt0, bool lmt1, bool lmt2, CoreId sw, CoreId ne);
int nx_do_quit(runState *s);
void nx_set_epoch(runState *s, snnOptions *opts);
void nx_fast_init(volatile void *ptr, size_t num, size_t size, size_t stride, void *data);
void nx_fast_init32(volatile void *ptr, size_t num, uint32_t data);
void nx_fast_init64(volatile void *ptr, size_t num, uint64_t data);
void nx_fast_init_multicore(volatile void *ptr, size_t num, size_t size, size_t stride, void *data, CoreId *ids, size_t numIds);
int printf(const char *format, ...);
int sprintf(char *str, const char *format, ...);

uint64_t timestamp();

typedef union {
  CspRecvPort recv;
  CspSendPort send;
} CspChannel;

typedef enum {
  SEND,
  RECV
} ChannelDirection;

typedef struct {
  char *name;
  ChannelDirection direction;
  CspChannel cspChannel;
} Channel;

extern Channel *channels;
extern uint32_t *phaseTimes;
extern int8_t spikeIdx;
extern int8_t learnIdx;
extern int8_t mgmtIdx;
extern int8_t prelearn_mgmtIdx;
extern int32_t tsBuffSize;
extern int32_t tsBinSize;
extern int32_t tsStart;
extern int32_t tsEnd;
extern int8_t numPhaseBins;

// API's for channel read-write.
int32_t createChannel(char* channelName, uint32_t numMsgs, uint32_t msgSize, ChannelDirection direction, uint32_t slack);
int32_t getChannelID(char* channelName);
int32_t readChannel(uint32_t channelID, void* data, uint32_t numMsgs);
int32_t writeChannel(uint32_t channelID, void* data, uint32_t numMsgs);
uint8_t probeChannel(uint32_t channelID);

void dvsInit(uint32_t mode);

#define NEURON_PTR(core) \
  ((NeuronCore *) (LOIHI_BASE + ((uintptr_t) (((core).id&MASK_MESH_XYP)<<W_MESH_ADDR))))


uint16_t nx_num_chips();
ChipId nx_my_chipid();
ChipId nx_min_chipid();
ChipId nx_max_chipid();
ChipId nx_nth_chipid(uint16_t n);
ChipId nx_chipid(uint8_t X, uint8_t Y, uint8_t Z);
CoreId nx_min_coreid();
CoreId nx_max_coreid();
CoreId nx_nth_coreid(uint16_t n);
ChipId nx_nth_chipid(uint16_t n);


#define DVS_LIVE_SPIKES_PER_MESSAGE 30
#define DVS_LIVE_RECEIVE_NAME "dvs_live_receive"
#define DVS_FILE_SPIKES_PER_MESSAGE 256
#define DVS_FILE_RECEIVE_NAME "dvs_file_receive"


typedef struct __attribute__((packed)) {
  uint8_t x;
  uint8_t y;
} DvsSpike;

typedef struct __attribute__((packed)) {
  DvsSpike spikes[DVS_LIVE_SPIKES_PER_MESSAGE];
  uint32_t polarity;
} DvsData;

typedef struct __attribute__((packed)) {
  uint8_t x;
  uint8_t y;
  uint8_t time;
  uint8_t p;
} DvsFileSpike;


#endif
