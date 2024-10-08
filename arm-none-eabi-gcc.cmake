cmake_minimum_required(VERSION 3.6)

set(CMAKE_CROSSCOMPILING ON)
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
set(CMAKE_COLOR_DIAGNOSTICS ON)

if (NOT DEFINED TOOLCHAIN_PREFIX)
    set(TOOLCHAIN_PREFIX "arm-none-eabi-")
endif ()
if (NOT DEFINED TOOLCHAIN_SUFFIX)
    set(TOOLCHAIN_SUFFIX "")
endif ()
if (NOT DEFINED TOOLCHAIN_PATH)
    find_program(TOOLCHAIN_PATH "${TOOLCHAIN_PREFIX}gcc${TOOLCHAIN_SUFFIX}" NO_CACHE)
    if (NOT TOOLCHAIN_PATH)
        message(FATAL_ERROR "arm-none-eabi-gcc toolchain not found!")
    endif ()
    get_filename_component(TOOLCHAIN_PATH "${TOOLCHAIN_PATH}" DIRECTORY)
endif ()
if (WIN32)
    set(TOOLCHAIN_EXT_NAME ".exe")
else ()
    set(TOOLCHAIN_EXT_NAME "")
endif ()

set(CMAKE_ASM_COMPILER ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}gcc${TOOLCHAIN_SUFFIX}${TOOLCHAIN_EXT_NAME})
set(CMAKE_C_COMPILER ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}gcc${TOOLCHAIN_SUFFIX}${TOOLCHAIN_EXT_NAME})
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}g++${TOOLCHAIN_SUFFIX}${TOOLCHAIN_EXT_NAME})
set(CMAKE_AR ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}gcc-ar${TOOLCHAIN_SUFFIX}${TOOLCHAIN_EXT_NAME})
set(CMAKE_RANLIB ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}gcc-ranlib${TOOLCHAIN_SUFFIX}${TOOLCHAIN_EXT_NAME})
set(CMAKE_OBJCOPY ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}objcopy${TOOLCHAIN_SUFFIX}${TOOLCHAIN_EXT_NAME})
set(CMAKE_SIZE ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}size${TOOLCHAIN_SUFFIX}${TOOLCHAIN_EXT_NAME})

set(CMAKE_EXECUTABLE_SUFFIX .elf)
set(CMAKE_EXECUTABLE_SUFFIX_ASM .elf)
set(CMAKE_EXECUTABLE_SUFFIX_C .elf)
set(CMAKE_EXECUTABLE_SUFFIX_CXX .elf)

execute_process(
        COMMAND ${CMAKE_C_COMPILER} --print-sysroot
        OUTPUT_VARIABLE TOOLCHAIN_SYSROOT
        OUTPUT_STRIP_TRAILING_WHITESPACE
)
set(CMAKE_SYSROOT ${TOOLCHAIN_SYSROOT})
set(CMAKE_FIND_ROOT_PATH ${TOOLCHAIN_PATH})
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})

function(generate_hex TARGET)
    add_custom_command(
            TARGET ${TARGET}
            POST_BUILD
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            COMMAND ${CMAKE_OBJCOPY} ARGS -O ihex $<TARGET_FILE:${TARGET}> $<TARGET_NAME:${TARGET}>.hex
    )
endfunction()

function(generate_bin TARGET)
    add_custom_command(
            TARGET ${TARGET}
            POST_BUILD
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            COMMAND ${CMAKE_OBJCOPY} ARGS -O binary $<TARGET_FILE:${TARGET}> $<TARGET_NAME:${TARGET}>.bin
    )
endfunction()