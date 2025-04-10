#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
联盟项目UDS终端 - 拆分式启动器
先完全展示启动画面，然后再启动主窗口
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, QEventLoop
from ui.splash_screen import StartupSplashScreen
from ui.main_window import MainWindow

def main():
    """启动器主函数"""
    try:
        print("正在初始化应用程序...")
        
        # 记录系统信息
        print(f"Python版本: {sys.version}")
        print(f"系统: {sys.platform}")
        print(f"当前路径: {os.getcwd()}")
        
        # 创建QApplication
        print("创建QApplication实例...")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")  # 使用fusion风格,跨平台一致性更好
        
        # 创建一个全局窗口引用，防止垃圾回收
        global main_window
        
        # 完全简化启动流程
        print("启动应用程序组件...")
        
        # 先显示启动画面
        splash = StartupSplashScreen()
        
        # 确保启动画面显示在屏幕中央
        screen_geometry = app.primaryScreen().geometry()
        x = int((screen_geometry.width() - splash.width()) / 2)
        y = int((screen_geometry.height() - splash.height()) / 2)
        splash.move(x, y)
        
        # 显示启动画面
        splash.show()
        app.processEvents()  # 强制处理事件,确保立即显示
        print("启动画面已显示")
        
        # 显示启动消息 - 更详细的系统检查步骤
        messages = [
            "正在初始化系统内核...",
            "加载加密模块...",
            "初始化内存分配...",
            "检查系统完整性...",
            "加载UDS翻译协议 v1.5...",
            "建立安全网络连接...",
            "验证联盟授权密钥...",
            "扫描潜在安全威胁...",
            "加载用户界面组件...",
            "初始化翻译引擎...",
            "连接联盟数据库...",
            "系统检查完毕 - 联盟工程部研发",
            "墨水、伍德、HDC联合开发",
            "UDS访问已授权 - 权限级别: ALPHA",
            "正在启动主界面..."
        ]
        
        # 使用打字机效果显示消息
        def show_next_message(index):
            if index >= len(messages):
                return
                
            msg = messages[index]
            print(f"显示消息: {msg}")
            
            # 使用打字机效果显示消息
            def on_message_complete():
                # 消息显示完成后，延迟显示下一条
                delay = 500  # 增加基础延迟，确保消息有足够时间显示
                
                # 为不同消息设置不同的延迟
                if index == 0 or index == len(messages) - 1:
                    delay = 800  # 第一条和最后一条消息显示更长时间
                elif "授权" in msg or "安全" in msg:
                    delay = 700  # 安全相关消息显示稍长
                
                # 确保前一条消息完全显示后再显示下一条
                QTimer.singleShot(delay, lambda: show_next_message(index + 1))
            
            # 显示消息并设置完成回调
            splash.showMessageWithCallback(msg, on_message_complete)
            app.processEvents()  # 确保消息立即开始显示
        
        # 开始显示第一条消息
        show_next_message(0)
        
        # 创建事件循环等待所有消息显示完成
        loop = QEventLoop()
        QTimer.singleShot(len(messages) * 800, loop.quit)  # 估计总时间
        loop.exec()
        
        # 等待足够长的时间，让用户欣赏启动动画
        time.sleep(1.5)
        
        print("创建主窗口...")
        # 创建主窗口
        main_window = MainWindow()
        
        # 确保窗口在屏幕中央
        screen_geometry = app.primaryScreen().geometry()
        window_geometry = main_window.geometry()
        x = int((screen_geometry.width() - window_geometry.width()) / 2)
        y = int((screen_geometry.height() - window_geometry.height()) / 2)
        main_window.move(x, y)
        
        # 显示窗口，使用标准Qt方法
        main_window.show()
        print("主窗口已创建并显示")
        
        # 关闭启动画面
        splash.close()
        print("启动画面已关闭")
        
        # 强制处理事件
        app.processEvents()
        
        # 强制窗口活跃并置于前台
        main_window.activateWindow()
        main_window.raise_()
        main_window.setWindowState(main_window.windowState() | Qt.WindowState.WindowActive)
        print("窗口已激活")
        
        # 进入应用事件循环
        print("进入应用事件循环...")
        return app.exec()
        
    except Exception as e:
        print(f"程序启动出错: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")
        return 1

# 这里删除了未使用的函数

if __name__ == "__main__":
    sys.exit(main())
