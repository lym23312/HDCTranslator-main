#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
科幻风格模拟表盘时钟
实现带有科幻元素的模拟时钟效果
"""

import math
import random
import time
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QSize, QRectF, QPointF, QDateTime
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QRadialGradient, 
    QLinearGradient, QPainterPath, QPolygonF, QBrush
)

class AnalogClock(QWidget):
    """科幻风格的模拟表盘时钟"""
    
    def __init__(self, parent=None):
        """初始化表盘时钟"""
        super().__init__(parent)
        
        self.setMinimumSize(150, 150)
        
        self.hour_hand_length = 0.5
        self.minute_hand_length = 0.7
        self.second_hand_length = 0.9
        
        self.outer_ring_angle = 0
        self.inner_ring_angle = 0
        self.scan_line_angle = 0
        
        self.data_points = []
        self.generate_data_points(20)
        
        self.pulse_value = 0
        self.pulse_direction = 1
        
        self.markers = []
        self.generate_markers(6)
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_animation)
        self.update_timer.start(50)
    
    def start_clock(self):
        """启动时钟"""
        if not self.update_timer.isActive():
            self.update_timer.start(50)
    
    def stop_clock(self):
        """停止时钟"""
        if self.update_timer.isActive():
            self.update_timer.stop()
    
    def generate_data_points(self, count):
        """生成随机数据点"""
        self.data_points = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.65, 0.9)
            intensity = random.randint(150, 255)
            
            self.data_points.append({
                'angle': angle,
                'distance': distance,
                'intensity': intensity,
                'size': random.uniform(1.5, 3.5),
                'blink_rate': random.uniform(0.02, 0.1),
                'blink_state': random.random()
            })
    
    def generate_markers(self, count):
        """生成标记点"""
        self.markers = []
        for i in range(count):
            angle = (i / count) * 2 * math.pi
            self.markers.append({
                'angle': angle,
                'label': f"M{i+1}",
                'distance': 0.82,
                'active': random.choice([True, False])
            })
    
    def update_animation(self):
        """更新动画效果"""
        self.outer_ring_angle = (self.outer_ring_angle + 0.3) % 360
        self.inner_ring_angle = (self.inner_ring_angle - 0.2) % 360
        self.scan_line_angle = (self.scan_line_angle + 1.5) % 360
        
        self.pulse_value += 0.05 * self.pulse_direction
        if self.pulse_value >= 1.0:
            self.pulse_value = 1.0
            self.pulse_direction = -1
        elif self.pulse_value <= 0.0:
            self.pulse_value = 0.0
            self.pulse_direction = 1
        
        for point in self.data_points:
            point['blink_state'] += point['blink_rate']
            if point['blink_state'] >= 1.0:
                point['blink_state'] = 0.0
        
        if random.random() < 0.02:
            marker = random.choice(self.markers)
            marker['active'] = not marker['active']
        
        self.update()
    
    def paintEvent(self, event):
        """绘制时钟"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.draw_clock_face(painter)
        self.draw_clock_hands(painter)
        self.draw_decorations(painter)
    
    def draw_clock_face(self, painter):
        """绘制表盘"""
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(center_x, center_y) * 0.9
        
        background_gradient = QRadialGradient(center_x, center_y, radius)
        background_gradient.setColorAt(0, QColor(0, 30, 0))
        background_gradient.setColorAt(0.8, QColor(0, 15, 0))
        background_gradient.setColorAt(1, QColor(0, 5, 0))
        
        painter.setBrush(background_gradient)
        painter.setPen(QPen(QColor(0, 100, 0), 1))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        outer_pen = QPen(QColor(0, 180, 0, 150), 2)
        painter.setPen(outer_pen)
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        inner_radius = radius * 0.85
        inner_pen = QPen(QColor(0, 150, 0, 100), 1)
        painter.setPen(inner_pen)
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)
        
        painter.setPen(QPen(QColor(0, 200, 0, 200), 1))
        
        for i in range(60):
            angle = i * 6
            rad_angle = math.radians(angle)
            
            start_radius = radius * (0.9 if i % 5 == 0 else 0.95)
            end_radius = radius * 1.0
            
            start_x = center_x + start_radius * math.cos(rad_angle - math.pi/2)
            start_y = center_y + start_radius * math.sin(rad_angle - math.pi/2)
            end_x = center_x + end_radius * math.cos(rad_angle - math.pi/2)
            end_y = center_y + end_radius * math.sin(rad_angle - math.pi/2)
            
            if i % 5 == 0:
                painter.setPen(QPen(QColor(0, 255, 0, 220), 2))
            else:
                painter.setPen(QPen(QColor(0, 180, 0, 150), 1))
                
            painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))
        
        number_radius = radius * 0.75
        font = QFont("Courier New", int(radius/10), QFont.Weight.Bold)
        painter.setFont(font)
        
        for i in range(12):
            angle = i * 30
            rad_angle = math.radians(angle)
            
            x = center_x + number_radius * math.cos(rad_angle - math.pi/2)
            y = center_y + number_radius * math.sin(rad_angle - math.pi/2)
            
            text = str((i if i > 0 else 12))
            
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            
            painter.setPen(QColor(0, 255, 0))
            painter.drawText(int(x - text_width/2), int(y + text_height/4), text)
    
    def draw_clock_hands(self, painter):
        """绘制时钟指针"""
        current_time = QDateTime.currentDateTime().time()
        h, m, s = current_time.hour(), current_time.minute(), current_time.second()
        ms = current_time.msec()
        
        hour_angle = (h % 12 + m / 60.0) * 30
        minute_angle = (m + s / 60.0) * 6
        second_angle = (s + ms / 1000.0) * 6
        
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(center_x, center_y) * 0.9
        
        self.draw_hand(painter, center_x, center_y, radius, hour_angle, 
                      self.hour_hand_length, 4, QColor(0, 200, 0, 220))
        
        self.draw_hand(painter, center_x, center_y, radius, minute_angle, 
                      self.minute_hand_length, 3, QColor(0, 255, 0, 220))
        
        self.draw_hand(painter, center_x, center_y, radius, second_angle, 
                      self.second_hand_length, 2, QColor(0, 255, 0, 180))
        
        painter.setPen(QPen(QColor(0, 255, 0), 1))
        painter.setBrush(QBrush(QColor(0, 200, 0)))
        painter.drawEllipse(QPointF(center_x, center_y), 4, 4)
    
    def draw_hand(self, painter, center_x, center_y, radius, angle, length, width, color):
        """绘制指针"""
        rad_angle = math.radians(angle)
        
        end_x = center_x + radius * length * math.cos(rad_angle - math.pi/2)
        end_y = center_y + radius * length * math.sin(rad_angle - math.pi/2)
        
        pointer = QPolygonF()
        
        side_angle1 = rad_angle - math.pi/2 + math.pi/2
        side_angle2 = rad_angle - math.pi/2 - math.pi/2
        side_length = width
        
        side_x1 = center_x + side_length * math.cos(side_angle1)
        side_y1 = center_y + side_length * math.sin(side_angle1)
        
        side_x2 = center_x + side_length * math.cos(side_angle2)
        side_y2 = center_y + side_length * math.sin(side_angle2)
        
        pointer.append(QPointF(side_x1, side_y1))
        pointer.append(QPointF(end_x, end_y))
        pointer.append(QPointF(side_x2, side_y2))
        
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        painter.drawPolygon(pointer)
    
    def draw_decorations(self, painter):
        """绘制装饰元素"""
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(center_x, center_y) * 0.9
        
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.outer_ring_angle)
        
        painter.setPen(QPen(QColor(0, 150, 0, 80), 1, Qt.PenStyle.DotLine))
        painter.drawEllipse(QPointF(0, 0), radius * 1.05, radius * 1.05)
        
        for i in range(30):
            angle = i * (360 / 30)
            rad_angle = math.radians(angle)
            
            length = random.uniform(5, 10)
            start_x = (radius + 2) * math.cos(rad_angle)
            start_y = (radius + 2) * math.sin(rad_angle)
            end_x = (radius + 2 + length) * math.cos(rad_angle)
            end_y = (radius + 2 + length) * math.sin(rad_angle)
            
            intensity = random.randint(100, 200)
            painter.setPen(QPen(QColor(0, intensity, 0, 130), 1))
            painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))
        
        painter.restore()
        
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(-self.inner_ring_angle)
        
        inner_radius = radius * 0.4
        painter.setPen(QPen(QColor(0, 120, 0, 100), 1, Qt.PenStyle.DashLine))
        painter.drawEllipse(QPointF(0, 0), inner_radius, inner_radius)
        
        for i in range(6):
            angle = i * (360 / 6)
            rad_angle = math.radians(angle)
            
            start_x = inner_radius * 0.7 * math.cos(rad_angle)
            start_y = inner_radius * 0.7 * math.sin(rad_angle)
            end_x = inner_radius * 1.1 * math.cos(rad_angle)
            end_y = inner_radius * 1.1 * math.sin(rad_angle)
            
            painter.setPen(QPen(QColor(0, 150, 0, 120), 1))
            painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))
        
        painter.restore()
        
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.scan_line_angle)
        
        scan_pen = QPen(QColor(0, 255, 0, 100), 2)
        painter.setPen(scan_pen)
        painter.drawLine(0, 0, 0, int(-radius * 1.1))
        
        glow_size = 3 + 2 * self.pulse_value
        glow_color = QColor(50, 255, 100, 150)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(QPen(glow_color, 1))
        painter.drawEllipse(QPointF(0, -radius * 1.05), glow_size, glow_size)
        
        painter.restore()
        
        pulse_radius = radius * (0.6 + 0.1 * self.pulse_value)
        pulse_color = QColor(0, 200, 0, int(40 + 30 * self.pulse_value))
        painter.setPen(QPen(pulse_color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(center_x, center_y), pulse_radius, pulse_radius)
        
        for point in self.data_points:
            angle = point['angle']
            distance = point['distance']
            
            x = center_x + radius * distance * math.cos(angle)
            y = center_y + radius * distance * math.sin(angle)
            
            blink_alpha = int(100 + 150 * math.sin(point['blink_state'] * math.pi))
            point_color = QColor(0, point['intensity'], 0, blink_alpha)
            
            painter.setPen(QPen(point_color, 1))
            painter.setBrush(QBrush(point_color))
            painter.drawEllipse(QPointF(x, y), point['size'], point['size'])
        
        small_font = QFont("Courier New", int(radius/15))
        painter.setFont(small_font)
        
        for marker in self.markers:
            angle = marker['angle']
            distance = marker['distance']
            
            x = center_x + radius * distance * math.cos(angle)
            y = center_y + radius * distance * math.sin(angle)
            
            if marker['active']:
                marker_color = QColor(0, 255, 0, 220)
            else:
                marker_color = QColor(0, 100, 0, 150)
            
            painter.setPen(QPen(marker_color, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(x, y), 6, 6)
            
            text_x = x + 8 * math.cos(angle)
            text_y = y + 8 * math.sin(angle)
            
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(marker['label'])
            text_height = fm.height()
            
            text_x = max(min(text_x, self.width() - text_width), 0)
            text_y = max(min(text_y + text_height/2, self.height() - 2), text_height)
            
            painter.setPen(marker_color)
            painter.drawText(int(text_x), int(text_y), marker['label'])
        
        current_date = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        date_font = QFont("Courier New", int(radius/12))
        painter.setFont(date_font)
        
        date_y = center_y + radius * 0.3
        date_width = painter.fontMetrics().horizontalAdvance(current_date)
        
        painter.setPen(QColor(0, 200, 0))
        painter.drawText(int(center_x - date_width/2), int(date_y), current_date)
        
        status_text = "ALLIANCE SEC"
        status_font = QFont("Courier New", int(radius/13), QFont.Weight.Bold)
        painter.setFont(status_font)
        
        status_y = center_y - radius * 0.25
        status_width = painter.fontMetrics().horizontalAdvance(status_text)
        
        painter.setPen(QColor(0, 255, 0))
        painter.drawText(int(center_x - status_width/2), int(status_y), status_text)

# 测试代码
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    clock = AnalogClock()
    clock.setStyleSheet("background-color: black;")
    clock.resize(300, 300)
    clock.show()
    
    sys.exit(app.exec())
