#include "motor.h"

void motor_init(Motor *m) {
    if (!m) return;
    if (m->driver && m->driver->motor.init) {
        m->driver->motor.init(&m->driver->motor);
    }
    if (m->driver && m->driver->sensor.init) {
        m->driver->sensor.init(&m->driver->sensor);
    }
    if (m->controller.init) {
        m->controller.init(&m->controller);
    }
    m->controller.state = CONTROLLER_STATE_IDLE;
}

void motor_set_target(Motor *m, float target) {
    if (!m || !m->controller.params) return;
    m->controller.params->target = target;
}

void motor_update(Motor *m) {
    if (!m) return;

    float output = 0.0f;
    if (m->controller.update) {
        output = m->controller.update(&m->controller);
    }

    if (m->controller.state == CONTROLLER_STATE_BRAKE) {
        if (m->driver && m->driver->motor.brake) {
            m->driver->motor.brake(&m->driver->motor, MOTOR_BRAKE_HARDWARE);
        }
    } else {
        if (m->driver && m->driver->motor.set_target) {
            m->driver->motor.set_target(&m->driver->motor, output);
        }
    }
}
