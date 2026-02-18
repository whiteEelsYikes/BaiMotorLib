# BaiMotorLib/common/constants.py
"""
电机库通用常量定义：所有常量以静态类属性形式提供，仅通过类名调用，不实例化
"""

class ControllerState:
    """控制器运行状态常量"""
    CONTROLLER_STATE_IDLE = 0      # 未运行
    CONTROLLER_STATE_RUNNING = 1   # 正常运行
    CONTROLLER_STATE_BRAKE = 2     # 刹车中（输出应被抑制）
    CONTROLLER_STATE_ERROR = 3     # 错误状态（可选）

class MotorBrakeMode:
    """电机刹车模式常量"""
    MOTOR_BRAKE_NONE = 0           # 无刹车
    MOTOR_BRAKE_SOFTWARE = 1       # 软件刹车
    MOTOR_BRAKE_HARDWARE = 2       # 硬件刹车

class MotorDirection:
    """电机转向常量"""
    MOTOR_DIR_FORWARD = 0          # 正转
    MOTOR_DIR_BACKWARD = 1         # 反转

# 禁止实例化（可选，强化静态类特性）
ControllerState.__init__ = lambda self: None
MotorBrakeMode.__init__ = lambda self: None
MotorDirection.__init__ = lambda self: None