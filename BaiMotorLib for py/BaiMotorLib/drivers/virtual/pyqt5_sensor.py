from BaiMotorLib.drivers.driver import SensorDriver
import random

class VirtualSensor(SensorDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化虚拟传感器参数
        self._speed = 0.0       # 转速 (rpm)
        self._position = 0.0    # 位置 (rad)
        self._current = 0.0     # 电流 (A)
        self._voltage = 24.0    # 电压 (V)
        self._noise = 0.01      # 模拟噪声系数

    def update(self):
        """更新传感器数据，模拟真实传感器的数值变化（带微小噪声）"""
        # 模拟转速小幅波动
        self._speed += random.uniform(-self._noise, self._noise)
        self._speed = max(0.0, self._speed)  # 转速非负
        # 模拟位置随转速累加（简单积分）
        self._position += (self._speed / 60) * (2 * 3.14159) * 0.001  # 按毫秒级更新
        # 模拟电流小幅波动
        self._current += random.uniform(-self._noise * 0.1, self._noise * 0.1)
        self._current = max(0.0, min(self._current, 5.0))  # 电流限制在0~5A

    def get_speed(self):
        """获取当前转速"""
        return round(self._speed, 2)

    def get_position(self):
        """获取当前位置"""
        return round(self._position, 4)

    def get_current(self):
        """获取当前电流"""
        return round(self._current, 2)

    def get_voltage(self):
        """获取当前电压（虚拟电压固定）"""
        return self._voltage