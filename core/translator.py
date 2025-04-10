#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译模块
集成各种高级AI模型的翻译API，提供统一的翻译接口
"""

import os
import json
import time
import random
import requests
from dotenv import load_dotenv
from PyQt6.QtCore import QObject, pyqtSignal

# 加载环境变量中的API密钥
load_dotenv()

import re

class TranslatorManager(QObject):
    """翻译管理器，集成多种翻译API"""
    
    # 定义信号
    translation_completed = pyqtSignal(str, str)  # 原文, 译文
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # API配置
        self.api_type = "None"  # 默认不使用API
        self.api_key = None
        self.api_endpoint = None
        self.custom_api_params = {}
        
        # 占位符相关
        self.placeholder_pattern = r'\[([^\]]+)\]'  # 匹配[xxx]格式的占位符
        self.placeholders = {}  # 存储占位符映射
        
        # 加载配置
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "settings", "api_config.json"
        )
        self.load_config()
    
    def load_config(self):
        """从配置文件加载API设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    self.api_type = config.get('api_type', 'None')
                    self.api_key = config.get('api_key', None)
                    self.api_endpoint = config.get('api_endpoint', None)
                    self.custom_api_params = config.get('custom_params', {})
        except Exception as e:
            self.error_occurred.emit(f"加载API配置失败: {str(e)}")
    
    def save_config(self):
        """保存API设置到配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            config = {
                'api_type': self.api_type,
                'api_key': self.api_key,
                'api_endpoint': self.api_endpoint,
                'custom_params': self.custom_api_params
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                
            return True
        except Exception as e:
            self.error_occurred.emit(f"保存API配置失败: {str(e)}")
            return False
    
    def set_api(self, api_type, api_key=None, api_endpoint=None, custom_params=None):
        """
        设置API类型和参数
        
        Args:
            api_type: API类型（OpenAI、Claude、DeepSeek、OpenRouter）
            api_key: API密钥
            api_endpoint: API端点URL
            custom_params: 自定义参数字典
        
        Returns:
            bool: 是否设置成功
        """
        self.api_type = api_type
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        
        if custom_params:
            self.custom_api_params = custom_params
        
        return self.save_config()
    
    def protect_placeholders(self, text):
        """
        保护文本中的占位符，将其替换为特殊标记
        
        Args:
            text: 原始文本
            
        Returns:
            tuple: (处理后的文本, 占位符映射字典)
        """
        # 清空之前的占位符映射
        self.placeholders = {}
        
        # 查找所有[xxx]格式的占位符
        processed_text = text
        placeholder_matches = re.finditer(self.placeholder_pattern, text)
        
        # 收集所有占位符，以便后续按长度排序处理（避免替换子字符串问题）
        placeholder_list = []
        for i, match in enumerate(placeholder_matches):
            # 生成唯一标记
            placeholder = match.group(0)  # 完整的[xxx]
            placeholder_list.append((placeholder, i))
        
        # 按长度倒序排列，先替换较长的占位符
        placeholder_list.sort(key=lambda x: len(x[0]), reverse=True)
        
        # 执行替换
        for placeholder, i in placeholder_list:
            marker = f"__PLACEHOLDER_{i}__"
            
            # 存储映射关系
            self.placeholders[marker] = placeholder
            
            # 替换文本中的占位符
            processed_text = processed_text.replace(placeholder, marker)
        
        return processed_text, self.placeholders
    
    def restore_placeholders(self, translated_text):
        """
        将译文中的特殊标记还原为原始占位符
        
        Args:
            translated_text: 包含特殊标记的译文
            
        Returns:
            str: 还原占位符后的译文
        """
        result = translated_text
        
        # 按照占位符标记的格式查找
        for marker, placeholder in self.placeholders.items():
            result = result.replace(marker, placeholder)
        
        # 执行常见的翻译错误修正
        # 将翻译模型可能翻译的占位符转换回原始形式
        common_translations = {
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
        
        # 执行替换
        for translated, original in common_translations.items():
            result = result.replace(translated, original)
        
        return result
    
    def translate(self, text, target_lang="zh", source_lang="en"):
        """
        翻译文本，保护[xxx]格式的占位符
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言代码
            source_lang: 源语言代码
            
        Returns:
            str: 翻译后的文本
        """
        if not text or not text.strip():
            return ""
            
        # 直接提取所有[xxx]格式的占位符
        placeholder_pattern = r'\[([^\]]+)\]'
        placeholders = re.findall(placeholder_pattern, text)
        
        if not placeholders:
            # 没有占位符，直接翻译整个文本
            result = self._do_translate(text, target_lang, source_lang)
            if result:
                self.translation_completed.emit(text, result)
            return result
        
        print(f"发现 {len(placeholders)} 个占位符")
        
        # 将原文分割成文本片段和占位符
        segments = []
        last_end = 0
        
        # 按顺序查找占位符的位置
        for match in re.finditer(placeholder_pattern, text):
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
                translated = self._do_translate(segment["content"], target_lang, source_lang)
                result += translated
            else:
                # 原样保留占位符
                result += segment["content"]
        
        # 检查常见错误并修正（以防某些API仍然翻译了占位符）
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
        
        # 发出翻译完成信号
        if result:
            self.translation_completed.emit(text, result)
        
        return result
    
    def _do_translate(self, text, target_lang="zh", source_lang="en"):
        """
        执行实际的翻译
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言代码
            source_lang: 源语言代码
            
        Returns:
            str: 翻译结果
        """
        # 根据API类型调用不同的翻译方法
        try:
            if self.api_type == "OpenAI":
                result = self._translate_with_openai(text, target_lang, False)
            elif self.api_type == "Claude":
                result = self._translate_with_claude(text, target_lang, False)
            elif self.api_type == "DeepSeek":
                result = self._translate_with_deepseek(text, target_lang, False)
            elif self.api_type == "OpenRouter":
                result = self._translate_with_openrouter(text, target_lang, False)
            else:
                # 如果没有配置API，返回原文
                return text
            
            return result
        except Exception as e:
            self.error_occurred.emit(f"翻译失败: {str(e)}")
            return text
    
    def _translate_with_openai(self, text, target_lang, has_placeholders=False):
        """
        使用OpenAI API进行翻译
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言
            has_placeholders: 是否包含占位符
            
        Returns:
            str: 翻译结果
        """
        if not self.api_key:
            self.error_occurred.emit("缺少OpenAI API密钥")
            return text
        
        # 设置API端点
        endpoint = self.api_endpoint or "https://api.openai.com/v1/chat/completions"
        
        # 发送请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 准备提示文本
        language_name = "中文" if target_lang == "zh" else target_lang
        
        system_prompt = f"你是一名专业翻译，将以下英文文本翻译成优雅流畅的{language_name}。保留原文的意思和语调。只返回翻译结果，不要添加解释或额外内容。"
        
        # 如果文本包含占位符，添加特殊说明
        if has_placeholders:
            system_prompt += f"文本中包含特殊标记格式为 __PLACEHOLDER_X__，这些是原始代码中的变量占位符，必须在翻译时完全保留。请勿翻译这些标记或尝试理解其含义，只需在输出中原样保留它们。这些标记会在后续处理中被还原为程序需要的格式。"
        
        # 从custom_api_params获取模型名称，如果没有则使用默认值
        model = self.custom_api_params.get("model", "gpt-4o")
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3
        }
        
        response = requests.post(endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            resp_json = response.json()
            translation = resp_json["choices"][0]["message"]["content"].strip()
            return translation
        else:
            self.error_occurred.emit(f"OpenAI API错误: {response.status_code}, {response.text}")
            return text
            
    def _translate_with_claude(self, text, target_lang, has_placeholders=False):
        """
        使用Claude API进行翻译
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言
            has_placeholders: 是否包含占位符
            
        Returns:
            str: 翻译结果
        """
        if not self.api_key:
            self.error_occurred.emit("缺少Claude API密钥")
            return text
        
        # 设置API端点
        endpoint = self.api_endpoint or "https://api.anthropic.com/v1/messages"
        
        # 发送请求
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # 准备提示文本
        language_name = "中文" if target_lang == "zh" else target_lang
        
        user_content = f"将以下英文文本翻译成优雅流畅的{language_name}，保留原始格式，只返回翻译结果，不要添加任何解释或额外内容。\n\n{text}"
        
        # 从custom_api_params获取模型名称，如果没有则使用默认值
        model = self.custom_api_params.get("model", "claude-3-opus-20240229")
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        response = requests.post(endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            resp_json = response.json()
            if "content" in resp_json and len(resp_json["content"]) > 0:
                for item in resp_json["content"]:
                    if item.get("type") == "text":
                        translation = item.get("text", "").strip()
                        return translation
            
            # 尝试旧版格式
            if "completion" in resp_json:
                return resp_json["completion"].strip()
                
            self.error_occurred.emit("Claude API返回了无效的响应格式")
            return text
        else:
            self.error_occurred.emit(f"Claude API错误: {response.status_code}, {response.text}")
            return text
            
    def _translate_with_deepseek(self, text, target_lang, has_placeholders=False):
        """
        使用DeepSeek API进行翻译
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言
            has_placeholders: 是否包含占位符
            
        Returns:
            str: 翻译结果
        """
        if not self.api_key:
            self.error_occurred.emit("缺少DeepSeek API密钥")
            return text
        
        # 设置API端点
        endpoint = self.api_endpoint or "https://api.deepseek.com/v1/chat/completions"
        
        # 发送请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 准备提示文本
        language_name = "中文" if target_lang == "zh" else target_lang
        
        system_prompt = f"你是一名专业翻译，将以下英文文本翻译成优雅流畅的{language_name}。保留原始格式，只返回翻译结果，不要添加解释或额外内容。"
        
        # 从custom_api_params获取模型名称，如果没有则使用默认值
        model = self.custom_api_params.get("model", "deepseek-chat")
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3
        }
        
        response = requests.post(endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            resp_json = response.json()
            if "choices" in resp_json and len(resp_json["choices"]) > 0:
                translation = resp_json["choices"][0]["message"]["content"].strip()
                return translation
            else:
                self.error_occurred.emit("DeepSeek API返回了无效的响应格式")
                return text
        else:
            self.error_occurred.emit(f"DeepSeek API错误: {response.status_code}, {response.text}")
            return text
    
    def _translate_with_openrouter(self, text, target_lang, has_placeholders=False):
        """
        使用OpenRouter API进行翻译
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言
            has_placeholders: 是否包含占位符
            
        Returns:
            str: 翻译结果
        """
        if not self.api_key:
            self.error_occurred.emit("缺少OpenRouter API密钥")
            return text
        
        # 设置API端点
        endpoint = self.api_endpoint or "https://openrouter.ai/api/v1/chat/completions"
        
        # 发送请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://hdctranslator.app",  # 应用域名
            "X-Title": "HDCTranslator"  # 应用名称
        }
        
        # 准备提示文本
        language_name = "中文" if target_lang == "zh" else target_lang
        
        # 从custom_api_params获取模型名称，如果没有则使用默认值
        model = self.custom_api_params.get("model", "anthropic/claude-3-opus:beta")
        
        system_prompt = f"你是一名专业翻译，将以下英文文本翻译成优雅流畅的{language_name}。保留原始格式，只返回翻译结果，不要添加解释或额外内容。"
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3
        }
        
        response = requests.post(endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            resp_json = response.json()
            if "choices" in resp_json and len(resp_json["choices"]) > 0:
                translation = resp_json["choices"][0]["message"]["content"].strip()
                return translation
            else:
                self.error_occurred.emit("OpenRouter API返回了无效的响应格式")
                return text
        else:
            self.error_occurred.emit(f"OpenRouter API错误: {response.status_code}, {response.text}")
            return text
    
    def test_connection(self):
        """
        测试API连接
        
        Returns:
            bool: 连接是否成功
            str: 连接状态信息
        """
        test_text = "Hello world, this is a test."
        
        try:
            if self.api_type == "None":
                return False, "未配置API"
            
            # 执行翻译测试
            result = self.translate(test_text)
            
            if result and result != test_text:
                return True, f"连接成功，测试翻译结果: {result}"
            else:
                return False, "API连接成功但翻译失败"
            
        except Exception as e:
            return False, f"连接测试失败: {str(e)}"

# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtCore import QCoreApplication
    
    app = QCoreApplication(sys.argv)
    
    translator = TranslatorManager()
    translator.translation_completed.connect(
        lambda src, dst: print(f"翻译完成: {src} -> {dst}")
    )
    translator.error_occurred.connect(
        lambda err: print(f"错误: {err}")
    )
    
    # 测试翻译
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        translator.set_api("OpenAI", api_key)
        result = translator.translate("Hello world, this is a test.", "zh")
        print(f"OpenAI翻译结果: {result}")
    else:
        print("没有找到OpenAI API密钥，跳过测试")
    
    sys.exit(0)
