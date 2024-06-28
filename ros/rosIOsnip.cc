/*
INTEL CORPORATION CONFIDENTIAL AND PROPRIETARY

Copyright © 2019-2021 Intel Corporation.

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

// include/import standard lirbaries
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <memory>
#include <string>
#include "nxsdkhost.h"
#include "ros/ros.h"
#include "ros/transport_hints.h"
#include "std_msgs/Int32.h"

// ROS Topic process that publishes and subscribes to a ROS Topic
// input Channel is used to write data to the embedded snip 
// and feedback channel is used to read data fromt the embedded snip
namespace ros_demo {
const char TOPIC[] = "loihiTopic";
const char input_channel[] = "input";
const char feedback_channel[] = "feedback";
const int QUEUE_SIZE = 10; // Queue of 1 int is a 32-bit message 

// The class PubSubProcess inherits from ConcurrentHostSnip
// ConcurrentHostSnip is a base class for snips that run concurrently with the Loihi model

class PubSubProcess : public ConcurrentHostSnip {
  // ROS Node Handle
  std::unique_ptr<ros::NodeHandle> _node;
  // ROS Topic Publisher (Reads from feedback_channel and publishes to TOPIC)
  ros::Publisher _pub;
  // ROS Topic Subscriber (Subscribes to TOPIC and writes to input_channel)
  ros::Subscriber _sub;
  // boolean flag to determine a loop is now complete, old data has been processed and new data has arrived
  bool _control_loop_complete;



 public:
  PubSubProcess() : _control_loop_complete(true) {
    // Write some initial data to input channel
    uint32_t data[1] = {0};
    writeChannel(input_channel, data, 1);

    // Initializes ROS
    int argc = 1;
    const char* argv[1] = {"PubSubProcess"};
    ros::init(argc, const_cast<char**>(argv), "pubsub");

    // Create the ROS Node Handle that will allows to communicate with the ROS system. 
    // including publishing and  sucbcribing to topics, aka node
    _node = std::make_unique<ros::NodeHandle>();

    // Subscribes to a ROS Topic "example" and registers a callback
    _sub = _node->subscribe(TOPIC, QUEUE_SIZE, &PubSubProcess::callback, this, ros::TransportHints().reliable().tcpNoDelay());

    // Register to publish to ROS Topic "example"
    _pub = _node->advertise<std_msgs::Int32>(TOPIC, QUEUE_SIZE);

    const int array_size = 100; 
    std::vector<int> array(array_size, 0);

    const double scale 10.0; 
    const double shift = array_size / 2.0;
  }

  void run(std::atomic_bool& endOfExecution) override {
    // Set the rate of processing at 1000 Hz
    ros::Rate loop_rate(1000);

    // Loop to publish and subscribe
    while (ros::ok() && !endOfExecution) {
      if (publish()) {
        // Execute all callbacks till control loop is complete
        _control_loop_complete = false;
        while(!_control_loop_complete) {
            ros::spinOnce();
        }
        loop_rate.sleep();
      }
    }
  }

  // Callback method called by the Subscriber when it receives a message
  void callback(const std_msgs::Int32::ConstPtr& msg) {
    // Write to the input channel
    int32_t data[] = {msg->data};
    writeChannel(input_channel, data, 1);
    // Demonstrates logging using ROS_INFO
    ROS_INFO("Received: [%d]", msg->data);

    // Set control loop completion to true as new data has been read from topic
    _control_loop_complete = true;
  }

  // Reads from feedback_channel and publishes data to ROS Topic
  // Returns true if any messages were published. Otherwise, returns false
  bool publish() {
    int numMessagesToRead = probeChannel(feedback_channel);
    // Read an integer from feedback channel
    if (numMessagesToRead > 0) {
      uint32_t data[1] = {0};
      readChannel(feedback_channel, data, 1);

      // Create a ROS Message 
      std_msgs::Int32 msg;
      msg.data = data[0];

      // Publish the message to the registered ROS Topic "example"
      _pub.publish(msg);

      // Demonstrates ROS Logging
      ROS_INFO("Sent: [%d]", msg.data);
      return true;
    } else {
      return false;
    }
  }
};

}  // namespace ros_demo

using ros_demo::PubSubProcess;

// Each ConcurrentHostSnip is run within a thread
// If you have more threads on the host cpu, you can choose to create individual
// snips for publishers and subscribers
REGISTER_SNIP(PubSubProcess, ConcurrentHostSnip);
