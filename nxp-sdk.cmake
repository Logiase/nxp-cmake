cmake_minimum_required(VERSION 3.19)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(_NXP_SDK_PYTHON_SCRIPT_PATH ${CMAKE_CURRENT_LIST_DIR}/nxp_sdk_parser.py)

function(nxp_sdk)
    set(ONE_VALUE_ARGS SDK_ROOT DEVICE OUTPUT)
    set(MULTI_VALUE_ARGS DRIVERS)
    cmake_parse_arguments(PARAM "" "${ONE_VALUE_ARGS}" "${MULTI_VALUE_ARGS}" ${ARGN})

    # set(COMMAND ${Python3_EXECUTABLE} ${_NXP_SDK_PYTHON_SCRIPT_PATH} --sdk_root ${PARAM_SDK_ROOT} --drivers ${PARAM_DRIVERS})
    # if(PARAM_DEVICE)
    #     set(COMMAND ${COMMAND} --device ${PARAM_DEVICE})
    # endif()

    set(COMMAND ${Python3_EXECUTABLE} ${_NXP_SDK_PYTHON_SCRIPT_PATH} --sdk_root ${PARAM_SDK_ROOT})
    if(PARAM_DEVICE)
        set(COMMAND ${COMMAND} --device ${PARAM_DEVICE})
    endif()
    set(COMMAND ${COMMAND} sources ${PARAM_DRIVERS})

    execute_process(
        COMMAND ${COMMAND}
        COMMAND_ECHO STDERR
        OUTPUT_VARIABLE STDOUT_RESULT
        COMMAND_ERROR_IS_FATAL ANY
    )
    string(STRIP "${STDOUT_RESULT}" STDOUT_RESULT)
    set(${PARAM_OUTPUT} ${STDOUT_RESULT} PARENT_SCOPE)
endfunction()

function(nxp_sdk_device_dir)
    set(ONE_VALUE_ARGS SDK_ROOT DEVICE VARIABLE)
    cmake_parse_arguments(PARAM "" "${ONE_VALUE_ARGS}" "" ${ARGN})
    if(NOT PARAM_VARIABLE)
        message(FATAL_ERROR "VARIABLE not defined")
        return()
    endif()
    if(NOT ${PARMA_SDK_ROOT})
        message(FATAL_ERROR "SDK_ROOT not defined")
    endif()

    if(PARAM_DEVICE)
        if(IS_DIRECTORY "${PARAM_SDK_ROOT}/devices/${PARAM_DEVICE}")
            set(${PARAM_VARIABLE} "${PARAM_SDK_ROOT}/devices/${PARAM_DEVICE}" PARENT_SCOPE)
            return()
        endif()
        message(FATAL_ERROR "${PARAM_SDK_ROOT}/devices/${PARAM_DEVICE} is not a directory")
    endif()

    file(GLOB SUBS "${PARAM_SDK_ROOT}/devices/*")
    list(LENGTH SUBS SUBS_LEN)
    list(GET SUBS 0 DIR)
    if(NOT(${SUBS_LEN} STREQUAL "1"))
        message(WARNING "multi device found, use first")
    endif()
    set(${PARAM_VARIABLE} ${DIR} PARENT_SCOPE)
endfunction()
