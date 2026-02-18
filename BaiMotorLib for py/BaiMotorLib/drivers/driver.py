
class MotorDriver:
    MOTOR_DIR_FORWARD = 0
    MOTOR_DIR_BACKWARD = 1

    def __init__(self):
        pass
    def set_target(self):
        pass
    def set_direction(self):
        pass
    def brake(self):
        pass

class SensorDriver:
    def __init__(self):
        pass
    def update(self):
        pass
    def get_speed(self):
        pass
    def get_position(self):
        pass
    def get_current(self):
        pass
    def get_voltage(self):
        pass

class Driver:

    def __init__(self, motor_driver, sensor_driver):
        self.MotorDriver = MotorDriver
        self.SensorDriver = sensor_driver

