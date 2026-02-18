#include "test_drv.h"
#include "controller.h"
#include "openloop.h"
#include "motor.h"
#include <stdio.h>

int main() {
    TestMotorHW hw = { .pwm_ch = 1, .dir_pin = 2 };
    MotorDriver drv = TestMotorDriver_Create(&hw);

    drv.init(&drv);
    drv.set_direction(&drv, MOTOR_DIR_FORWARD);
    drv.set_target(&drv, 0.75f);
    drv.brake(&drv, MOTOR_BRAKE_SOFTWARE);
    drv.set_target(&drv, 0.0f);

    // Motor motor = { .driver = &drv, .controller = TestController_Create(1.0f, 0.1f, 0.05f) };
    // motor_update(&motor);  // Just to check compilation


    Controller c = OpenLoopController_Create();
    c.init(&c);

    float out = c.update(&c, 0.75f, 0.0f);
    printf("output = %.2f\n", out);

    printf("input = %d\n", c.get_input(&c));
    printf("put_output = %d\n", c.put_output(&c));

    return 0;
}
