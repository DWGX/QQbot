import sys
import subprocess
import psutil
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QLineEdit
)
from PySide6.QtCore import QTimer

class PortInfoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("端口管理与服务信息")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout(self)

        # 创建一个输入框用于搜索端口
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("搜索端口...")
        self.layout.addWidget(self.search_input)

        # 创建一个列表以显示端口
        self.port_list = QListWidget(self)
        self.layout.addWidget(self.port_list)

        # 创建一个按钮以显示详细信息
        self.details_button = QPushButton("显示详细信息", self)
        self.details_button.clicked.connect(self.show_details)
        self.layout.addWidget(self.details_button)

        # 创建一个关闭端口的按钮
        self.close_button = QPushButton("关闭端口", self)
        self.close_button.clicked.connect(self.close_port)
        self.layout.addWidget(self.close_button)

        # 创建一个关闭应用程序的按钮
        self.exit_button = QPushButton("关闭", self)
        self.exit_button.clicked.connect(self.close)
        self.layout.addWidget(self.exit_button)

        # 连接搜索框的文本变化信号
        self.search_input.textChanged.connect(self.filter_ports)

        # 定时器，每5秒刷新一次端口信息
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.populate_ports)
        self.timer.start(5000)  # 5000毫秒（5秒）

        self.populate_ports()

    def populate_ports(self):
        # 清空当前的端口列表
        self.port_list.clear()

        # 获取开放的端口（Windows）
        command = ["netstat", "-ano"]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            output = result.stdout.splitlines()
            for line in output[4:]:  # 跳过前面几行
                if line.strip():  # 确保不是空行
                    self.port_list.addItem(line.strip())
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取端口信息时出错: {e}")

    def filter_ports(self):
        filter_text = self.search_input.text().lower()
        for index in range(self.port_list.count()):
            item = self.port_list.item(index)
            item.setHidden(filter_text not in item.text().lower())

    def show_details(self):
        current_item = self.port_list.currentItem()
        if current_item:
            port_info = current_item.text()
            QMessageBox.information(self, "端口详细信息", port_info)
        else:
            QMessageBox.warning(self, "警告", "请先选择一个端口！")

    def close_port(self):
        current_item = self.port_list.currentItem()
        if current_item:
            port_info = current_item.text()
            parts = port_info.split()
            if len(parts) > 1:
                pid = parts[-1]  # 获取 PID
                command = ["taskkill", "/F", "/PID", pid]
                try:
                    result = subprocess.run(command, capture_output=True, text=True)
                    if result.returncode == 0:
                        QMessageBox.information(self, "成功", f"端口 {port_info} 已关闭。")
                        self.populate_ports()  # 更新端口列表
                    else:
                        QMessageBox.critical(self, "错误", f"关闭端口时出错: {result.stderr}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"关闭端口时出错: {e}")
            else:
                QMessageBox.warning(self, "警告", "无法获取端口 PID。")
        else:
            QMessageBox.warning(self, "警告", "请先选择一个端口！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PortInfoApp()
    window.show()
    sys.exit(app.exec())
