nxp_sdk(
    SDK_ROOT ${NXP_SDK_ROOT}
    VARIABLE CORE_DRIVERS
    DRIVERS common
)

target_sources(core0
    PRIVATE
        main.c
        ${CORE0_DRIVERS}
        # board/pin_mux.c board/clock_config.c board/peripherals.c
        ${DEVICE_DIR}/system_MCXN947_cm33_core0.c
        ${DEVICE_DIR}/gcc/startup_MCXN947_cm33_core0.S
        ${CMAKE_SOURCE_DIR}/../../syscall_stub.c
)
target_include_directories(core0
    PRIVATE
        ${COMMON_INCLUDE_DIRS}
)
target_compile_definitions(core0
    PRIVATE
        CPU_MCXN947VDF_cm33_core0
)
target_link_options(core0
    PUBLIC
        -mcpu=cortex-m33 -mfpu=auto
        -T ${DEVICE_DIR}/gcc/MCXN947_cm33_core0_flash.ld
        --specs=nosys.specs --specs=nano.specs
)
