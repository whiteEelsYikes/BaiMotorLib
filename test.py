import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QSlider, QLabel, QSpinBox,
                             QGroupBox, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QFont
# 替换qcustomplot为matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文乱码
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示

# 电机模拟核心参数（可根据需求修改）
HALL_PHASE_NUM = 6  # 三相霍尔6个换向状态
ENCODER_PPR = 1000  # 编码器线数（每转脉冲数）
MAX_RPM = 5000      # 最大模拟转速(RPM)
MIN_RPM = 0         # 最小模拟转速
DEFAULT_ACCEL = 100 # 默认加减速斜率(RPM/100ms)
WAVE_DATA_LEN = 200 # 波形显示数据长度（点数）
REFRESH_RATE = 50   # 界面刷新频率(ms)

class MotorSimThread(QThread):
    """电机模拟子线程：独立计算霍尔/编码器状态，避免阻塞界面"""
    state_update = pyqtSignal(int, int, int, bool)  # 霍尔状态、A相、B相、运行状态
    param_update = pyqtSignal(int, str)             # 转速、转向

    def __init__(self):
        super().__init__()
        # 电机核心参数
        self.current_rpm = 0
        self.target_rpm = 0
        self.accel_rate = DEFAULT_ACCEL
        self.dir = 1  # 1-正转，0-反转
        self.running = False  # 运行状态
        # 霍尔信号配置
        self.hall_state = 0
        self.hall_pos_forward = [0x01, 0x03, 0x02, 0x06, 0x04, 0x05]  # 正转状态表
        self.hall_pos_reverse = self.hall_pos_forward[::-1]          # 反转状态表（逆序）
        self.hall_tick = 0
        self.hall_period = 0  # 霍尔状态切换周期(ms)
        # 编码器信号配置
        self.encoder_phase = 0  # 0-3：正交相位状态
        self.encoder_tick = 0
        self.encoder_period = 0  # 编码器相位切换周期(ms)
        # 定时器：5ms刷新一次（高精度计算）
        self.timer = QTimer()
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.calc_motor_state)

    def calc_motor_state(self):
        """核心计算：根据目标转速更新实际转速，计算霍尔/编码器周期并更新状态"""
        if not self.running:
            self.target_rpm = 0
        # 1. 加减速控制：实际转速向目标转速逼近
        if self.current_rpm < self.target_rpm:
            self.current_rpm = min(self.current_rpm + self.accel_rate/20, self.target_rpm)
        elif self.current_rpm > self.target_rpm:
            self.current_rpm = max(self.current_rpm - self.accel_rate/20, self.target_rpm)
        self.current_rpm = int(self.current_rpm)

        # 2. 计算霍尔和编码器周期（转速→频率→周期）
        if self.current_rpm == 0:
            self.hall_period = 0
            self.encoder_period = 0
            ha, hb, hc = 0, 0, 0
            enc_a, enc_b = 0, 0
        else:
            # 霍尔周期：每转6个状态，周期=60000/(转速*6) （ms/状态）
            self.hall_period = 60000 / (self.current_rpm * HALL_PHASE_NUM) if self.current_rpm else 0
            # 编码器周期：每转PPR个脉冲，每个脉冲4个相位，周期=60000/(转速*ENCODER_PPR*4) （ms/相位）
            self.encoder_period = 60000 / (self.current_rpm * ENCODER_PPR * 4) if self.current_rpm else 0

            # 3. 更新霍尔状态（6个状态循环）
            self.hall_tick += 5
            if self.hall_tick >= self.hall_period:
                self.hall_tick = 0
                self.hall_state = (self.hall_state + 1) % HALL_PHASE_NUM
            # 解析霍尔状态为HA/HB/HC电平（1-高，0-低）
            hall_val = self.hall_pos_forward[self.hall_state] if self.dir else self.hall_pos_reverse[self.hall_state]
            ha = (hall_val & 0x01) >> 0
            hb = (hall_val & 0x02) >> 1
            hc = (hall_val & 0x04) >> 2

            # 4. 更新编码器正交相位（4个相位循环，正反转相位顺序相反）
            self.encoder_tick += 5
            if self.encoder_tick >= self.encoder_period:
                self.encoder_tick = 0
                self.encoder_phase = (self.encoder_phase + 1) % 4
            # 正转：A超前B90°；反转：B超前A90°
            if self.dir:
                enc_phase_map = [(1,0), (1,1), (0,1), (0,0)]  # 正转相位表
            else:
                enc_phase_map = [(0,1), (1,1), (1,0), (0,0)]  # 反转相位表
            enc_a, enc_b = enc_phase_map[self.encoder_phase]

        # 5. 发射状态更新信号（传递给主线程绘制）
        hall_combined = (ha << 2) | (hb << 1) | hc  # 合并HA(2)/HB(1)/HC(0)
        self.state_update.emit(hall_combined, enc_a, enc_b, self.running)
        self.param_update.emit(self.current_rpm, "正转" if self.dir else "反转")

    def start_motor(self):
        """启动电机"""
        self.running = True
        if not self.timer.isActive():
            self.timer.start()

    def stop_motor(self):
        """停止电机（急停）"""
        self.running = False

    def toggle_dir(self):
        """切换转向"""
        self.dir = 1 - self.dir

    def set_target_rpm(self, rpm):
        """设置目标转速"""
        self.target_rpm = max(MIN_RPM, min(MAX_RPM, rpm))

    def set_accel(self, accel):
        """设置加减速斜率"""
        self.accel_rate = accel

    def run(self):
        """线程运行"""
        self.exec_()

class HallEncoderMotorSim(QMainWindow):
    """主窗口：可视化界面+波形绘制+参数交互"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("直流霍尔编码电机可视化模拟器")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("font-size:12px; background-color:#f5f5f5;")

        # 初始化波形数据（存储最新WAVE_DATA_LEN个点）
        self.x_data = np.linspace(0, WAVE_DATA_LEN-1, WAVE_DATA_LEN)
        self.ha_data = np.zeros(WAVE_DATA_LEN)
        self.hb_data = np.zeros(WAVE_DATA_LEN)
        self.hc_data = np.zeros(WAVE_DATA_LEN)
        self.enc_a_data = np.zeros(WAVE_DATA_LEN)
        self.enc_b_data = np.zeros(WAVE_DATA_LEN)

        # 初始化电机模拟子线程
        self.motor_thread = MotorSimThread()
        self.motor_thread.state_update.connect(self.update_wave_data)
        self.motor_thread.param_update.connect(self.update_param_display)
        self.motor_thread.start()

        # 构建主界面
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20,20,20,20)

        # 左侧：参数调节区
        self._build_control_panel()
        # 右侧：波形显示+状态显示区
        self._build_display_panel()

        # 界面刷新定时器（与波形刷新率同步）
        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(REFRESH_RATE)
        self.refresh_timer.timeout.connect(self.replot_waves)
        self.refresh_timer.start()

    def _build_control_panel(self):
        """构建左侧参数调节面板"""
        control_panel = QGroupBox("参数调节")
        control_panel.setMinimumWidth(300)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(20,20,20,20)

        # 1. 电机控制按钮（启停、正反转）
        btn_group = QGroupBox("电机控制")
        btn_layout = QHBoxLayout(btn_group)
        self.start_btn = QPushButton("启动")
        self.stop_btn = QPushButton("停止")
        self.dir_btn = QPushButton("切换转向（当前：正转）")
        for btn in [self.start_btn, self.stop_btn, self.dir_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("QPushButton{background-color:#4CAF50; color:white; border:none; border-radius:5px;}"
                              "QPushButton:hover{background-color:#45a049;}"
                              "QPushButton:disabled{background-color:#cccccc;}")
        self.stop_btn.setStyleSheet("QPushButton{background-color:#f44336; color:white; border:none; border-radius:5px;}"
                                    "QPushButton:hover{background-color:#d32f2f;}")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.dir_btn)
        control_layout.addWidget(btn_group)

        # 2. 转速调节
        rpm_group = QGroupBox("转速调节（0~5000RPM）")
        rpm_layout = QGridLayout(rpm_group)
        rpm_layout.addWidget(QLabel("目标转速："), 0,0)
        self.rpm_spin = QSpinBox()
        self.rpm_spin.setRange(MIN_RPM, MAX_RPM)
        self.rpm_spin.setValue(0)
        self.rpm_spin.setMinimumHeight(30)
        self.rpm_slider = QSlider(Qt.Horizontal)
        self.rpm_slider.setRange(MIN_RPM, MAX_RPM)
        self.rpm_slider.setValue(0)
        self.rpm_slider.setMinimumHeight(30)
        rpm_layout.addWidget(self.rpm_spin, 0,1)
        rpm_layout.addWidget(self.rpm_slider, 1,0,1,2)
        control_layout.addWidget(rpm_group)

        # 3. 加减速斜率调节
        accel_group = QGroupBox("加减速斜率（50~500RPM/100ms）")
        accel_layout = QGridLayout(accel_group)
        accel_layout.addWidget(QLabel("斜率值："), 0,0)
        self.accel_spin = QSpinBox()
        self.accel_spin.setRange(50, 500)
        self.accel_spin.setValue(DEFAULT_ACCEL)
        self.accel_spin.setMinimumHeight(30)
        self.accel_slider = QSlider(Qt.Horizontal)
        self.accel_slider.setRange(50, 500)
        self.accel_slider.setValue(DEFAULT_ACCEL)
        self.accel_slider.setMinimumHeight(30)
        accel_layout.addWidget(self.accel_spin, 0,1)
        accel_layout.addWidget(self.accel_slider, 1,0,1,2)
        control_layout.addWidget(accel_group)

        # 信号连接：控件操作→电机参数更新
        self.start_btn.clicked.connect(self.motor_thread.start_motor)
        self.stop_btn.clicked.connect(self.motor_thread.stop_motor)
        self.dir_btn.clicked.connect(self._on_dir_toggle)
        self.rpm_spin.valueChanged.connect(self._on_rpm_change)
        self.rpm_slider.valueChanged.connect(self.rpm_spin.setValue)
        self.accel_spin.valueChanged.connect(self._on_accel_change)
        self.accel_slider.valueChanged.connect(self.accel_spin.setValue)

        self.main_layout.addWidget(control_panel)

    def _build_display_panel(self):
        """构建右侧波形显示+状态显示面板"""
        display_panel = QWidget()
        display_layout = QVBoxLayout(display_panel)
        display_layout.setSpacing(15)

        # 1. 电机状态显示
        state_group = QGroupBox("电机实时状态")
        state_layout = QGridLayout(state_group)
        state_layout.setSpacing(20)
        # 状态指示灯
        self.run_led = QLabel()
        self.run_led.setMinimumSize(20,20)
        self.run_led.setStyleSheet("background-color:#cccccc; border-radius:10px;")
        # 状态标签
        self.rpm_label = QLabel(f"当前转速：0 RPM")
        self.dir_label = QLabel(f"当前转向：正转")
        self.hall_label = QLabel(f"霍尔状态：000 (HA=0, HB=0, HC=0)")
        self.enc_label = QLabel(f"编码器状态：A=0, B=0")
        # 设置字体大小
        for lbl in [self.rpm_label, self.dir_label, self.hall_label, self.enc_label]:
            lbl.setFont(QFont("Arial", 14))
        # 布局
        state_layout.addWidget(QLabel("运行状态："), 0,0)
        state_layout.addWidget(self.run_led, 0,1)
        state_layout.addWidget(self.rpm_label, 0,2)
        state_layout.addWidget(self.dir_label, 1,0,1,2)
        state_layout.addWidget(self.hall_label, 1,2)
        state_layout.addWidget(self.enc_label, 2,0,1,3)
        display_layout.addWidget(state_group)

        # 2. 波形显示区（霍尔信号+编码器信号）- matplotlib适配
        wave_group = QGroupBox("实时波形显示（高=1，低=0）")
        wave_layout = QVBoxLayout(wave_group)
        # 霍尔信号波形图（HA/HB/HC）
        self.hall_fig = Figure(figsize=(8, 3), dpi=100)
        self.hall_canvas = FigureCanvas(self.hall_fig)
        self.hall_canvas.setMinimumHeight(300)
        self.hall_lines = self._init_plot(self.hall_fig, "霍尔信号", ["HA(红)", "HB(绿)", "HC(蓝)"], 
                                          ["red", "green", "blue"])
        # 编码器信号波形图（A/B相）
        self.enc_fig = Figure(figsize=(8, 2), dpi=100)
        self.enc_canvas = FigureCanvas(self.enc_fig)
        self.enc_canvas.setMinimumHeight(200)
        self.enc_lines = self._init_plot(self.enc_fig, "正交编码器信号", ["A相(黄)", "B相(紫)"], 
                                         ["gold", "purple"])
        # 添加到布局
        wave_layout.addWidget(self.hall_canvas)
        wave_layout.addWidget(self.enc_canvas)
        display_layout.addWidget(wave_group)

        self.main_layout.addWidget(display_panel)

    def _init_plot(self, plot_fig, title, legend_labels, colors):
        """初始化matplotlib波形图：设置标题、坐标轴、图例"""
        plot_fig.clear()
        ax = plot_fig.add_subplot(111)
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("采样点", fontsize=10)
        ax.set_ylabel("电平", fontsize=10)
        ax.set_ylim(-0.5, 1.5)  # 电平仅0/1，预留上下余量
        ax.set_xlim(0, WAVE_DATA_LEN-1)
        ax.grid(True, alpha=0.3)
        # 初始化波形曲线
        lines = []
        for i, (label, color) in enumerate(zip(legend_labels, colors)):
            line, = ax.plot(self.x_data, np.zeros(WAVE_DATA_LEN), color=color, label=label, linewidth=2)
            lines.append(line)
        ax.legend(loc="upper right", fontsize=10)
        return lines

    def _on_dir_toggle(self):
        """切换转向回调"""
        self.motor_thread.toggle_dir()
        self.dir_btn.setText(f"切换转向（当前：{self.dir_label.text().split('：')[1]}）")

    def _on_rpm_change(self, rpm):
        """转速变化回调"""
        self.motor_thread.set_target_rpm(rpm)
        self.rpm_slider.setValue(rpm)

    def _on_accel_change(self, accel):
        """加减速斜率变化回调"""
        self.motor_thread.set_accel(accel)
        self.accel_slider.setValue(accel)

    def update_wave_data(self, hall_combined, enc_a, enc_b, running):
        """更新波形数据：移除最旧点，添加最新点"""
        # 解析霍尔组合值为HA/HB/HC
        ha = (hall_combined >> 2) & 0x01
        hb = (hall_combined >> 1) & 0x01
        hc = hall_combined & 0x01

        # 波形数据滚动更新（保持固定长度）
        self.ha_data = np.roll(self.ha_data, -1)
        self.hb_data = np.roll(self.hb_data, -1)
        self.hc_data = np.roll(self.hc_data, -1)
        self.enc_a_data = np.roll(self.enc_a_data, -1)
        self.enc_b_data = np.roll(self.enc_b_data, -1)
        # 添加最新电平值
        self.ha_data[-1] = ha
        self.hb_data[-1] = hb
        self.hc_data[-1] = hc
        self.enc_a_data[-1] = enc_a
        self.enc_b_data[-1] = enc_b

        # 更新状态显示
        self.run_led.setStyleSheet(f"background-color:{'#4CAF50' if running else '#cccccc'}; border-radius:10px;")
        self.hall_label.setText(f"霍尔状态：{ha}{hb}{hc} (HA={ha}, HB={hb}, HC={hc})")
        self.enc_label.setText(f"编码器状态：A={enc_a}, B={enc_b}")

    def update_param_display(self, rpm, dir):
        """更新转速、转向参数显示"""
        self.rpm_label.setText(f"当前转速：{rpm} RPM")
        self.dir_label.setText(f"当前转向：{dir}")
        self.dir_btn.setText(f"切换转向（当前：{dir}）")

    def replot_waves(self):
        """重绘波形：将最新数据更新到matplotlib图表"""
        # 重绘霍尔信号
        self.hall_lines[0].set_ydata(self.ha_data)
        self.hall_lines[1].set_ydata(self.hb_data)
        self.hall_lines[2].set_ydata(self.hc_data)
        self.hall_fig.canvas.draw_idle()
        # 重绘编码器信号
        self.enc_lines[0].set_ydata(self.enc_a_data)
        self.enc_lines[1].set_ydata(self.enc_b_data)
        self.enc_fig.canvas.draw_idle()

    def closeEvent(self, event):
        """窗口关闭事件：停止线程和定时器"""
        self.motor_thread.timer.stop()
        self.motor_thread.quit()
        self.motor_thread.wait()
        self.refresh_timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HallEncoderMotorSim()
    window.show()
    sys.exit(app.exec_())