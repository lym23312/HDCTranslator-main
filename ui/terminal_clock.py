#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
终端时钟组件
显示带有科幻终端风格的数字时钟
"""

import time
import random
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTime, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPainterPath

class DataStreamVisualizer(QWidget):
    """数据流可视化组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(100, 30)
        self.setMaximumHeight(30)
        
        self.data_points = []
        self.generate_data_points()
        
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)
    
    def generate_data_points(self):
        """生成随机数据点"""
        self.data_points = []
        for i in range(100):
            height = random.uniform(0.1, 0.9)
            self.data_points.append(height)
    
    def update_animation(self):
        """更新动画"""
        self.offset = (self.offset + 1) % len(self.data_points)
        self.update()
    
    def paintEvent(self, event):
        """绘制数据流"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        pen = QPen(QColor(0, 150, 0))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width(), self.height())
        
        width = self.width() - 4
        height = self.height() - 4
        
        painter.setPen(QColor(0, 255, 0, 150))
        
        for i in range(width):
            idx = (self.offset + i) % len(self.data_points)
            y = 2 + int(self.data_points[idx] * height)
            painter.drawLine(i + 2, height + 2, i + 2, height + 2 - y)



class TerminalClock(QWidget):
    """科幻风格的终端时钟组件"""
    
    # 添加标记为已翻译的信号
    mark_selected_as_translated = pyqtSignal()
    mark_all_as_translated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(150, 50)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(5)
        
        self.data_stream = DataStreamVisualizer()
        time_layout.addWidget(self.data_stream, 1)
        
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.time_label.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        self.time_label.setStyleSheet("""
            color: #55FF55; 
            background-color: transparent;
            text-shadow: 0px 0px 3px #33FF33;
        """)
        time_layout.addWidget(self.time_label, 2)
        
        main_layout.addLayout(time_layout)
        
        date_layout = QHBoxLayout()
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(5)
        
        # 添加标记按钮容器
        mark_buttons_container = QWidget()
        mark_buttons_layout = QVBoxLayout(mark_buttons_container)
        mark_buttons_layout.setContentsMargins(0, 0, 0, 0)
        mark_buttons_layout.setSpacing(2)
        
        # 标记选中按钮
        self.mark_selected_btn = QPushButton("标记选中")
        self.mark_selected_btn.setFont(QFont("Courier New", 8))
        self.mark_selected_btn.setStyleSheet("""
            QPushButton {
                background-color: #001800;
                color: #33FF33;
                border: 1px solid #33FF33;
                border-radius: 0px;
                padding: 2px;
                min-height: 12px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #003300;
                border: 1px solid #66FF66;
            }
            QPushButton:pressed {
                background-color: #33FF33;
                color: #000000;
            }
        """)
        self.mark_selected_btn.clicked.connect(self.mark_selected_as_translated.emit)
        mark_buttons_layout.addWidget(self.mark_selected_btn)
        
        # 标记全部按钮
        self.mark_all_btn = QPushButton("标记全部")
        self.mark_all_btn.setFont(QFont("Courier New", 8))
        self.mark_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #001800;
                color: #33FF33;
                border: 1px solid #33FF33;
                border-radius: 0px;
                padding: 2px;
                min-height: 12px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #003300;
                border: 1px solid #66FF66;
            }
            QPushButton:pressed {
                background-color: #33FF33;
                color: #000000;
            }
        """)
        self.mark_all_btn.clicked.connect(self.mark_all_as_translated.emit)
        mark_buttons_layout.addWidget(self.mark_all_btn)
        
        date_layout.addWidget(mark_buttons_container, 1)
        
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.date_label.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        self.date_label.setStyleSheet("""
            color: #55FF55; 
            background-color: transparent;
            text-shadow: 0px 0px 3px #33FF33;
        """)
        date_layout.addWidget(self.date_label, 2)
        
        main_layout.addLayout(date_layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        
        self.update_time()
    
    def start_clock(self):
        """启动时钟"""
        self.timer.start(1000)
    
    def stop_clock(self):
        """停止时钟"""
        self.timer.stop()
    
    def update_time(self):
        """更新时间显示"""
        now = QDateTime.currentDateTime()
        
        time_str = now.toString("HH:mm:ss")
        date_str = now.toString("yyyy/MM/dd")
        
        time_str = "UDS TIME: " + time_str
        date_str = "ALLIANCE DATE: " + date_str
        
        self.time_label.setText(time_str)
        self.date_label.setText(date_str)
    
    def paintEvent(self, event):
        """自定义绘制"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor(0, 200, 0))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
        
        painter.setPen(QColor(0, 130, 0, 180))
        painter.drawLine(10, self.height() // 2, self.width() - 10, self.height() // 2)
        painter.drawLine(10, 5, 10, self.height() - 5)

# 测试代码
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    clock = TerminalClock()
    clock.setStyleSheet("background-color: black;")
    clock.resize(200, 60)
    clock.start_clock()
    clock.show()
    
    sys.exit(app.exec())
