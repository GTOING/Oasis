"""
UI 加载工具类
用于动态加载 .ui 文件并应用样式
"""

import os
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication


class UILoader:
    """UI 文件加载器"""
    
    @staticmethod
    def load_ui(ui_file_name, parent_widget=None):
        """
        加载 UI 文件
        
        Args:
            ui_file_name: UI 文件名（不包含路径）
            parent_widget: 父窗口部件，如果为 None 则创建新窗口
            
        Returns:
            加载的 UI 对象
        """
        # 获取 UI 文件路径
        ui_dir = os.path.dirname(__file__)
        ui_path = os.path.join(ui_dir, ui_file_name)
        
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"UI 文件不存在: {ui_path}")
        
        # 加载 UI 文件
        if parent_widget is None:
            # 创建新窗口
            ui_object = uic.loadUi(ui_path)
        else:
            # 加载到现有窗口
            ui_object = uic.loadUi(ui_path, parent_widget)
        
        return ui_object
    
    @staticmethod
    def load_stylesheet(style_file_name="styles.qss"):
        """
        加载样式表文件
        
        Args:
            style_file_name: 样式表文件名
            
        Returns:
            样式表内容字符串
        """
        ui_dir = os.path.dirname(__file__)
        style_path = os.path.join(ui_dir, style_file_name)
        
        if not os.path.exists(style_path):
            print(f"警告: 样式表文件不存在: {style_path}")
            return ""
        
        try:
            with open(style_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取样式表失败: {e}")
            return ""
    
    @staticmethod
    def apply_stylesheet(widget, style_file_name="styles.qss"):
        """
        应用样式表到窗口部件
        
        Args:
            widget: 要应用样式的窗口部件
            style_file_name: 样式表文件名
        """
        stylesheet = UILoader.load_stylesheet(style_file_name)
        if stylesheet:
            widget.setStyleSheet(stylesheet)
    
    @staticmethod
    def get_ui_path(ui_file_name):
        """
        获取 UI 文件的完整路径
        
        Args:
            ui_file_name: UI 文件名
            
        Returns:
            UI 文件的完整路径
        """
        ui_dir = os.path.dirname(__file__)
        return os.path.join(ui_dir, ui_file_name)


class UIComponent:
    """UI 组件基类，提供 UI 文件加载功能"""
    
    def __init__(self, ui_file_name):
        """
        初始化 UI 组件
        
        Args:
            ui_file_name: UI 文件名
        """
        self.ui_file_name = ui_file_name
        self.ui = None
        
    def load_ui(self, parent_widget=None):
        """加载 UI"""
        self.ui = UILoader.load_ui(self.ui_file_name, parent_widget)
        return self.ui
    
    def apply_stylesheet(self, style_file_name="styles.qss"):
        """应用样式表"""
        if self.ui:
            UILoader.apply_stylesheet(self.ui, style_file_name)


# 预定义的 UI 文件名常量
UI_FILES = {
    'MAIN_WINDOW': 'main_window.ui',
    'SETTINGS_DIALOG': 'settings_dialog.ui',
}


def setup_ui_environment():
    """设置 UI 环境，确保正确加载资源"""
    app = QApplication.instance()
    if app is None:
        return False
    
    # 设置应用程序属性
    app.setApplicationName("Oasis 目标检测系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Oasis Team")
    
    return True


def validate_ui_files():
    """验证所有 UI 文件是否存在"""
    missing_files = []
    ui_dir = os.path.dirname(__file__)
    
    for name, filename in UI_FILES.items():
        file_path = os.path.join(ui_dir, filename)
        if not os.path.exists(file_path):
            missing_files.append(f"{name}: {filename}")
    
    if missing_files:
        print("缺少以下 UI 文件:")
        for file_info in missing_files:
            print(f"  - {file_info}")
        return False
    
    print("所有 UI 文件验证通过")
    return True


# 使用示例
if __name__ == "__main__":
    # 验证 UI 文件
    validate_ui_files()
    
    # 测试加载主窗口 UI
    try:
        main_ui = UILoader.load_ui(UI_FILES['MAIN_WINDOW'])
        print("主窗口 UI 加载成功")
        
        # 测试加载样式表
        stylesheet = UILoader.load_stylesheet()
        if stylesheet:
            print("样式表加载成功")
        else:
            print("样式表加载失败")
            
    except Exception as e:
        print(f"UI 加载测试失败: {e}")
