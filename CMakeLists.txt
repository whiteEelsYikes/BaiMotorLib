cmake_minimum_required(VERSION 3.10)
project(BaiMotorLibTest C)

set(CMAKE_C_STANDARD 11)

include_directories(BEFORE
    BaiMotorLib/drivers
)

include_directories(
    BaiMotorLib/drivers
    BaiMotorLib/common/include
    BaiMotorLib/controllers
    BaiMotorLib/controllers/openloop
    BaiMotorLib/drivers/dc_motor/test_drv
    BaiMotorLib/drivers/sensors/test_drv
)

file(GLOB DRIVER_SRCS
    BaiMotorLib/drivers/*.c
    BaiMotorLib/drivers/dc_motor/test_drv/*.c
    BaiMotorLib/drivers/sensors/test_drv/*.c
)

file(GLOB COMMON_SRCS
    BaiMotorLib/common/*.c
)

file(GLOB CONTROLLER_SRCS
    BaiMotorLib/controllers/*.c
    BaiMotorLib/controllers/**/*.c
)

add_library(bai_motor_lib STATIC
    ${DRIVER_SRCS}
    ${COMMON_SRCS}
    ${CONTROLLER_SRCS}
)

add_executable(test main.c)
target_link_libraries(test bai_motor_lib)
