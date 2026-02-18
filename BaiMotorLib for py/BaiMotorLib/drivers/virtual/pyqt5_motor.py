from BaiMotorLib.common.motor import Motor
from BaiMotorLib.drivers.driver import MotorDriver
from BaiMotorLib.common.constants import MotorDirection, MotorBrakeMode

class VirtualMotorDriver(MotorDriver):
    def __init__(self):
        super().__init__()
        self._target_speed = 0.0    # 目标转速（rpm）
        self._direction = MotorDirection.MOTOR_DIR_FORWARD  # 默认正转
        self._brake_mode = MotorBrakeMode.MOTOR_BRAKE_NONE  # 默认无刹车

    def set_target(self, speed):
        """设置目标转速，非负限制"""
        self._target_speed = max(0.0, speed)

    def set_direction(self, direction):
        """设置电机转向，仅支持预定义正/反转"""
        if direction in [MotorDirection.MOTOR_DIR_FORWARD, MotorDirection.MOTOR_DIR_BACKWARD]:
            self._direction = direction

    def brake(self, mode):
        """设置刹车模式，刹车时强制目标转速为0"""
        if mode in [MotorBrakeMode.MOTOR_BRAKE_NONE,
                    MotorBrakeMode.MOTOR_BRAKE_SOFTWARE,
                    MotorBrakeMode.MOTOR_BRAKE_HARDWARE]:
            self._brake_mode = mode
            if self._brake_mode != MotorBrakeMode.MOTOR_BRAKE_NONE:
                self._target_speed = 0.0

    # 新增：获取当前目标转速（供传感器/界面读取）
    def get_target_speed(self):
        return self._target_speed

class VirtualMotor(Motor):
    def __init__(self, driver=None, controller=None):
        # 未传入驱动时，默认初始化虚拟电机驱动
        if driver is None:
            driver = VirtualMotorDriver()
        # 严格按父类参数要求：driver和controller为必传（适配大写属性）
        super().__init__(driver, controller)