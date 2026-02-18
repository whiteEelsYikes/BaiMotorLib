#include "test_drv.h"
#include <stddef.h>

/* ============================
 * 电机驱动接口实现
 * ============================ */

static void test_motor_init(MotorDriver *self) {
    TestMotorHW *hw = (TestMotorHW *)self->hw;
    hw->pwm_output = 0.0f;
}

static void test_motor_set_target(MotorDriver *self, float pwm) {
    TestMotorHW *hw = (TestMotorHW *)self->hw;
    hw->pwm_output = pwm;
}

static void test_motor_brake(MotorDriver *self, MotorBrakeMode mode) {
    TestMotorHW *hw = (TestMotorHW *)self->hw;
    hw->pwm_output = 0.0f;
}

/* ============================
 * 传感器接口实现
 * ============================ */

static void test_sensor_init(SensorDriver *self) {
    TestMotorHW *hw = (TestMotorHW *)self->hw;
    hw->speed_feedback = 0.0f;
}

static float test_sensor_get_speed(SensorDriver *self) {
    TestMotorHW *hw = (TestMotorHW *)self->hw;

    /* 模拟速度 = pwm_output * 常数 */
    hw->speed_feedback = hw->pwm_output * 100.0f;
    return hw->speed_feedback;
}

/* ============================
 * 创建测试驱动器
 * ============================ */
Driver TestDriver_Create(TestMotorHW *hw) {

    MotorDriver motor = {
        .init       = test_motor_init,
        .set_target = test_motor_set_target,
        .brake      = test_motor_brake,
        .hw        = hw
    };

    SensorDriver sensor = {
        .init       = test_sensor_init,
        .get_speed  = test_sensor_get_speed,
        .hw        = hw
    };

    Driver d = {
        .motor  = motor,
        .sensor = sensor
    };

    return d;
}
