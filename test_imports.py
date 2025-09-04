#!/usr/bin/env python3
"""
导入测试脚本
用于验证所有必要的模块是否能正确导入
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_config_import():
    """测试配置模块导入"""
    print("🧪 测试配置模块导入...")
    try:
        from ui.config import config_manager
        print("✅ config_manager 导入成功")
        print(f"  检测类别数量: {len(config_manager.detection.target_classes)}")
        return True
    except Exception as e:
        print(f"❌ config_manager 导入失败: {e}")
        return False

def test_main_window_import():
    """测试主窗口模块导入"""
    print("\n🧪 测试主窗口模块导入...")
    try:
        from ui.main_window import MainWindow
        print("✅ MainWindow 导入成功")
        return True
    except Exception as e:
        print(f"❌ MainWindow 导入失败: {e}")
        return False

def test_main_window_ui_import():
    """测试UI文件版本主窗口导入"""
    print("\n🧪 测试UI文件版本主窗口导入...")
    try:
        from ui.main_window_ui import MainWindowUI
        print("✅ MainWindowUI 导入成功")
        return True
    except Exception as e:
        print(f"❌ MainWindowUI 导入失败: {e}")
        return False

def test_settings_dialog_import():
    """测试设置对话框导入"""
    print("\n🧪 测试设置对话框导入...")
    try:
        from ui.settings_dialog import SettingsDialog
        print("✅ SettingsDialog 导入成功")
        return True
    except Exception as e:
        print(f"❌ SettingsDialog 导入失败: {e}")
        return False

def test_ui_loader_import():
    """测试UI加载器导入"""
    print("\n🧪 测试UI加载器导入...")
    try:
        from ui.ui_loader import UILoader
        print("✅ UILoader 导入成功")
        return True
    except Exception as e:
        print(f"❌ UILoader 导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Oasis 模块导入测试")
    print("=" * 60)
    
    tests = [
        ("配置模块", test_config_import),
        ("主窗口模块", test_main_window_import),
        ("UI文件主窗口", test_main_window_ui_import),
        ("设置对话框", test_settings_dialog_import),
        ("UI加载器", test_ui_loader_import),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 导入测试结果汇总")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 所有导入测试通过！可以正常启动应用程序。")
        return 0
    else:
        print("⚠️  部分导入测试失败，请检查代码。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
