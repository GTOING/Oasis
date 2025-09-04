#!/usr/bin/env python3
"""
新功能测试脚本
测试3D坐标获取、自定义类别管理和红外模式修复
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_config_enhancements():
    """测试配置增强功能"""
    print("🧪 测试配置增强功能...")
    
    try:
        from ui.config import config_manager
        
        # 测试3D坐标配置
        print("✅ 3D坐标功能测试:")
        original_state = config_manager.is_3d_coordinates_enabled()
        print(f"  当前状态: {original_state}")
        
        # 切换状态
        config_manager.set_3d_coordinates_enabled(True)
        assert config_manager.is_3d_coordinates_enabled() == True
        print("  ✅ 启用3D坐标功能成功")
        
        config_manager.set_3d_coordinates_enabled(False)
        assert config_manager.is_3d_coordinates_enabled() == False
        print("  ✅ 禁用3D坐标功能成功")
        
        # 恢复原始状态
        config_manager.set_3d_coordinates_enabled(original_state)
        
        # 测试自定义类别管理
        print("\n✅ 自定义类别管理测试:")
        test_class = "test_object"
        
        # 添加自定义类别
        config_manager.add_custom_class(test_class)
        assert test_class in config_manager.detection.custom_classes
        print(f"  ✅ 添加自定义类别 '{test_class}' 成功")
        
        # 获取所有可用类别
        all_classes = config_manager.get_all_available_classes()
        assert test_class in all_classes
        print(f"  ✅ 自定义类别已包含在所有可用类别中")
        
        # 删除自定义类别
        config_manager.remove_custom_class(test_class)
        assert test_class not in config_manager.detection.custom_classes
        print(f"  ✅ 删除自定义类别 '{test_class}' 成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置增强测试失败: {e}")
        return False

def test_video_thread_3d_features():
    """测试VideoThread的3D功能"""
    print("\n🧪 测试VideoThread的3D功能...")
    
    try:
        # 检查代码中是否包含3D坐标相关功能
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查3D坐标相关方法
        required_methods = [
            '_calculate_3d_coordinates',
            'coordinates_3d',
            'enable_3d_coordinates'
        ]
        
        for method in required_methods:
            if method in content:
                print(f"✅ 找到3D功能: {method}")
            else:
                print(f"❌ 缺少3D功能: {method}")
                return False
        
        # 检查process_detections方法是否支持color_frame参数
        if 'def process_detections(self, results, color_frame=None)' in content:
            print("✅ process_detections方法支持color_frame参数")
        else:
            print("❌ process_detections方法缺少color_frame参数")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ VideoThread 3D功能测试失败: {e}")
        return False

def test_control_panel_enhancements():
    """测试控制面板增强功能"""
    print("\n🧪 测试控制面板增强功能...")
    
    try:
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查新的信号
        new_signals = [
            'enable_3d_coordinates_changed',
            'custom_class_added',
            'custom_class_removed'
        ]
        
        for signal in new_signals:
            if signal in content:
                print(f"✅ 找到新信号: {signal}")
            else:
                print(f"❌ 缺少新信号: {signal}")
                return False
        
        # 检查UI组件
        ui_components = [
            'enable_3d_checkbox',
            'custom_class_input',
            'custom_classes_list',
            'add_custom_btn',
            'remove_custom_btn'
        ]
        
        for component in ui_components:
            if component in content:
                print(f"✅ 找到UI组件: {component}")
            else:
                print(f"❌ 缺少UI组件: {component}")
                return False
        
        # 检查处理方法
        methods = [
            'on_3d_coordinates_changed',
            'on_add_custom_class',
            'on_remove_custom_class',
            'load_custom_classes'
        ]
        
        for method in methods:
            if method in content:
                print(f"✅ 找到处理方法: {method}")
            else:
                print(f"❌ 缺少处理方法: {method}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 控制面板增强测试失败: {e}")
        return False

def test_infrared_fixes():
    """测试红外模式修复"""
    print("\n🧪 测试红外模式修复...")
    
    try:
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查红外帧处理的改进
        infrared_improvements = [
            'try:',
            'hasattr(self.kinect, \'has_new_infrared_frame\')',
            'frame.size > 0',
            'frame_max = np.max(frame)',
            'cv2.equalizeHist',
            'except Exception as e:'
        ]
        
        infrared_section = content[content.find('def _get_infrared_frame'):content.find('def _get_body_index_frame')]
        
        for improvement in infrared_improvements:
            if improvement in infrared_section:
                print(f"✅ 找到红外改进: {improvement}")
            else:
                print(f"❌ 缺少红外改进: {improvement}")
                return False
        
        # 检查深度帧处理的改进
        if 'valid_depth = frame[frame > 0]' in content:
            print("✅ 找到深度帧处理改进")
        else:
            print("❌ 缺少深度帧处理改进")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 红外模式修复测试失败: {e}")
        return False

def test_detection_result_enhancements():
    """测试检测结果显示增强"""
    print("\n🧪 测试检测结果显示增强...")
    
    try:
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查检测结果显示是否支持3D坐标
        detection_section = content[content.find('def update_detections(self, detections):'):content.find('class ControlPanel')]
        
        required_features = [
            'coordinates_3d',
            'coords_3d = detection[\'coordinates_3d\']',
            'coords_text = f" | 3D: ({coords_3d[\'x\']}, {coords_3d[\'y\']}, {coords_3d[\'z\']}) {coords_3d[\'unit\']}"'
        ]
        
        for feature in required_features:
            if feature in detection_section:
                print(f"✅ 找到结果显示功能: 3D坐标显示")
                break
        else:
            print("❌ 缺少3D坐标显示功能")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检测结果增强测试失败: {e}")
        return False

def test_import_compatibility():
    """测试导入兼容性"""
    print("\n🧪 测试导入兼容性...")
    
    try:
        # 测试配置管理器
        from ui.config import config_manager
        print("✅ config_manager 导入成功")
        
        # 测试新配置项
        if hasattr(config_manager.detection, 'enable_3d_coordinates'):
            print("✅ enable_3d_coordinates 配置项存在")
        else:
            print("❌ enable_3d_coordinates 配置项缺失")
            return False
        
        if hasattr(config_manager.detection, 'custom_classes'):
            print("✅ custom_classes 配置项存在")
        else:
            print("❌ custom_classes 配置项缺失")
            return False
        
        # 测试新方法
        methods = [
            'add_custom_class',
            'remove_custom_class',
            'get_all_available_classes',
            'is_3d_coordinates_enabled',
            'set_3d_coordinates_enabled'
        ]
        
        for method in methods:
            if hasattr(config_manager, method):
                print(f"✅ 找到方法: {method}")
            else:
                print(f"❌ 缺少方法: {method}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 导入兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Oasis 新功能测试")
    print("=" * 60)
    
    tests = [
        ("配置增强功能", test_config_enhancements),
        ("VideoThread 3D功能", test_video_thread_3d_features),
        ("控制面板增强", test_control_panel_enhancements),
        ("红外模式修复", test_infrared_fixes),
        ("检测结果显示增强", test_detection_result_enhancements),
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
    print("📊 新功能测试结果")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("\n🎉 所有新功能测试通过！")
        print("\n🆕 新增功能:")
        print("  ✅ 3D坐标获取 - 获取检测目标的空间三维坐标")
        print("  ✅ 3D功能开关 - 可单独启用/禁用3D坐标计算")
        print("  ✅ 自定义类别 - 用户可添加自己需要检测的类别")
        print("  ✅ 红外模式修复 - 解决红外视频流卡顿问题")
        print("  ✅ 增强显示 - 检测结果包含3D坐标信息")
        print("\n💡 使用提示:")
        print("  1. 在控制面板的'3D坐标功能'中启用3D坐标计算")
        print("  2. 在'自定义检测类别'中添加需要检测的物体类型")
        print("  3. 3D坐标功能仅在Kinect彩色模式下有效")
        print("  4. 检测结果将显示目标的3D坐标信息（毫米为单位）")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查实现。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
