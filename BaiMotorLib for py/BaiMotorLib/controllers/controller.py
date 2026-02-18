# BaiMotorLib/controllers/controller.py
from BaiMotorLib.common.constants import ControllerState, MotorBrakeMode

class Controller:
    """控制器基类：所有控制器的统一父类"""
    def __init__(self):
        # 统一通过静态类属性引用常量，消除本地常量定义
        self.Target = None          # 控制目标值（如转速、位置）
        self.BrakeMode = MotorBrakeMode.MOTOR_BRAKE_NONE  # 初始无刹车
        self.state = ControllerState.CONTROLLER_STATE_IDLE  # 初始未运行

    # 预留抽象方法，子类必须实现
    def set_target(self, target):
        raise NotImplementedError("子类必须实现set_target方法")

    def update(self):
        raise NotImplementedError("子类必须实现update方法")

    def execute(self):
        raise NotImplementedError("子类必须实现execute方法")