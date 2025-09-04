"""
Oasis 目标检测系统 UI 模块
"""

from .config import config_manager

# UI 文件版本的导入（按需导入，避免依赖问题）
def get_main_window_ui():
    from .main_window_ui import MainWindowUI
    return MainWindowUI

def get_settings_dialog_ui():
    from .settings_dialog_ui import SettingsDialogUI
    return SettingsDialogUI

def get_main_window():
    from .main_window import MainWindow
    return MainWindow

def get_settings_dialog():
    from .settings_dialog import SettingsDialog
    return SettingsDialog

__all__ = ['config_manager', 'get_main_window_ui', 'get_settings_dialog_ui', 
           'get_main_window', 'get_settings_dialog']
