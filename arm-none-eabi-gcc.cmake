cmake_minimum_required(VERSION 3.6)

set(CMAKE_CROSSCOMPILING TRUE)
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
set(CMAKE_COLOR_DIAGNOSTICS TRUE)

set(TOOLCHAIN_PREFIX "arm-none-eabi-")
if(WIN32)
    set(TOOLCHAIN_SUFFIX ".exe")
else()
    set(TOOLCHAIN_SUFFIX "")
endif()

if(NOT DEFINED TOOLCHAIN_PATH)
    find_program(TOOLCHAIN_PATH "${TOOLCHAIN_PREFIX}gcc${TOOLCHAIN_SUFFIX}" NO_CACHE)
    if(NOT TOOLCHAIN_PATH)
        message(FATAL_ERROR "arm-none-eabi-gcc toolchain not found.")
    endif()
    get_filename_component(TOOLCHAIN_PATH ${TOOLCHAIN_PATH} DIRECTORY)
endif()

set(CMAKE_ASM_COMPILER ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}gcc${TOOLCHAIN_SUFFIX})
set(CMAKE_C_COMPILER   ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}gcc${TOOLCHAIN_SUFFIX})
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}g++${TOOLCHAIN_SUFFIX})
set(CMAKE_AR           ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}gcc-ar${TOOLCHAIN_SUFFIX})
set(CMAKE_RANLIB       ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}gcc-ranlib${TOOLCHAIN_SUFFIX})
set(CMAKE_OBJCOPY      ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}objcopy${TOOLCHAIN_SUFFIX})
set(CMAKE_SIZE         ${TOOLCHAIN_PATH}/${TOOLCHAIN_PREFIX}size${TOOLCHAIN_SUFFIX})

set(CMAKE_EXECUTABLE_SUFFIX_C   .elf)
set(CMAKE_EXECUTABLE_SUFFIX_CXX .elf)
set(CMAKE_EXECUTABLE_SUFFIX_ASM .elf)

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

function(toolchain_set_flags_init)
    set(OPTIONS 
            THUMB 
            OPTIMIZE_DATA_SECTIONS 
            OPTIMIZE_FUNCTION_SECTIONS 
            OPTIMIZE_CXX_NO_RTTI 
            OPTIMIZE_CXX_NO_EXCEPTIONS 
            SPEC_NOSYS 
            SPEC_NONE 
            SPEC_RDIMON)
    set(ONE_VALUE_ARGS 
            CPU)
    set(MULTI_VALUE_ARGS 
            LANGUAGES 
            FLAGS)
    cmake_parse_arguments(PARAM "${OPTIONS}" "${ONE_VALUE_ARGS}" "${MULTI_VALUE_ARGS}" ${ARGN})

    set(ALLOWED_LANGUAGES C CXX ASM)

    # message(STATUS "LANGUAGES: ${PARAM_LANGUAGES}")
    foreach(LANG ${PARAM_LANGUAGES})
        if(NOT (${LANG} IN_LIST ALLOWED_LANGUAGES))
            message(FATAL_ERROR "LANGUAGE ${LANG} should in C CXX ASM")
        endif()
        set(FLAGS ${PARAM_FLAGS})
        if(PARAM_THUMB)
            set(FLAGS "${FLAGS} -mthumb")
        endif()
        if(PARAM_OPTIMIZE_DATA_SECTIONS)
            set(FLAGS "${FLAGS} -ffdata-sections")
        endif()
        if(PARAM_OPTIMIZE_FUNCTION_SECTIONS)
            set(FLAGS "${FLAGS} -ffunction-sections")
        endif()
        if(PARAM_OPTIMIZE_CXX_NO_RTTI AND ${LANG} STREQUAL "CXX")
            set(FLAGS "${FLAGS} -fno-rtti")
        endif()
        if(PARAM_OPTIMIZE_CXX_NO_EXCEPTIONS AND ${LANG} STREQUAL "CXX")
            set(FLAGS "${FLAGS} -fno-exceptions")
        endif()

        if(PARAM_SPEC_NOSYS)
            set(FLAGS "${FLAGS} --specs=nosys.specs")
        endif()
        if(PARAM_SPEC_NONE)
            set(FLAGS "${FLAGS} --specs=none.specs")
        endif()
        if(PARAM_SPEC_RDIMON)
            set(FLAGS "${FLAGS} --specs=rdimon.specs")
        endif()

        if(PARAM_CPU)
            set(FLAGS "${FLAGS} --mcpu=${PARAM_CPU}")
        endif()
        
        set(CMAKE_${LANG}_FLAGS_INIT "${FLAGS}" PARENT_SCOPE)
    endforeach()
endfunction()

function(toolchain_set_linker_flags_init)
    set(OPTIONS
            GC_SECTIONS
            PRINT_MEMORY_USAGE)
    set(MULTI_VALUE_ARGS
            FLAGS)
    cmake_parse_arguments(PARAM "${OPTIONS}" "" "${MULTI_VALUE_ARGS}" ${ARGN})

    set(FLAGS ${PARAM_FLAGS})
    
    if(PARAM_GC_SECTIONS)
        set(FLAGS "${FLAGS} -Wl,--gc-sections")
    endif()
    if(PARAM_PRINT_MEMORY_USAGE)
        set(FLAGS "${FLAGS} -Wl,--print-memory-usage")
    endif()

    set(CMAKE_EXE_LINKER_FLAGS_INIT "${FLAGS}" PARENT_SCOPE)
endfunction()