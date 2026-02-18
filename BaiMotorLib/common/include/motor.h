#ifndef _BAI_MOTOR_LIB_MOTOR_H_
#define _BAI_MOTOR_LIB_MOTOR_H_

#include "../controllers/controller.h"
#include "../drivers/drivers.h"


/* ============================
 * 电机对象
 * ============================ */
typedef struct {
    Driver *driver;           /* 驱动器 */
    Controller controller;    /* 控制器 */
    MotorBrakeMode brake_mode;/* 刹车模式 */
} Motor;

/* ============================
 * 电机接口
 * ============================ */
void motor_init(Motor *m);
void motor_set_target(Motor *m, float target);
// void motor_set_brake(Motor *m, MotorBrakeMode mode);
void motor_update(Motor *m);

#endif
