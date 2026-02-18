#ifndef _MOTORLIB_TIME_SYS_H_
#define _MOTORLIB_TIME_SYS_H_

#include <stdint.h>

/*
 * motorlib 时间系统模块
 * - 内部维护毫秒、秒、分、时
 * - 提供毫秒 tick、秒计数和格式化时间
 * - 与平台无关，便于解耦与复用
 */

typedef struct {
    uint32_t ms;      /* 毫秒 [0, 999] */
    uint32_t sec;     /* 秒   [0, 59]  */
    uint32_t min;     /* 分   [0, 59]  */
    uint32_t hour;    /* 时   [0, ∞)   */
} motorlib_time_t;

/* 初始化时间系统 */
void motorlib_time_sys_init(void);

/* 每 1ms 调用一次（由 SysTick 或定时器中断触发） */
void motorlib_time_sys_tick_inc(void);

/* 获取当前毫秒（0~999） */
uint32_t motorlib_time_sys_get_ms(void);

/* 获取当前秒（0~59） */
uint32_t motorlib_time_sys_get_sec(void);

/* 获取格式化时间（时:分:秒:毫秒） */
motorlib_time_t motorlib_time_sys_get_time(void);

#endif
