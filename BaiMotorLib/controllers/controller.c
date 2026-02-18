#include "controller.h"
#include "../common/include/motorlib_time_sys.h"
#include <stdlib.h>

/* ============================
 * 初始化控制器配置
 * ============================ */
void controller_config_init(Controller *ctrl, uint32_t period_ms) {
    if (!ctrl) return;

    if (!ctrl->params) {
        ctrl->params = (ControllerParams *)malloc(sizeof(ControllerParams));
        ctrl->params->target = 0.0f;
        ctrl->params->last_update_tick = 0;
    }

    ctrl->params->update_period_ms = period_ms;
    ctrl->params->last_update_tick = 0;
}

/* ============================
 * MotorManager 调度时调用的统一处理函数
 * - 判断周期是否到达
 * - 调用控制器 update()
 * ============================ */
void controller_process(Controller *ctrl, uint32_t now_ms) {
    // if (!ctrl || !ctrl->update) return ;
    // if (!ctrl->params) return ;

    /* 如果没有配置周期，默认立即更新 */
    if (ctrl->params->update_period_ms == 0) {
        ctrl->update(ctrl);
        return;
    }

    /* 判断周期是否到达 */
    if (now_ms - ctrl->params->last_update_tick < ctrl->params->update_period_ms) {
        return; /* 周期未到，不更新 */
    }

    ctrl->params->last_update_tick = now_ms;

    ctrl->update(ctrl);
}
