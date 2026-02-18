#include "motor_manager.h"
#include "../common/motorlib_sys_time.h"

void motor_manager_process(MotorManager *mgr) {
    uint32_t now = motorlib_sys_time_get();

    if (now - mgr->last_update_tick < mgr->update_period_ms)
        return;

    mgr->last_update_tick = now;

    for (int i = 0; i < mgr->motor_count; i++) {
        motor_update(mgr->motors[i]);
    }
}
