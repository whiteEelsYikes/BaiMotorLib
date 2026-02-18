#ifndef _BAI_MOTOR_LIB_OPENLOOP_H_
#define _BAI_MOTOR_LIB_OPENLOOP_H_

#include "../controller.h"

/*
 * 开环控制器（OpenLoop）
 * - 输出 = target
 * - 内部对象仅记录 last_input / last_output
 * - 目标值统一存放在 ControllerParams 中
 */

/* 创建一个开环控制器 */
Controller OpenLoopController_Create(void);

#endif
