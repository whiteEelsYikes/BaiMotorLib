#ifndef _MOTORLIB_MOTOR_MANAGER_H_
#define _MOTORLIB_MOTOR_MANAGER_H_

#include "motor.h"

#define MOTOR_MANAGER_MAX_MOTORS  8

typedef struct {
    Motor *motors[MOTOR_MANAGER_MAX_MOTORS];
    int motor_count;

    uint32_t update_period_ms;   /* 每隔多少 ms 调用 motor_update */
    uint32_t last_update_tick;   /* 上次更新时间 */
} MotorManager;

/* 初始化管理器 */
void motor_manager_init(MotorManager *mgr, uint32_t period_ms);

/* 添加电机 */
int motor_manager_add(MotorManager *mgr, Motor *m);

/* 在主循环中周期性调用 */
void motor_manager_process(MotorManager *mgr);

#endif
