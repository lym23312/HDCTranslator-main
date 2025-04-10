#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
联盟项目UDS终端 - 启动画面
显示带有科幻元素的应用启动界面
"""

import os
import sys
import time
import random
import math
from PyQt6.QtWidgets import (
    QApplication, QSplashScreen, QLabel, QVBoxLayout, QWidget, QFrame
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QRect, QPropertyAnimation, 
    QEasingCurve
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QBrush, QPen, 
    QLinearGradient, QRadialGradient
)

class StartupSplashScreen(QSplashScreen):
    """应用启动画面"""
    
    def __init__(self):
        """初始化启动画面"""
        splash_size = QSize(800, 600)
        pixmap = QPixmap(splash_size)
        pixmap.fill(Qt.GlobalColor.black)
        
        super().__init__(pixmap)
        
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        self.current_message = ""
        self.display_message = ""
        self.typing_index = 0
        self.typing_speed = 1
        self.typing_active = False
        self.typing_complete_callback = None
        
        self.displayed_messages = []
        self.message_y_start = 270
        self.message_line_height = 40

        self.version_info = """
UDS翻译终端
版本: 1.4
联盟科研部门授权终端
工程师: 墨水, 伍德, HDC
联盟安全协议 ECSP-2248369521-B
"""

        self.scan_line_pos = 0
        self.scan_speed = 5
        self.initial_scan_active = True
        self.initial_scan_pos = -10
        self.initial_scan_speed = 15
        
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(20)
        
        self.noise_count = 0
        
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.update_typing)
        self.typing_timer.setInterval(15)
        
        self.terminal_line = 0
        self.max_terminal_lines = 40
        self.terminal_timer = QTimer(self)
        self.terminal_timer.timeout.connect(self.update_terminal_display)
        self.terminal_timer.start(10)
    
    def update_animation(self):
        """更新动画效果"""
        if self.initial_scan_active:
            self.initial_scan_pos += self.initial_scan_speed
            if self.initial_scan_pos > self.height() + 10:
                self.initial_scan_active = False
        
        self.scan_line_pos = (self.scan_line_pos + self.scan_speed) % self.height()
        self.noise_count += 1
        self.update()
    
    def update_terminal_display(self):
        """更新终端逐行显示效果"""
        if self.terminal_line < self.max_terminal_lines:
            self.terminal_line += 1
            self.update()
    
    def update_typing(self):
        """更新打字机效果"""
        if not self.typing_active:
            return
            
        if self.typing_index < len(self.current_message):
            next_index = min(self.typing_index + self.typing_speed, len(self.current_message))
            self.display_message = self.current_message[:next_index]
            self.typing_index = next_index
            self.update()
        else:
            self.typing_active = False
            self.typing_timer.stop()
            self.displayed_messages.append(self.current_message)
            
            if self.typing_complete_callback:
                callback = self.typing_complete_callback
                self.typing_complete_callback = None
                callback()
    
    def showMessage(self, message, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft, color=Qt.GlobalColor.green):
        """显示消息（重写QSplashScreen的方法）"""
        self.current_message = message
        self.typing_index = 0
        self.display_message = ""
        self.typing_active = True
        
        if not self.typing_timer.isActive():
            self.typing_timer.start()
    
    def showMessageWithCallback(self, message, callback, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft, color=Qt.GlobalColor.green):
        """显示消息并在完成后执行回调"""
        self.typing_complete_callback = callback
        self.showMessage(message, alignment, color)
    
    def drawContents(self, painter):
        """绘制启动画面内容（重写QSplashScreen的方法）"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        line_height = self.height() / self.max_terminal_lines
        visible_height = int(self.terminal_line * line_height)
        
        self.draw_scan_lines(painter, visible_height)
        self.draw_noise(painter, visible_height)
        self.draw_logo(painter, visible_height)
        self.draw_version_info(painter, visible_height)
        
        if visible_height > self.height() * 0.4:
            self.draw_message(painter)
        
        self.draw_border(painter, visible_height)
        self.draw_system_status(painter, visible_height)
    
    def draw_scan_lines(self, painter, visible_height):
        """绘制扫描线效果"""
        for y in range(0, min(visible_height, self.height()), 2):
            painter.setPen(QColor(0, 50, 0, 30))
            painter.drawLine(0, y, self.width(), y)
        
        if self.initial_scan_active:
            scan_gradient = QLinearGradient(0, self.initial_scan_pos - 10, 0, self.initial_scan_pos + 10)
            scan_gradient.setColorAt(0, QColor(0, 100, 0, 0))
            scan_gradient.setColorAt(0.3, QColor(0, 200, 0, 100))
            scan_gradient.setColorAt(0.5, QColor(0, 255, 0, 180))
            scan_gradient.setColorAt(0.7, QColor(0, 200, 0, 100))
            scan_gradient.setColorAt(1, QColor(0, 100, 0, 0))
            
            painter.fillRect(QRect(0, self.initial_scan_pos - 10, self.width(), 20), scan_gradient)
            
            afterglow_height = 50
            afterglow_gradient = QLinearGradient(0, self.initial_scan_pos, 0, self.initial_scan_pos + afterglow_height)
            afterglow_gradient.setColorAt(0, QColor(0, 255, 0, 40))
            afterglow_gradient.setColorAt(1, QColor(0, 50, 0, 0))
            
            painter.fillRect(QRect(0, self.initial_scan_pos, self.width(), afterglow_height), afterglow_gradient)
        
        if self.scan_line_pos < visible_height and not self.initial_scan_active:
            scan_gradient = QLinearGradient(0, self.scan_line_pos - 5, 0, self.scan_line_pos + 5)
            scan_gradient.setColorAt(0, QColor(0, 100, 0, 0))
            scan_gradient.setColorAt(0.5, QColor(0, 200, 0, 70))
            scan_gradient.setColorAt(1, QColor(0, 100, 0, 0))
            
            painter.fillRect(QRect(0, self.scan_line_pos - 5, self.width(), 10), scan_gradient)
    
    def draw_noise(self, painter, visible_height):
        """绘制随机噪点"""
        random.seed(self.noise_count)
        painter.setPen(QColor(0, 255, 0, 40))
        
        for _ in range(100):
            x = random.randint(0, self.width())
            y = random.randint(0, min(visible_height, self.height()))
            painter.drawPoint(x, y)
    
    def draw_logo(self, painter, visible_height):
        """绘制联盟标志"""
        self.draw_3d_rotating_logo(painter, visible_height)
        
        line_height = self.height() / self.max_terminal_lines
        version_line = 20
        title_line = version_line + 2
        left_margin = 50
        
        if self.terminal_line >= version_line:
            font = QFont("Courier New", 12, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QColor(0, 255, 0))
            
            version_text = "Europa Coalition UDS Terminal"
            version_y = int(version_line * line_height)
            
            painter.drawText(left_margin, version_y, version_text)
        
        if self.terminal_line >= title_line:
            font = QFont("Courier New", 14, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QColor(0, 255, 0))
            
            title_text = "联盟安全系统"
            title_y = int(title_line * line_height)
            
            painter.drawText(left_margin, title_y, title_text)
    
    def draw_3d_rotating_logo(self, painter, visible_height):
        """绘制3D旋转的北约标志"""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        center_x = self.width() // 2
        center_y = 150
        
        if center_y + 80 <= visible_height:
            angle = (self.noise_count % 360) * 0.5
            
            painter.translate(center_x, center_y)
            painter.rotate(angle)
            
            size = 100
            
            painter.setBrush(QBrush(QColor(0, 60, 165)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(-size), int(-size), int(size*2), int(size*2))
            
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(int(-size), int(-size), int(size*2), int(size*2))
            
            painter.setPen(QPen(QColor(255, 255, 255), 4))
            
            for i in range(16):
                angle_rad = math.radians(i * 22.5)
                cos_val = math.cos(angle_rad)
                sin_val = math.sin(angle_rad)
                
                if i % 4 == 0:
                    length = size * 0.9
                    painter.setPen(QPen(QColor(255, 255, 255), 4))
                elif i % 2 == 0:
                    length = size * 0.7
                    painter.setPen(QPen(QColor(255, 255, 255), 3))
                else:
                    length = size * 0.5
                    painter.setPen(QPen(QColor(255, 255, 255), 2))
                
                start_x = int(cos_val * 20)
                start_y = int(sin_val * 20)
                end_x = int(cos_val * length)
                end_y = int(sin_val * length)
                
                painter.drawLine(start_x, start_y, end_x, end_y)
            
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(-15, -15, 30, 30)
            
            pulse_size = 20 + 8 * abs(math.sin(self.noise_count * 0.05))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(255, 255, 255, 150), 3))
            painter.drawEllipse(int(-pulse_size), int(-pulse_size), int(pulse_size*2), int(pulse_size*2))
        
        painter.restore()
    
    def draw_version_info(self, painter, visible_height):
        """绘制版本信息"""
        line_height = self.height() / self.max_terminal_lines
        start_line = 25
        left_margin = 50
        
        font = QFont("Courier New", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(0, 255, 0))
        
        info_lines = self.version_info.strip().split('\n')
        
        for i, line in enumerate(info_lines):
            current_line = start_line + i
            
            if self.terminal_line >= current_line:
                line_y = int(current_line * line_height)
                
                if line_y <= visible_height:
                    painter.drawText(left_margin, line_y, line)
    
    def draw_message(self, painter):
        """绘制累积的消息列表"""
        if not self.displayed_messages and not self.current_message:
            return
        
        font = QFont("Courier New", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(0, 255, 0))
        
        max_messages = (self.height() - self.message_y_start) // self.message_line_height - 1
        
        display_messages = self.displayed_messages
        if len(display_messages) > max_messages:
            display_messages = display_messages[-max_messages:]
        
        message_x = self.width() - 350
        
        y_pos = self.height() - 250
        for msg in display_messages:
            painter.drawText(message_x, y_pos, msg)
            y_pos += self.message_line_height
        
        if self.typing_active:
            if y_pos + self.message_line_height <= self.height() - 20:
                painter.drawText(message_x, y_pos, self.display_message)
                
                if self.noise_count % 10 < 5:
                    cursor_x = message_x + painter.fontMetrics().horizontalAdvance(self.display_message)
                    cursor_y = y_pos
                    painter.drawText(int(cursor_x), int(cursor_y), "_")
    
    def draw_system_status(self, painter, visible_height):
        """绘制系统状态指示器"""
        status_x = 20
        status_y = 20
        
        if visible_height < status_y:
            return
            
        font = QFont("Courier New", 8)
        painter.setFont(font)
        
        status_width = 180
        status_height = 150
        
        painter.fillRect(
            QRect(status_x, status_y, status_width, status_height),
            QColor(0, 20, 0, 100)
        )
        
        painter.setPen(QPen(QColor(0, 150, 0, 150), 1))
        painter.drawRect(status_x, status_y, status_width, status_height)
        
        painter.setPen(QColor(0, 255, 0))
        painter.drawText(
            QRect(status_x, status_y - 15, status_width, 15),
            Qt.AlignmentFlag.AlignCenter,
            "系统状态"
        )
        
        status_items = [
            ("内核", "ACTIVE"),
            ("内存", f"{random.randint(60, 90)}% FREE"),
            ("网络", "SECURE"),
            ("加密", "QUANTUM"),
            ("安全级别", "ALPHA"),
            ("授权", "VERIFIED")
        ]
        
        item_y = status_y + 15
        for i, (label, value) in enumerate(status_items):
            line_y = item_y + i * 20
            if line_y <= visible_height:
                painter.setPen(QColor(0, 200, 0))
                painter.drawText(
                    QRect(status_x + 10, line_y, 80, 20),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    label
                )
                
                value_color = QColor(0, 255, 0) if "ACTIVE" in value or "VERIFIED" in value else QColor(200, 200, 0)
                painter.setPen(value_color)
                painter.drawText(
                    QRect(status_x + 90, line_y, 80, 20),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    value
                )
    
    def draw_border(self, painter, visible_height):
        """绘制边框"""
        pen = QPen(QColor(0, 200, 0, 200))
        pen.setWidth(2)
        painter.setPen(pen)
        
        painter.drawLine(1, 1, self.width() - 2, 1)
        painter.drawLine(1, 1, 1, min(visible_height, self.height() - 2))
        painter.drawLine(self.width() - 2, 1, self.width() - 2, min(visible_height, self.height() - 2))
        
        if visible_height >= self.height() - 2:
            painter.drawLine(1, self.height() - 2, self.width() - 2, self.height() - 2)
        
        pen.setWidth(1)
        pen.setColor(QColor(0, 150, 0, 150))
        painter.setPen(pen)
        
        painter.drawLine(20, 20, self.width() - 20, 20)
        
        if visible_height >= self.height() - 20:
            painter.drawLine(20, self.height() - 20, self.width() - 20, self.height() - 20)

# 测试代码
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    splash = StartupSplashScreen()
    splash.show()
    
    messages = [
        "初始化系统...",
        "加载UDS翻译协议...",
        "建立安全连接...",
        "验证联盟授权...",
        "准备终端界面...",
        "UDS访问已授权 - 权限已验证",
        "正在启动主界面..."
    ]
    
    def show_next_message(index=0):
        if index < len(messages):
            splash.showMessageWithCallback(
                messages[index],
                lambda: QTimer.singleShot(200, lambda: show_next_message(index + 1))
            )
        else:
            QTimer.singleShot(500, app.quit)
    
    QTimer.singleShot(1000, lambda: show_next_message(0))
    
    sys.exit(app.exec())
