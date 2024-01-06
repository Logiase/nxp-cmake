# Logiase's CMake Utils

A collection of cmake files for better embedded development

## Introduction

This repo contains some helpful cmake script and tools.
Including `arm-none-eabi-gcc` toolchain, NXP MCUX sdk helper.

## Usage

Just cloen this repo into your project, for example:
`$ git submodule add https://github.com/Logiase/cmake_utils.git cmake`.
Then include needed cmake file.

### arm-none-eabi-gcc toolchain

This cmake script helps setting `arm-none-eabi-gcc` toolchain, and create some functions
to help user set common compile and link flags.

User should use **set** `set(CMAKE_TOOLCHAIN_FILE "cmake/arm-none-eabi-gcc.cmake")` in main `CMakeLists.txt`,
but not **include**.

### NXP MCUX SDK helper

This cmake script helps resolve NXP MCUX sdk drivers' dependencies.

```cmake
# ...

include("cmake/nxp-sdk.cmake")
set(NXP_SDK_ROOT "path/to/sdk") # please put only one device in SDK
set(NXP_SDK_DRIVERS common power flexcomm_usart)
nxp_sdk(
    VARIABLE NXP_SDK_DRIVER_SRCS
    SDK_ROOT ${NXP_SDK_ROOT}
    DRIVERS ${NXP_SDK_DRIVERS}
)
# Now needed sources are stored in variable NXP_SDK_DRIVER_SRCS
# add them to your target, do not forget to include
target_sources(your_target
    PRIVATE # or PUBLIC or INTERFACE
        ${NXP_SDK_DRIVER_SRCS}
)

# ...
```