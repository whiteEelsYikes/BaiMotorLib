#include <stdio.h>
#include <stdlib.h>
#include "motor.h"
#include "motor_manager.h"
#include "openloop.h"
#include "controller.h"
#include "drivers.h"
#include "motorlib_time_sys.h"

/* ====== 示例 MotorDriver 实现 ====== */
static void dummy_motor_init(struct MotorDriver *self) {
    printf("[Driver] Motor init\n");
}

static void dummy_motor_set_target(struct MotorDriver *self, float value) {
    printf("[Driver] Motor set target: %.2f\n", value);
}

static void dummy_motor_set_direction(struct MotorDriver *self, MotorDirection dir) {
    printf("[Driver] Motor set direction: %d\n", dir);
}

static void dummy_motor_brake(struct MotorDriver *self, MotorBrakeMode mode) {
    printf("[Driver] Motor brake mode: %d\n", mode);
}

/* ====== 示例 SensorDriver 实现 ====== */
static void dummy_sensor_init(struct SensorDriver *self) {
    printf("[Driver] Sensor init\n");
}

static int dummy_sensor_update(struct SensorDriver *self) {
    return 0; /* 示例返回值 */
}

static float dummy_sensor_get_speed(struct SensorDriver *self) {
    return 0.0f;
}

static float dummy_sensor_get_position(struct SensorDriver *self) {
    return 0.0f;
}

static float dummy_sensor_get_current(struct SensorDriver *self) {
    return 0.0f;
}

static float dummy_sensor_get_voltage(struct SensorDriver *self) {
    return 0.0f;
}

/* ====== 主程序入口 ====== */
int main(void) {
    /* 初始化时间系统 */
    motorlib_time_sys_init();

    /* 创建驱动器 */
    Driver driver = {
        .motor = {
            .init = dummy_motor_init,
            .set_target = dummy_motor_set_target,
            .set_direction = dummy_motor_set_direction,
            .brake = dummy_motor_brake,
            .hw = NULL
        },
        .sensor = {
            .init = dummy_sensor_init,
            .update = dummy_sensor_update,
            .get_speed = dummy_sensor_get_speed,
            .get_position = dummy_sensor_get_position,
            .get_current = dummy_sensor_get_current,
            .get_voltage = dummy_sensor_get_voltage,
            .hw = NULL
        }
    };

    /* 创建开环控制器 */
    Controller ctrl = OpenLoopController_Create();
    controller_config_init(&ctrl, 10);  /* 设置更新周期为 10ms */

    /* 创建电机对象 */
    Motor motor = {
        .driver = &driver,
        .controller = ctrl
    };

    /* 初始化电机 */
    motor_init(&motor);

    /* 创建 MotorManager */
    MotorManager mgr;
    motor_manager_init(&mgr, 10);  /* 设置调度周期为 10ms */
    motor_manager_add(&mgr, &motor);

    /* 设置目标值 */
    motor_set_target(&motor, 0.5f);

    /* 主循环 */
    while (1) {
        motor_manager_process(&mgr);
        motorlib_time_sys_tick_inc();

        // motorlib_time_sys_delay_ms(10); /* 模拟周期调度 */

        static uint32_t last_print = 0;
        uint32_t now = motorlib_time_sys_get_ms();

        if (now - last_print >= 100) {
            last_print = now;

            printf("[time %02u:%02u:%02u.%03u]\n",
                   motorlib_time_sys_get_time().hour,
                   motorlib_time_sys_get_time().min,
                   motorlib_time_sys_get_time().sec,
                   motorlib_time_sys_get_time().ms
                   );
        }
    }

    return 0;
}
