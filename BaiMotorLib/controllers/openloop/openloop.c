#include "openloop.h"
#include <stdlib.h>

/* 开环控制器内部对象 */
typedef struct {
    float last_input;
    float last_output;
} OpenLoopObj;

/* 初始化函数 */
static void openloop_init(Controller *self) {
    OpenLoopObj *obj = (OpenLoopObj *)self->obj;
    if (!obj) return;

    obj->last_input = 0.0f;
    obj->last_output = 0.0f;
    self->state = CONTROLLER_STATE_IDLE;
}

/* 更新函数：直接输出 target */
static float openloop_update(Controller *self) {
    OpenLoopObj *obj = (OpenLoopObj *)self->obj;
    if (!obj || !self->params) return 0.0f;

    if (self->state == CONTROLLER_STATE_BRAKE) {
        obj->last_output = 0.0f;
        return 0.0f;
    }

    self->state = CONTROLLER_STATE_RUNNING;

    obj->last_input  = self->params->target;
    obj->last_output = self->params->target;
    return obj->last_output;
}

/* 设置刹车模式 */
static void openloop_set_brake(Controller *self, MotorBrakeMode mode) {
    if (mode == MOTOR_BRAKE_NONE) {
        self->state = CONTROLLER_STATE_RUNNING;
    } else {
        self->state = CONTROLLER_STATE_BRAKE;
    }
}

/* 调试接口：获取输入 */
static int openloop_get_input(Controller *self) {
    OpenLoopObj *obj = (OpenLoopObj *)self->obj;
    return obj ? (int)(obj->last_input * 1000) : 0;
}

/* 调试接口：获取输出 */
static int openloop_put_output(Controller *self) {
    OpenLoopObj *obj = (OpenLoopObj *)self->obj;
    return obj ? (int)(obj->last_output * 1000) : 0;
}

/* 创建开环控制器 */
Controller OpenLoopController_Create(void) {
    Controller c;

    OpenLoopObj *obj = (OpenLoopObj *)malloc(sizeof(OpenLoopObj));
    ControllerParams *params = (ControllerParams *)malloc(sizeof(ControllerParams));

    obj->last_input = 0.0f;
    obj->last_output = 0.0f;

    params->target = 0.0f;
    params->update_period_ms = 0;   /* 默认立即更新 */
    params->last_update_tick = 0;

    c.init        = openloop_init;
    c.update      = openloop_update;
    c.get_input   = openloop_get_input;
    c.put_output  = openloop_put_output;
    c.set_brake   = openloop_set_brake;
    c.params      = params;
    c.obj         = obj;
    c.state       = CONTROLLER_STATE_IDLE;

    return c;
}
