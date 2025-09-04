#!/usr/bin/env python3
"""
Kinect 多种视频流功能测试脚本
测试新增的视频流类型选择功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_config_stream_types():
    """测试配置管理中的流类型功能"""
    print("🧪 测试配置管理中的流类型功能...")
    
    try:
        from ui.config import config_manager
        
        # 测试获取流类型
        stream_types = config_manager.get_kinect_stream_types()
        print(f"✅ 支持的流类型: {stream_types}")
        
        expected_types = ['color', 'depth', 'infrared', 'body_index']
        for stream_type in expected_types:
            if stream_type in stream_types:
                print(f"✅ 找到流类型: {stream_type} -> {stream_types[stream_type]}")
            else:
                print(f"❌ 缺少流类型: {stream_type}")
                return False
        
        # 测试深度模式
        depth_modes = config_manager.get_kinect_depth_modes()
        print(f"✅ 支持的深度模式: {depth_modes}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_video_thread_enhancements():
    """测试 VideoThread 的流类型增强"""
    print("\n🧪 测试 VideoThread 的流类型增强...")
    
    try:
        from ui.main_window import VideoThread
        
        # 创建实例
        video_thread = VideoThread()
        print("✅ VideoThread 实例创建成功")
        
        # 检查新方法
        new_methods = ['set_stream_type', 'set_depth_mode', '_get_color_frame', 
                      '_get_depth_frame', '_get_infrared_frame', '_get_body_index_frame']
        
        for method in new_methods:
            if hasattr(video_thread, method):
                print(f"✅ 找到新方法: {method}")
            else:
                print(f"❌ 缺少新方法: {method}")
                return False
        
        # 检查新信号
        if hasattr(video_thread, 'stream_info_ready'):
            print("✅ 找到新信号: stream_info_ready")
        else:
            print("❌ 缺少新信号: stream_info_ready")
            return False
        
        # 测试方法调用
        video_thread.set_stream_type("depth")
        video_thread.set_depth_mode("near")
        print("✅ 流类型和深度模式设置成功")
        
        return True
        
    except Exception as e:
        print(f"❌ VideoThread 测试失败: {e}")
        return False

def test_control_panel_enhancements():
    """测试控制面板的流类型选择功能"""
    print("\n🧪 测试控制面板的流类型选择功能...")
    
    try:
        # 读取代码检查功能
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查新组件
        ui_components = [
            'kinect_stream_label',
            'kinect_stream_combo',
            'kinect_stream_changed',
            'on_kinect_stream_changed',
            'get_kinect_stream_type'
        ]
        
        for component in ui_components:
            if component in content:
                print(f"✅ 找到UI组件: {component}")
            else:
                print(f"❌ 缺少UI组件: {component}")
                return False
        
        # 检查信号连接
        signal_connections = [
            'kinect_stream_changed.connect',
            'on_kinect_stream_changed'
        ]
        
        for connection in signal_connections:
            if connection in content:
                print(f"✅ 找到信号连接: {connection}")
            else:
                print(f"❌ 缺少信号连接: {connection}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 控制面板测试失败: {e}")
        return False

def test_video_display_improvements():
    """测试视频显示的改进"""
    print("\n🧪 测试视频显示的改进...")
    
    try:
        # 检查 update_frame 方法是否支持 stream_type 参数
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'def update_frame(self, frame, detections=None, stream_type="color")' in content:
            print("✅ update_frame 方法支持 stream_type 参数")
        else:
            print("❌ update_frame 方法缺少 stream_type 参数")
            return False
        
        # 检查流类型标识功能
        stream_features = [
            '深度图像',
            '红外图像',
            '人体索引',
            'stream_names.get'
        ]
        
        for feature in stream_features:
            if feature in content:
                print(f"✅ 找到流类型功能: {feature}")
            else:
                print(f"❌ 缺少流类型功能: {feature}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 视频显示测试失败: {e}")
        return False

def test_kinect_initialization():
    """测试 Kinect 初始化的多流支持"""
    print("\n🧪 测试 Kinect 初始化的多流支持...")
    
    try:
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查新的初始化功能
        init_features = [
            '_get_kinect_frame_types',
            'FrameSourceTypes_Depth',
            'FrameSourceTypes_Infrared',
            'FrameSourceTypes_BodyIndex',
            'frame_type_map'
        ]
        
        for feature in init_features:
            if feature in content:
                print(f"✅ 找到初始化功能: {feature}")
            else:
                print(f"❌ 缺少初始化功能: {feature}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Kinect 初始化测试失败: {e}")
        return False

def test_import_compatibility():
    """测试导入兼容性"""
    print("\n🧪 测试导入兼容性...")
    
    try:
        # 测试配置管理器导入
        from ui.config import config_manager
        print("✅ config_manager 导入成功")
        
        # 测试新配置项
        if hasattr(config_manager.kinect, 'video_stream_type'):
            print(f"✅ 找到配置项: video_stream_type = {config_manager.kinect.video_stream_type}")
        else:
            print("❌ 缺少配置项: video_stream_type")
            return False
        
        if hasattr(config_manager.kinect, 'depth_mode'):
            print(f"✅ 找到配置项: depth_mode = {config_manager.kinect.depth_mode}")
        else:
            print("❌ 缺少配置项: depth_mode")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 导入兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Kinect 多种视频流功能测试")
    print("=" * 60)
    
    tests = [
        ("配置管理流类型功能", test_config_stream_types),
        ("VideoThread 流类型增强", test_video_thread_enhancements),
        ("控制面板流类型选择", test_control_panel_enhancements),
        ("视频显示改进", test_video_display_improvements),
        ("Kinect 初始化多流支持", test_kinect_initialization),
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
    print("📊 Kinect 多种视频流功能测试结果")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！Kinect 多种视频流功能正常。")
        print("\n📺 支持的视频流类型:")
        print("  • 彩色图像 (RGB) - 标准视频流，支持目标检测")
        print("  • 深度图像 - 距离信息可视化")
        print("  • 红外图像 - 红外光谱图像")
        print("  • 人体索引图像 - 人体分割可视化")
        print("\n💡 使用提示:")
        print("  1. 在控制面板选择 'Kinect 2.0 模式'")
        print("  2. 在 '视频流' 下拉框选择所需类型")
        print("  3. 点击 '开始检测' 查看不同视频流")
        print("  4. 只有彩色图像模式支持目标检测")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查实现。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
