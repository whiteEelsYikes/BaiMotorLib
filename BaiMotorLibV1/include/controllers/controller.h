#ifndef _BAI_MOTOR_LIB_CONTROLLER_H_
#define _BAI_MOTOR_LIB_CONTROLLER_H_

#include <stdint.h>
#include "../drivers/drivers.h"

/* ============================
 * 控制器状态
 * ============================ */
typedef enum {
    CONTROLLER_STATE_IDLE = 0,     /* 未运行 */
    CONTROLLER_STATE_RUNNING,      /* 正常运行 */
    CONTROLLER_STATE_BRAKE,        /* 刹车中（输出应被抑制） */
    CONTROLLER_STATE_ERROR         /* 错误状态（可选） */
} ControllerState;


/*
 * Controller 是一个“策略模式”抽象：
 * - update() 是核心控制逻辑
 * - get_input() / put_output() 用于读取内部状态（调试、监控）
 * - params 保存公共参数（如 target）
 * - obj 保存控制器内部状态（如 PID 参数、误差、积分等）
 */
typedef struct Controller {

    void (*init)(struct Controller *self);  /* 初始化控制器（可选） */
    float (*execute)(struct Controller *self);  /* 控制器执行函数： 返回控制量（如 PWM、电流、扭矩）*/
    int (*get_input)(struct Controller *self);  /* 获取控制器内部输入状态（调试） */
    int (*put_output)(struct Controller *self);  /* 获取控制器输出状态（调试） */
    void (*set_brake)(struct Controller *self, MotorBrakeMode mode);  /* 设置刹车模式 */
    void *obj;  /* 控制器内部对象（PID 参数、误差、积分等） */
    ControllerState state;  /* 控制器状态 */
    float target;   /* 控制器目标值（所有控制器必备） */
    uint32_t update_period_ms; /* 控制器更新周期 */ 
    uint32_t last_update_tick; /* 上次更新时间 */
} Controller;


/* ============================
 * 通用控制器工具函数
 * ============================ */
void controller_process(Controller *ctrl, uint32_t now_ms);  /* MotorManager 调度时调用的统一处理函数 */ 

#endif
