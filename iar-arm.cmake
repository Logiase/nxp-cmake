# IAR Arm toolchain support
# some code copy from https://github.com/IARSystems/cmake-tutorial

message(STATUS "setting IAR")

set(CMAKE_CROSSCOMPILING TRUE)
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

find_program(CMAKE_C_COMPILER
    NAMES iccarm
    PATHS ${TOOLCHAIN_PATH}
          "$ENV{ProgramFiles}/IAR Systems/*"
          "$ENV{ProgramFiles\(x86\)}/IAR Systems/*"
          /opt/iarsystems/bxarm
    PATH_SUFFIXES bin arm/bin
    REQUIRED
)
set(CMAKE_CXX_COMPILER ${CMAKE_C_COMPILER})
find_program(CMAKE_ASM_COMPILER
    NAMES iasmarm aarm
    PATHS ${TOOLCHAIN_PATH}
          "$ENV{ProgramFiles}/IAR Systems/*"
          "$ENV{ProgramFiles\(x86\)}/IAR Systems/*"
          /opt/iarsystems/bxarm
    PATH_SUFFIXES bin arm/bin
    REQUIRED
)
find_program(CMAKE_ELFTOOL
    NAMES ielftool
    PATHS ${TOOLCHAIN_PATH}
          "$ENV{ProgramFiles}/IAR Systems/*"
          "$ENV{ProgramFiles\(x86\)}/IAR Systems/*"
          /opt/iarsystems/bxarm
    PATH_SUFFIXES bin arm/bin
    REQUIRED
)

set(CMAKE_EXECUTABLE_SUFFIX .elf)

function(_toolchain_elf_to TARGET TO OUTPUT_EXT)
    get_target_property(TARGET_OUTPUT_NAME ${TARGET} OUTPUT_NAME)
    if(TARGET_OUTPUT_NAME)
        set(OUTPUT_NAME "${TARGET_OUTPUT_NAME}.${OUTPUT_EXT}")
    else()
        set(OUTPUT_NAME "${TARGET}.${OUTPUT_EXT}")
    endif()

    get_target_property(RUNTIME_OUTPUT_DIRECTORY ${TARGET} RUNTIME_OUTPUT_DIRECTORY)
    if(RUNTIME_OUTPUT_DIRECTORY)
        set(OUTPUT_PATH "${RUNTIME_OUTPUT_DIRECTORY}/${OUTPUT_NAME}")
    else()
        set(OUTPUT_PATH "${OUTPUT_NAME}")
    endif()

    add_custom_command(
        TARGET ${TARGET}
        POST_BUILD
        COMMAND ${CMAKE_ELFTOOL} --silent --${TO} "$<TARGET_FILE:${TARGET}>" ${OUTPUT_PATH}
        BYPRODUCTS ${OUTPUT_PATH}
    )
endfunction()

function(toolchain_elf_to_hex TARGET)
    _toolchain_elf_to(${TARGET} ihex hex)
endfunction()

function(toolchain_elf_to_bin TARGET)
    _toolchain_elf_to(${TARGET} bin bin)
endfunction()

function(toolchain_elf_to_srec TARGET)
    _toolchain_elf_to(${TARGET} srec srec)
endfunction()
