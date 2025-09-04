#!/usr/bin/env python3
"""
UI 加载功能测试脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_ui_files():
    """测试 UI 文件是否存在"""
    print("🧪 测试 UI 文件...")
    
    from ui.ui_loader import validate_ui_files, UI_FILES
    
    # 检查 UI 文件
    ui_dir = os.path.join(project_root, 'ui')
    print(f"UI 目录: {ui_dir}")
    
    for name, filename in UI_FILES.items():
        file_path = os.path.join(ui_dir, filename)
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {filename}")
    
    # 运行验证
    result = validate_ui_files()
    print(f"\n验证结果: {'通过' if result else '失败'}")
    
    return result

def test_ui_loader():
    """测试 UI 加载器"""
    print("\n🧪 测试 UI 加载器...")
    
    try:
        from ui.ui_loader import UILoader
        
        # 测试样式表加载
        stylesheet = UILoader.load_stylesheet()
        if stylesheet:
            print("✅ 样式表加载成功")
            print(f"  样式表长度: {len(stylesheet)} 字符")
        else:
            print("❌ 样式表加载失败")
        
        # 测试 UI 路径获取
        ui_path = UILoader.get_ui_path('main_window.ui')
        print(f"✅ UI 路径: {ui_path}")
        print(f"  文件存在: {os.path.exists(ui_path)}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI 加载器测试失败: {e}")
        return False

def test_config_manager():
    """测试配置管理器"""
    print("\n🧪 测试配置管理器...")
    
    try:
        from ui.config import config_manager
        
        print("✅ 配置管理器导入成功")
        print(f"  检测类别数量: {len(config_manager.detection.target_classes)}")
        print(f"  模型路径: {config_manager.detection.model_path}")
        print(f"  置信度阈值: {config_manager.detection.confidence_threshold}")
        
        # 测试获取所有类别
        all_classes = config_manager.get_all_classes()
        print(f"  所有类别数量: {len(all_classes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("🧪 Oasis UI 系统测试")
    print("=" * 50)
    
    tests = [
        ("UI 文件检查", test_ui_files),
        ("UI 加载器", test_ui_loader),
        ("配置管理器", test_config_manager),
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
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！UI 系统准备就绪。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
