#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译进度饼图控件
显示翻译完成情况的科幻风格饼图
"""

import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QRadialGradient, QLinearGradient, QPainterPath

class ProgressChart(QWidget):
    """科幻风格的翻译进度饼图"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(200, 150)
        self.translated_count = 0
        self.total_count = 1
        
        self.current_angle = 0
        self.target_angle = 0
        self.update_speed = 5
        
        self.grid_points = []
        self.generate_grid_points(20)
        
        self.wave_offset = 0
        self.data_points = []
        self.generate_data_points()
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_animation)
        self.update_timer.start(50)
        
        self.update_target_angle()
    
    def set_progress(self, translated, total):
        """设置翻译进度"""
        if total > 0:
            self.translated_count = min(translated, total)
            self.total_count = max(total, 1)
            self.update_target_angle()
    
    def update_target_angle(self):
        """根据翻译进度更新目标角度"""
        # 安全检查确保不会除以零
        if self.total_count <= 0:
            self.target_angle = 0
            # 强制更新当前角度为0，避免显示不正确
            self.current_angle = 0
            self.update()
            return
            
        # 计算进度比例并转换为角度
        progress_ratio = min(1.0, max(0.0, self.translated_count / self.total_count))
        self.target_angle = 360 * progress_ratio
        
        # 如果变化很大，直接更新当前角度，避免动画延迟
        if abs(self.current_angle - self.target_angle) > 90:
            self.current_angle = self.target_angle
        
        # 强制立即重绘以确保显示最新状态
        self.update()
        
        # 输出调试信息
        print(f"饼图更新: 已翻译 {self.translated_count}/{self.total_count} = {progress_ratio*100:.1f}%, 角度: {self.target_angle}")
    
    def generate_grid_points(self, count):
        """生成随机网格点"""
        self.grid_points = []
        for _ in range(count):
            x = random.randint(0, 100) / 100
            y = random.randint(0, 100) / 100
            self.grid_points.append((x, y))
    
    def generate_data_points(self):
        """生成模拟数据点"""
        self.data_points = []
        for i in range(100):
            x = i / 100
            y = 0.3 * math.sin(x * 2 * math.pi) + 0.2 * math.cos(x * 6 * math.pi)
            self.data_points.append((x, y))
    
    def update_animation(self):
        """更新动画效果"""
        if abs(self.current_angle - self.target_angle) > self.update_speed:
            if self.current_angle < self.target_angle:
                self.current_angle += self.update_speed
            else:
                self.current_angle -= self.update_speed
        else:
            self.current_angle = self.target_angle
        
        self.wave_offset = (self.wave_offset + 0.02) % 1.0
        self.update()
    
    def resizeEvent(self, event):
        """窗口大小改变时重新生成数据"""
        super().resizeEvent(event)
        self.generate_data_points()
    
    def paintEvent(self, event):
        """绘制控件"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        background_gradient = QLinearGradient(0, 0, self.width(), self.height())
        background_gradient.setColorAt(0, QColor(5, 15, 5, 220))
        background_gradient.setColorAt(1, QColor(0, 5, 0, 220))
        painter.fillRect(self.rect(), background_gradient)
        
        border_pen = QPen(QColor(0, 150, 0, 180), 2)
        painter.setPen(border_pen)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        self.draw_grid(painter)
        self.draw_waveform(painter)
        self.draw_pie_chart(painter)
        self.draw_stats_text(painter)
    
    def draw_grid(self, painter):
        """绘制背景网格"""
        painter.setPen(QPen(QColor(0, 100, 0, 40), 1, Qt.PenStyle.DotLine))
        
        for i in range(1, 5):
            y = int(self.height() * (i / 5))
            painter.drawLine(0, y, self.width(), y)
        
        for i in range(1, 5):
            x = int(self.width() * (i / 5))
            painter.drawLine(x, 0, x, self.height())
        
        painter.setPen(QColor(0, 150, 0, 30))
        for point in self.grid_points:
            x = int(point[0] * self.width())
            y = int(point[1] * self.height())
            painter.drawPoint(x, y)
    
    def draw_waveform(self, painter):
        """绘制波形曲线"""
        wave_pen = QPen(QColor(0, 180, 0, 100), 2)
        painter.setPen(wave_pen)
        
        chart_x = int(self.width() * 0.15)
        chart_width = int(self.width() * 0.7)
        chart_height = int(self.height() * 0.15)
        chart_y = int(self.height() * 0.75)
        
        painter.setPen(QPen(QColor(0, 150, 0, 150), 1))
        painter.drawLine(
            chart_x, chart_y, 
            chart_x + chart_width, chart_y
        )
        painter.drawLine(
            chart_x, chart_y - chart_height, 
            chart_x, chart_y
        )
        
        painter.setFont(QFont("Courier New", 6))
        for i in range(5):
            x = int(chart_x + (chart_width * i / 4))
            painter.drawLine(x, chart_y, x, chart_y + 3)
            painter.drawText(
                QRectF(x - 10, chart_y + 3, 20, 10), 
                Qt.AlignmentFlag.AlignCenter, 
                f"{i*25}"
            )
        
        path = QPainterPath()
        first_point = True
        
        for i, point in enumerate(self.data_points):
            x_pos = (point[0] + self.wave_offset) % 1.0
            y_val = point[1]
            
            x = chart_x + x_pos * chart_width
            y = chart_y - (y_val + 0.5) * chart_height
            
            if first_point:
                path.moveTo(x, y)
                first_point = False
            else:
                path.lineTo(x, y)
        
        painter.setPen(QPen(QColor(0, 220, 0, 150), 1.5))
        painter.drawPath(path)
        
        painter.setPen(QPen(QColor(50, 255, 50, 200), 3))
        for _ in range(3):
            if random.random() < 0.3:
                i = random.randint(0, len(self.data_points)-1)
                point = self.data_points[i]
                x_pos = (point[0] + self.wave_offset) % 1.0
                y_val = point[1]
                
                x = chart_x + x_pos * chart_width
                y = chart_y - (y_val + 0.5) * chart_height
                
                painter.drawPoint(QPointF(x, y))
    
    def draw_pie_chart(self, painter):
        """绘制饼图"""
        chart_size = min(self.width(), self.height()) * 0.5
        chart_rect = QRectF(
            (self.width() - chart_size) * 0.3,
            (self.height() - chart_size) * 0.2,
            chart_size,
            chart_size
        )
        
        bg_pen = QPen(QColor(0, 100, 0), 1)
        painter.setPen(bg_pen)
        painter.setBrush(QBrush(QColor(0, 30, 0, 100)))
        painter.drawEllipse(chart_rect)
        
        progress_pen = QPen(QColor(0, 200, 0), 2)
        painter.setPen(progress_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawEllipse(chart_rect)
        
        if self.current_angle > 0:
            progress_brush = QBrush(QColor(0, 255, 0, 80))
            painter.setBrush(progress_brush)
            start_angle = 90 * 16
            span_angle = -int(self.current_angle * 16)
            painter.drawPie(chart_rect, start_angle, span_angle)
        
        inner_size = chart_size * 0.7
        inner_rect = QRectF(
            chart_rect.x() + (chart_size - inner_size) / 2,
            chart_rect.y() + (chart_size - inner_size) / 2,
            inner_size,
            inner_size
        )
        painter.setPen(QPen(QColor(0, 150, 0), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(inner_rect)
        
        center_x = chart_rect.x() + chart_rect.width() / 2
        center_y = chart_rect.y() + chart_rect.height() / 2
        radius = chart_size / 2
        
        for i in range(12):
            angle = math.radians(i * 30)
            inner_x = center_x + math.cos(angle) * radius * 0.7
            inner_y = center_y + math.sin(angle) * radius * 0.7
            outer_x = center_x + math.cos(angle) * radius
            outer_y = center_y + math.sin(angle) * radius
            
            if i % 3 == 0:
                painter.setPen(QPen(QColor(0, 200, 0), 2))
            else:
                painter.setPen(QPen(QColor(0, 100, 0), 1))
            
            painter.drawLine(
                QPointF(inner_x, inner_y),
                QPointF(outer_x, outer_y)
            )
    
    def draw_stats_text(self, painter):
        """绘制统计文字"""
        percentage = 0
        if self.total_count > 0:
            percentage = (self.translated_count / self.total_count) * 100
        
        painter.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        
        title_rect = QRectF(0, 5, self.width(), 20)
        painter.setPen(QColor(0, 200, 0))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "翻译进度")
        
        percentage_rect = QRectF(0, self.height() / 2 - 15, self.width(), 20)
        painter.setPen(QColor(0, 255, 0))
        painter.drawText(percentage_rect, Qt.AlignmentFlag.AlignCenter, f"{percentage:.1f}%")
        
        count_rect = QRectF(0, self.height() / 2 + 5, self.width(), 20)
        painter.setPen(QColor(0, 200, 0))
        painter.drawText(count_rect, Qt.AlignmentFlag.AlignCenter, f"{self.translated_count}/{self.total_count}")

# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    progress_chart = ProgressChart()
    window.setCentralWidget(progress_chart)
    window.setStyleSheet("background-color: black;")
    window.resize(300, 200)
    window.setWindowTitle("翻译进度图表测试")
    window.show()
    
    sys.exit(app.exec())
