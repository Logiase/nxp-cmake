nxp_sdk(
    SDK_ROOT ${NXP_SDK_ROOT}
    VARIABLE CORE1_DRIVERS
    DRIVERS common
)

target_sources(core1
    PRIVATE
        main.c
        ${CORE1_DRIVERS}
        # board/pin_mux.c board/clock_config.c board/peripherals.c
        ${DEVICE_DIR}/system_MCXN947_cm33_core1.c
        ${DEVICE_DIR}/gcc/startup_MCXN947_cm33_core1.S
        ${CMAKE_SOURCE_DIR}/../../syscall_stub.c
)
target_include_directories(core1
    PRIVATE
        ${COMMON_INCLUDE_DIRS}
)
target_compile_definitions(core1
    PRIVATE
        CPU_MCXN947VDF_cm33_core1
)
target_link_options(core1
    PUBLIC
        -mcpu=cortex-m33+nodsp+nofp -mfpu=auto 
        -T ${DEVICE_DIR}/gcc/MCXN947_cm33_core1_flash.ld
        --specs=nosys.specs --specs=nano.specs
)
