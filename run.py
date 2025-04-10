#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
潜渊症汉化终端入口程序
联盟科研部门 - UDS翻译终端
"""

import sys
import os
import traceback

# 确保当前目录在sys.path中，以便能够导入本地模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    """主函数"""
    try:
        print("正在启动潜渊症汉化终端...")
        print(f"Python版本: {sys.version}")
        print(f"系统平台: {sys.platform}")
        print(f"当前路径: {os.getcwd()}")
        
        # 导入和应用程序相关的模块
        from app import main as start_app
        
        # 启动应用程序
        return start_app()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("\n缺少必要的依赖库，请确保已安装以下Python库:")
        print("- PyQt6")
        print("- lxml")
        print("- pandas")
        print("- requests")
        print("- openpyxl")
        print("\n可以使用以下命令安装依赖:")
        print("pip install PyQt6 lxml pandas requests openpyxl")
        input("\n按Enter键退出...")
        return 1
        
    except Exception as e:
        print(f"启动错误: {e}")
        traceback.print_exc()
        input("\n按Enter键退出...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
