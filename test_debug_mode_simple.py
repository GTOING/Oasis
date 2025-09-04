#!/usr/bin/env python3
"""
调试模式功能简化测试脚本
只测试代码结构，不测试实际的摄像头功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_camera_thread_class():
    """测试摄像头线程类"""
    print("🧪 测试摄像头线程类...")
    
    try:
        from ui.main_window import CameraThread
        print("✅ CameraThread 类导入成功")
        
        # 创建实例
        camera_thread = CameraThread()
        print("✅ CameraThread 实例创建成功")
        
        # 检查必要的方法
        required_methods = ['set_model', 'set_camera_index', 'set_target_classes', 'run', 'stop']
        for method in required_methods:
            if hasattr(camera_thread, method):
                print(f"✅ 找到方法: {method}")
            else:
                print(f"❌ 缺少方法: {method}")
                return False
        
        # 检查信号
        required_signals = ['frame_ready', 'detection_ready', 'error_occurred']
        for signal in required_signals:
            if hasattr(camera_thread, signal):
                print(f"✅ 找到信号: {signal}")
            else:
                print(f"❌ 缺少信号: {signal}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ CameraThread 测试失败: {e}")
        return False

def test_control_panel_debug_features():
    """测试控制面板调试功能"""
    print("\n🧪 测试控制面板调试功能...")
    
    try:
        from ui.main_window import ControlPanel
        print("✅ ControlPanel 类导入成功")
        
        # 创建实例
        control_panel = ControlPanel()
        print("✅ ControlPanel 实例创建成功")
        
        # 检查调试模式相关的信号
        debug_signals = ['debug_mode_changed', 'camera_index_changed']
        for signal in debug_signals:
            if hasattr(control_panel, signal):
                print(f"✅ 找到调试信号: {signal}")
            else:
                print(f"❌ 缺少调试信号: {signal}")
                return False
        
        # 检查调试模式相关的方法
        debug_methods = ['on_mode_changed', 'on_camera_changed', 'is_debug_mode', 'get_camera_index']
        for method in debug_methods:
            if hasattr(control_panel, method):
                print(f"✅ 找到调试方法: {method}")
            else:
                print(f"❌ 缺少调试方法: {method}")
                return False
        
        # 检查UI组件
        ui_components = ['kinect_mode_rb', 'debug_mode_rb', 'camera_combo']
        for component in ui_components:
            if hasattr(control_panel, component):
                print(f"✅ 找到UI组件: {component}")
            else:
                print(f"❌ 缺少UI组件: {component}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ ControlPanel 调试功能测试失败: {e}")
        return False

def test_main_window_debug_integration():
    """测试主窗口调试模式集成"""
    print("\n🧪 测试主窗口调试模式集成...")
    
    try:
        from ui.main_window import MainWindow
        print("✅ MainWindow 类导入成功")
        
        # 检查调试模式相关的属性
        # 注意：我们不能创建实例，因为会尝试初始化GUI
        main_window_code = open('ui/main_window.py', 'r', encoding='utf-8').read()
        
        debug_features = [
            'camera_thread',
            'debug_mode',
            'on_debug_mode_changed',
            'on_camera_index_changed',
            'on_camera_error'
        ]
        
        for feature in debug_features:
            if feature in main_window_code:
                print(f"✅ 找到调试功能: {feature}")
            else:
                print(f"❌ 缺少调试功能: {feature}")
                return False
        
        # 检查是否有CameraThread的使用
        if 'CameraThread()' in main_window_code:
            print("✅ 找到 CameraThread 的使用")
        else:
            print("❌ 未找到 CameraThread 的使用")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ MainWindow 调试集成测试失败: {e}")
        return False

def test_code_structure():
    """测试代码结构完整性"""
    print("\n🧪 测试代码结构完整性...")
    
    try:
        # 检查文件是否存在
        required_files = [
            'ui/main_window.py',
            'main.py',
            'ui/config.py'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"✅ 文件存在: {file_path}")
            else:
                print(f"❌ 文件缺失: {file_path}")
                return False
        
        # 检查main.py的内容是否被集成
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            main_window_content = f.read()
        
        # 检查是否有电脑摄像头相关的代码
        camera_features = [
            'cv2.VideoCapture',
            'camera.read()',
            'CAP_PROP_FRAME_WIDTH'
        ]
        
        for feature in camera_features:
            if feature in main_window_content:
                print(f"✅ 找到摄像头功能: {feature}")
            else:
                print(f"⚠️  摄像头功能可能不完整: {feature}")
        
        return True
        
    except Exception as e:
        print(f"❌ 代码结构测试失败: {e}")
        return False

def test_import_compatibility():
    """测试导入兼容性"""
    print("\n🧪 测试导入兼容性...")
    
    try:
        # 测试基础导入
        from ui.config import config_manager
        print("✅ config_manager 导入成功")
        
        # 测试PyQt6组件导入（如果可用）
        try:
            from PyQt6.QtCore import QThread, pyqtSignal
            print("✅ PyQt6 核心组件导入成功")
        except ImportError:
            print("⚠️  PyQt6 未安装，但代码结构正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Oasis 调试模式代码结构测试")
    print("=" * 60)
    
    tests = [
        ("摄像头线程类", test_camera_thread_class),
        ("控制面板调试功能", test_control_panel_debug_features),
        ("主窗口调试集成", test_main_window_debug_integration),
        ("代码结构完整性", test_code_structure),
        ("导入兼容性", test_import_compatibility),
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
    print("📊 调试模式代码结构测试结果")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("\n🎉 调试模式代码结构完整！")
        print("\n📋 调试模式功能:")
        print("  ✅ 电脑摄像头视频线程类 (CameraThread)")
        print("  ✅ 调试模式切换控件")
        print("  ✅ 摄像头选择下拉框")
        print("  ✅ 双模式检测支持 (Kinect + 摄像头)")
        print("  ✅ 错误处理和状态反馈")
        print("\n💡 使用说明:")
        print("  1. 启动应用后，在控制面板中选择检测模式")
        print("  2. Kinect 2.0 模式：使用 Kinect 深度相机")
        print("  3. 调试模式：使用电脑内置或外接摄像头")
        print("  4. 调试模式下可选择不同的摄像头索引")
        print("\n🚀 准备启动:")
        print("  python main_ui_safe.py  # 推荐启动方式")
        return 0
    else:
        print("\n⚠️  代码结构存在问题，请检查。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
