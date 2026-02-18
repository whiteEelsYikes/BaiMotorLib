from .motorlib_time_sys import *

class MotorManager:
    def __init__(self, time_sys, *args):
        """
        电机管理器初始化
        :param time_sys: 时间系统实例（MotorlibTimeSys），用于电机更新的时间基准
        :param args: 可变参数，初始化时传入的多个电机实例
        """
        # 绑定时间系统，指定类型注解确保类型匹配
        self.time_sys: MotorlibTimeSys = time_sys
        # 初始化电机列表，接收可变参数的电机实例
        self.motors: list = list(args)

    def add_motor(self, motor):
        """
        添加电机实例到管理器，避免重复添加
        :param motor: 待添加的电机实例
        """
        if motor not in self.motors:
            self.motors.append(motor)

    def remove_motor(self, motor):
        """
        从管理器中移除指定电机实例，兼容电机不存在的情况（无报错）
        :param motor: 待移除的电机实例
        """
        if motor in self.motors:
            self.motors.remove(motor)

    def update_motor(self):
        """
        按时间系统基准批量更新电机状态
        核心逻辑：遍历所有电机，通过时间系统比较电机的下一次更新时间（motor.Controller.NextUpdate）
        若更新时间已到（等于当前时间）或已过期（早于当前时间），触发电机控制器的update()方法
        注：motor.Controller.NextUpdate 需为 (ms, sec, min, hour) 格式的元组，与compare_time参数匹配
        """
        # 遍历管理器中所有电机，逐台判断是否需要更新
        for motor in self.motors:
            # 取出电机控制器的下一次更新时间，解包后传入时间比较方法
            next_update = motor.Controller.NextUpdate
            # 比较下一次更新时间与当前时间的关系
            time_state = self.time_sys.compare_time(*next_update)
            if time_state is None:
                motor.Controller.update()
            # 时间已到/已过期，触发电机控制器更新
            if time_state in (self.time_sys.NowTheTime, self.time_sys.OnceUponATime):
                motor.Controller.update()
