#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
潜渊症汉化终端 - 依赖安装脚本
检查并安装必要的依赖项
"""

import sys
import subprocess
import importlib
import os
import platform

def check_module(module_name):
    """检查模块是否已安装"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def install_module(module_name, package_name=None):
    """安装Python模块"""
    package = package_name or module_name
    print(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", package])
        return True
    except subprocess.CalledProcessError:
        print(f"安装 {package} 失败!")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("潜渊症汉化终端 - 依赖安装脚本")
    print("=" * 60)
    print(f"Python版本: {platform.python_version()}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print("-" * 60)
    
    # 必需的依赖项列表，格式为：(模块名, 包名[可选])
    required_modules = [
        ("PyQt6", "PyQt6"),
        ("lxml", "lxml"),
        ("pandas", "pandas"),
        ("requests", "requests"),
        ("openpyxl", "openpyxl")
    ]
    
    all_installed = True
    
    # 检查并安装缺失的模块
    print("检查必要的Python模块...")
    for module_info in required_modules:
        module_name = module_info[0]
        package_name = module_info[1] if len(module_info) > 1 else None
        
        if check_module(module_name):
            print(f"✓ {module_name} 已安装")
        else:
            print(f"✗ {module_name} 未安装")
            success = install_module(module_name, package_name)
            if not success:
                all_installed = False
    
    print("-" * 60)
    
    # 安装结果
    if all_installed:
        print("✅ 所有依赖项已成功安装!")
        print("👉 现在可以通过运行 UDS_Terminal.py 启动应用程序")
        
        # 为Windows用户创建批处理文件
        if platform.system() == "Windows":
            try:
                with open("启动潜渊症汉化终端.bat", "w") as f:
                    f.write(f'@echo off\n"{sys.executable}" "%~dp0UDS_Terminal.py"\npause')
                print("✅ 已创建Windows启动批处理文件 '启动潜渊症汉化终端.bat'")
            except:
                print("❌ 创建Windows启动批处理文件失败")
        
    else:
        print("⚠️ 部分依赖项安装失败，请检查错误信息并手动安装。")
        print("你可以使用以下命令手动安装所有依赖：")
        print(f"{sys.executable} -m pip install -U PyQt6 lxml pandas requests openpyxl")
    
    print("\n按Enter键退出...")
    input()

if __name__ == "__main__":
    main()
