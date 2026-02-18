import sys
from PyQt5.QtWidgets import QApplication
from MotorSimulation.qt5_simulation_ui import MotorQt5SimulationUI

# 安装依赖提示：若缺少库，执行 pip install pyqt5 pyqtgraph numpy
def main():
    # 初始化PyQt5应用
    app = QApplication(sys.argv)
    # 启动仿真界面
    sim_ui = MotorQt5SimulationUI()
    sim_ui.show()
    # 运行应用主循环
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()