#!/usr/bin/env python3
"""
Oasis UI 启动脚本
包含所有问题修复的完整版本
"""

import sys
import os

def main():
    print("🚀 启动 Oasis 目标检测系统...")
    print("版本: 完整修复版 (2024)")
    print("功能: 3D坐标计算 + 多视频流 + Windows布局优化")
    print("=" * 60)
    
    # 设置高DPI支持
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        app = QApplication(sys.argv)
        
        # 尝试设置高DPI缩放（兼容不同PyQt6版本）
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # 新版本PyQt6默认启用高DPI
            pass
            
        from ui.main_window import MainWindow
        
        window = MainWindow()
        window.show()
        
        print("✅ 界面启动成功！")
        print("💡 新功能:")
        print("   • 3D坐标计算：在Kinect彩色模式下实时获取目标空间坐标")
        print("   • 深度图优化：改进的可视化和异常处理")
        print("   • 滚动布局：Windows下窗口缩放不会重叠")
        print("   • 颜色修复：正确的RGB颜色显示")
        print("   • 自定义类别：可添加自己的检测类别")
        print("   • 调试模式：无Kinect时使用电脑摄像头")
        print("")
        print("🔧 使用提示:")
        print("   1. 连接Kinect 2.0设备")
        print("   2. 选择检测模式（Kinect或调试模式）")
        print("   3. 启用3D坐标功能获取空间位置")
        print("   4. 切换不同Kinect视频流（彩色/深度/红外）")
        print("   5. 添加自定义检测类别")
        
        return app.exec()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖:")
        print("  pip install PyQt6 ultralytics opencv-python numpy")
        if 'pykinect2' in str(e):
            print("  pip install pykinect2")
        return 1
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
