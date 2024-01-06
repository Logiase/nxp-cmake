cmake_minimum_required(VERSION 3.20)

set(NXP_SDK_ROOT "C:\\Users\\Logiase\\Documents\\MCUXpressoSDK\\MCXN947_2_13_1")

set(CMAKE_TOOLCHAIN_FILE "../../arm-none-eabi-gcc.cmake")

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED TRUE)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

project(nxp_dualcore_exmaple C CXX ASM)

toolchain_set_flags(
    LANGUAGES C CXX ASM
    THUMB OPTIMIZE_DATA_SECTIONS OPTIMIZE_FUNCTION_SECTIONS OPTIMIZE_CXX_NO_EXCEPTIONS OPTIMIZE_CXX_NO_RTTI
)
toolchain_set_linker_flags(GC_SECTIONS PRINT_MEMORY_USAGE)

include("../../nxp-sdk.cmake")
nxp_sdk_device_dir(
    SDK_ROOT ${NXP_SDK_ROOT}
    VARIABLE DEVICE_DIR
)
set(COMMON_INCLUDE_DIRS
    "${NXP_SDK_ROOT}/CMSIS/Core/Include"
    "${DEVICE_DIR}"
    "${DEVICE_DIR}/drivers"
)

add_library(core0_flags INTERFACE)
target_compile_options(core0_flags
    INTERFACE
        -mcpu=cortex-m33 -mfpu=auto --specs=nano.specs --specs=nosys.specs
)

add_library(core1_flags INTERFACE)
target_compile_options(core1_flags
    INTERFACE
        -mcpu=cortex-m33+nodsp+nofp -mfpu=auto --specs=nano.specs --specs=nosys.specs
)

add_executable(core0)
add_subdirectory(core0)

add_executable(core1)
add_subdirectory(core1)

# This library is used for core0
add_library(lib1)
add_subdirectory(lib1)
target_link_libraries(lib1 core0_flags)

target_link_libraries(core0 core0_flags lib1)
target_link_libraries(core1 core1_flags)