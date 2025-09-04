#!/usr/bin/env python3
"""
Oasis 目标检测系统 - 安全启动器
自动处理 PyQt6 版本兼容性问题

这个版本会自动检测和处理常见的 PyQt6 兼容性问题，
确保在不同版本的 PyQt6 环境中都能正常运行。

作者: Oasis Team
版本: 1.0 (安全版本)
"""

import sys
import os
import traceback

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def check_pyqt6_compatibility():
    """检查 PyQt6 兼容性"""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import Qt
        return True, None
    except ImportError as e:
        return False, f"PyQt6 导入失败: {e}"
    except Exception as e:
        return False, f"PyQt6 检查失败: {e}"


def create_safe_application():
    """创建兼容的 QApplication"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("Oasis 目标检测系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Oasis Team")
    app.setOrganizationDomain("oasis.ai")
    
    # 安全地设置高 DPI 支持
    high_dpi_attributes = [
        'AA_EnableHighDpiScaling',
        'AA_UseHighDpiPixmaps',
    ]
    
    for attr_name in high_dpi_attributes:
        try:
            if hasattr(Qt.ApplicationAttribute, attr_name):
                attr = getattr(Qt.ApplicationAttribute, attr_name)
                app.setAttribute(attr, True)
                print(f"✅ 高DPI支持: {attr_name} 已启用")
            else:
                print(f"ℹ️  高DPI支持: {attr_name} 不可用 (可能在此版本中已默认启用)")
        except Exception as e:
            print(f"⚠️  高DPI设置警告: {attr_name} - {e}")
    
    return app


def show_startup_info():
    """显示启动信息"""
    print("=" * 60)
    print("🎯 Oasis 目标检测系统 v1.0 (安全启动版本)")
    print("=" * 60)
    print("📋 功能特性:")
    print("  • 实时 Kinect 2.0 视频流")
    print("  • 调试模式 (电脑摄像头)")
    print("  • YOLO 深度学习目标检测")
    print("  • 可自定义检测类别")
    print("  • 现代化 PyQt6 界面")
    print("  • 自动版本兼容性处理")
    print("  • 丰富的配置选项")
    print()


def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
    missing_deps = []
    
    # 检查 PyQt6 兼容性
    pyqt_ok, pyqt_error = check_pyqt6_compatibility()
    if not pyqt_ok:
        missing_deps.append(f"PyQt6: {pyqt_error}")
    
    # 检查配置文件
    try:
        from ui.config import config_manager
        
        # 检查 YOLO 模型文件
        model_path = config_manager.detection.model_path
        if not os.path.exists(model_path):
            missing_deps.append(f"YOLO 模型文件: {model_path}")
            
    except ImportError:
        missing_deps.append("配置模块: ui.config")
    except Exception as e:
        missing_deps.append(f"配置检查: {e}")
    
    # 检查其他依赖
    optional_deps = [
        ('cv2', 'OpenCV (opencv-python)'),
        ('numpy', 'NumPy'),
        ('ultralytics', 'YOLO (ultralytics)'),
    ]
    
    for module_name, display_name in optional_deps:
        try:
            __import__(module_name)
        except ImportError:
            missing_deps.append(display_name)
    
    # 检查 Kinect SDK
    try:
        import pykinect2
    except ImportError:
        print("⚠️  Kinect SDK 未安装 (可选，用于 Kinect 2.0 支持)")
    
    return missing_deps


def try_import_ui_module():
    """尝试导入 UI 模块"""
    ui_modules = [
        ('ui.main_window_ui', 'MainWindowUI', 'UI文件版本'),
        ('ui.main_window', 'MainWindow', '原始版本'),
    ]
    
    for module_name, class_name, version_name in ui_modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            main_window_class = getattr(module, class_name)
            print(f"✅ UI模块加载成功: {version_name}")
            return main_window_class, version_name
        except ImportError as e:
            print(f"⚠️  {version_name} 不可用: {e}")
        except Exception as e:
            print(f"❌ {version_name} 加载失败: {e}")
    
    return None, None


def show_error_dialog(title, message, details=None):
    """显示错误对话框"""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if details:
            msg_box.setDetailedText(details)
        
        msg_box.exec()
        
    except Exception:
        # 如果无法显示图形对话框，则在控制台显示
        print(f"\n❌ {title}")
        print(f"   {message}")
        if details:
            print(f"   详细信息: {details}")


def main():
    """主函数"""
    try:
        # 显示启动信息
        show_startup_info()
        
        # 检查依赖项
        missing_deps = check_dependencies()
        
        if missing_deps:
            error_msg = "缺少以下依赖项，程序无法启动："
            details = "\n".join(f"• {dep}" for dep in missing_deps)
            
            print("❌ 依赖检查失败:")
            print(details)
            print()
            print("💡 解决方案:")
            print("  1. 安装 PyQt6: pip install PyQt6")
            print("  2. 安装其他依赖: pip install -r requirements.txt")
            print("  3. 确保 yolo11n.pt 模型文件在项目根目录")
            
            show_error_dialog("依赖项缺失", error_msg, details)
            return 1
        
        print("✅ 依赖项检查通过")
        
        # 创建应用程序
        print("🚀 创建应用程序...")
        app = create_safe_application()
        
        # 尝试导入 UI 模块
        print("📦 加载 UI 模块...")
        main_window_class, version_name = try_import_ui_module()
        
        if main_window_class is None:
            error_msg = "无法加载任何 UI 模块，请检查代码完整性。"
            print(f"❌ {error_msg}")
            show_error_dialog("UI 模块加载失败", error_msg)
            return 1
        
        # 创建并显示主窗口
        print(f"🎨 启动界面 ({version_name})...")
        main_window = main_window_class()
        main_window.show()
        
        print("✅ 界面启动成功!")
        print("💡 使用提示:")
        print("  • 点击'开始检测'按钮开始实时检测")
        print("  • 使用菜单栏访问设置和功能")
        print("  • 按 Ctrl+Q 或关闭窗口退出应用")
        print()
        
        # 运行应用程序
        return app.exec()
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        return 0
        
    except Exception as e:
        error_msg = f"应用程序启动失败: {e}"
        error_details = traceback.format_exc()
        
        print(f"❌ {error_msg}")
        print("详细错误信息:")
        print(error_details)
        
        show_error_dialog("启动失败", error_msg, error_details)
        return 1


if __name__ == "__main__":
    sys.exit(main())
