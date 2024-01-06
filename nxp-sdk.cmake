find_package(Python3 REQUIRED COMPONENTS Interpreter)

function(nxp_sdk)
    set(ONE_VALUE_ARGS SDK_ROOT VARIABLE)
    set(MULTI_VALUE_ARGS DRIVERS)
    cmake_parse_arguments(PARAM "" "${ONE_VALUE_ARGS}" "${MULTI_VALUE_ARGS}" ${ARGN})
    execute_process(
        COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/nxp_sdk_parser.py --sdk_root ${PARAM_SDK_ROOT} ${PARAM_DRIVERS}
        COMMAND_ECHO STDERR
        OUTPUT_VARIABLE STDOUT_RESULT
    )
    set(${PARAM_VARIABLE} ${STDOUT_RESULT} PARENT_SCOPE)
endfunction()
