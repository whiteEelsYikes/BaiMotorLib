#include <stdio.h>
#include "motor.h"
#include "openloop.h"
#include "test_drv.h"

int main() {

    TestMotorHW hw = {0};

    Driver driver = TestDriver_Create(&hw);
    Controller ctrl = OpenLoopController_Create();

    Motor motor = {
        .driver = &driver,
        .controller = ctrl,
        .brake_mode = MOTOR_BRAKE_NONE
    };

    motor_init(&motor);

    motor_set_target(&motor, 0.5f);

    for (int i = 0; i < 5; i++) {
        motor_update(&motor);
        printf("loop %d: pwm = %.2f, speed = %.2f\n",
               i,
               hw.pwm_output,
               hw.speed_feedback);
    }

    motor_set_brake(&motor, MOTOR_BRAKE_SOFTWARE);
    motor_update(&motor);

    printf("after brake: pwm = %.2f\n", hw.pwm_output);

    return 0;
}
