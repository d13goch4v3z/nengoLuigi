# INTEL CONFIDENTIAL
#
# Copyright © 2018-2021 Intel Corporation.
#
# This software and the related documents are Intel copyrighted
# materials, and your use of them is governed by the express
# license under which they were provided to you (License). Unless
# the License provides otherwise, you may not use, modify, copy,
# publish, distribute, disclose or transmit  this software or the
# related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with
# no express or implied warranties, other than those that are
# expressly stated in the License.

# Adapted from https://stackoverflow.com/questions/50324348/can-a-ros-node-be-created-outside-a-catkin-workspace

cmake_minimum_required(VERSION 3.5)
project(rosIO LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 14)

# find ROS packages
LINK_DIRECTORIES(/opt/ros/noetic/lib)
link_directories(/opt/ros/noetic/lib)

# set up our program
add_library(rosIOsnip SHARED rosIOsnip.cc)

# add nxsdkhost.h include
target_include_directories(rosIOsnip
    PUBLIC ${PROJECT_SOURCE_DIR}/build/includes/nxsdk/include
)

target_include_directories(rosIOsnip PUBLIC /opt/ros/noetic/include)

# link with ROS libraries
target_link_libraries(rosIOsnip PUBLIC roscpp rostime rosconsole roscpp_serialization)
