#!/usr/bin/env python3
"""
Oasis 目标检测系统 - PyQt6 图形界面版本
基于 Kinect 2.0 和 YOLO 的实时目标检测应用

使用说明:
1. 确保已安装 Kinect for Windows SDK 2.0
2. 将 Kinect 2.0 传感器连接到 USB 3.0 端口
3. 确保 yolo11n.pt 模型文件在项目根目录
4. 运行此脚本启动图形界面

依赖包:
- PyQt6
- ultralytics
- opencv-python
- numpy
- pykinect2

作者: Oasis Team
版本: 1.0
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    from ui.main_window import MainWindow
    from ui.config import config_manager
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有必需的依赖包:")
    print("pip install PyQt6 ultralytics opencv-python numpy pykinect2")
    sys.exit(1)


def check_dependencies():
    """检查依赖项"""
    missing_deps = []
    
    # 检查 YOLO 模型文件
    model_path = config_manager.detection.model_path
    if not os.path.exists(model_path):
        missing_deps.append(f"YOLO 模型文件: {model_path}")
    
    # 检查 Kinect SDK
    try:
        import pykinect2
    except ImportError:
        missing_deps.append("pykinect2 (Kinect for Windows SDK 2.0)")
    
    # 检查其他依赖
    try:
        import cv2
        import numpy as np
        from ultralytics import YOLO
    except ImportError as e:
        missing_deps.append(f"Python 包: {e}")
    
    return missing_deps


def show_startup_info():
    """显示启动信息"""
    print("=" * 60)
    print("🎯 Oasis 目标检测系统 v1.0")
    print("=" * 60)
    print("📋 功能特性:")
    print("  • 实时 Kinect 2.0 视频流")
    print("  • YOLO 深度学习目标检测")
    print("  • 可自定义检测类别")
    print("  • 现代化 PyQt6 界面")
    print("  • 丰富的配置选项")
    print()
    print("⚙️  配置信息:")
    print(f"  • 模型: {config_manager.detection.model_path}")
    print(f"  • 置信度阈值: {config_manager.detection.confidence_threshold}")
    print(f"  • 目标类别: {len(config_manager.detection.target_classes)} 个")
    print(f"  • 窗口尺寸: {config_manager.ui.window_size}")
    print()


def main():
    """主函数"""
    # 显示启动信息
    show_startup_info()
    
    # 检查依赖项
    print("🔍 检查依赖项...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        print("❌ 缺少以下依赖项:")
        for dep in missing_deps:
            print(f"  • {dep}")
        print()
        print("💡 解决方案:")
        print("  1. 安装 Kinect for Windows SDK 2.0")
        print("  2. 确保 yolo11n.pt 模型文件在项目根目录")
        print("  3. 运行: pip install PyQt6 ultralytics opencv-python numpy pykinect2")
        return 1
    
    print("✅ 依赖项检查通过")
    print()
    
    # 创建 Qt 应用
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("Oasis 目标检测系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Oasis Team")
    app.setOrganizationDomain("oasis.ai")
    
    # 设置高 DPI 支持 (PyQt6 兼容性)
    try:
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # PyQt6 中这些属性可能不存在或已被弃用
        # 在 PyQt6 中，高 DPI 支持是默认启用的
        pass
    
    try:
        print("🚀 启动图形界面...")
        
        # 创建主窗口
        main_window = MainWindow()
        main_window.show()
        
        print("✅ 界面启动成功!")
        print("💡 使用提示:")
        print("  • 点击'开始检测'按钮开始实时检测")
        print("  • 使用菜单栏 -> 文件 -> 设置来配置系统")
        print("  • 按 Ctrl+Q 或关闭窗口退出应用")
        print("  • 按 'q' 键可在视频窗口中退出检测")
        print()
        
        # 自动启动检测（如果配置了）
        if config_manager.ui.auto_start:
            print("🔄 自动启动检测...")
            main_window.control_panel.on_start_clicked()
        
        # 运行应用
        return app.exec()
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        
        # 显示错误对话框
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("启动错误")
        error_msg.setText("应用启动失败")
        error_msg.setDetailedText(str(e))
        error_msg.exec()
        
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 意外错误: {e}")
        sys.exit(1)
