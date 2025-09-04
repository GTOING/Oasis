"""
Oasis 目标检测系统 - 设置对话框 (UI文件版本)
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QCheckBox, QSlider, QSpinBox,
                             QDoubleSpinBox, QComboBox, QPushButton, QGroupBox,
                             QGridLayout, QColorDialog, QFileDialog, QMessageBox,
                             QListWidget, QListWidgetItem, QFrame, QSpacerItem,
                             QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette
from .config import config_manager
from .ui_loader import UILoader, UI_FILES


class ColorButton(QPushButton):
    """颜色选择按钮"""
    color_changed = pyqtSignal(tuple)
    
    def __init__(self, color=(0, 255, 0), parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(60, 30)
        self.update_color()
        self.clicked.connect(self.choose_color)
    
    def update_color(self):
        """更新按钮颜色"""
        r, g, b = self.color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({r}, {g}, {b});
                border: 1px solid #C7C7CC;
                border-radius: 4px;
            }}
        """)
    
    def choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(QColor(*self.color), self, "选择颜色")
        if color.isValid():
            self.color = (color.red(), color.green(), color.blue())
            self.update_color()
            self.color_changed.emit(self.color)
    
    def set_color(self, color):
        """设置颜色"""
        self.color = color
        self.update_color()


class SettingsDialogUI(QDialog):
    """设置对话框 - 使用 UI 文件版本"""
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 加载 UI 文件
        self.ui = UILoader.load_ui(UI_FILES['SETTINGS_DIALOG'], self)
        
        # 应用样式表
        UILoader.apply_stylesheet(self)
        
        # 设置检测选项卡
        self.setup_detection_tab()
        
        # 设置显示选项卡
        self.setup_display_tab()
        
        # 设置 Kinect 选项卡
        self.setup_kinect_tab()
        
        # 连接信号
        self.connect_signals()
        
        # 加载设置
        self.load_settings()
        
    def setup_detection_tab(self):
        """设置检测选项卡"""
        # 添加所有类别到列表
        all_classes = config_manager.get_all_classes()
        for class_name in all_classes:
            item = QListWidgetItem(class_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.ui.classes_list.addItem(item)
            
    def setup_display_tab(self):
        """设置显示选项卡"""
        # 替换颜色按钮为自定义组件
        self.bbox_color_btn = ColorButton()
        self.text_color_btn = ColorButton()
        
        # 替换 UI 中的按钮
        self.replace_color_button('bbox_color_btn', self.bbox_color_btn)
        self.replace_color_button('text_color_btn', self.text_color_btn)
        
    def replace_color_button(self, ui_button_name, new_button):
        """替换 UI 中的颜色按钮"""
        old_button = getattr(self.ui, ui_button_name)
        parent = old_button.parent()
        layout = parent.layout()
        
        # 找到按钮在布局中的位置
        for i in range(layout.count()):
            if layout.itemAt(i).widget() == old_button:
                # 移除旧按钮
                layout.removeWidget(old_button)
                old_button.deleteLater()
                
                # 添加新按钮
                layout.addWidget(new_button, i // layout.columnCount(), i % layout.columnCount())
                
                # 更新引用
                setattr(self.ui, ui_button_name, new_button)
                break
                
    def setup_kinect_tab(self):
        """设置 Kinect 选项卡"""
        # 初始状态检测
        self.refresh_kinect_status()
        
    def connect_signals(self):
        """连接信号槽"""
        # 检测设置信号
        self.ui.confidence_slider.valueChanged.connect(self.update_confidence_label)
        self.ui.browse_btn.clicked.connect(self.browse_model)
        self.ui.select_all_btn.clicked.connect(self.select_all_classes)
        self.ui.select_none_btn.clicked.connect(self.select_no_classes)
        self.ui.select_common_btn.clicked.connect(self.select_common_classes)
        
        # 显示设置信号
        self.bbox_color_btn.color_changed.connect(lambda: None)  # 颜色改变会自动处理
        self.text_color_btn.color_changed.connect(lambda: None)
        
        # Kinect 设置信号
        self.ui.refresh_btn.clicked.connect(self.refresh_kinect_status)
        
        # 按钮信号
        self.ui.reset_btn.clicked.connect(self.reset_defaults)
        self.ui.cancel_btn.clicked.connect(self.reject)
        self.ui.save_btn.clicked.connect(self.save_settings)
        
    def update_confidence_label(self, value):
        """更新置信度标签"""
        self.ui.confidence_value_label.setText(f"{value/100:.2f}")
    
    def browse_model(self):
        """浏览模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模型文件", "", "YOLO模型 (*.pt);;所有文件 (*)"
        )
        if file_path:
            self.ui.model_path_combo.setCurrentText(file_path)
    
    def select_all_classes(self):
        """选择所有类别"""
        for i in range(self.ui.classes_list.count()):
            item = self.ui.classes_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
    
    def select_no_classes(self):
        """取消选择所有类别"""
        for i in range(self.ui.classes_list.count()):
            item = self.ui.classes_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
    
    def select_common_classes(self):
        """选择常用类别"""
        common_classes = ['bottle', 'cup', 'cell phone', 'mouse', 'pen', 'laptop', 'book']
        
        for i in range(self.ui.classes_list.count()):
            item = self.ui.classes_list.item(i)
            if item.text() in common_classes:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                
    def refresh_kinect_status(self):
        """刷新 Kinect 设备状态"""
        try:
            from pykinect2 import PyKinectV2, PyKinectRuntime
            kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
            if kinect:
                self.ui.status_label.setText("✓ Kinect 2.0 设备已连接并就绪")
                kinect.close()
            else:
                self.ui.status_label.setText("✗ 未检测到 Kinect 2.0 设备")
        except Exception as e:
            self.ui.status_label.setText(f"✗ Kinect 初始化失败: {str(e)}")
    
    def load_settings(self):
        """加载设置"""
        self.load_detection_settings()
        self.load_display_settings()
        self.load_kinect_settings()
        
    def load_detection_settings(self):
        """加载检测设置"""
        config = config_manager.detection
        
        self.ui.model_path_combo.setCurrentText(config.model_path)
        self.ui.confidence_slider.setValue(int(config.confidence_threshold * 100))
        self.ui.max_detections_spin.setValue(config.max_detections)
        
        # 设置目标类别
        for i in range(self.ui.classes_list.count()):
            item = self.ui.classes_list.item(i)
            if item.text() in config.target_classes:
                item.setCheckState(Qt.CheckState.Checked)
                
    def load_display_settings(self):
        """加载显示设置"""
        config = config_manager.display
        
        self.ui.show_confidence_cb.setChecked(config.show_confidence)
        self.ui.show_class_names_cb.setChecked(config.show_class_names)
        self.ui.bbox_thickness_spin.setValue(config.bbox_thickness)
        self.ui.font_scale_spin.setValue(config.font_scale)
        self.bbox_color_btn.set_color(config.bbox_color)
        self.text_color_btn.set_color(config.text_color)
        
    def load_kinect_settings(self):
        """加载 Kinect 设置"""
        config = config_manager.kinect
        
        self.ui.resolution_combo.setCurrentText(config.color_resolution)
        self.ui.fps_spin.setValue(config.fps)
        self.ui.auto_exposure_cb.setChecked(config.auto_exposure)
    
    def reset_defaults(self):
        """重置为默认值"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置所有设置为默认值吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            config_manager.reset_to_defaults()
            
            # 重新加载设置
            self.load_settings()
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存检测设置
            self.save_detection_settings()
            
            # 保存显示设置
            self.save_display_settings()
            
            # 保存 Kinect 设置
            self.save_kinect_settings()
            
            # 保存配置文件
            config_manager.save_config()
            
            # 发出设置改变信号
            self.settings_changed.emit()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存设置时出错: {e}")
            
    def save_detection_settings(self):
        """保存检测设置"""
        config = config_manager.detection
        
        config.model_path = self.ui.model_path_combo.currentText()
        config.confidence_threshold = self.ui.confidence_slider.value() / 100.0
        config.max_detections = self.ui.max_detections_spin.value()
        
        # 获取选中的类别
        selected_classes = []
        for i in range(self.ui.classes_list.count()):
            item = self.ui.classes_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_classes.append(item.text())
        
        config.target_classes = selected_classes
        
    def save_display_settings(self):
        """保存显示设置"""
        config = config_manager.display
        
        config.show_confidence = self.ui.show_confidence_cb.isChecked()
        config.show_class_names = self.ui.show_class_names_cb.isChecked()
        config.bbox_thickness = self.ui.bbox_thickness_spin.value()
        config.font_scale = self.ui.font_scale_spin.value()
        config.bbox_color = self.bbox_color_btn.color
        config.text_color = self.text_color_btn.color
        
    def save_kinect_settings(self):
        """保存 Kinect 设置"""
        config = config_manager.kinect
        
        config.color_resolution = self.ui.resolution_combo.currentText()
        config.fps = self.ui.fps_spin.value()
        config.auto_exposure = self.ui.auto_exposure_cb.isChecked()
