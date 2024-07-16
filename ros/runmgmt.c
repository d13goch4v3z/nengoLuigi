/*
INTEL CORPORATION CONFIDENTIAL AND PROPRIETARY

Copyright © 2018-2021 Intel Corporation.

This software and the related documents are Intel copyrighted
materials, and your use of them is governed by the express
license under which they were provided to you (License). Unless
the License provides otherwise, you may not use, modify, copy,
publish, distribute, disclose or transmit  this software or the
related documents without Intel's prior written permission.

This software and the related documents are provided as is, with
no express or implied warranties, other than those that are
expressly stated in the License.
*/

#include <stdlib.h>
#include <string.h>
#include "runmgmt.h"
#include <time.h>
#include <unistd.h>

#define NUM_CONNECTIONS 100
int feedbackChannelId = -1; //Store the IDs of the communication channels
int inputChannelId = -1; //Store the IDs for the communication channels

int do_run_mgmt(runState *s) {
    // Runs on every timestep till the 1000th timestep
     if (s->time_step == 1) {
    feedbackChannelId = getChannelID("feedback"); //Get ID for the feedback channel
    inputChannelId = getChannelID("input"); //Get ID for the input channel
    }
    return 1;
}

void run_mgmt(runState *s) {

    int data[1] = {0};
    readChannel(inputChannelId, data, 1);

    uint16_t coreId = data[0];
    //coreId = 1 << 14 | (coreId & 0x3FFF);

    //Inject spike in the core
    printf("Spike injected in Core: %d\n", data[0]);
    nx_send_discrete_spike(s->time_step, nx_nth_coreid(0), data[0]);

    // Increment data
    data[0] += 1;

    writeChannel(feedbackChannelId, data, 1);
}
