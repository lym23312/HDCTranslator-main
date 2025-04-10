#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CRT效果组件
模拟老式CRT显示器的视觉效果
"""

import random
import math
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QRect, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QRadialGradient, QLinearGradient,
    QPainterPath, QBrush, QImage, QPixmap
)

class CRTEffectWidget(QWidget):
    """CRT显示器效果覆盖层"""

    def __init__(self, parent=None):
        """初始化CRT效果组件"""
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        if parent:
            self.raise_()
            parent.installEventFilter(self)

        self.scan_line_strength = 0.4
        self.vignette_strength = 0.6
        self.distortion_strength = 0.03
        self.flicker_strength = 0.05
        self.current_flicker = 0
        self.aberration_strength = 1.5
        self.curvature_strength = 0.05

        self.scan_line_y = 0
        self.scan_line_speed = 2
        self.noise_frame = 0

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_effects)
        self.update_timer.start(50)

    def update_effects(self):
        """更新动态效果"""
        self.scan_line_y = (self.scan_line_y + self.scan_line_speed) % (self.height() or 600)

        if random.random() < 0.05:
            self.current_flicker = random.uniform(-self.flicker_strength, self.flicker_strength)
        else:
            self.current_flicker = random.uniform(-self.flicker_strength/3, self.flicker_strength/3)

        self.noise_frame += 1
        self.update()

    def resizeEvent(self, event):
        """窗口大小改变时的处理"""
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())

    def eventFilter(self, obj, event):
        """事件过滤器，用于响应父组件的变化"""
        if obj == self.parent() and event.type() == event.Type.Resize:
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        """绘制CRT效果"""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_crt_effects(painter)

    def draw_crt_effects(self, painter):
        """绘制各种CRT效果"""
        self.draw_screen_curvature(painter)
        self.draw_vignette(painter)
        self.draw_scan_lines(painter)
        self.draw_noise(painter)
        self.draw_chromatic_aberration(painter)
        self.draw_crt_frame(painter)

    def draw_screen_curvature(self, painter):
        """绘制屏幕曲率效果"""
        if self.curvature_strength <= 0:
            return

        width = self.width()
        height = self.height()

        edge_gradient = QRadialGradient(width/2, height/2, width * 0.7)
        edge_gradient.setColorAt(0, QColor(0, 0, 0, 0))
        edge_gradient.setColorAt(0.85, QColor(0, 0, 0, int(30 * self.curvature_strength)))
        edge_gradient.setColorAt(0.95, QColor(0, 0, 0, int(100 * self.curvature_strength)))
        edge_gradient.setColorAt(1, QColor(0, 0, 0, int(200 * self.curvature_strength)))

        painter.fillRect(0, 0, width, height, edge_gradient)

        highlight_gradient = QLinearGradient(0, 0, width, height)
        highlight_gradient.setColorAt(0, QColor(255, 255, 255, int(15 * self.curvature_strength)))
        highlight_gradient.setColorAt(0.1, QColor(255, 255, 255, 0))
        highlight_gradient.setColorAt(0.9, QColor(255, 255, 255, 0))
        highlight_gradient.setColorAt(1, QColor(255, 255, 255, int(10 * self.curvature_strength)))

        painter.fillRect(0, 0, width, height, highlight_gradient)

    def draw_vignette(self, painter):
        """绘制暗角效果"""
        rect = QRectF(0, 0, self.width(), self.height())
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = max(self.width(), self.height()) * 0.8

        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.6, QColor(0, 0, 0, int(50 * self.vignette_strength)))
        gradient.setColorAt(1, QColor(0, 0, 0, int(120 * self.vignette_strength)))

        painter.fillRect(rect, gradient)

    def draw_scan_lines(self, painter):
        """绘制扫描线效果"""
        scan_line_spacing = 2
        scan_line_opacity = int(70 * self.scan_line_strength)

        painter.setPen(QPen(QColor(0, 0, 0, scan_line_opacity), 1))

        for y in range(0, self.height(), scan_line_spacing):
            painter.drawLine(0, y, self.width(), y)

        bright_scan_y = self.scan_line_y
        bright_gradient = QLinearGradient(0, bright_scan_y - 10, 0, bright_scan_y + 10)
        bright_gradient.setColorAt(0, QColor(255, 255, 255, 0))
        bright_gradient.setColorAt(0.5, QColor(255, 255, 255, 20))
        bright_gradient.setColorAt(1, QColor(255, 255, 255, 0))

        scan_rect = QRectF(0, bright_scan_y - 10, self.width(), 20)
        painter.fillRect(scan_rect, bright_gradient)

    def draw_noise(self, painter):
        """绘制随机噪点"""
        noise_opacity = int(30 + 10 * self.current_flicker)
        noise_count = int(self.width() * self.height() / 20000)

        painter.setPen(QPen(QColor(255, 255, 255, noise_opacity), 1))

        random.seed(self.noise_frame)

        for _ in range(noise_count):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            size = random.randint(1, 2)
            painter.drawPoint(x, y)
            if size > 1:
                painter.drawPoint(x+1, y)
                painter.drawPoint(x, y+1)

    def draw_chromatic_aberration(self, painter):
        """绘制色差效果"""
        if self.aberration_strength > 0:
            edge_width = int(5 * self.aberration_strength)

            painter.setPen(QPen(QColor(255, 0, 0, 30), edge_width))
            painter.drawLine(edge_width, 0, edge_width, self.height())
            painter.drawLine(0, edge_width, self.width(), edge_width)

            painter.setPen(QPen(QColor(0, 0, 255, 30), edge_width))
            painter.drawLine(self.width() - edge_width, 0, self.width() - edge_width, self.height())
            painter.drawLine(0, self.height() - edge_width, self.width(), self.height() - edge_width)

    def draw_crt_frame(self, painter):
        """绘制CRT显示器边框效果"""
        width = self.width()
        height = self.height()

        outer_border_width = 10
        painter.fillRect(0, 0, width, outer_border_width, QColor(0, 0, 0, 200))
        painter.fillRect(0, height - outer_border_width, width, outer_border_width, QColor(0, 0, 0, 200))
        painter.fillRect(0, outer_border_width, outer_border_width, height - 2*outer_border_width, QColor(0, 0, 0, 200))
        painter.fillRect(width - outer_border_width, outer_border_width, outer_border_width, height - 2*outer_border_width, QColor(0, 0, 0, 200))

        inner_glow_pen = QPen(QColor(0, 200, 0, 50), 2)
        painter.setPen(inner_glow_pen)
        painter.drawRect(outer_border_width, outer_border_width,
                         width - 2*outer_border_width, height - 2*outer_border_width)

        corner_size = 30

        corner_gradient = QLinearGradient(0, 0, corner_size, corner_size)
        corner_gradient.setColorAt(0, QColor(50, 50, 50, 200))
        corner_gradient.setColorAt(1, QColor(20, 20, 20, 150))
        painter.fillRect(0, 0, corner_size, corner_size, corner_gradient)

        corner_gradient = QLinearGradient(width, 0, width - corner_size, corner_size)
        corner_gradient.setColorAt(0, QColor(50, 50, 50, 200))
        corner_gradient.setColorAt(1, QColor(20, 20, 20, 150))
        painter.fillRect(width - corner_size, 0, corner_size, corner_size, corner_gradient)

        corner_gradient = QLinearGradient(0, height, corner_size, height - corner_size)
        corner_gradient.setColorAt(0, QColor(50, 50, 50, 200))
        corner_gradient.setColorAt(1, QColor(20, 20, 20, 150))
        painter.fillRect(0, height - corner_size, corner_size, corner_size, corner_gradient)

        corner_gradient = QLinearGradient(width, height, width - corner_size, height - corner_size)
        corner_gradient.setColorAt(0, QColor(50, 50, 50, 200))
        corner_gradient.setColorAt(1, QColor(20, 20, 20, 150))
        painter.fillRect(width - corner_size, height - corner_size, corner_size, corner_size, corner_gradient)

        highlight_color = QColor(255, 255, 255, 10 + int(5 * self.current_flicker))
        painter.setPen(highlight_color)

        path = QPainterPath()
        path.moveTo(0, corner_size)
        path.lineTo(0, 0)
        path.lineTo(corner_size, 0)
        painter.drawPath(path)

        path = QPainterPath()
        path.moveTo(width - corner_size, height)
        path.lineTo(width, height)
        path.lineTo(width, height - corner_size)
        painter.drawPath(path)

# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QMainWindow, QLabel

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setStyleSheet("background-color: black;")
    window.resize(800, 600)

    label = QLabel("联盟科研部门 - 深海异物研究终端", window)
    label.setStyleSheet("color: #33FF33; font-family: 'Courier New'; font-size: 24px;")
    label.setGeometry(200, 250, 400, 100)

    crt_effect = CRTEffectWidget(window)
    crt_effect.setGeometry(0, 0, window.width(), window.height())

    window.setWindowTitle("CRT效果测试")
    window.show()

    sys.exit(app.exec())
