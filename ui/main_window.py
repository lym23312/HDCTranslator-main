#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
潜渊症汉化工具 - 主窗口
实现复古科幻终端风格的翻译工具界面
"""

import os
import sys
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QPushButton, QLabel, QComboBox, QLineEdit,
    QFileDialog, QSplitter, QFrame, QToolBar,
    QStatusBar, QApplication, QTextEdit, QProgressBar,
    QMessageBox, QCheckBox, QSlider, QGroupBox, QScrollArea
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QRect, QPropertyAnimation, 
    QEasingCurve, QThread, pyqtSignal, QDateTime,
    QMimeData, QUrl
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QBrush, QLinearGradient, 
    QPainter, QPen, QFontDatabase, QPixmap, QIcon,
    QDragEnterEvent, QDropEvent
)

from ui.terminal_clock import TerminalClock
from ui.analog_clock import AnalogClock
from ui.data_stream_background import DataStreamBackground
from ui.typewriter_label import TypewriterLabel
from ui.crt_effect import CRTEffectWidget
from ui.progress_chart import ProgressChart
from ui.translation_stats_widget import TranslationStatsWidget

from core.xml_handler import XMLHandler
from core.translation_api import TranslationAPI
from ui.api_dialog import APISettingsDialog

# 主题颜色
BACKGROUND_COLOR = "#000000"  # 纯黑色背景
TEXT_COLOR = "#33FF33"        # 荧光绿文字
HIGHLIGHT_COLOR = "#00FFFF"   # 高亮颜色
ACCENT_COLOR = "#33FF33"      # 强调色也改为荧光绿

# 默认饱和度值
DEFAULT_SATURATION = 85      # 默认饱和度值(0-100)

class MainWindow(QMainWindow):
    """联盟项目UDS终端主窗口"""
    
    def __init__(self):
        # 首先调用父类构造函数
        super().__init__(None)  # 确保没有父窗口
        
        # 设置窗口基本属性
        self.setWindowTitle("联盟项目UDS终端 v1.5")
        self.setMinimumSize(800, 600)  # 设置更小的最小尺寸，使用滚动区域确保UI可用
        self.resize(1635, 1211)  # 设置为用户指定的理想尺寸
        
        # 关闭所有可能的标志，使用纯Qt.WindowType.Window
        self.setWindowFlags(Qt.WindowType.Window)
        
        # 启用拖放功能
        self.setAcceptDrops(True)
        
        # 初始化饱和度值
        self.text_saturation = DEFAULT_SATURATION
        
        # 初始化翻译API
        self.current_api_type = "openai"
        self.translator = TranslationAPI.create_api(self.current_api_type)
        self.translator.translation_completed.connect(self.on_translation_completed)
        self.translator.error_occurred.connect(self.on_translation_error)
        
        # 初始化XML处理器
        self.xml_handler = XMLHandler()
        self.xml_handler.progress_updated.connect(self.on_xml_progress)
        self.xml_handler.error_occurred.connect(self.on_xml_error)
        
        # 在屏幕中央显示窗口
        self.centerWindow()
        
        # 加载自定义字体
        self.setup_fonts()
        
        # 应用终端风格
        self.apply_terminal_style()
        
        # 初始化UI组件
        self.init_ui()
        
        # 启动复古终端效果
        self.start_terminal_effects()
        
        # 显示欢迎消息
        self.display_welcome_message()
        
        # 进度条增长控制
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.current_progress = 0
        self.progress_target = 0
        
        # 翻译队列和正在翻译的标志
        self.translation_queue = []
        self.is_translating = False
    
    def centerWindow(self):
        """将窗口定位在屏幕中央"""
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

    def setup_fonts(self):
        """加载和设置自定义等宽字体"""
        # 在实际应用中，你应该从资源文件夹加载自定义字体
        # 这里我们使用系统自带的等宽字体
        self.terminal_font = QFont("Courier New", 10)
        self.terminal_font.setStyleHint(QFont.StyleHint.Monospace)
        QApplication.setFont(self.terminal_font)

    def apply_terminal_style(self):
        """应用复古终端风格到整个窗口"""
        # 根据饱和度计算文字颜色
        text_color = self.get_text_color_with_saturation()
        
        # 设置终端风格的调色板
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND_COLOR))
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.Base, QColor(BACKGROUND_COLOR))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#0F0F0F"))
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.Button, QColor(BACKGROUND_COLOR))
        palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        palette.setColor(QPalette.ColorRole.BrightText, QColor(HIGHLIGHT_COLOR))
        palette.setColor(QPalette.ColorRole.Highlight, text_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        self.setPalette(palette)
        
        # 设置样式表
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #000000;
                color: #33FF33;
            }
            QTableWidget {
                background-color: #000000;
                color: #33FF33;
                gridline-color: #33FF33;
                border: 1px solid #33FF33;
                border-radius: 0px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #33FF33;
                background-color: #000000;
                color: #33FF33;
            }
            QTableWidget::item:selected {
                background-color: #003300;
                color: #33FF33;
            }
            QHeaderView::section {
                background-color: #000000;
                color: #33FF33;
                border: 1px solid #33FF33;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #001800;
                color: #33FF33;
                border: 2px solid #33FF33;
                border-radius: 0px;
                padding: 5px;
                min-height: 45px;
                min-width: 170px;
                font-weight: bold;
                font-size: 14pt;
                margin: 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #003300;
                color: #33FF33;
                border: 2px solid #66FF66;
            }
            QPushButton:pressed {
                background-color: #33FF33;
                color: #000000;
                border: 2px solid #FFFFFF;
            }
            QLabel {
                color: #33FF33;
                background-color: transparent;
                border: none;
            }
            QLineEdit, QComboBox {
                background-color: #001800;
                color: #33FF33;
                border: 2px solid #33FF33;
                border-radius: 0px;
                padding: 5px;
                font-size: 12pt;
                font-weight: bold;
                min-height: 30px;
            }
            QLineEdit:focus, QComboBox:focus {
                background-color: #002800;
                border: 2px solid #66FF66;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 2px solid #33FF33;
                background-color: #003300;
            }
            QComboBox::down-arrow {
                width: 15px;
                height: 15px;
                background-color: #33FF33;
            }
            QComboBox QAbstractItemView {
                background-color: #001800;
                color: #33FF33;
                border: 2px solid #33FF33;
                selection-background-color: #003300;
                selection-color: #FFFFFF;
                outline: none;
            }
            QFrame {
                background-color: #000000;
                border: 1px solid #33FF33;
                color: #33FF33;
            }
            QStatusBar {
                background-color: #000000;
                color: #33FF33;
                border-top: 1px solid #33FF33;
            }
            QProgressBar {
                border: 1px solid #33FF33;
                border-radius: 0px;
                background-color: #000000;
                text-align: center;
                color: #33FF33;
            }
            QProgressBar::chunk {
                background-color: #33FF33;
            }
            QScrollBar {
                background-color: #000000;
                border: 1px solid #33FF33;
            }
            QScrollBar::handle {
                background-color: #003300;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background-color: #000000;
            }
            QFileDialog {
                background-color: #000000;
                color: #33FF33;
            }
            QMessageBox {
                background-color: #000000;
                color: #33FF33;
            }
        """)

    def init_ui(self):
        """初始化UI组件"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 添加CRT效果覆盖层
        self.crt_effect = CRTEffectWidget(self)
        self.crt_effect.setGeometry(self.rect())
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 顶部区域 - 标题、翻译统计和时钟
        top_layout = QHBoxLayout()
        
        # 标题标签
        title_label = TypewriterLabel("联盟项目UDS终端 v1.5", typing_speed=50)
        title_label.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        top_layout.addWidget(title_label, 2)  # 比例从4调整为2
        
        # 添加翻译统计组件
        self.translation_stats_widget = TranslationStatsWidget()
        # 连接API状态检查信号，在自动检查时不显示弹窗
        self.translation_stats_widget.check_api_status.connect(lambda: self.test_api_connection(False))
        # 连接Excel导入导出信号
        self.translation_stats_widget.import_excel_requested.connect(self.import_excel)
        self.translation_stats_widget.export_excel_requested.connect(self.export_excel)
        top_layout.addWidget(self.translation_stats_widget, 5)  # 占据最大空间比例
        
        # 时钟容器
        clock_container = QWidget()
        clock_layout = QHBoxLayout(clock_container)
        clock_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加模拟表盘时钟
        self.analog_clock = AnalogClock()
        self.analog_clock.setMinimumSize(120, 120)
        self.analog_clock.setMaximumSize(120, 120)
        clock_layout.addWidget(self.analog_clock)
        
        # 数字时钟
        self.terminal_clock = TerminalClock()
        # 不再需要连接Excel导入导出信号，因为按钮已移到翻译统计组件中
        # 连接标记为已翻译的信号
        self.terminal_clock.mark_selected_as_translated.connect(self.mark_selected_as_translated)
        self.terminal_clock.mark_all_as_translated.connect(self.mark_all_as_translated)
        clock_layout.addWidget(self.terminal_clock)
        
        top_layout.addWidget(clock_container, 3)  # 保持时钟比例不变
        
        main_layout.addLayout(top_layout)
        
        # 上部区域 - 添加数据流背景
        top_data_stream = DataStreamBackground()
        top_data_stream.setMinimumHeight(200)  # 给定足够的高度显示多个术语
        main_layout.addWidget(top_data_stream)
        
        # 中间区域 - 控制面板和右侧区域(包含拖放区和表格)
        middle_layout = QHBoxLayout()
        
        # 左侧区域 - 包含控制面板和翻译统计
        left_side = QWidget()
        left_layout = QVBoxLayout(left_side)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # 创建滚动区域包装控制面板
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #001100;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #33FF33;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 控制面板
        control_panel = self.create_control_panel()
        # 保存对控制面板中的组的引用，以便在调整大小时使用
        self.file_group = control_panel.findChild(QFrame, name="file_group")
        self.api_group = control_panel.findChild(QFrame, name="api_group")
        self.translation_group = control_panel.findChild(QFrame, name="translation_group")
        
        # 将控制面板设置为滚动区域的内容
        scroll_area.setWidget(control_panel)
        left_layout.addWidget(scroll_area, 7)
        
        # 添加翻译进度饼图
        self.progress_chart = self.create_progress_chart()
        left_layout.addWidget(self.progress_chart, 3)
        
        # 设置左侧控制面板的最小宽度，确保在窗口变小时不会被过度压缩
        left_side.setMinimumWidth(350)
        
        # 将左侧区域添加到中间布局，增加比例为3，使其获得更多空间
        middle_layout.addWidget(left_side, 3)  # 30% 宽度
        
        # 右侧区域 - 包含拖放区和表格
        right_side = QWidget()
        right_layout = QVBoxLayout(right_side)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # 创建拖放区域框架
        self.drop_area = QFrame()
        self.drop_area.setFrameShape(QFrame.Shape.StyledPanel)
        self.drop_area.setLineWidth(2)
        self.drop_area.setStyleSheet("""
            QFrame {
                border: 2px dashed #33FF33;
                background-color: rgba(0, 51, 0, 0.3);
                padding: 10px;
            }
        """)
        drop_area_layout = QVBoxLayout(self.drop_area)
        
        # 拖放图标和文字
        drop_icon_label = QLabel("↓↓↓")
        drop_icon_label.setFont(QFont("Courier New", 24, QFont.Weight.Bold))
        drop_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_icon_label.setStyleSheet("border: none; color: #33FF33;")
        
        drop_text_label = QLabel("将潜渊症XML文件拖放到此处导入")
        drop_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_text_label.setStyleSheet("border: none; color: #33FF33; font-size: 16px;")
        
        drop_area_layout.addWidget(drop_icon_label)
        drop_area_layout.addWidget(drop_text_label)
        drop_area_layout.addStretch()
        
        # 添加拖放区域
        right_layout.addWidget(self.drop_area, 2)
        
        # 翻译表格
        self.translation_table = self.create_translation_table()
        right_layout.addWidget(self.translation_table, 8)
        
        # 添加右侧区域到中间布局，减少比例为7，使其让出一些空间给左侧
        middle_layout.addWidget(right_side, 7)  # 70% 宽度
        
        main_layout.addLayout(middle_layout, 1)
        
        # 底部区域 - 数据监控和状态栏
        bottom_widget = self.create_bottom_area()
        main_layout.addWidget(bottom_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = TypewriterLabel("准备就绪...")
        self.status_bar.addWidget(self.status_label, 1)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 创建一个拖放提示标签（当拖放开始时显示）
        self.drop_highlight_frame = QFrame(self)
        self.drop_highlight_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.drop_highlight_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 51, 0, 0.7);
                border: 3px solid #33FF33;
            }
        """)
        self.drop_highlight_frame.hide()

    def create_control_panel(self):
        """创建控制面板"""
        control_panel = QFrame()
        control_panel.setFrameShape(QFrame.Shape.StyledPanel)
        control_panel.setFrameShadow(QFrame.Shadow.Raised)
        control_panel.setLineWidth(1)
        
        layout = QVBoxLayout(control_panel)
        layout.setSpacing(15)
        
        # 控制面板标题 - 使用更大更粗的字体和背景色增强可见性
        title = TypewriterLabel("控制面板")
        title.complete_typing()  # 立即完成打字效果
        title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #33FF33; background-color: #003300; padding: 5px; border: 2px solid #33FF33;")
        layout.addWidget(title)
        
        # 文件操作区域
        file_group = QFrame()
        file_group.setObjectName("file_group")  # 添加对象名称
        file_group.setFrameShape(QFrame.Shape.StyledPanel)
        file_layout = QVBoxLayout(file_group)
        
        file_title = TypewriterLabel("文件操作")
        file_title.complete_typing()  # 立即完成打字效果
        file_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_title.setStyleSheet("color: #33FF33; background-color: #002200; padding: 3px; font-weight: bold; border: 1px solid #33FF33;")
        file_title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        file_layout.addWidget(file_title)
        
        import_btn = QPushButton("导入文件")
        import_btn.clicked.connect(self.import_file)
        import_btn.setFont(self.terminal_font)  # 确保使用终端字体
        file_layout.addWidget(import_btn)
        
        export_btn = QPushButton("导出翻译")
        export_btn.clicked.connect(self.export_translation)
        export_btn.setFont(self.terminal_font)  # 确保使用终端字体
        file_layout.addWidget(export_btn)
        
        layout.addWidget(file_group)
        
        # 筛选区域
        filter_group = QFrame()
        filter_group.setObjectName("filter_group")  # 添加对象名称
        filter_group.setFrameShape(QFrame.Shape.StyledPanel)
        filter_layout = QVBoxLayout(filter_group)
        
        filter_title = TypewriterLabel("筛选选项")
        filter_title.complete_typing()  # 立即完成打字效果
        filter_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        filter_title.setStyleSheet("color: #33FF33; background-color: #002200; padding: 3px; font-weight: bold; border: 1px solid #33FF33;")
        filter_title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        filter_layout.addWidget(filter_title)
        
        # 物品标签筛选
        category_layout = QHBoxLayout()
        category_label = QLabel("物品标签:")
        category_label.setFont(self.terminal_font)
        category_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.setFont(self.terminal_font)
        self.category_combo.addItem("全部")
        self.category_combo.currentTextChanged.connect(self.filter_entries)
        category_layout.addWidget(self.category_combo)
        
        filter_layout.addLayout(category_layout)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        search_label.setFont(self.terminal_font)
        search_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setFont(self.terminal_font)
        self.search_edit.textChanged.connect(self.filter_entries)
        search_layout.addWidget(self.search_edit)
        
        filter_layout.addLayout(search_layout)
        
        # 翻译状态筛选选项
        translation_status_layout = QHBoxLayout()
        
        # 只显示已翻译选项
        self.translated_only_check = QCheckBox("只显示已翻译")
        self.translated_only_check.setFont(self.terminal_font)
        self.translated_only_check.stateChanged.connect(self.filter_entries)
        translation_status_layout.addWidget(self.translated_only_check)
        
        # 只显示未翻译选项
        self.untranslated_only_check = QCheckBox("只显示未翻译")
        self.untranslated_only_check.setFont(self.terminal_font)
        self.untranslated_only_check.stateChanged.connect(self.filter_entries)
        translation_status_layout.addWidget(self.untranslated_only_check)
        
        filter_layout.addLayout(translation_status_layout)
        
        layout.addWidget(filter_group)
        
        # API设置区域
        api_group = QFrame()
        api_group.setObjectName("api_group")  # 添加对象名称
        api_group.setFrameShape(QFrame.Shape.StyledPanel)
        api_layout = QVBoxLayout(api_group)
        
        api_title = TypewriterLabel("API设置")
        api_title.complete_typing()  # 立即完成打字效果
        api_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        api_title.setStyleSheet("color: #33FF33; background-color: #002200; padding: 3px; font-weight: bold; border: 1px solid #33FF33;")
        api_title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        api_layout.addWidget(api_title)
        
        # API类型选择
        self.api_combo = QComboBox()
        self.api_combo.addItems(["OpenAI", "Claude", "DeepSeek", "OpenRouter"])
        self.api_combo.setFont(self.terminal_font)  # 确保使用终端字体
        self.api_combo.currentTextChanged.connect(self.on_api_type_changed)
        api_layout.addWidget(self.api_combo)
        
        # API设置按钮
        api_settings_btn = QPushButton("API设置")
        api_settings_btn.setFont(self.terminal_font)  # 确保使用终端字体
        api_settings_btn.clicked.connect(self.open_api_settings)
        api_layout.addWidget(api_settings_btn)
        
        # 测试API连接
        test_api_btn = QPushButton("测试连接")
        test_api_btn.setFont(self.terminal_font)  # 确保使用终端字体
        test_api_btn.clicked.connect(self.test_api_connection)
        api_layout.addWidget(test_api_btn)
        
        layout.addWidget(api_group)
        
        # 翻译操作区域
        translation_group = QFrame()
        translation_group.setObjectName("translation_group")  # 添加对象名称
        translation_group.setFrameShape(QFrame.Shape.StyledPanel)
        translation_layout = QVBoxLayout(translation_group)
        
        translation_title = TypewriterLabel("翻译操作")
        translation_title.complete_typing()  # 立即完成打字效果
        translation_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        translation_title.setStyleSheet("color: #33FF33; background-color: #002200; padding: 3px; font-weight: bold; border: 1px solid #33FF33;")
        translation_title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        translation_layout.addWidget(translation_title)
        
        # 翻译选中项按钮
        self.translate_selected_btn = QPushButton("翻译选中项")
        self.translate_selected_btn.setFont(self.terminal_font)  # 确保使用终端字体
        self.translate_selected_btn.clicked.connect(self.translate_selected_items)
        translation_layout.addWidget(self.translate_selected_btn)
        
        # 翻译全部按钮
        self.translate_all_btn = QPushButton("翻译全部")
        self.translate_all_btn.setFont(self.terminal_font)  # 确保使用终端字体
        self.translate_all_btn.clicked.connect(self.translate_all_items)
        translation_layout.addWidget(self.translate_all_btn)
        
        layout.addWidget(translation_group)
        
        # 底部填充
        layout.addStretch(1)
        
        return control_panel
        
    def create_translation_table(self):
        """创建翻译表格"""
        table = QTableWidget(0, 3)  # 0行，3列
        table.setHorizontalHeaderLabels(["条目ID", "原文", "译文"])
        table.setFont(self.terminal_font)  # 确保使用终端字体
        
        # 设置列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID列自适应内容
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 原文列伸展
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 译文列伸展
        
        # 设置表格属性
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)  # 隐藏垂直表头
        
        # 启用自动换行
        table.setWordWrap(True)
        
        # 设置行高自适应内容
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # 当单元格内容改变时更新进度图表
        table.itemChanged.connect(self.update_translation_stats)
        
        # 启用右键菜单
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_translation_table_context_menu)
        
        return table

    def create_progress_chart(self):
        """创建翻译进度饼图"""
        progress_chart = ProgressChart()
        
        # 设置初始进度数据
        translated_count = 0
        total_count = 0
        progress_chart.set_progress(translated_count, total_count)
        
        return progress_chart
    
    def create_bottom_area(self):
        """创建底部区域 - 数据监控"""
        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.Shape.StyledPanel)
        bottom_frame.setMaximumHeight(100)
        
        layout = QHBoxLayout(bottom_frame)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建一个带有CRT效果的背景
        data_stream = DataStreamBackground()
        data_stream.setMinimumHeight(80)
        layout.addWidget(data_stream)
        
        # 添加一个状态日志区域
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setFixedHeight(80)
        self.status_log.setFont(self.terminal_font)  # 确保使用终端字体
        self.status_log.setStyleSheet("""
            background-color: #000000;
            color: #33FF33;
            border: 1px solid #33FF33;
        """)
        layout.addWidget(self.status_log, 2)  # 日志占据空间的2/3
        
        return bottom_frame
        
    def get_text_color_with_saturation(self):
        """根据饱和度值计算文字颜色"""
        # 解析原始颜色
        color = QColor(TEXT_COLOR)
        h, s, v, a = color.getHsvF()
        
        # 应用饱和度值
        s = self.text_saturation / 100.0
        
        # 创建新颜色
        new_color = QColor.fromHsvF(h, s, v, a)
        return new_color
    
    def start_terminal_effects(self):
        """启动终端效果"""
        # 启动终端时钟
        self.terminal_clock.start_clock()
        
        # 这里可以添加其他动态效果的启动
    
    def display_welcome_message(self):
        """显示欢迎消息"""
        self.status_label.set_text("欢迎使用联盟项目UDS终端 - 潜渊症汉化工具 v1.5")
        self.add_log_entry("系统初始化完成")
        self.add_log_entry("潜渊症汉化工具准备就绪")
        self.add_log_entry("可将潜渊症XML文件拖放到指定区域或使用导入按钮")
    
    def add_log_entry(self, message):
        """添加一条日志条目"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.status_log.append(log_entry)
        # 自动滚动到底部
        self.status_log.verticalScrollBar().setValue(self.status_log.verticalScrollBar().maximum())
    
    def update_progress(self):
        """更新进度条"""
        if self.current_progress < self.progress_target:
            increment = max(1, int((self.progress_target - self.current_progress) / 10))
            self.current_progress = min(self.current_progress + increment, self.progress_target)
            self.progress_bar.setValue(self.current_progress)
        else:
            self.progress_timer.stop()
            
    def on_translation_completed(self, original_text, translated_text):
        """翻译完成的回调"""
        if not self.is_translating:
            return
        
        # 查找原文对应的行
        for row in range(self.translation_table.rowCount()):
            item = self.translation_table.item(row, 1)
            if item and item.text() == original_text:
                # 设置译文
                self.translation_table.setItem(row, 2, QTableWidgetItem(translated_text))
                break
        
        # 先更新XML条目，确保翻译被保存
        self.update_xml_from_table()
        
        # 更新统计信息
        self.update_translation_stats()
        
        # 显式更新饼图 - 确保显示正确
        entries = self.xml_handler.get_translation_entries()
        if entries:
            total_count = len(entries)
            translated_count = sum(1 for entry in entries 
                                  if entry['translation'] != entry['original'] 
                                  and entry['translation'].strip())
            self.progress_chart.set_progress(translated_count, total_count)
            self.translation_stats_widget.update_translation_count(translated_count, total_count)
        
        # 继续翻译队列中的下一项
        if self.translation_queue:
            row, text = self.translation_queue[0]
            self.translation_queue = self.translation_queue[1:]
            
            # 更新状态
            total = self.translation_table.rowCount()
            progress = int((total - len(self.translation_queue) - 1) / total * 100)
            self.progress_bar.setValue(progress)
            self.status_label.set_text(f"正在翻译第 {total - len(self.translation_queue)} 条，共 {total} 条...")
            
            # 调用翻译器
            self.translator.translate(text)
        else:
            # 翻译完成
            self.is_translating = False
            self.progress_bar.setValue(100)
            self.add_log_entry("翻译完成")
            self.status_label.set_text("翻译完成!")
    
    def on_translation_error(self, error_message):
        """翻译错误的回调"""
        self.add_log_entry(f"翻译错误: {error_message}")
        
    # 拖放事件处理
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖入事件"""
        # 检查是否有文件拖入
        if event.mimeData().hasUrls():
            # 获取所有URL
            urls = event.mimeData().urls()
            # 检查是否有XML文件
            for url in urls:
                if url.toLocalFile().lower().endswith('.xml'):
                    # 接受拖放
                    event.acceptProposedAction()
                    # 显示拖放高亮
                    self.drop_highlight_frame.setGeometry(self.drop_area.geometry())
                    self.drop_highlight_frame.raise_()
                    self.drop_highlight_frame.show()
                    return
        
        # 如果没有XML文件，拒绝拖放
        event.ignore()
    
    def dragMoveEvent(self, event):
        """处理拖动移动事件"""
        # 如果有XML文件，接受拖放
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.xml'):
                    event.acceptProposedAction()
                    return
        
        # 否则拒绝
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """处理拖动离开事件"""
        # 隐藏拖放高亮
        self.drop_highlight_frame.hide()
        event.accept()
    
    def dropEvent(self, event: QDropEvent):
        """处理拖放事件"""
        # 隐藏拖放高亮
        self.drop_highlight_frame.hide()
        
        # 检查是否有文件拖入
        if event.mimeData().hasUrls():
            # 获取所有URL
            urls = event.mimeData().urls()
            
            # 查找第一个XML文件
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.xml'):
                    # 接受拖放
                    event.acceptProposedAction()
                    
                    # 加载XML文件
                    self.add_log_entry(f"正在导入拖放的文件: {file_path}")
                    
                    # 清空表格
                    self.translation_table.setRowCount(0)
                    
                    # 加载XML文件
                    if self.xml_handler.load_file(file_path):
                        self.populate_translation_table()
                        self.add_log_entry(f"成功加载文件: {os.path.basename(file_path)}")
                        self.update_translation_stats()
                        
                        # 更新分类过滤器
                        self.update_category_filter()
                    else:
                        self.add_log_entry("文件加载失败")
                    
                    return
        
        # 如果没有XML文件，拒绝拖放
        event.ignore()
        
        # 如果还在翻译队列中，则继续下一个
        if self.is_translating and self.translation_queue:
            row, text = self.translation_queue[0]
            self.translation_queue = self.translation_queue[1:]
            
            # 更新状态
            total = self.translation_table.rowCount()
            progress = int((total - len(self.translation_queue) - 1) / total * 100)
            self.progress_bar.setValue(progress)
            self.status_label.set_text(f"正在翻译第 {total - len(self.translation_queue)} 条，共 {total} 条...")
            
            # 调用翻译器
            self.translator.translate(text)
        else:
            # 翻译完成或中止
            self.is_translating = False
            self.progress_bar.setValue(100)
            self.add_log_entry("翻译过程中止")
            self.status_label.set_text("翻译过程中止!")
    
    def on_xml_progress(self, value, message):
        """XML处理进度更新的回调"""
        self.progress_bar.setValue(value)
        self.status_label.set_text(message)
    
    def on_xml_error(self, error_message):
        """XML处理错误的回调"""
        self.add_log_entry(f"XML处理错误: {error_message}")
        QMessageBox.critical(self, "XML处理错误", error_message)
    
    def populate_translation_table(self):
        """将所有翻译条目填充到表格中"""
        # 获取所有翻译条目
        entries = self.xml_handler.get_translation_entries()
        
        # 填充表格
        self.populate_table_with_entries(entries)
    
    def populate_table_with_entries(self, entries):
        """使用给定的条目列表填充表格"""
        # 禁用表格更新，提高性能
        self.translation_table.setUpdatesEnabled(False)
        self.translation_table.blockSignals(True)
        
        # 设置表格行数
        row_count = len(entries)
        self.translation_table.setRowCount(row_count)
        
        # 填充数据
        for row, entry in enumerate(entries):
            # 填充ID列
            id_item = QTableWidgetItem(entry['id'])
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # ID不可编辑
            self.translation_table.setItem(row, 0, id_item)
            
            # 填充原文列
            original_item = QTableWidgetItem(entry['original'])
            original_item.setFlags(original_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 原文不可编辑
            self.translation_table.setItem(row, 1, original_item)
            
            # 填充译文列
            translation_item = QTableWidgetItem(entry['translation'])
            self.translation_table.setItem(row, 2, translation_item)
        
        # 恢复表格更新
        self.translation_table.blockSignals(False)
        self.translation_table.setUpdatesEnabled(True)
        
        # 调整行高
        self.translation_table.resizeRowsToContents()
    
    def update_category_filter(self):
        """更新物品分类下拉框"""
        # 保存当前选中的分类
        current_category = self.category_combo.currentText()
        
        # 获取所有物品标签
        categories = ["全部"] + self.xml_handler.get_item_tags()
        
        # 清空下拉框并填充新分类
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItems(categories)
        
        # 尝试恢复之前选中的分类
        index = self.category_combo.findText(current_category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.category_combo.blockSignals(False)
    
    def import_file(self):
        """导入XML文件处理"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择XML文件",
            "",
            "XML文件 (*.xml);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        self.add_log_entry(f"正在导入文件: {file_path}")
        
        # 清空表格
        self.translation_table.setRowCount(0)
        
        # 加载XML文件
        if self.xml_handler.load_file(file_path):
            self.populate_translation_table()
            self.add_log_entry(f"成功加载文件: {os.path.basename(file_path)}")
            self.update_translation_stats()
            
            # 更新分类过滤器
            self.update_category_filter()
        else:
            self.add_log_entry("文件加载失败")
    
    def export_translation(self):
        """导出翻译结果"""
        if not self.xml_handler.get_translation_entries():
            QMessageBox.warning(self, "导出错误", "没有可导出的翻译内容")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存XML文件",
            "",
            "XML文件 (*.xml);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        self.add_log_entry(f"正在导出翻译到: {file_path}")
        
        # 保存XML文件
        if self.xml_handler.save_xml(file_path):
            self.add_log_entry(f"成功导出翻译到: {os.path.basename(file_path)}")
        else:
            self.add_log_entry("导出翻译失败")
    
    def filter_entries(self):
        """根据筛选条件过滤表格内容"""
        # 获取筛选条件
        entry_type = None  # 现在不按条目类型筛选
        search_text = self.search_edit.text()
        
        # 获取物品分类
        category = self.category_combo.currentText()
        if category == "全部":
            category = None
        
        # 翻译状态筛选
        translated_only = self.translated_only_check.isChecked()
        untranslated_only = self.untranslated_only_check.isChecked()
        
        # 如果两个都选中或都未选中，则不按翻译状态筛选
        if translated_only and untranslated_only:
            translated_only = False
            untranslated_only = False
        
        # 筛选条目
        filtered_entries = self.xml_handler.filter_entries(
            entry_type=entry_type,
            search_text=search_text,
            translated_only=translated_only,
            item_category=category,
            untranslated_only=untranslated_only
        )
        
        # 清空表格
        self.translation_table.setRowCount(0)
        
        # 填充筛选后的条目
        self.populate_table_with_entries(filtered_entries)
    
    def update_translation_stats(self):
        """更新翻译统计"""
        entries = self.xml_handler.get_translation_entries()
        
        if not entries:
            self.progress_chart.set_progress(0, 0)
            self.translation_stats_widget.update_translation_count(0, 0)
            return
        
        total_count = len(entries)
        translated_count = 0
        
        # 计算已翻译数量 - 同时考虑常规翻译和标记的条目
        for entry in entries:
            # 检查是否是正常翻译的条目（译文与原文不同且非空）
            is_translated = (entry['translation'] != entry['original'] and entry['translation'].strip())
            
            # 检查是否是已标记的条目（以"[已标记]"开头）
            is_marked = entry['translation'].strip().startswith("[已标记]")
            
            # 两种情况都算作已翻译
            if is_translated or is_marked:
                translated_count += 1
        
        # 打印调试信息
        print(f"统计更新: 已翻译 {translated_count}/{total_count} = {(translated_count/total_count*100 if total_count else 0):.1f}%")
        
        # 更新饼图
        self.progress_chart.set_progress(translated_count, total_count)
        
        # 更新翻译统计组件
        self.translation_stats_widget.update_translation_count(
            translated_count, 
            total_count
        )
    
    def import_excel(self):
        """导入Excel文件"""
        if not self.xml_handler.get_translation_entries():
            QMessageBox.warning(self, "导入错误", "请先加载XML文件")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Excel文件",
            "",
            "Excel文件 (*.xlsx *.xls);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        self.add_log_entry(f"正在从Excel导入翻译: {file_path}")
        
        # 导入Excel文件
        if self.xml_handler.import_from_excel(file_path):
            # 刷新表格
            self.filter_entries()  # 使用当前筛选条件重新加载表格
            self.update_translation_stats()
            self.add_log_entry(f"成功从Excel导入翻译: {os.path.basename(file_path)}")
        else:
            self.add_log_entry("Excel导入失败")
    
    def export_excel(self):
        """导出翻译到Excel文件"""
        if not self.xml_handler.get_translation_entries():
            QMessageBox.warning(self, "导出错误", "没有可导出的翻译内容")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存Excel文件",
            "",
            "Excel文件 (*.xlsx);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        # 确保文件有.xlsx扩展名
        if not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'
        
        self.add_log_entry(f"正在导出翻译到Excel: {file_path}")
        
        # 导出Excel文件
        if self.xml_handler.export_to_excel(file_path):
            self.add_log_entry(f"成功导出翻译到Excel: {os.path.basename(file_path)}")
        else:
            self.add_log_entry("Excel导出失败")
    
    def test_api_connection(self, show_message_box=True):
        """测试当前API连接
        
        Args:
            show_message_box: 是否显示弹窗，手动测试时为True，自动检测时为False
        """
        self.add_log_entry("正在测试API连接...")
        
        # 显示API测试中的状态
        self.status_label.set_text("正在测试API连接...")
        
        # 创建一个测试短文本
        test_text = "This is a test message."
        
        # 使用当前API尝试翻译
        try:
            self.translator.translation_completed.disconnect(self.on_translation_completed)
            self.translator.error_occurred.disconnect(self.on_translation_error)
            
            # 连接临时的测试回调，传递是否显示弹窗参数
            self.translator.translation_completed.connect(
                lambda orig, trans: self.on_api_test_success(orig, trans, show_message_box)
            )
            self.translator.error_occurred.connect(
                lambda err: self.on_api_test_error(err, show_message_box)
            )
            
            # 启动翻译测试
            self.translator.translate(test_text)
            
        except Exception as e:
            self.add_log_entry(f"API测试错误: {str(e)}")
            self.status_label.set_text("API测试失败")
            
            # 重新连接原始信号处理器
            self.translator.translation_completed.connect(self.on_translation_completed)
            self.translator.error_occurred.connect(self.on_translation_error)
    
    def on_api_test_success(self, original_text, translated_text, show_message_box=True):
        """API测试成功回调
        
        Args:
            original_text: 测试文本原文
            translated_text: 测试文本译文
            show_message_box: 是否显示弹窗，默认为True
        """
        # 重新连接原始信号处理器
        self.translator.translation_completed.disconnect()
        self.translator.error_occurred.disconnect()
        self.translator.translation_completed.connect(self.on_translation_completed)
        self.translator.error_occurred.connect(self.on_translation_error)
        
        # 更新状态
        self.add_log_entry(f"API测试成功: {translated_text}")
        self.status_label.set_text("API连接测试成功!")
        self.translation_stats_widget.set_api_status(True)
        
        # 仅在手动测试时显示弹窗
        if show_message_box:
            QMessageBox.information(self, "API测试", "API连接测试成功!")
    
    def on_api_test_error(self, error_message, show_message_box=True):
        """API测试错误回调
        
        Args:
            error_message: 错误信息
            show_message_box: 是否显示弹窗，默认为True
        """
        # 重新连接原始信号处理器
        self.translator.translation_completed.disconnect()
        self.translator.error_occurred.disconnect()
        self.translator.translation_completed.connect(self.on_translation_completed)
        self.translator.error_occurred.connect(self.on_translation_error)
        
        # 更新状态
        self.add_log_entry(f"API测试失败: {error_message}")
        self.status_label.set_text("API连接测试失败")
        self.translation_stats_widget.set_api_status(False)
        
        # 仅在手动测试时显示弹窗
        if show_message_box:
            QMessageBox.critical(self, "API测试", f"API连接测试失败: {error_message}")
    
    def on_api_type_changed(self, api_type):
        """API类型改变时的处理"""
        # 转换为小写并处理中文名称映射
        if api_type == "OpenAI":
            api_type = "openai"
        elif api_type == "Claude":
            api_type = "claude"
        elif api_type == "DeepSeek":
            api_type = "deepseek"
        elif api_type == "OpenRouter":
            api_type = "openrouter"
        
        # 如果API类型没有变化，不做任何处理
        if api_type == self.current_api_type:
            return
        
        self.add_log_entry(f"切换API类型: {api_type}")
        
        # 更新当前API类型
        self.current_api_type = api_type
        
        # 创建新的API对象
        self.translator = TranslationAPI.create_api(api_type)
        
        # 重新连接信号
        self.translator.translation_completed.connect(self.on_translation_completed)
        self.translator.error_occurred.connect(self.on_translation_error)
        
        # 重置API状态
        self.translation_stats_widget.set_api_status(None)
    
    def open_api_settings(self):
        """打开API设置对话框"""
        dialog = APISettingsDialog(self)
        
        # 根据当前API类型选择对应的选项卡
        api_names = {
            "openai": 0,
            "claude": 1,
            "deepseek": 2,
            "openrouter": 3,
            "baidu": 4,
            "youdao": 5,
            "custom": 6
        }
        
        if self.current_api_type in api_names:
            dialog.tab_widget.setCurrentIndex(api_names[self.current_api_type])
        
        if dialog.exec():
            # 如果用户点击确定，更新API设置
            self.add_log_entry(f"更新API设置: {self.current_api_type}")
            
            # 刷新API实例
            self.translator = TranslationAPI.create_api(self.current_api_type)
            self.translator.translation_completed.connect(self.on_translation_completed)
            self.translator.error_occurred.connect(self.on_translation_error)
    
    def translate_selected_items(self):
        """翻译选中项"""
        if not self.xml_handler.get_translation_entries():
            QMessageBox.warning(self, "翻译错误", "没有可翻译的内容")
            return
        
        # 获取选中的行
        selected_rows = set()
        for item in self.translation_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            self.add_log_entry("未选中任何条目")
            return
        
        # 准备翻译队列
        self.translation_queue = []
        for row in selected_rows:
            # 获取原文
            original_item = self.translation_table.item(row, 1)
            if original_item and original_item.text():
                # 检查是否已翻译
                translation_item = self.translation_table.item(row, 2)
                if not translation_item or not translation_item.text() or translation_item.text() == original_item.text():
                    self.translation_queue.append((row, original_item.text()))
        
        if not self.translation_queue:
            self.add_log_entry("选中项已全部翻译")
            return
        
        # 开始翻译
        self.start_translation()
    
    def translate_all_items(self):
        """翻译所有未翻译的条目"""
        if not self.xml_handler.get_translation_entries():
            QMessageBox.warning(self, "翻译错误", "没有可翻译的内容")
            return
        
        # 准备翻译队列
        self.translation_queue = []
        for row in range(self.translation_table.rowCount()):
            # 获取原文
            original_item = self.translation_table.item(row, 1)
            if original_item and original_item.text():
                # 检查是否已翻译
                translation_item = self.translation_table.item(row, 2)
                if not translation_item or not translation_item.text() or translation_item.text() == original_item.text():
                    self.translation_queue.append((row, original_item.text()))
        
        if not self.translation_queue:
            self.add_log_entry("所有条目已翻译")
            return
        
        # 开始翻译
        self.start_translation()
    
    def start_translation(self):
        """开始翻译队列"""
        if not self.translation_queue:
            return
        
        # 设置正在翻译标志
        self.is_translating = True
        
        # 更新状态
        total = len(self.translation_queue)
        self.add_log_entry(f"开始翻译 {total} 个条目")
        self.status_label.set_text(f"正在翻译第 1 条，共 {total} 条...")
        self.progress_bar.setValue(0)
        
        # 开始翻译第一个条目
        row, text = self.translation_queue[0]
        self.translation_queue = self.translation_queue[1:]
        self.translator.translate(text)
        
    def mark_selected_as_translated(self):
        """将选中的条目标记为已翻译（不实际翻译，只更改状态）"""
        selected_rows = set()
        for item in self.translation_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            self.add_log_entry("未选中任何条目")
            return
        
        # 阻止表格信号，避免每次单元格变化都触发更新
        self.translation_table.blockSignals(True)
        
        count = 0
        for row in selected_rows:
            # 检查原文列是否有内容
            original_item = self.translation_table.item(row, 1)
            if original_item and original_item.text():
                # 获取原文文本
                original_text = original_item.text()
                
                # 获取当前译文状态（如果存在）
                translation_item = self.translation_table.item(row, 2)
                
                # 使用明显的前缀标记译文，确保能被统计识别
                translation_text = "[已标记] " + original_text
                self.translation_table.setItem(row, 2, QTableWidgetItem(translation_text))
                count += 1
        
        # 恢复表格信号
        self.translation_table.blockSignals(False)
        
        if count > 0:
            # 先更新XML条目，确保标记被保存
            self.update_xml_from_table()
            
            # 然后强制刷新统计信息
            self.update_translation_stats()
            
            # 再次更新饼图 - 确保显示正确
            # 获取翻译状态并更新饼图显示
            entries = self.xml_handler.get_translation_entries()
            if entries:
                total_count = len(entries)
                translated_count = sum(1 for entry in entries 
                                       if entry['translation'] != entry['original'] 
                                       and entry['translation'].strip())
                self.progress_chart.set_progress(translated_count, total_count)
                self.translation_stats_widget.update_translation_count(translated_count, total_count)
            
            # 记录日志
            self.add_log_entry(f"已将 {count} 个选中条目标记为已翻译")
        else:
            self.add_log_entry("选中条目已全部翻译，无需标记")
    
    def update_xml_from_table(self):
        """将表格中的翻译更新到XML处理器"""
        # 更新XML处理器中的翻译
        for row in range(self.translation_table.rowCount()):
            # 获取ID和译文
            id_item = self.translation_table.item(row, 0)
            translation_item = self.translation_table.item(row, 2)
            
            if id_item and translation_item:
                entry_id = id_item.text()
                translation = translation_item.text()
                
                # 更新XML处理器中的翻译
                self.xml_handler.update_translation(entry_id, translation)
    
    def show_translation_table_context_menu(self, position):
        """显示翻译表格的右键菜单"""
        # 获取鼠标点击位置的行和列
        row = self.translation_table.rowAt(position.y())
        column = self.translation_table.columnAt(position.x())
        
        # 如果点击位置不存在行或列，则不显示菜单
        if row < 0 or column < 0:
            return
        
        # 创建右键菜单
        menu = QMenu(self)
        
        # 如果点击的是原文列，添加"复制到译文"选项
        if column == 1:  # 原文列
            copy_to_translation_action = menu.addAction("复制到译文")
            copy_to_translation_action.triggered.connect(lambda: self.copy_original_to_translation(row))
        
        # 如果菜单不为空，在鼠标位置显示
        if not menu.isEmpty():
            menu.exec(self.translation_table.viewport().mapToGlobal(position))
    
    def copy_original_to_translation(self, row):
        """将原文复制到译文"""
        if row < 0 or row >= self.translation_table.rowCount():
            return
        
        # 获取原文
        original_item = self.translation_table.item(row, 1)
        if original_item and original_item.text():
            original_text = original_item.text()
            
            # 创建译文单元格项
            translation_item = QTableWidgetItem(original_text)
            
            # 设置译文单元格项
            self.translation_table.setItem(row, 2, translation_item)
            
            # 更新XML处理器中的翻译
            id_item = self.translation_table.item(row, 0)
            if id_item:
                entry_id = id_item.text()
                self.xml_handler.update_translation(entry_id, original_text)
            
            # 更新统计信息
            self.add_log_entry(f"已将第 {row+1} 行原文复制到译文")
    
    def mark_all_as_translated(self):
        """将所有未翻译条目标记为已翻译（不实际翻译，只更改状态）"""
        # 创建进度对话框
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("正在处理")
        progress_dialog.setText("正在标记所有未翻译条目...\n这可能需要一些时间，请耐心等待。")
        progress_dialog.setIcon(QMessageBox.Icon.Information)
        progress_dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
        
        # 添加进度条
        progress_bar = QProgressBar(progress_dialog)
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #33FF33;
                border-radius: 0px;
                background-color: #000000;
                text-align: center;
                color: #33FF33;
                min-height: 20px;
            }
            QProgressBar::chunk {
                background-color: #33FF33;
            }
        """)
        
        # 获取对话框的布局并添加进度条
        layout = progress_dialog.layout()
        layout.addWidget(progress_bar, 1, 0, 1, layout.columnCount())
        
        # 显示对话框，但不阻塞界面
        progress_dialog.setModal(False)
        progress_dialog.show()
        
        # 确保对话框显示并处理事件
        QApplication.processEvents()
        
        try:
            # 阻止表格信号，避免每次单元格变化都触发更新
            self.translation_table.blockSignals(True)
            
            # 获取需要检查的总行数
            total_rows = self.translation_table.rowCount()
            
            # 首先扫描所有需要标记的行，避免在处理过程中计算
            rows_to_mark = []
            for row in range(total_rows):
                # 检查原文列是否有内容
                original_item = self.translation_table.item(row, 1)
                if original_item and original_item.text():
                    # 检查译文列是否为空或与原文相同
                    translation_item = self.translation_table.item(row, 2)
                    
                    # 条件1：译文为空
                    is_empty = not translation_item or not translation_item.text().strip()
                    
                    # 条件2：译文与原文相同（未翻译）
                    is_same_as_original = False
                    if translation_item and translation_item.text():
                        is_same_as_original = translation_item.text() == original_item.text()
                    
                    # 条件3：检查是否已经标记为已翻译（防止重复标记）
                    is_already_marked = False
                    if translation_item and translation_item.text():
                        is_already_marked = translation_item.text().strip().startswith("[已标记]")
                    
                    # 如果未翻译且未标记，则加入标记列表
                    if (is_empty or is_same_as_original) and not is_already_marked:
                        rows_to_mark.append(row)
                
                # 更新进度条 - 扫描阶段占50%
                if row % 10 == 0 or row == total_rows - 1:  # 每10行更新一次UI
                    progress_bar.setValue(int(row / total_rows * 50))
                    QApplication.processEvents()  # 确保UI响应
                    
                    # 检查是否点击了取消按钮
                    if not progress_dialog.isVisible():
                        self.translation_table.blockSignals(False)
                        self.add_log_entry("标记过程被取消")
                        return
            
            # 标记阶段 - 占另外50%的进度
            count = 0
            total_to_mark = len(rows_to_mark)
            
            # 分批处理，每处理一批就更新UI
            batch_size = 50  # 每批处理的行数
            for i in range(0, total_to_mark, batch_size):
                # 处理当前批次
                end = min(i + batch_size, total_to_mark)
                for j in range(i, end):
                    row = rows_to_mark[j]
                    original_item = self.translation_table.item(row, 1)
                    # 使用明显的前缀标记译文，确保与mark_selected_as_translated功能一致
                    original_text = original_item.text()
                    translation_text = "[已标记] " + original_text
                    self.translation_table.setItem(row, 2, QTableWidgetItem(translation_text))
                    count += 1
                
                # 更新进度 - 标记阶段占50%-100%
                if total_to_mark > 0:  # 避免除以零
                    current_progress = 50 + int((end / total_to_mark) * 50)
                    progress_bar.setValue(current_progress)
                
                # 处理UI事件
                QApplication.processEvents()
                
                # 检查是否点击了取消按钮
                if not progress_dialog.isVisible():
                    break
            
            # 确保进度条显示100%完成
            progress_bar.setValue(100)
            QApplication.processEvents()
            
            if count > 0:
                # 先更新XML条目，确保标记被保存
                self.update_xml_from_table()
                
                # 手动计算翻译进度，避免依赖缓存
                entries = self.xml_handler.get_translation_entries()
                if entries:
                    total_count = len(entries)
                    translated_count = 0
                    
                    # 强制计算已翻译数量，不依赖缓存
                    for entry in entries:
                        if ((entry['translation'] != entry['original'] and entry['translation'].strip()) or 
                            (entry['translation'].strip().startswith("[已标记]"))):
                            translated_count += 1
                    
                    # 强制更新饼图和统计
                    self.add_log_entry(f"正在更新进度统计：已翻译 {translated_count}/{total_count}")
                    self.progress_chart.set_progress(translated_count, total_count)
                    self.translation_stats_widget.update_translation_count(translated_count, total_count)
                
                # 刷新统计信息
                self.update_translation_stats()
                
                # 记录日志
                self.add_log_entry(f"已将所有 {count} 个未翻译条目标记为已翻译")
            else:
                self.add_log_entry("所有条目已翻译，无需标记")
                
        finally:
            # 无论如何都恢复表格信号并关闭进度对话框
            self.translation_table.blockSignals(False)
            
            # 关闭进度对话框
            if progress_dialog.isVisible():
                progress_dialog.close()
