#!/usr/bin/env python3
"""
config_manager 修复验证脚本
专门用于验证 config_manager 导入问题是否已修复
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_config_manager_in_main_window():
    """测试主窗口文件中的 config_manager 引用"""
    print("🧪 测试主窗口文件中的 config_manager...")
    
    try:
        # 读取文件内容
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有 config_manager 导入
        if 'from .config import config_manager' in content:
            print("✅ main_window.py 中已添加 config_manager 导入")
        else:
            print("❌ main_window.py 中缺少 config_manager 导入")
            return False
        
        # 检查是否有 config_manager 的使用
        config_usage_count = content.count('config_manager')
        if config_usage_count > 1:  # 至少有导入和使用
            print(f"✅ config_manager 在文件中被使用了 {config_usage_count} 次")
        else:
            print("⚠️  config_manager 导入了但可能没有被使用")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def test_config_manager_direct_import():
    """直接测试 config_manager 导入"""
    print("\n🧪 直接测试 config_manager 导入...")
    
    try:
        from ui.config import config_manager
        print("✅ config_manager 导入成功")
        print(f"  配置文件类型: {type(config_manager)}")
        print(f"  检测类别: {config_manager.detection.target_classes}")
        print(f"  模型路径: {config_manager.detection.model_path}")
        return True
    except Exception as e:
        print(f"❌ config_manager 导入失败: {e}")
        return False

def test_other_imports_in_main_window():
    """测试主窗口文件中的其他导入"""
    print("\n🧪 检查主窗口文件中的其他导入...")
    
    required_imports = [
        'from .config import config_manager',
        'from .settings_dialog import SettingsDialog',
        'QAction',
        'QMessageBox',
        'import os'
    ]
    
    try:
        with open('ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if not missing_imports:
            print("✅ 所有必需的导入都已添加")
            return True
        else:
            print(f"❌ 缺少以下导入: {missing_imports}")
            return False
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def test_syntax_check():
    """语法检查"""
    print("\n🧪 Python 语法检查...")
    
    files_to_check = [
        'ui/main_window.py',
        'ui/config.py',
        'ui/settings_dialog.py'
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的语法检查
            compile(content, file_path, 'exec')
            print(f"✅ {file_path} 语法正确")
            
        except SyntaxError as e:
            print(f"❌ {file_path} 语法错误: {e}")
            all_good = False
        except Exception as e:
            print(f"⚠️  {file_path} 检查时出错: {e}")
    
    return all_good

def main():
    """主测试函数"""
    print("=" * 60)
    print("🔧 config_manager 修复验证")
    print("=" * 60)
    
    tests = [
        ("配置管理器导入检查", test_config_manager_in_main_window),
        ("直接导入测试", test_config_manager_direct_import),
        ("其他导入检查", test_other_imports_in_main_window),
        ("Python语法检查", test_syntax_check),
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
    print("📊 修复验证结果")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 config_manager 导入问题已完全修复！")
        print("\n💡 现在可以尝试运行应用程序:")
        print("  python main_ui_safe.py  # 推荐")
        print("  python main_ui.py       # 标准版本")
        return 0
    else:
        print("⚠️  仍有部分问题需要解决。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
