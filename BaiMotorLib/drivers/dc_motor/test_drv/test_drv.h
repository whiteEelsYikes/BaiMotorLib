#ifndef _BAI_MOTOR_LIB_TEST_DRV_H_
#define _BAI_MOTOR_LIB_TEST_DRV_H_

#include "../../drivers/drivers.h"

/* 测试硬件结构体（模拟 PWM、方向、速度） */
typedef struct {
    float pwm_output;
    float speed_feedback;
} TestMotorHW;

/* 创建测试驱动器 */
Driver TestDriver_Create(TestMotorHW *hw);

#endif
