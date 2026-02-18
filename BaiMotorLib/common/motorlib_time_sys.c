#include "motorlib_time_sys.h"

static volatile uint32_t tick_ms   = 0;
static volatile uint32_t tick_sec  = 0;
static volatile uint32_t tick_min  = 0;
static volatile uint32_t tick_hour = 0;

void motorlib_time_sys_init(void) {
    tick_ms   = 0;
    tick_sec  = 0;
    tick_min  = 0;
    tick_hour = 0;
}

void motorlib_time_sys_tick_inc(void) {
    tick_ms++;

    if (tick_ms >= 1000) {
        tick_ms = 0;
        tick_sec++;

        if (tick_sec >= 60) {
            tick_sec = 0;
            tick_min++;

            if (tick_min >= 60) {
                tick_min = 0;
                tick_hour++;
            }
        }
    }
}

uint32_t motorlib_time_sys_get_ms(void) {
    return tick_ms;
}

uint32_t motorlib_time_sys_get_sec(void) {
    return tick_sec;
}

motorlib_time_t motorlib_time_sys_get_time(void) {
    motorlib_time_t t;

    t.ms   = tick_ms;
    t.sec  = tick_sec;
    t.min  = tick_min;
    t.hour = tick_hour;

    return t;
}
