#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译API模块
提供对各种高级AI模型的统一翻译接口，包括OpenAI、Claude、DeepSeek和OpenRouter
"""

import os
import json
import requests
import re
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

class TranslationAPI(QObject):
    """翻译API基类，提供统一接口"""
    
    # 信号定义
    translation_completed = pyqtSignal(str, str)  # 原文, 译文
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("HDCTranslator", "Translation")
        # 用于占位符处理的正则表达式
        self.placeholder_pattern = r'\[([^\]]+)\]'
    
    def translate(self, text):
        """
        翻译文本(由子类实现)
        
        Args:
            text: 要翻译的文本
            
        Returns:
            str: 翻译后的文本
        """
        raise NotImplementedError("需要由子类实现")
    
    def process_with_placeholder_protection(self, text):
        """
        处理带有占位符的文本，将占位符保护起来再翻译
        
        Args:
            text: 要翻译的文本
            
        Returns:
            str: 处理后的翻译文本
        """
        # 直接提取所有[xxx]格式的占位符
        placeholders = re.findall(self.placeholder_pattern, text)
        
        if not placeholders:
            # 没有占位符，直接翻译整个文本
            result = self._do_translate(text)
            # 发送翻译完成信号
            self.translation_completed.emit(text, result)
            return result
        
        print(f"发现 {len(placeholders)} 个占位符，将分离处理")
        
        # 将原文分割成文本片段和占位符
        segments = []
        last_end = 0
        
        # 按顺序查找占位符的位置
        for match in re.finditer(self.placeholder_pattern, text):
            start, end = match.span()
            placeholder = match.group(0)  # 完整的[xxx]
            
            # 添加占位符前的文本（如果有）
            if start > last_end:
                text_before = text[last_end:start]
                if text_before.strip():
                    segments.append({"type": "text", "content": text_before})
            
            # 添加占位符
            segments.append({"type": "placeholder", "content": placeholder})
            
            last_end = end
        
        # 添加最后一个占位符后的文本（如果有）
        if last_end < len(text):
            text_after = text[last_end:]
            if text_after.strip():
                segments.append({"type": "text", "content": text_after})
        
        # 只翻译文本部分，保留占位符
        result = ""
        for segment in segments:
            if segment["type"] == "text":
                # 翻译文本
                translated = self._do_translate(segment["content"])
                result += translated
            else:
                # 原样保留占位符
                result += segment["content"]
        
        # 检查常见错误并修正
        corrections = {
            '[姓名]': '[name]', 
            '[名字]': '[name]',
            '[人名]': '[name]',
            '[用户]': '[name]',
            '[玩家]': '[name]',
            '[角色]': '[character]',
            '[数值]': '[value]',
            '[数字]': '[number]',
            '[地点]': '[location]',
            '[物品]': '[item]',
            '[武器]': '[weapon]'
        }
        
        for wrong, correct in corrections.items():
            result = result.replace(wrong, correct)
        
        # 发送翻译完成信号
        self.translation_completed.emit(text, result)
        
        return result
    
    def _do_translate(self, text):
        """
        实际的翻译逻辑，由子类实现
        
        Args:
            text: 要翻译的文本
            
        Returns:
            str: 翻译后的文本
        """
        raise NotImplementedError("需要由子类实现")
    
    def test_connection(self):
        """
        测试API连接(由子类实现)
        
        Returns:
            bool: 连接是否成功
        """
        raise NotImplementedError("需要由子类实现")
    
    def save_settings(self):
        """保存API设置"""
        self.settings.sync()
    
    @staticmethod
    def create_api(api_type):
        """
        创建特定类型的API实例
        
        Args:
            api_type: API类型 ("openai", "claude", "deepseek", "openrouter")
            
        Returns:
            TranslationAPI: API实例
        """
        api_map = {
            "openai": OpenAITranslator,
            "claude": ClaudeTranslator,
            "deepseek": DeepSeekTranslator,
            "openrouter": OpenRouterTranslator
        }
        
        if api_type.lower() in api_map:
            return api_map[api_type.lower()]()
        else:
            # 默认使用OpenAI API
            return OpenAITranslator()


class OpenAITranslator(TranslationAPI):
    """OpenAI API翻译器，支持最新GPT-4模型"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_key = self.settings.value("openai/api_key", "")
        self.model = self.settings.value("openai/model", "gpt-4o")  # 默认使用最新的GPT-4o模型
        self.base_url = self.settings.value("openai/base_url", "https://api.openai.com/v1/chat/completions")
    
    def set_api_key(self, api_key):
        """设置API密钥"""
        self.api_key = api_key
        self.settings.setValue("openai/api_key", api_key)
    
    def set_model(self, model):
        """设置模型名称"""
        self.model = model
        self.settings.setValue("openai/model", model)
    
    def set_base_url(self, base_url):
        """设置API基础URL"""
        self.base_url = base_url
        self.settings.setValue("openai/base_url", base_url)
    
    def translate(self, text):
        """使用OpenAI API翻译文本并保护占位符"""
        # 使用基类的占位符保护处理方法
        return self.process_with_placeholder_protection(text)
        
    def _do_translate(self, text):
        """实际执行OpenAI API翻译"""
        if not self.api_key:
            self.error_occurred.emit("OpenAI API密钥未设置")
            return ""
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一名专业翻译，将以下英文文本翻译成优雅流畅的中文。保留原文的意思和语调。只返回翻译结果，不要添加解释或额外内容。"},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.3
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                self.error_occurred.emit("OpenAI API返回了无效的响应格式")
                return ""
                
        except Exception as e:
            self.error_occurred.emit(f"OpenAI翻译错误: {str(e)}")
            return ""
    
    def test_connection(self):
        """测试OpenAI API连接"""
        if not self.api_key:
            self.error_occurred.emit("OpenAI API密钥未设置")
            return False
        
        try:
            # 使用一个简单的文本进行测试
            test_text = "Hello, this is a test."
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a translator."},
                    {"role": "user", "content": test_text}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            return True
                
        except Exception as e:
            self.error_occurred.emit(f"OpenAI连接测试失败: {str(e)}")
            return False


class ClaudeTranslator(TranslationAPI):
    """Anthropic Claude API翻译器，支持最新Claude 3模型"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_key = self.settings.value("claude/api_key", "")
        # 默认使用最新的Claude 3 Opus模型
        self.model = self.settings.value("claude/model", "claude-3-opus-20240229")
        self.base_url = self.settings.value("claude/base_url", "https://api.anthropic.com/v1/messages")
    
    def set_api_key(self, api_key):
        """设置API密钥"""
        self.api_key = api_key
        self.settings.setValue("claude/api_key", api_key)
    
    def set_model(self, model):
        """设置模型名称"""
        self.model = model
        self.settings.setValue("claude/model", model)
    
    def set_base_url(self, base_url):
        """设置API基础URL"""
        self.base_url = base_url
        self.settings.setValue("claude/base_url", base_url)
    
    def translate(self, text):
        """使用Claude API翻译文本并保护占位符"""
        # 使用基类的占位符保护处理方法
        return self.process_with_placeholder_protection(text)
        
    def _do_translate(self, text):
        """实际执行Claude API翻译"""
        if not self.api_key:
            self.error_occurred.emit("Claude API密钥未设置")
            return ""
        
        try:
            # 使用最新的API版本
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": f"将以下英文文本翻译成优雅流畅的中文。保留原文的意思和语调。只返回翻译结果，不要添加解释或额外内容。\n\n{text}"}
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # 处理响应格式
            if "content" in result:
                # 新版API响应格式
                content = result.get("content", [])
                if isinstance(content, list) and len(content) > 0:
                    for item in content:
                        if item.get("type") == "text":
                            return item.get("text", "").strip()
            
            # 尝试旧版格式
            if "completion" in result:
                return result.get("completion", "").strip()
                
            self.error_occurred.emit("Claude API返回了无效的响应格式")
            return ""
                
        except Exception as e:
            self.error_occurred.emit(f"Claude翻译错误: {str(e)}")
            return ""
    
    def test_connection(self):
        """测试Claude API连接"""
        if not self.api_key:
            self.error_occurred.emit("Claude API密钥未设置")
            return False
        
        try:
            # 使用一个简单的文本进行测试
            test_text = "Hello, this is a test."
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": f"Translate this text to Chinese: {test_text}"}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            return True
                
        except Exception as e:
            self.error_occurred.emit(f"Claude连接测试失败: {str(e)}")
            return False


class OpenRouterTranslator(TranslationAPI):
    """OpenRouter API翻译器，支持多种最新模型"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_key = self.settings.value("openrouter/api_key", "")
        # 支持各种最新模型
        self.model = self.settings.value("openrouter/model", "anthropic/claude-3-opus:beta")
        self.base_url = self.settings.value("openrouter/base_url", "https://openrouter.ai/api/v1/chat/completions")
    
    def set_api_key(self, api_key):
        """设置API密钥"""
        self.api_key = api_key
        self.settings.setValue("openrouter/api_key", api_key)
    
    def set_model(self, model):
        """设置模型名称"""
        self.model = model
        self.settings.setValue("openrouter/model", model)
    
    def set_base_url(self, base_url):
        """设置API基础URL"""
        self.base_url = base_url
        self.settings.setValue("openrouter/base_url", base_url)
    
    def translate(self, text):
        """使用OpenRouter API翻译文本并保护占位符"""
        # 使用基类的占位符保护处理方法
        return self.process_with_placeholder_protection(text)
        
    def _do_translate(self, text):
        """实际执行OpenRouter API翻译"""
        if not self.api_key:
            self.error_occurred.emit("OpenRouter API密钥未设置")
            return ""
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://hdctranslator.app",
                "X-Title": "HDCTranslator"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一名专业翻译，将以下英文文本翻译成优雅流畅的中文。保留原文的意思和语调。只返回翻译结果，不要添加解释或额外内容。"},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.3
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                self.error_occurred.emit("OpenRouter API返回了无效的响应格式")
                return ""
                
        except Exception as e:
            self.error_occurred.emit(f"OpenRouter翻译错误: {str(e)}")
            return ""
    
    def test_connection(self):
        """测试OpenRouter API连接"""
        if not self.api_key:
            self.error_occurred.emit("OpenRouter API密钥未设置")
            return False
        
        try:
            # 使用一个简单的文本进行测试
            test_text = "Hello, this is a test."
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://hdctranslator.app",
                "X-Title": "HDCTranslator"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a translator."},
                    {"role": "user", "content": test_text}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            return True
                
        except Exception as e:
            self.error_occurred.emit(f"OpenRouter连接测试失败: {str(e)}")
            return False


class DeepSeekTranslator(TranslationAPI):
    """DeepSeek API翻译器，支持最新中英双语模型"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_key = self.settings.value("deepseek/api_key", "")
        # 使用最新的DeepSeek模型
        self.model = self.settings.value("deepseek/model", "deepseek-chat")
        self.base_url = self.settings.value("deepseek/base_url", "https://api.deepseek.com/v1/chat/completions")
    
    def set_api_key(self, api_key):
        """设置API密钥"""
        self.api_key = api_key
        self.settings.setValue("deepseek/api_key", api_key)
    
    def set_model(self, model):
        """设置模型名称"""
        self.model = model
        self.settings.setValue("deepseek/model", model)
    
    def set_base_url(self, base_url):
        """设置API基础URL"""
        self.base_url = base_url
        self.settings.setValue("deepseek/base_url", base_url)
    
    def translate(self, text):
        """使用DeepSeek API翻译文本并保护占位符"""
        # 使用基类的占位符保护处理方法
        return self.process_with_placeholder_protection(text)
        
    def _do_translate(self, text):
        """实际执行DeepSeek API翻译"""
        if not self.api_key:
            self.error_occurred.emit("DeepSeek API密钥未设置")
            return ""
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一名专业翻译，将以下英文文本翻译成优雅流畅的中文。保留原文的意思和语调。只返回翻译结果，不要添加解释或额外内容。"},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.3
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                self.error_occurred.emit("DeepSeek API返回了无效的响应格式")
                return ""
                
        except Exception as e:
            self.error_occurred.emit(f"DeepSeek翻译错误: {str(e)}")
            return ""
    
    def test_connection(self):
        """测试DeepSeek API连接"""
        if not self.api_key:
            self.error_occurred.emit("DeepSeek API密钥未设置")
            return False
        
        try:
            # 使用一个简单的文本进行测试
            test_text = "Hello, this is a test."
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a translator."},
                    {"role": "user", "content": test_text}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            return True
                
        except Exception as e:
            self.error_occurred.emit(f"DeepSeek连接测试失败: {str(e)}")
            return False


# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtCore import QCoreApplication
    
    app = QCoreApplication(sys.argv)
    
    # 创建OpenAI翻译器
    translator = OpenAITranslator()
    
    # 测试信号
    def on_translation_completed(original, translated):
        print(f"翻译完成:\n原文: {original}\n译文: {translated}")
    
    def on_error(message):
        print(f"错误: {message}")
    
    translator.translation_completed.connect(on_translation_completed)
    translator.error_occurred.connect(on_error)
    
    # 需要设置你的API密钥才能测试
    # translator.set_api_key("your-api-key")
    # print(translator.translate("Hello, world!"))
    
    sys.exit(0)
