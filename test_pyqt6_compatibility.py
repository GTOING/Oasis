#!/usr/bin/env python3
"""
PyQt6 兼容性测试脚本
用于检查 PyQt6 的版本兼容性问题
"""

import sys
import os

def test_pyqt6_basic():
    """测试 PyQt6 基本功能"""
    print("🧪 测试 PyQt6 基本功能...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
        from PyQt6.QtCore import Qt
        print("✅ PyQt6 模块导入成功")
        
        # 创建应用程序
        app = QApplication(sys.argv)
        print("✅ QApplication 创建成功")
        
        # 测试高 DPI 属性兼容性
        high_dpi_attrs = [
            ('AA_EnableHighDpiScaling', 'AA_EnableHighDpiScaling'),
            ('AA_UseHighDpiPixmaps', 'AA_UseHighDpiPixmaps'),
        ]
        
        for attr_name, attr_display in high_dpi_attrs:
            try:
                attr = getattr(Qt.ApplicationAttribute, attr_name)
                app.setAttribute(attr, True)
                print(f"✅ {attr_display} 设置成功")
            except AttributeError:
                print(f"ℹ️  {attr_display} 属性不存在 (PyQt6 中可能已弃用，这是正常的)")
        
        # 创建简单窗口测试
        window = QMainWindow()
        window.setWindowTitle("PyQt6 兼容性测试")
        window.resize(300, 200)
        
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        label = QLabel("PyQt6 测试成功!", central_widget)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        print("✅ 窗口创建成功")
        
        # 显示窗口（快速测试）
        window.show()
        print("✅ 窗口显示成功")
        
        # 立即关闭（避免阻塞）
        window.close()
        app.quit()
        
        print("✅ PyQt6 基本功能测试完成")
        return True
        
    except ImportError as e:
        print(f"❌ PyQt6 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ PyQt6 测试失败: {e}")
        return False

def test_ui_file_loading():
    """测试 UI 文件加载功能"""
    print("\n🧪 测试 UI 文件加载...")
    
    try:
        from PyQt6 import uic
        print("✅ PyQt6.uic 模块导入成功")
        
        # 检查 UI 文件是否存在
        ui_files = [
            'ui/main_window.ui',
            'ui/settings_dialog.ui'
        ]
        
        for ui_file in ui_files:
            if os.path.exists(ui_file):
                print(f"✅ {ui_file} 文件存在")
                
                # 尝试加载 UI 文件（不创建实例）
                try:
                    with open(ui_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if '<ui version="4.0">' in content:
                        print(f"✅ {ui_file} 格式正确")
                    else:
                        print(f"⚠️  {ui_file} 格式可能有问题")
                except Exception as e:
                    print(f"❌ {ui_file} 读取失败: {e}")
            else:
                print(f"❌ {ui_file} 文件不存在")
        
        return True
        
    except ImportError as e:
        print(f"❌ PyQt6.uic 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ UI 文件测试失败: {e}")
        return False

def test_dependencies():
    """测试其他依赖项"""
    print("\n🧪 测试其他依赖项...")
    
    dependencies = [
        ('numpy', 'NumPy'),
        ('cv2', 'OpenCV'),
        ('ultralytics', 'YOLO'),
    ]
    
    missing_deps = []
    
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {display_name} 导入成功")
        except ImportError:
            print(f"❌ {display_name} 未安装")
            missing_deps.append(display_name)
    
    if missing_deps:
        print(f"\n⚠️  缺少依赖项: {', '.join(missing_deps)}")
        print("运行以下命令安装:")
        print("pip install opencv-python ultralytics numpy")
        return False
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Oasis PyQt6 兼容性测试")
    print("=" * 60)
    
    tests = [
        ("PyQt6 基本功能", test_pyqt6_basic),
        ("UI 文件加载", test_ui_file_loading),
        ("依赖项检查", test_dependencies),
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
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！系统准备就绪。")
        print("\n💡 建议:")
        print("  - 运行 'python main_ui.py' 启动原始版本")
        print("  - 运行 'python main_ui_loader.py' 启动 UI 文件版本")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置。")
        
        if not any(result for name, result in results if "PyQt6" in name):
            print("\n💡 PyQt6 相关问题解决方案:")
            print("  1. 重新安装 PyQt6: pip install --upgrade PyQt6")
            print("  2. 检查 Python 版本: python --version (需要 3.8+)")
            print("  3. 清理缓存: pip cache purge")
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 用户中断测试")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 测试脚本异常: {e}")
        sys.exit(1)
