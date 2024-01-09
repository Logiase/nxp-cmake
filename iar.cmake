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

function(toolchain_elf_to_hex TARGET)
    add_custom_command(
        TARGET ${TARGET}
        COMMAND ${CMAKE_ELFTOOL} --silent --ihex $<TARGET_FILE:${TARGET}> $<IF:$<BOOL:$<TARGET_PROPERTY:${TARGET}, OUTPUT_NAME>>, $<TARGET_PROPERTY:${TARGET}, OUTPUT_NAME>, $<TARGET_PROPERTY:${TARGET}, NAME>>.hex
        POST_BUILD
    )
endfunction()

function(toolchain_elf_to_bin TARGET)
    add_custom_command(
        TARGET ${TARGET}
        COMMAND ${CMAKE_ELFTOOL} --silent --bin $<TARGET_FILE:${TARGET}> $<IF:$<BOOL:$<TARGET_PROPERTY:${TARGET}, OUTPUT_NAME>>, $<TARGET_PROPERTY:${TARGET}, OUTPUT_NAME>, $<TARGET_PROPERTY:${TARGET}, NAME>>.bin
        POST_BUILD
    )
endfunction()

function(toolchain_elf_to_hex TARGET)
    add_custom_command(
        TARGET ${TARGET}
        COMMAND ${CMAKE_ELFTOOL} --silent --srec $<TARGET_FILE:${TARGET}> $<IF:$<BOOL:$<TARGET_PROPERTY:${TARGET}, OUTPUT_NAME>>, $<TARGET_PROPERTY:${TARGET}, OUTPUT_NAME>, $<TARGET_PROPERTY:${TARGET}, NAME>>.srec
        POST_BUILD
    )
endfunction()