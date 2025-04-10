#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API设置对话框
用于配置各种翻译API的参数
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTabWidget, QWidget, QFormLayout, QComboBox,
    QMessageBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSettings, pyqtSlot
from PyQt6.QtGui import QFont

from core.translation_api import (
    TranslationAPI, OpenAITranslator, ClaudeTranslator, DeepSeekTranslator,
    OpenRouterTranslator
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
        self.openai_api = OpenAITranslator()
        self.claude_api = ClaudeTranslator()
        self.deepseek_api = DeepSeekTranslator()
        self.openrouter_api = OpenRouterTranslator()
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Courier New", 10))
        
        # 创建各个API的设置页面
        self.create_openai_tab()
        self.create_claude_tab()
        self.create_deepseek_tab()
        self.create_openrouter_tab()
        
        layout.addWidget(self.tab_widget)
        
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
    
    def create_openai_tab(self):
        """创建OpenAI设置页面"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # API密钥
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_input.setPlaceholderText("输入你的OpenAI API密钥")
        layout.addRow("API密钥:", self.openai_key_input)
        
        # 模型选择
        self.openai_model_combo = QComboBox()
        self.openai_model_combo.addItems([
            "gpt-4o", 
            "gpt-4-turbo",
            "gpt-4", 
            "gpt-3.5-turbo"
        ])
        layout.addRow("模型:", self.openai_model_combo)
        
        # API基础URL
        self.openai_url_input = QLineEdit()
        self.openai_url_input.setPlaceholderText("https://api.openai.com/v1/chat/completions")
        layout.addRow("API URL:", self.openai_url_input)
        
        # 说明文本
        instructions = QLabel(
            "OpenAI API用于高质量翻译。需要设置有效的API密钥。\n"
            "默认使用gpt-4o模型，也可以选择其他模型。\n"
            "如果使用代理服务，可以修改API基础URL。"
        )
        instructions.setStyleSheet("color: #33FF33;")
        instructions.setWordWrap(True)
        layout.addRow(instructions)
        
        self.tab_widget.addTab(tab, "OpenAI")
        
    def create_claude_tab(self):
        """创建Claude设置页面"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # API密钥
        self.claude_key_input = QLineEdit()
        self.claude_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.claude_key_input.setPlaceholderText("输入你的Anthropic Claude API密钥")
        layout.addRow("API密钥:", self.claude_key_input)
        
        # 模型选择
        self.claude_model_combo = QComboBox()
        self.claude_model_combo.addItems([
            "claude-3-opus-20240229", 
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20240620",
            "claude-3-5-sonnet-20240620-v2:0",
            "claude-3-haiku-20240307-v1:0"
        ])
        layout.addRow("模型:", self.claude_model_combo)
        
        # API基础URL
        self.claude_url_input = QLineEdit()
        self.claude_url_input.setPlaceholderText("https://api.anthropic.com/v1/messages")
        layout.addRow("API URL:", self.claude_url_input)
        
        # 说明文本
        instructions = QLabel(
            "Anthropic Claude API提供高质量翻译。需要设置有效的API密钥。\n"
            "默认使用claude-3-opus-20240229模型，也可以选择其他模型。\n"
            "如果使用代理服务，可以修改API基础URL。"
        )
        instructions.setStyleSheet("color: #33FF33;")
        instructions.setWordWrap(True)
        layout.addRow(instructions)
        
        self.tab_widget.addTab(tab, "Claude")
        
    def create_deepseek_tab(self):
        """创建DeepSeek设置页面"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # API密钥
        self.deepseek_key_input = QLineEdit()
        self.deepseek_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.deepseek_key_input.setPlaceholderText("输入你的DeepSeek API密钥")
        layout.addRow("API密钥:", self.deepseek_key_input)
        
        # 模型选择
        self.deepseek_model_combo = QComboBox()
        self.deepseek_model_combo.addItems([
            "deepseek-chat", 
            "deepseek-coder",
            "deepseek-llm-67b-chat",
            "deepseek-llm-7b-chat",
            "deepseek-coder-6.7b-instruct",
            "deepseek-coder-33b-instruct"
        ])
        layout.addRow("模型:", self.deepseek_model_combo)
        
        # API基础URL
        self.deepseek_url_input = QLineEdit()
        self.deepseek_url_input.setPlaceholderText("https://api.deepseek.com/v1/chat/completions")
        layout.addRow("API URL:", self.deepseek_url_input)
        
        # 说明文本
        instructions = QLabel(
            "DeepSeek API提供高质量翻译。需要设置有效的API密钥。\n"
            "默认使用deepseek-chat模型，也可以选择其他模型。\n"
            "如果使用代理服务，可以修改API基础URL。"
        )
        instructions.setStyleSheet("color: #33FF33;")
        instructions.setWordWrap(True)
        layout.addRow(instructions)
        
        self.tab_widget.addTab(tab, "DeepSeek")
    
    def create_openrouter_tab(self):
        """创建OpenRouter设置页面"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # API密钥
        self.openrouter_key_input = QLineEdit()
        self.openrouter_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openrouter_key_input.setPlaceholderText("输入你的OpenRouter API密钥")
        layout.addRow("API密钥:", self.openrouter_key_input)
        
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
        layout.addRow("模型:", self.openrouter_model_combo)
        
        # API基础URL
        self.openrouter_url_input = QLineEdit()
        self.openrouter_url_input.setPlaceholderText("https://openrouter.ai/api/v1/chat/completions")
        layout.addRow("API URL:", self.openrouter_url_input)
        
        # 说明文本
        instructions = QLabel(
            "OpenRouter是一个API聚合服务，提供对多种大型语言模型的统一访问。\n"
            "需要在OpenRouter网站注册并获取API密钥。\n"
            "支持OpenAI、Anthropic Claude、Meta Llama、Mistral等多种模型。\n"
            "网址: https://openrouter.ai"
        )
        instructions.setStyleSheet("color: #33FF33;")
        instructions.setWordWrap(True)
        layout.addRow(instructions)
        
        self.tab_widget.addTab(tab, "OpenRouter")
    
    def load_settings(self):
        """从设置加载值到控件"""
        # OpenAI设置
        self.openai_key_input.setText(self.settings.value("openai/api_key", ""))
        model = self.settings.value("openai/model", "gpt-4o")  # 更新默认模型为gpt-4o
        index = self.openai_model_combo.findText(model)
        if index >= 0:
            self.openai_model_combo.setCurrentIndex(index)
        self.openai_url_input.setText(self.settings.value("openai/base_url", "https://api.openai.com/v1/chat/completions"))
        
        # Claude设置
        self.claude_key_input.setText(self.settings.value("claude/api_key", ""))
        model = self.settings.value("claude/model", "claude-3-opus-20240229")
        index = self.claude_model_combo.findText(model)
        if index >= 0:
            self.claude_model_combo.setCurrentIndex(index)
        self.claude_url_input.setText(self.settings.value("claude/base_url", "https://api.anthropic.com/v1/messages"))
        
        # DeepSeek设置
        self.deepseek_key_input.setText(self.settings.value("deepseek/api_key", ""))
        model = self.settings.value("deepseek/model", "deepseek-chat")
        index = self.deepseek_model_combo.findText(model)
        if index >= 0:
            self.deepseek_model_combo.setCurrentIndex(index)
        self.deepseek_url_input.setText(self.settings.value("deepseek/base_url", "https://api.deepseek.com/v1/chat/completions"))
        
        # OpenRouter设置
        self.openrouter_key_input.setText(self.settings.value("openrouter/api_key", ""))
        model = self.settings.value("openrouter/model", "anthropic/claude-3-opus:beta")  # 更新默认模型
        index = self.openrouter_model_combo.findText(model)
        if index >= 0:
            self.openrouter_model_combo.setCurrentIndex(index)
        self.openrouter_url_input.setText(self.settings.value("openrouter/base_url", "https://openrouter.ai/api/v1/chat/completions"))
    
    def save_settings(self):
        """保存控件值到设置"""
        # OpenAI设置
        self.openai_api.set_api_key(self.openai_key_input.text())
        self.openai_api.set_model(self.openai_model_combo.currentText())
        self.openai_api.set_base_url(self.openai_url_input.text())
        
        # Claude设置
        self.claude_api.set_api_key(self.claude_key_input.text())
        self.claude_api.set_model(self.claude_model_combo.currentText())
        self.claude_api.set_base_url(self.claude_url_input.text())
        
        # DeepSeek设置
        self.deepseek_api.set_api_key(self.deepseek_key_input.text())
        self.deepseek_api.set_model(self.deepseek_model_combo.currentText())
        self.deepseek_api.set_base_url(self.deepseek_url_input.text())
        
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
        """测试当前选中的API连接"""
        current_tab = self.tab_widget.currentIndex()
        
        # 先保存当前设置
        self.save_settings()
        
        api = None
        api_name = ""
        
        if current_tab == 0:  # OpenAI
            api = self.openai_api
            api_name = "OpenAI"
        elif current_tab == 1:  # Claude
            api = self.claude_api
            api_name = "Claude"
        elif current_tab == 2:  # DeepSeek
            api = self.deepseek_api
            api_name = "DeepSeek"
        elif current_tab == 3:  # OpenRouter
            api = self.openrouter_api
            api_name = "OpenRouter"
        
        if api:
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
