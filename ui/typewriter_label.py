#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
打字机效果标签
实现终端风格的逐字打印文本效果
"""

from PyQt6.QtWidgets import QLabel, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot

class TypewriterLabel(QLabel):
    """带有打字机动画效果的标签控件"""

    typing_finished = pyqtSignal()

    def __init__(self, text="", typing_speed=100, parent=None):
        """初始化打字机标签"""
        super().__init__(parent)

        self.full_text = text
        self.current_text = ""
        self.current_position = 0
        self.typing_speed = typing_speed
        self.cursor_visible = True

        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.type_next_character)

        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self.toggle_cursor)
        self.cursor_timer.start(500)

        if text:
            self.set_text(text)

    def set_text(self, text, start_typing=True):
        """设置要显示的文本"""
        self.typing_timer.stop()
        self.full_text = text
        self.current_position = 0
        self.current_text = ""

        self.update_display_text()

        if start_typing and text:
            self.start_typing()

    def start_typing(self):
        """开始或恢复打字效果"""
        if self.current_position < len(self.full_text):
            self.typing_timer.start(self.typing_speed)

    def pause_typing(self):
        """暂停打字效果"""
        self.typing_timer.stop()

    def stop_typing(self):
        """停止打字效果并清除状态"""
        self.typing_timer.stop()
        self.current_position = 0
        self.current_text = ""
        self.update_display_text()

    def complete_typing(self):
        """立即完成打字效果，显示全部文本"""
        self.typing_timer.stop()
        self.current_position = len(self.full_text)
        self.current_text = self.full_text
        self.update_display_text()
        self.typing_finished.emit()

    def set_typing_speed(self, speed):
        """设置打字速度"""
        self.typing_speed = speed
        if self.typing_timer.isActive():
            self.typing_timer.setInterval(speed)

    def type_next_character(self):
        """处理下一个字符的显示"""
        if self.current_position < len(self.full_text):
            self.current_text = self.full_text[:self.current_position + 1]
            self.current_position += 1

            self.update_display_text()

            if self.current_position >= len(self.full_text):
                self.typing_timer.stop()
                self.typing_finished.emit()

    def toggle_cursor(self):
        """切换光标可见性"""
        self.cursor_visible = not self.cursor_visible

        if self.typing_timer.isActive() or self.current_position < len(self.full_text):
            self.update_display_text()

    def update_display_text(self):
        """更新显示文本，包括光标"""
        display_text = self.current_text

        if self.current_position < len(self.full_text) and self.cursor_visible:
            display_text += "█"

        super().setText(display_text)

    def setText(self, text):
        """重写QLabel的setText方法，使用打字机效果"""
        self.set_text(text)

# 测试代码
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    window = QWidget()
    window.setStyleSheet("background-color: black;")
    layout = QVBoxLayout(window)

    label = TypewriterLabel("正在初始化联盟安全系统...\n扫描木星分离主义者活动...\n检测到接近！", typing_speed=80)
    label.setStyleSheet("color: #33FF33; font-family: 'Courier New'; font-size: 14px;")
    layout.addWidget(label)

    label.typing_finished.connect(lambda: print("打字效果完成！"))

    window.resize(400, 200)
    window.show()

    sys.exit(app.exec())
