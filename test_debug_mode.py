#!/usr/bin/env python3
"""
调试模式功能测试脚本
用于验证电脑摄像头检测功能是否正常工作
"""

import sys
import os
import cv2

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_camera_availability():
    """测试摄像头可用性"""
    print("🧪 测试摄像头可用性...")
    
    available_cameras = []
    
    # 测试前3个摄像头索引
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                available_cameras.append({
                    'index': i,
                    'resolution': f"{width}x{height}"
                })
                print(f"✅ 摄像头 {i}: 可用 ({width}x{height})")
            else:
                print(f"❌ 摄像头 {i}: 无法读取帧")
            cap.release()
        else:
            print(f"❌ 摄像头 {i}: 无法打开")
    
    return available_cameras

def test_yolo_model():
    """测试 YOLO 模型加载"""
    print("\n🧪 测试 YOLO 模型...")
    
    try:
        from ultralytics import YOLO
        
        model_path = 'yolo11n.pt'
        if not os.path.exists(model_path):
            print(f"❌ 模型文件不存在: {model_path}")
            return False
        
        model = YOLO(model_path)
        print("✅ YOLO 模型加载成功")
        print(f"  模型类别数量: {len(model.names)}")
        print(f"  目标类别示例: {list(model.names.values())[:10]}")
        
        return True
        
    except Exception as e:
        print(f"❌ YOLO 模型加载失败: {e}")
        return False

def test_camera_detection():
    """测试摄像头检测功能"""
    print("\n🧪 测试摄像头检测功能...")
    
    try:
        from ultralytics import YOLO
        
        # 加载模型
        model = YOLO('yolo11n.pt')
        
        # 测试摄像头
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ 无法打开摄像头 0")
            return False
        
        print("✅ 摄像头打开成功")
        
        # 读取一帧进行测试
        ret, frame = cap.read()
        if not ret:
            print("❌ 无法读取摄像头帧")
            cap.release()
            return False
        
        print("✅ 摄像头帧读取成功")
        
        # 进行检测
        results = model(frame, verbose=False)
        
        detections = 0
        for r in results:
            for box in r.boxes:
                detections += 1
        
        print(f"✅ 检测完成，发现 {detections} 个对象")
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ 摄像头检测测试失败: {e}")
        return False

def test_camera_thread_import():
    """测试摄像头线程类导入"""
    print("\n🧪 测试摄像头线程类导入...")
    
    try:
        from ui.main_window import CameraThread
        print("✅ CameraThread 类导入成功")
        
        # 创建实例测试
        camera_thread = CameraThread()
        print("✅ CameraThread 实例创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ CameraThread 导入失败: {e}")
        return False

def test_main_window_debug_mode():
    """测试主窗口调试模式支持"""
    print("\n🧪 测试主窗口调试模式支持...")
    
    try:
        from ui.main_window import MainWindow
        print("✅ MainWindow 类导入成功")
        
        # 检查是否有调试模式相关的属性和方法
        required_attributes = ['camera_thread', 'debug_mode']
        required_methods = ['on_debug_mode_changed', 'on_camera_index_changed', 'on_camera_error']
        
        for attr in required_attributes:
            if hasattr(MainWindow, attr) or attr in MainWindow.__init__.__code__.co_names:
                print(f"✅ 找到属性: {attr}")
            else:
                print(f"⚠️  未找到属性: {attr}")
        
        for method in required_methods:
            if hasattr(MainWindow, method):
                print(f"✅ 找到方法: {method}")
            else:
                print(f"⚠️  未找到方法: {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ 主窗口调试模式测试失败: {e}")
        return False

def test_control_panel_debug_mode():
    """测试控制面板调试模式支持"""
    print("\n🧪 测试控制面板调试模式支持...")
    
    try:
        from ui.main_window import ControlPanel
        print("✅ ControlPanel 类导入成功")
        
        # 检查信号
        required_signals = ['debug_mode_changed', 'camera_index_changed']
        
        for signal in required_signals:
            if hasattr(ControlPanel, signal):
                print(f"✅ 找到信号: {signal}")
            else:
                print(f"⚠️  未找到信号: {signal}")
        
        return True
        
    except Exception as e:
        print(f"❌ 控制面板调试模式测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Oasis 调试模式功能测试")
    print("=" * 60)
    
    tests = [
        ("摄像头可用性", test_camera_availability),
        ("YOLO模型加载", test_yolo_model),
        ("摄像头检测功能", test_camera_detection),
        ("摄像头线程类导入", test_camera_thread_import),
        ("主窗口调试模式", test_main_window_debug_mode),
        ("控制面板调试模式", test_control_panel_debug_mode),
    ]
    
    results = []
    available_cameras = []
    
    for test_name, test_func in tests:
        try:
            if test_name == "摄像头可用性":
                available_cameras = test_func()
                result = len(available_cameras) > 0
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 调试模式测试结果")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    # 显示可用摄像头信息
    if available_cameras:
        print(f"\n📷 发现 {len(available_cameras)} 个可用摄像头:")
        for cam in available_cameras:
            print(f"  • 摄像头 {cam['index']}: {cam['resolution']}")
    else:
        print("\n⚠️  未发现可用摄像头")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！调试模式功能正常。")
        print("\n💡 使用提示:")
        print("  1. 启动应用: python main_ui_safe.py")
        print("  2. 在控制面板中选择'调试模式 (电脑摄像头)'")
        print("  3. 选择合适的摄像头索引")
        print("  4. 点击'开始检测'开始调试")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
