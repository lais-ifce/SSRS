cmake_minimum_required(VERSION 3.8)
project(dsfs)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/libintl)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/easyloggingpp)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/encfs)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)

# Compile-time configuration.
configure_file (${CMAKE_CURRENT_LIST_DIR}/config.h.cmake
        ${CMAKE_BINARY_DIR}/config.h)

include_directories (${CMAKE_BINARY_DIR})
include_directories (${CMAKE_CURRENT_LIST_DIR})

add_definitions (-D_FILE_OFFSET_BITS=64 -DFUSE_USE_VERSION=26)

# Logging.
add_definitions (-DELPP_THREAD_SAFE -DELPP_DISABLE_DEFAULT_CRASH_HANDLING)
add_definitions (-DELPP_NO_DEFAULT_LOG_FILE)

add_definitions(-DELPP_SYSLOG)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES src/main.cpp src/context.cpp src/context.h src/operations.h src/operations.cpp src/event.h src/event.cpp)
add_executable(dsfs ${SOURCE_FILES})

target_link_libraries(dsfs pthread)
target_link_libraries(dsfs encfs)
target_link_libraries(dsfs fuse)
target_link_libraries(dsfs zmq)

