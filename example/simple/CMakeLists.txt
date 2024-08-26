cmake_minimum_required(VERSION 3.20)

set(CMAKE_TOOLCHAIN_FILE ../../arm-none-eabi-gcc.cmake)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)

project(simple LANGUAGES ASM C)

# apply flags to global only if your project support one cpu type(cortex-m33)
add_compile_options(
        -mthumb -mcpu=cortex-m33
        --specs=nano.specs --specs=nosys.specs
        -fdata-sections -ffunction-sections
)
add_link_options(
        -mthumb -mcpu=cortex-m33
        --specs=nano.specs --specs=nosys.specs
        -Wl,--gc-sections
)

# set SDK path and device, you can set it when configure project to avoid set in CMakeLists.txt
# eg: cmake -S . -B build -DMCUXPRESSO_SDK_PATH=path/to/sdk -DMCUXPRESSO_SDK_DEVICE_PACKAGE MCXN947VDF
#
# set(MCUXPRESSO_SDK_PATH path/to/SDK)
# set(MCUXPRESSO_SDK_DEVICE_PACKAGE MCXN947VDF)
find_package(MCUXpressoSDK REQUIRED)

add_executable(simple)
target_sources(simple PRIVATE main.c)
set(drivers common common_arm clock spc reset)
target_link_libraries(simple
    PUBLIC
        MCUXpressoSDK::CMSIS
        MCUXpressoSDK::Device::cm33_core0
        MCUXpressoSDK::Linker::cm33_core0::flash
        MCUXpressoSDK::Startup::cm33_core0
        MCUXpressoSDK::Syscall
)
foreach (driver IN LISTS drivers)
    target_link_libraries(simple PUBLIC MCUXpressoSDK::Drivers::${driver})
endforeach ()

generate_hex(simple)
generate_bin(simple)
