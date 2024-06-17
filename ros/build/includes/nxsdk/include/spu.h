#define W_SYN_MEM 64
#define N_SYN_MAX 60
#define W_FMT_IDX 4
#define W_NSYN 6
#define W_WGT_U 8
#define W_WGT (W_WGT_U + 1)
#define W_TAG_U  (W_WGT_U)
#define W_TAG  (W_WGT)
#define W_LEN 1
#define NSYN_IN_PREFIX 63
#define N_DA_BANKS 4
#define TERM_IDX  4
#define W_ENTRY_MIN  5  // enough to get termination marker
#define W_CIDX 12
#define W_DLY 6

#include "stdint.h"

// Compression type
enum Compression {
    C_SPARSE,
    C_RUNLEN,
    C_DENSE = 3,
    C_MASKED
};

// Unpacking states
enum Unpack_state{
    UNPACK_STATE_PREFIX,
    UNPACK_STATE_FIRST,
    UNPACK_STATE_SYN,
    UNPACK_STATE_EOW,
    UNPACK_STATE_EOL,
    UNPACK_STATE_DONE
};

// Learning config
enum Learning_state {
   L_DISABLED,
   L_EN_ALL,  
   L_EN_ENTRY,
   L_EN_SYN  
};


// Fanout type
enum Fanout_type{
  F_NULL,    // null (empty SYNAPSE_CFG word)
  F_MIXED,   // weight sign bits embeddedin weight values
  F_EXC,     // excitatory 
  F_INH      // inhibitory
};


// Synapse types
enum Synapse_type{
  SYN_TYPE_NORMAL,    // Normal (Wgt,Dly,Tag) synapse
  SYN_TYPE_BOX ,    // Box synapse (Dly must be enabled)
  SYN_TYPE_2TAG    // Dly field serves as second tag
};

// Repacking states
enum Repack_state{
  REPACK_STATE_PREFIX,
  REPACK_STATE_FLUSH,
  REPACK_STATE_SYN,
  REPACK_STATE_DONE
};

typedef int Boolean;

typedef struct {
      int           CIdx;
      int           Wgt;
      int           Dly;
      int           Tag;      // only for response to STDP
      int           StdpProfile;
      Boolean       IgnoreDly;// Don't treat Dly as synaptic delay
      Boolean       LrnEn;    // Learning enabled, only for STDP
      Boolean       Valid;
      Boolean       Tail;     // End of synaptic entry (common format)
      Boolean       Eol;      // End of synaptic list (maybe w/ ~Valid)
}Synapse_n2;

typedef struct __attribute__((packed)){
    uint64_t CIdx : 10;
    int64_t Wgt  : 9;
    uint64_t Dly  : 6;
    int64_t Tag  : 9;
    uint64_t LrnEn : 1;
    uint64_t synFmtId : 4;
    uint64_t _ : 25;
}Synapse;

typedef struct {
    Synapse *syn;
    int size;
}Synapse_array;

typedef struct {
    uint64_t *synapse_mem;
    int size;
}SynapseMem_array;

typedef struct {
    int synMemId;
    int synMemOffset;
    int numBits;
    uint64_t data;
    int first_synId;
}SynapseMemMap;

typedef struct {
    uint64_t w[2];
}Buffer;

typedef struct {
    uint64_t wd;
    Boolean valid;
    int offset;
}RepackResult;

typedef struct{
      int                   synFmtId;
      SynFormat             format;
      int                   words;
      Buffer                buffer;
      int                   valid_bits;    // buffer bits that are valid
      Boolean               prefix_lrn_en;
      uint64_t              nz_wgt_mask;
      int                   nsyn;
      int                   idx;
      int                   state;
      Synapse               first_syn;
      int                   simd;
      Boolean               do_tail;        // need to send tail to repack
      Boolean               end_of_word;
      Boolean               ack_next;       // was next_word consumed?
      Boolean               valid_synapse;  // was a synapse extracted?
}SynUnpackState;


typedef struct{
    SynUnpackState ups;
    uint32_t synMemPtr;
    uint32_t synMemLen;
    uint32_t cxBase;
    uint64_t next_word;
}SupperUnpackState;

typedef struct {
      int Compression;            // Same as SynFormat encoding
      Boolean   DiscMaxWgt;            // Same as SynFormat encoding
      int FanoutType;            // Same as SynFormat encoding
      Boolean   IsRunLength;           // For SkipBits handling
      int IdxSkipBits;           // # bits of Index or Skip per synapse
      int ReuseSynData;          // Same as SynFormat encoding
      int WgtBits;               // Same as SynFormat encoding
      int DlyBits;               // Same as SynFormat encoding
      int TagBits;               // Same as SynFormat encoding
      int LrnEnBits;             // LE bit included in synapse or not
}SynRepackFormat;


typedef struct {
      int                state;
      int                idx;
      int                nsyn;
      SynFormat          format;
      int                wdtl_bits;  // precomputed (Wgt,Dly,Tag,LrnEn) bits
      Boolean            rcv_tail;
      Boolean            rcv_eol;    // Last word of list was received
      Buffer             buffer;
      int                offset;
      Boolean            first;      // first synapse to be repacked
      int                simd;
}SynRepackState;


#define IGNORE_DEBUG 1
#define false 0
#define true 1

#if IGNORE_DEBUG
#define debugprintf(msg...) ((void) 0)
#else
#define debugprintf(msg...) printf(msg)
#endif

#ifdef SUPERHOST
    #define MAYBE_VOLATILE
    SupperUnpackState initSupperUnpackState(int synMemLen, int cxBase);
    int synMemWordsToSyn(SynFormat *synapse_format, uint64_t *synapse_mem, SupperUnpackState *ups, Synapse *syn);
    SynapseMem_array synToSynMemWords(Synapse *syn, int numSyn, SynFormat *synFmt, int CxBase, SynapseMemMap * synMap);
#else
    #define MAYBE_VOLATILE volatile
    SupperUnpackState initSupperUnpackState(int synMemId, int synMemLen, int cxBase);
    int synMemWordsToSyn(NeuronCore *neuron, SupperUnpackState *ups, Synapse *syn);
    int synToSynMemWords(Synapse *syn, int numSyn, NeuronCore *nc, int synMemId, int CxBase);
#endif

