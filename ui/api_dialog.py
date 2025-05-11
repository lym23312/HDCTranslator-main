#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API设置对话框
用于配置翻译API的参数
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QWidget, QFormLayout, QComboBox,
    QMessageBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSettings, pyqtSlot
from PyQt6.QtGui import QFont

from core.translation_api import (
    TranslationAPI, OpenRouterTranslator
)

class APISettingsDialog(QDialog):
    """翻译API设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("翻译API设置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # 设置默认按钮，使得按下回车键时验证并关闭对话框
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # 加载保存的设置
        self.settings = QSettings("HDCTranslator", "Translation")
        
        # 创建API实例
        self.openrouter_api = OpenRouterTranslator()
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建OpenRouter设置面板
        self.main_panel = QWidget()
        self.main_layout = QFormLayout(self.main_panel)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        
        # 创建OpenRouter设置页面
        self.create_openrouter_settings()
        
        layout.addWidget(self.main_panel)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.test_button = QPushButton("测试连接")
        self.test_button.clicked.connect(self.test_connection)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        button_layout.addWidget(self.button_box)
        
        layout.addLayout(button_layout)
        
        # 加载保存的设置到控件
        self.load_settings()
    
    def create_openrouter_settings(self):
        """创建OpenRouter设置页面"""
        # API密钥
        self.openrouter_key_input = QLineEdit()
        self.openrouter_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openrouter_key_input.setPlaceholderText("输入你的OpenRouter API密钥")
        self.main_layout.addRow("API密钥:", self.openrouter_key_input)
        
        # 模型选择
        self.openrouter_model_combo = QComboBox()
        self.openrouter_model_combo.addItems([
            "anthropic/claude-3-opus:beta",
            "anthropic/claude-3-5-sonnet-20240620",
            "anthropic/claude-3-opus-20240229",
            "anthropic/claude-3-sonnet-20240229",
            "anthropic/claude-3-haiku-20240307",
            "openai/gpt-4o",
            "openai/gpt-4-turbo",
            "openai/gpt-4",
            "openai/gpt-3.5-turbo", 
            "meta-llama/llama-3-70b-instruct",
            "meta-llama/llama-3-8b-instruct",
            "mistralai/mistral-7b-instruct",
            "mistralai/mixtral-8x7b-instruct",
            "mistralai/mistral-large",
            "google/gemma-7b-it",
            "google/gemini-pro",
            "google/gemini-1.5-pro-latest"
        ])
        self.main_layout.addRow("模型:", self.openrouter_model_combo)
        
        # API基础URL
        self.openrouter_url_input = QLineEdit()
        self.openrouter_url_input.setPlaceholderText("https://openrouter.ai/api/v1/chat/completions")
        self.main_layout.addRow("API URL:", self.openrouter_url_input)
        
        # 说明文本
        instructions = QLabel(
            "OpenRouter是一个API聚合服务，提供对多种大型语言模型的统一访问。\n"
            "需要在OpenRouter网站注册并获取API密钥。\n"
            "支持OpenAI、Anthropic Claude、Meta Llama、Mistral等多种模型。\n"
            "网址: https://openrouter.ai"
        )
        instructions.setStyleSheet("color: #33FF33;")
        instructions.setWordWrap(True)
        self.main_layout.addRow(instructions)
    
    def load_settings(self):
        """从设置加载值到控件"""
        # OpenRouter设置
        self.openrouter_key_input.setText(self.settings.value("openrouter/api_key", ""))
        model = self.settings.value("openrouter/model", "anthropic/claude-3-opus:beta")  # 更新默认模型
        index = self.openrouter_model_combo.findText(model)
        if index >= 0:
            self.openrouter_model_combo.setCurrentIndex(index)
        self.openrouter_url_input.setText(self.settings.value("openrouter/base_url", "https://openrouter.ai/api/v1/chat/completions"))
    
    def save_settings(self):
        """保存控件值到设置"""
        # OpenRouter设置
        self.openrouter_api.set_api_key(self.openrouter_key_input.text())
        self.openrouter_api.set_model(self.openrouter_model_combo.currentText())
        self.openrouter_api.set_base_url(self.openrouter_url_input.text())
    
    def accept(self):
        """保存设置并关闭对话框"""
        self.save_settings()
        super().accept()
    
    @pyqtSlot()
    def test_connection(self):
        """测试API连接"""
        # 先保存当前设置
        self.save_settings()
        
        # 测试OpenRouter连接
        api = self.openrouter_api
        api_name = "OpenRouter"
        
        QMessageBox.information(self, "测试中", f"正在测试{api_name}连接，请稍候...")
        
        # 测试连接
        success = api.test_connection()
        
        if success:
            QMessageBox.information(self, "连接成功", f"{api_name}连接测试成功!")
        else:
            QMessageBox.warning(self, "连接失败", f"{api_name}连接测试失败。请检查设置。")

# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    dialog = APISettingsDialog()
    dialog.show()
    
    sys.exit(app.exec())
