#include "motor_manager.h"
#include "include/motorlib_time_sys.h"
#include "../controllers/controller.h"


void motor_manager_init(MotorManager *mgr, uint32_t period_ms) {
    mgr->motor_count = 0;
    mgr->update_period_ms = period_ms;
    mgr->last_update_tick = 0;
}

int motor_manager_add(MotorManager *mgr, Motor *m) {
    if (mgr->motor_count >= MOTOR_MANAGER_MAX_MOTORS)
        return -1;

    mgr->motors[mgr->motor_count++] = m;
    return 0;
}

void motor_manager_process(MotorManager *mgr) {
    uint32_t now = motorlib_time_sys_get_ms();

    for (int i = 0; i < mgr->motor_count; i++) {
        Motor *m = mgr->motors[i];

        /* 调用通用控制器处理函数 */
        controller_process(&m->controller, now);

        if (m->controller.state == CONTROLLER_STATE_BRAKE) {
            if (m->driver && m->driver->motor.brake) {
                m->driver->motor.brake(&m->driver->motor, MOTOR_BRAKE_HARDWARE);
            }
        }
    }
}
