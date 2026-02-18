#include <stdio.h>

#include "motorlib_time_sys.h"
#include "motor_manager.h"

#include "motor.h"
#include "openloop.h"
#include "test_drv.h"

int main(void)
{
    /* 初始化 motorlib 时间系统 */
    motorlib_time_sys_init();

    /* 创建测试硬件对象 */
    TestMotorHW hw = {0};

    /* 创建驱动器 */
    Driver driver = TestDriver_Create(&hw);

    /* 创建开环控制器 */
    Controller ctrl = OpenLoopController_Create();

    /* 创建 Motor 对象 */
    Motor motor = {
        .driver = &driver,
        .controller = ctrl,
        .brake_mode = MOTOR_BRAKE_NONE
    };

    /* 初始化 Motor */
    motor_init(&motor);

    /* 创建 MotorManager，每 10ms 更新一次电机 */
    MotorManager mgr;
    motor_manager_init(&mgr, 10);
    motor_manager_add(&mgr, &motor);

    /* 设置目标值 */
    motor_set_target(&motor, 3.5f);

    printf("motorlib demo start\n");

    /* 主循环 */
    while (1) {

        /* 模拟 1ms tick（真实系统中由 SysTick 中断调用） */
        motorlib_time_sys_tick_inc();

        /* 调度电机更新 */
        motor_manager_process(&mgr);

        /* 打印调试信息（每 100ms 打印一次） */
        static uint32_t last_print = 0;
        uint32_t now = motorlib_time_sys_get_ms();

        if (now - last_print >= 100) {
            last_print = now;

            printf("[time %02u:%02u:%02u.%03u] pwm=%.2f speed=%.2f\n",
                   motorlib_time_sys_get_time().hour,
                   motorlib_time_sys_get_time().min,
                   motorlib_time_sys_get_time().sec,
                   motorlib_time_sys_get_time().ms,
                   hw.pwm_output,
                   hw.speed_feedback);
        }
        
    }

    return 0;
}
