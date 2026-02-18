import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QGroupBox, QGridLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
from pyqtgraph import PlotWidget

# 导入项目核心模块（仅使用，不修改）
from BaiMotorLib.common.motor_manager import MotorManager
from BaiMotorLib.common.motorlib_time_sys import MotorlibTimeSys
from BaiMotorLib.common.constants import ControllerState, MotorBrakeMode
from BaiMotorLib.drivers.virtual.pyqt5_motor import VirtualMotor, VirtualMotorDriver
from BaiMotorLib.drivers.virtual.pyqt5_sensor import VirtualSensor
from BaiMotorLib.controllers.virtual.pyqt5_controller import OpenLoopController

class MotorQt5SimulationUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("电机仿真系统 - PyQt5可视化（不修改驱动库）")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #f0f0f0;")

        # 1. 初始化仿真核心组件（严格遵循Motor类大写属性：self.Driver / self.Controller）
        self.time_sys = MotorlibTimeSys()
        self.sensor = VirtualSensor()  # 虚拟传感器（采集电机数据）
        self.motor_driver = VirtualMotorDriver()  # 虚拟电机驱动
        self.controller = OpenLoopController(motor_driver=self.motor_driver)  # 开环控制器
        # 严格按Motor库定义初始化：driver/controller为必传，绑定后通过大写属性访问
        self.motor = VirtualMotor(driver=self.motor_driver, controller=self.controller)
        # 电机管理器直接使用（不修改、不新增方法）
        self.motor_manager = MotorManager(self.time_sys, self.motor)

        # 2. 仿真状态变量
        self.simulation_running = False
        self.sim_data = {"time_ms": [], "speed": [], "current": [], "target_speed": []}
        self.max_data_len = 500  # 曲线最大显示数据点（避免卡顿）

        # 3. 初始化UI组件
        self._init_ui()

        # 4. 初始化定时器（1ms刷新，模拟实时仿真）
        self.timer = QTimer(self)
        self.timer.setInterval(1)  # 1ms周期，与仿真步长一致
        self.timer.timeout.connect(self._simulation_tick)

    def _init_ui(self):
        """初始化UI布局：控制区、数据显示区、曲线区（功能不变）"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ---- 顶部控制区 ----
        control_group = QGroupBox("仿真控制")
        control_group.setStyleSheet("QGroupBox {font-size: 16px; font-weight: bold; margin-top: 10px;}")
        control_layout = QHBoxLayout(control_group)
        control_layout.setSpacing(15)

        # 目标转速输入
        self.target_speed_input = QLineEdit()
        self.target_speed_input.setPlaceholderText("输入目标转速（rpm）")
        self.target_speed_input.setText("200")
        self.target_speed_input.setFixedSize(150, 35)
        self.target_speed_input.setStyleSheet("font-size: 14px; padding: 5px;")
        control_layout.addWidget(QLabel("目标转速：", font=QFont("Arial", 14)))
        control_layout.addWidget(self.target_speed_input)
        control_layout.addWidget(QLabel("rpm", font=QFont("Arial", 14)))

        # 启停/刹车按钮（样式不变）
        self.start_btn = QPushButton("启动仿真")
        self.stop_btn = QPushButton("停止仿真")
        self.brake_btn = QPushButton("紧急刹车")
        for btn in [self.start_btn, self.stop_btn, self.brake_btn]:
            btn.setFixedSize(120, 35)
            btn.setStyleSheet("""
                QPushButton {font-size: 14px; font-weight: bold; border-radius: 5px;}
                QPushButton#start {background-color: #4CAF50; color: white;}
                QPushButton#stop {background-color: #FF9800; color: white;}
                QPushButton#brake {background-color: #F44336; color: white;}
                QPushButton:hover {opacity: 0.8;}
            """)
        self.start_btn.setObjectName("start")
        self.stop_btn.setObjectName("stop")
        self.brake_btn.setObjectName("brake")
        # 绑定按钮事件（核心修改：绕过motor_manager，直接操作控制器）
        self.start_btn.clicked.connect(self._start_simulation)
        self.stop_btn.clicked.connect(self._stop_simulation)
        self.brake_btn.clicked.connect(self._emergency_brake)

        control_layout.addStretch()
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.brake_btn)
        main_layout.addWidget(control_group)

        # ---- 中间数据显示区 ----
        data_group = QGroupBox("实时数据")
        data_group.setStyleSheet("QGroupBox {font-size: 16px; font-weight: bold; margin-top: 10px;}")
        data_layout = QGridLayout(data_group)
        data_layout.setSpacing(15)
        self.data_labels = {
            "当前转速": QLabel("0.00 rpm"),
            "目标转速": QLabel("0.00 rpm"),
            "电机电流": QLabel("0.00 A"),
            "电机电压": QLabel(f"{self.sensor.get_voltage()} V"),
            "转子位置": QLabel("0.0000 rad"),
            "仿真状态": QLabel("未运行")
        }
        # 设置数据标签样式
        for lbl in self.data_labels.values():
            lbl.setStyleSheet("font-size: 14px; background-color: white; padding: 5px; border-radius: 3px;")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedSize(180, 35)
        # 添加到布局
        row, col = 0, 0
        for name, lbl in self.data_labels.items():
            data_layout.addWidget(QLabel(f"{name}：", font=QFont("Arial", 14)), row, col*2)
            data_layout.addWidget(lbl, row, col*2+1)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        main_layout.addWidget(data_group)

        # ---- 底部曲线区 ----
        plot_group = QGroupBox("实时曲线")
        plot_group.setStyleSheet("QGroupBox {font-size: 16px; font-weight: bold; margin-top: 10px;}")
        plot_layout = QVBoxLayout(plot_group)
        # 初始化PyQtGraph绘图组件
        self.plot_widget = PlotWidget()
        self.plot_widget.setStyleSheet("background-color: white;")
        self.plot_widget.setTitle("转速/电流实时曲线", font=QFont("Arial", 14, QFont.Bold))
        self.plot_widget.setLabel("left", "数值", font=QFont("Arial", 12))
        self.plot_widget.setLabel("bottom", "时间 (ms)", font=QFont("Arial", 12))
        self.plot_widget.addLegend()
        # 绘制曲线（颜色/样式不变）
        self.speed_curve = self.plot_widget.plot(pen=pg.mkPen(color="#2196F3", width=2), name="实际转速 (rpm)")
        self.target_speed_curve = self.plot_widget.plot(pen=pg.mkPen(color="#FFC107", width=2, style=Qt.DashLine), name="目标转速 (rpm)")
        self.current_curve = self.plot_widget.plot(pen=pg.mkPen(color="#9C27B0", width=2), name="电机电流 (A)", secondary_y=True)
        # 副坐标轴设置（电流）
        self.plot_widget.setLabel("right", "电流 (A)", color="#9C27B0", font=QFont("Arial", 12))
        self.plot_widget.getAxis("right").setPen(pg.mkPen(color="#9C27B0", width=2))
        plot_layout.addWidget(self.plot_widget)
        main_layout.addWidget(plot_group)

    def _start_simulation(self):
        """
        启动仿真（核心修改1：不调用motor_manager.start_motor()）
        直接操作控制器：设置目标转速 + 切换为运行状态
        """
        if self.simulation_running:
            return
        # 解析目标转速，参数校验
        try:
            target_speed = float(self.target_speed_input.text())
            if target_speed < 0:
                raise ValueError
            # 直接给控制器设置目标转速
            self.controller.set_target(target_speed)
        except ValueError:
            self.data_labels["仿真状态"].setText("参数错误！")
            self.data_labels["仿真状态"].setStyleSheet("color: red; font-size: 14px; background-color: white; padding: 5px;")
            return
        # 直接切换控制器为运行状态（绕过电机管理器）
        self.controller.set_state(ControllerState.CONTROLLER_STATE_RUNNING)
        # 启动定时器，开始仿真
        self.simulation_running = True
        self.timer.start()
        # 更新界面状态
        self.data_labels["仿真状态"].setText("运行中")
        self.data_labels["仿真状态"].setStyleSheet("color: green; font-size: 14px; background-color: white; padding: 5px;")
        self.start_btn.setEnabled(False)

    def _stop_simulation(self):
        """
        停止仿真（核心修改2：不调用motor_manager.stop_motor()）
        直接暂停定时器，重置状态（不触发刹车，仅停止仿真循环）
        """
        if not self.simulation_running:
            return
        # 直接暂停定时器，停止仿真步长更新
        self.timer.stop()
        self.simulation_running = False
        # 更新界面状态
        self.data_labels["仿真状态"].setText("已停止")
        self.data_labels["仿真状态"].setStyleSheet("color: orange; font-size: 14px; background-color: white; padding: 5px;")
        self.start_btn.setEnabled(True)

    def _emergency_brake(self):
        """
        紧急刹车（核心修改3：直接操作控制器触发硬件刹车）
        无需经过电机管理器，直接调用控制器刹车方法
        """
        if not self.simulation_running:
            return
        # 直接给控制器设置硬件刹车模式，强制转速归0
        self.controller.set_brake_mode(MotorBrakeMode.MOTOR_BRAKE_HARDWARE)
        # 停止仿真定时器
        self.timer.stop()
        self.simulation_running = False
        # 更新界面状态
        self.data_labels["仿真状态"].setText("紧急刹车")
        self.data_labels["仿真状态"].setStyleSheet("color: red; font-size: 14px; background-color: white; padding: 5px;")
        self.start_btn.setEnabled(True)

    def _simulation_tick(self):
        """
        仿真核心步长（1ms执行一次）
        仅保留对motor_manager.update_motor()的调用（库中原有方法，不修改）
        其余逻辑不变：更新时间→更新电机→更新传感器→记录数据→刷新界面
        """
        # 1. 时间系统步进1ms（库中原有方法）
        self.time_sys.tick_inc(ms=1)
        # 2. 调用电机管理器原有update_motor()方法（仅使用，不修改）
        self.motor_manager.update_motor()
        # 3. 更新传感器数据（带噪声，库中原有逻辑）
        self.sensor.update()
        # 4. 执行控制器输出（确保控制指令传递到驱动）
        self.controller.execute()
        # 5. 获取当前仿真数据（严格适配属性规范）
        current_time = self.time_sys.get_time()
        total_ms = current_time[3] + current_time[2]*1000 + current_time[1]*60*1000 + current_time[0]*3600*1000
        current_speed = self.sensor.get_speed()
        current_current = self.sensor.get_current()
        # 从电机驱动获取实际目标转速（驱动与控制器已绑定，数据一致）
        target_speed = self.motor_driver.get_target_speed()
        current_pos = self.sensor.get_position()
        # 6. 记录数据，限制长度避免内存溢出
        self.sim_data["time_ms"].append(total_ms)
        self.sim_data["speed"].append(current_speed)
        self.sim_data["current"].append(current_current)
        self.sim_data["target_speed"].append(target_speed)
        if len(self.sim_data["time_ms"]) > self.max_data_len:
            for key in self.sim_data:
                self.sim_data[key] = self.sim_data[key][-self.max_data_len:]
        # 7. 刷新实时数据标签
        self.data_labels["当前转速"].setText(f"{current_speed} rpm")
        self.data_labels["目标转速"].setText(f"{target_speed:.2f} rpm")
        self.data_labels["电机电流"].setText(f"{current_current:.2f} A")
        self.data_labels["转子位置"].setText(f"{current_pos:.4f} rad")
        # 8. 刷新实时曲线
        self.speed_curve.setData(self.sim_data["time_ms"], self.sim_data["speed"])
        self.target_speed_curve.setData(self.sim_data["time_ms"], self.sim_data["target_speed"])
        self.current_curve.setData(self.sim_data["time_ms"], self.sim_data["current"])