#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译统计组件
显示翻译速度、预估完成时间和API状态
"""

import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDateTime
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPainterPath, QBrush

class TranslationStatsWidget(QWidget):
    """翻译统计组件，显示翻译速度、预估时间和API状态"""
    
    # 信号
    check_api_status = pyqtSignal()    # 通知主窗口检查API状态
    import_excel_requested = pyqtSignal()  # 请求导入Excel
    export_excel_requested = pyqtSignal()  # 请求导出Excel
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(400, 100)
        
        # 翻译数据
        self.translation_history = []  # 存储(时间戳, 翻译条目数)的元组
        self.translation_speed = 0     # 每分钟的翻译速度
        self.remaining_entries = 0     # 剩余未翻译条目数
        self.total_entries = 0         # 总条目数
        self.api_connected = False     # API连接状态
        self.last_api_check = 0        # 上次检查API的时间戳
        
        # 初始化UI
        self.setup_ui()
        
        # 定时器 - 每3秒更新一次翻译速度
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_translation_speed)
        self.update_timer.start(3000)
        
        # 定时器 - 每30秒检查一次API状态
        self.api_check_timer = QTimer(self)
        self.api_check_timer.timeout.connect(self.check_api_status.emit)
        self.api_check_timer.start(30000)
    
    def setup_ui(self):
        """设置UI组件"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建标题
        title_label = QLabel("翻译统计面板")
        title_label.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #33FF33; background-color: #001800; padding: 3px; border: 1px solid #33FF33;")
        main_layout.addWidget(title_label)
        
        # 上部区域 - 速度和API状态
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        # 翻译速度
        self.speed_layout = QVBoxLayout()
        speed_label = QLabel("翻译速度:")
        speed_label.setFont(QFont("Courier New", 10))
        speed_label.setStyleSheet("color: #33FF33;")
        self.speed_layout.addWidget(speed_label)
        
        self.speed_value_label = QLabel("计算中...")
        self.speed_value_label.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        self.speed_value_label.setStyleSheet("color: #33FF33;")
        self.speed_layout.addWidget(self.speed_value_label)
        
        top_layout.addLayout(self.speed_layout)
        
        # API状态
        self.api_layout = QVBoxLayout()
        api_label = QLabel("API状态:")
        api_label.setFont(QFont("Courier New", 10))
        api_label.setStyleSheet("color: #33FF33;")
        self.api_layout.addWidget(api_label)
        
        self.api_status_label = QLabel("未检测")
        self.api_status_label.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        self.api_status_label.setStyleSheet("color: #FFFF33;")
        self.api_layout.addWidget(self.api_status_label)
        
        top_layout.addLayout(self.api_layout)
        
        main_layout.addLayout(top_layout)
        
        # 底部区域 - 预计剩余时间和Excel按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        # 左侧 - 预计剩余时间
        time_layout = QVBoxLayout()
        
        self.time_label = QLabel("预计剩余时间:")
        self.time_label.setFont(QFont("Courier New", 10))
        self.time_label.setStyleSheet("color: #33FF33;")
        time_layout.addWidget(self.time_label)
        
        self.time_value_label = QLabel("等待翻译中...")
        self.time_value_label.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        self.time_value_label.setStyleSheet("color: #33FF33;")
        time_layout.addWidget(self.time_value_label)
        
        bottom_layout.addLayout(time_layout, 3)  # 分配比例为3
        
        # 右侧 - Excel按钮
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        
        # 导入Excel按钮
        self.import_excel_btn = QPushButton("导入Excel")
        self.import_excel_btn.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        self.import_excel_btn.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background-color: #003300;
                border: 2px solid #33FF33;
                padding: 2px;
                font-weight: bold;
                min-height: 20px;
                max-height: 24px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #004400;
                color: #FFFFFF;
                border: 2px solid #55FF55;
            }
            QPushButton:pressed {
                background-color: #33FF33;
                color: #000000;
            }
        """)
        # 连接按钮点击信号
        self.import_excel_btn.clicked.connect(self.import_excel_requested.emit)
        button_layout.addWidget(self.import_excel_btn)
        
        # 导出Excel按钮
        self.export_excel_btn = QPushButton("导出Excel")
        self.export_excel_btn.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        self.export_excel_btn.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background-color: #003300;
                border: 2px solid #33FF33;
                padding: 2px;
                font-weight: bold;
                min-height: 20px;
                max-height: 24px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #004400;
                color: #FFFFFF;
                border: 2px solid #55FF55;
            }
            QPushButton:pressed {
                background-color: #33FF33;
                color: #000000;
            }
        """)
        # 连接按钮点击信号
        self.export_excel_btn.clicked.connect(self.export_excel_requested.emit)
        button_layout.addWidget(self.export_excel_btn)
        
        bottom_layout.addLayout(button_layout, 2)  # 分配比例为2
        
        main_layout.addLayout(bottom_layout)
    
    def update_translation_count(self, translated_count, total_count):
        """更新翻译计数并记录历史"""
        self.total_entries = total_count
        self.remaining_entries = total_count - translated_count
        
        # 记录当前时间和翻译数量
        timestamp = time.time()
        self.translation_history.append((timestamp, translated_count))
        
        # 只保留过去5分钟的记录
        cutoff_time = timestamp - 300  # 5分钟前
        self.translation_history = [
            (ts, count) for ts, count in self.translation_history 
            if ts >= cutoff_time
        ]
        
        # 更新UI
        self.update_translation_speed()
    
    def update_stats(self, translated_count, total_count, completion_percentage=None):
        """更新翻译统计数据 (兼容性方法，调用 update_translation_count)"""
        # 调用原有方法保持功能一致性
        self.update_translation_count(translated_count, total_count)
    
    def update_translation_speed(self):
        """计算并更新翻译速度和预计剩余时间"""
        if len(self.translation_history) < 2:
            # 数据不足，无法计算速度
            self.speed_value_label.setText("等待更多数据...")
            self.time_value_label.setText("等待翻译中...")
            return
        
        # 获取最新和一分钟前的记录
        now = time.time()
        latest_time, latest_count = self.translation_history[-1]
        
        # 查找大约一分钟前的记录
        one_minute_ago = now - 60
        for ts, count in reversed(self.translation_history[:-1]):
            if ts <= one_minute_ago:
                old_time, old_count = ts, count
                break
        else:
            # 没有足够老的记录，使用最早的记录
            old_time, old_count = self.translation_history[0]
        
        # 计算速度 (条/分钟)
        time_diff = (latest_time - old_time) / 60  # 转换为分钟
        if time_diff > 0:
            count_diff = latest_count - old_count
            self.translation_speed = count_diff / time_diff
            
            # 更新速度显示
            self.speed_value_label.setText(f"{self.translation_speed:.1f} 条/分钟")
            
            # 计算剩余时间
            if self.translation_speed > 0:
                remaining_minutes = self.remaining_entries / self.translation_speed
                
                if remaining_minutes < 1:
                    self.time_value_label.setText("不到1分钟")
                elif remaining_minutes < 60:
                    self.time_value_label.setText(f"约 {int(remaining_minutes)} 分钟")
                else:
                    hours = int(remaining_minutes / 60)
                    mins = int(remaining_minutes % 60)
                    self.time_value_label.setText(f"约 {hours} 小时 {mins} 分钟")
            else:
                self.time_value_label.setText("无法估计")
        else:
            self.speed_value_label.setText("计算中...")
            self.time_value_label.setText("等待更多数据...")
    
    def set_api_status(self, connected):
        """设置API连接状态"""
        self.api_connected = connected
        self.last_api_check = time.time()
        
        if connected:
            self.api_status_label.setText("连接正常 ✓")
            self.api_status_label.setStyleSheet("color: #33FF33;")
        else:
            self.api_status_label.setText("连接失败 ✗")
            self.api_status_label.setStyleSheet("color: #FF3333;")
    
    def paintEvent(self, event):
        """绘制背景和边框"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        background_brush = QBrush(QColor(0, 10, 0))
        painter.fillRect(self.rect(), background_brush)
        
        # 绘制边框
        pen = QPen(QColor(0, 150, 0))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        
        # 绘制装饰线
        painter.setPen(QPen(QColor(0, 80, 0, 80), 1))
        painter.drawLine(10, int(self.height() / 2), self.width() - 10, int(self.height() / 2))
        
        # 随机数据点，增强科技感
        painter.setPen(QColor(0, 255, 0, 100))
        path = QPainterPath()
        
        prev_x, prev_y = None, None
        for i in range(15, self.width() - 15, 10):
            x = i
            # y = self.height() - 15 - ((i / self.width()) * 25) + 5 * (0.5 - random.random())
            # path.lineTo(x, y)
            # 使用sin函数生成波形
            import math
            y = int(self.height() - 15 - 10 * math.sin(i / 30))
            
            if prev_x is None:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
            
            prev_x, prev_y = x, y
        
        painter.drawPath(path)
