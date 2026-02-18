from BaiMotorLib.controllers.controller import Controller
from BaiMotorLib.common.motor_manager import MotorManager
from BaiMotorLib.common.motorlib_time_sys import MotorlibTimeSys
from BaiMotorLib.common.constants import ControllerState, MotorBrakeMode
class OpenLoopController(Controller):
    def __init__(self, motor_driver=None, qt5_control_panel=None):
        super().__init__()
        self.MotorDriver = motor_driver  # 关联电机驱动（大写，与逻辑一致）
        self.qt5_control_panel = qt5_control_panel  # 预留QT面板交互
        self.updatePeriodMS = 10  # 控制更新周期（10ms）
        self.NextUpdate = (0, 0, 0, 0)  # 必须初始化！供MotorManager调用
        self._output_speed = 0.0  # 控制器输出转速
        self.Target = 0.0  # 初始化目标转速，避免空值
        # 重置初始状态（基于常量类）
        self.BrakeMode = MotorBrakeMode.MOTOR_BRAKE_NONE
        self.state = ControllerState.CONTROLLER_STATE_IDLE

    def set_target(self, target_speed):
        """设置控制器目标转速（rpm），非负限制"""
        self.Target = max(0.0, target_speed)
        self._calc_next_update()

    def set_brake_mode(self, brake_mode):
        """设置刹车模式，联动控制器状态"""
        if brake_mode in [MotorBrakeMode.MOTOR_BRAKE_NONE,
                          MotorBrakeMode.MOTOR_BRAKE_SOFTWARE,
                          MotorBrakeMode.MOTOR_BRAKE_HARDWARE]:
            self.BrakeMode = brake_mode
            if self.BrakeMode != MotorBrakeMode.MOTOR_BRAKE_NONE:
                self.state = ControllerState.CONTROLLER_STATE_BRAKE
                self._output_speed = 0.0
            else:
                self.state = ControllerState.CONTROLLER_STATE_RUNNING
            self._calc_next_update()

    def set_state(self, state):
        """设置控制器运行状态，仅支持预定义状态"""
        valid_states = [ControllerState.CONTROLLER_STATE_IDLE,
                        ControllerState.CONTROLLER_STATE_RUNNING,
                        ControllerState.CONTROLLER_STATE_BRAKE,
                        ControllerState.CONTROLLER_STATE_ERROR]
        if state in valid_states:
            self.state = state
            self._calc_next_update()

    def update(self):
        """控制器核心更新逻辑（开环控制：直接输出目标转速）"""
        if self.state == ControllerState.CONTROLLER_STATE_BRAKE:
            self._output_speed = 0.0  # 刹车中抑制输出
        elif self.state == ControllerState.CONTROLLER_STATE_RUNNING:
            self._output_speed = self.Target  # 运行中输出目标转速
        elif self.state == ControllerState.CONTROLLER_STATE_IDLE:
            self._output_speed = 0.0  # 未运行时输出0
        self.execute()
        self._calc_next_update()

    def execute(self):
        """执行控制输出：将转速指令传递给电机驱动"""
        if self.MotorDriver is not None:
            self.MotorDriver.set_target(self._output_speed)

    def get_input(self):
        """预留：获取传感器输入（闭环控制扩展用）"""
        pass

    def put_output(self):
        """返回当前控制器输出转速"""
        return self._output_speed

    def _calc_next_update(self):
        """计算下一次更新时间（处理时间进位）"""
        time_sys = MotorlibTimeSys()
        current_time = time_sys.get_time()  # 格式：(hour, min, sec, ms)
        ms = current_time[3] + self.updatePeriodMS
        sec, min, hour = current_time[2], current_time[1], current_time[0]

        # 处理毫秒/秒/分/小时进位
        if ms >= 1000:
            sec += 1
            ms -= 1000
        if sec >= 60:
            min += 1
            sec -= 60
        if min >= 60:
            hour += 1
            min -= 60

        self.NextUpdate = (ms, sec, min, hour)