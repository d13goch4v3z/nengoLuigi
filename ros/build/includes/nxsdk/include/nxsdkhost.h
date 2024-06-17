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

#pragma once
#include <atomic>
#include <cassert>
#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <type_traits>
#include <utility>
#include <valarray>

#define HOST_SNIP_API_VERSION 1

extern "C" void* SNIP_REGISTRY_PTR;
extern "C" const int MIN_SUPPORTED_API_VERSION;

#define CHECK_API_VERSION_COMPATIBILITY \
  assert(HOST_SNIP_API_VERSION >= MIN_SUPPORTED_API_VERSION);

// Supported Snip Types
enum class SNIP_TYPE : int {
  T_PreExecutionSequentialHostSnip = 1,
  T_PostExecutionSequentialHostSnip = 2,
  T_ConcurrentHostSnip = 3
};

using snip_factory = std::function<void*()>;
using snip_factory_map = std::multimap<SNIP_TYPE, snip_factory>;

#define REGISTER_SNIP(T, U)                                            \
  namespace {                                                          \
  struct T##U {                                                        \
    T##U() {                                                           \
      CHECK_API_VERSION_COMPATIBILITY                                  \
      static_assert(std::is_default_constructible<T>::value,           \
                    "" #T " must be default constructible");           \
      static_assert(std::is_convertible<T*, U*>::value,                \
                    "" #T " must inherit " #U " as public");           \
      auto snip_registry =                                             \
          reinterpret_cast<snip_factory_map*>(SNIP_REGISTRY_PTR);      \
      snip_registry->emplace(                                          \
          std::make_pair(SNIP_TYPE::T_##U, []() { return new T(); })); \
    }                                                                  \
  };                                                                   \
  static T##U snip_##T;                                                \
  }  // namespace

// API's for channel read-write.
extern "C" int32_t getChannelID(const char* name);
// API's for channel read-write.
// User should check the return value for success/failure.
 // Erroneous invocation returns -1
extern "C" int32_t writeChannel(const char* name, const void* data,
                                uint32_t numMsgs);
extern "C" int32_t readChannel(const char* name, void* data, uint32_t numMsgs);
// API to probe channel
// In case of send channel will return if one more messsage can be written by
// returning 1 for availability and 0 for not.
// In case of recv channel will return if one more messsage can be read by
// returning 1 and if not 0.  
// Returns -1 for error
extern "C" int32_t probeChannel(const char* channelName);

// Base classes for Sequential Host Snips
// Derived classes need to be default constructible
class AbstractSequentialHostSnip {
 public:
  // run will be invoked pre/post execution based on type of snip
  virtual void run(uint32_t timestep) = 0;
  // returns the schedule of the snip
  // @param timesteps: collection of timesteps to be run
  // @return collection of timesteps the snip should be scheduled on
  virtual std::valarray<uint32_t> schedule(
      const std::valarray<uint32_t>& timesteps) const = 0;
  virtual ~AbstractSequentialHostSnip() {}
};

// Base class for Pre execution sequential host snip
// User should override run and schedule - @see AbstractSequentialHostSnip
// Overriden method run is invoked at timesteps given by schedule
// Invocation precedes the embedded execution for any given timestep
class PreExecutionSequentialHostSnip : public AbstractSequentialHostSnip {};

// Base class for Post execution sequential host snip
// User should override run and schedule - @see AbstractSequentialHostSnip
// Overriden method run is invoked at timesteps given by schedule
// Invocation succeeds/follows the embedded execution for any given timestep
class PostExecutionSequentialHostSnip : public AbstractSequentialHostSnip {};

// Base class for Concurrent host snip (User should override run)
// Overriden method run is invoked within a host thread before the first
// execution (board.run) and keeps running till the host is shutdown.
// endOfExecution is set to true when host is being shutdown.
// Note: ConcurrentHostSnip does not have a notion of timestep
class ConcurrentHostSnip {
 public:
  virtual void run(std::atomic_bool& endOfExecution) = 0;  // NOLINT
  virtual ~ConcurrentHostSnip() {}
};
