from BaiMotorLib.common.motor_manager import MotorManager
from BaiMotorLib.common.motorlib_time_sys import MotorlibTimeSys
from BaiMotorLib.common.constants import ControllerState, MotorBrakeMode
from BaiMotorLib.drivers.virtual.pyqt5_motor import VirtualMotor, VirtualMotorDriver
from BaiMotorLib.drivers.virtual.pyqt5_sensor import VirtualSensor
from BaiMotorLib.controllers.virtual.pyqt5_controller import OpenLoopController


class MotorSimulationCore:
    def __init__(self, simulation_duration_ms=1000):
        self.time_sys = MotorlibTimeSys()
        self.simulation_duration_ms = simulation_duration_ms
        # 严格按大写属性绑定：先初始化驱动/控制器，再传入Motor
        self.sensor = VirtualSensor()
        self.motor_driver = VirtualMotorDriver()
        self.controller = OpenLoopController(motor_driver=self.motor_driver)
        self.motor = VirtualMotor(driver=self.motor_driver, controller=self.controller)  # 关键：必传driver+controller
        self.motor_manager = MotorManager(self.time_sys, self.motor)

        self.is_running = False
        self.simulation_data = []

    def start_simulation(self, target_speed=100.0):
        self.is_running = True
        self.controller.set_state(ControllerState.CONTROLLER_STATE_RUNNING)
        self.controller.set_target(target_speed)

        for _ in range(self.simulation_duration_ms):
            if not self.is_running:
                break
            self.time_sys.tick_inc(ms=1)
            self.motor_manager.update_motor()
            self.sensor.update()
            self.controller.execute()
            self._record_simulation_data()

        self.is_running = False
        print("仿真完成！")

    def stop_simulation(self):
        self.is_running = False
        self.controller.set_brake_mode(MotorBrakeMode.MOTOR_BRAKE_SOFTWARE)
        print("仿真已停止！")

    def _record_simulation_data(self):
        current_time = self.time_sys.get_time()
        total_ms = current_time[3] + current_time[2] * 1000 + current_time[1] * 60 * 1000 + current_time[
            0] * 3600 * 1000
        data = {
            "time_ms": total_ms,
            "speed": self.sensor.get_speed(),
            "position": self.sensor.get_position(),
            "current": self.sensor.get_current(),
            "voltage": self.sensor.get_voltage(),
            "target_speed": self.controller.Target,
            "controller_state": self.controller.state
        }
        self.simulation_data.append(data)

    def get_simulation_data(self):
        return self.simulation_data