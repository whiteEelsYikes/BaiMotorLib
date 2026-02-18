#ifndef _BAI_MOTOR_LIB_DRIVERS_H_
#define _BAI_MOTOR_LIB_DRIVERS_H_

#include <stdint.h>

/* ============================
 * 电机方向
 * ============================ */
typedef enum {
    MOTOR_DIR_FORWARD = 0,
    MOTOR_DIR_BACKWARD
} MotorDirection;

/* ============================
 * 刹车模式
 * ============================ */
typedef enum {
    MOTOR_BRAKE_NONE = 0,
    MOTOR_BRAKE_SOFTWARE,
    MOTOR_BRAKE_HARDWARE
} MotorBrakeMode;

/* ============================
 * MotorDriver 抽象接口
 * ============================ */
typedef struct MotorDriver {
    void (*init)(struct MotorDriver *self);
    void (*set_target)(struct MotorDriver *self, float target);
    void (*set_direction)(struct MotorDriver *self, MotorDirection dir);
    void (*brake)(struct MotorDriver *self, MotorBrakeMode mode);
    void *hw;
} MotorDriver;

/* ============================
 * SensorDriver 抽象接口
 * ============================ */
typedef struct SensorDriver {
    void (*init)(struct SensorDriver *self);
    int (*update)(struct SensorDriver *self);
    float (*get_speed)(struct SensorDriver *self);
    float (*get_position)(struct SensorDriver *self);
    float (*get_current)(struct SensorDriver *self);
    float (*get_voltage)(struct SensorDriver *self);
    void *hw;
} SensorDriver;

/* ============================
 * 统一 Driver 抽象
 * ============================ */
typedef struct Driver {
    MotorDriver motor;     // 电机驱动
    SensorDriver sensor;   // 传感器驱动
} Driver;

#endif
