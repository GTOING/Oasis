"""
Oasis 目标检测系统 - 设置对话框
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


class ColorButton(QPushButton):
    """颜色选择按钮"""
    color_changed = pyqtSignal(tuple)
    
    def __init__(self, color=(0, 255, 0)):
        super().__init__()
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


class DetectionSettingsTab(QWidget):
    """检测设置选项卡"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 模型设置组
        model_group = QGroupBox("模型设置")
        model_layout = QGridLayout()
        
        model_layout.addWidget(QLabel("模型文件:"), 0, 0)
        self.model_path_combo = QComboBox()
        self.model_path_combo.addItems(['yolo11n.pt', 'yolo11s.pt', 'yolo11m.pt', 'yolo11l.pt'])
        self.model_path_combo.setEditable(True)
        model_layout.addWidget(self.model_path_combo, 0, 1)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_model)
        model_layout.addWidget(browse_btn, 0, 2)
        
        model_layout.addWidget(QLabel("置信度阈值:"), 1, 0)
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(1, 100)
        self.confidence_slider.setValue(50)
        self.confidence_slider.valueChanged.connect(self.update_confidence_label)
        model_layout.addWidget(self.confidence_slider, 1, 1)
        
        self.confidence_label = QLabel("0.50")
        model_layout.addWidget(self.confidence_label, 1, 2)
        
        model_layout.addWidget(QLabel("最大检测数:"), 2, 0)
        self.max_detections_spin = QSpinBox()
        self.max_detections_spin.setRange(1, 1000)
        self.max_detections_spin.setValue(50)
        model_layout.addWidget(self.max_detections_spin, 2, 1)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # 目标类别组
        classes_group = QGroupBox("目标类别")
        classes_layout = QVBoxLayout()
        
        # 快速选择按钮
        buttons_layout = QHBoxLayout()
        select_all_btn = QPushButton("全选")
        select_none_btn = QPushButton("全不选")
        select_common_btn = QPushButton("常用物品")
        
        select_all_btn.clicked.connect(self.select_all_classes)
        select_none_btn.clicked.connect(self.select_no_classes)
        select_common_btn.clicked.connect(self.select_common_classes)
        
        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(select_none_btn)
        buttons_layout.addWidget(select_common_btn)
        buttons_layout.addStretch()
        
        classes_layout.addLayout(buttons_layout)
        
        # 类别列表
        self.classes_list = QListWidget()
        self.classes_list.setMaximumHeight(200)
        
        # 添加所有类别
        all_classes = config_manager.get_all_classes()
        for class_name in all_classes:
            item = QListWidgetItem(class_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.classes_list.addItem(item)
        
        classes_layout.addWidget(self.classes_list)
        classes_group.setLayout(classes_layout)
        layout.addWidget(classes_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_confidence_label(self, value):
        """更新置信度标签"""
        self.confidence_label.setText(f"{value/100:.2f}")
    
    def browse_model(self):
        """浏览模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模型文件", "", "YOLO模型 (*.pt);;所有文件 (*)"
        )
        if file_path:
            self.model_path_combo.setCurrentText(file_path)
    
    def select_all_classes(self):
        """选择所有类别"""
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
    
    def select_no_classes(self):
        """取消选择所有类别"""
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
    
    def select_common_classes(self):
        """选择常用类别"""
        common_classes = ['bottle', 'cup', 'cell phone', 'mouse', 'pen', 'laptop', 'book']
        
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            if item.text() in common_classes:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
    
    def load_settings(self):
        """加载设置"""
        config = config_manager.detection
        
        self.model_path_combo.setCurrentText(config.model_path)
        self.confidence_slider.setValue(int(config.confidence_threshold * 100))
        self.max_detections_spin.setValue(config.max_detections)
        
        # 设置目标类别
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            if item.text() in config.target_classes:
                item.setCheckState(Qt.CheckState.Checked)
    
    def save_settings(self):
        """保存设置"""
        config = config_manager.detection
        
        config.model_path = self.model_path_combo.currentText()
        config.confidence_threshold = self.confidence_slider.value() / 100.0
        config.max_detections = self.max_detections_spin.value()
        
        # 获取选中的类别
        selected_classes = []
        for i in range(self.classes_list.count()):
            item = self.classes_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_classes.append(item.text())
        
        config.target_classes = selected_classes


class DisplaySettingsTab(QWidget):
    """显示设置选项卡"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 显示选项组
        display_group = QGroupBox("显示选项")
        display_layout = QGridLayout()
        
        self.show_confidence_cb = QCheckBox("显示置信度")
        display_layout.addWidget(self.show_confidence_cb, 0, 0)
        
        self.show_class_names_cb = QCheckBox("显示类别名称")
        display_layout.addWidget(self.show_class_names_cb, 0, 1)
        
        display_layout.addWidget(QLabel("边框粗细:"), 1, 0)
        self.bbox_thickness_spin = QSpinBox()
        self.bbox_thickness_spin.setRange(1, 10)
        display_layout.addWidget(self.bbox_thickness_spin, 1, 1)
        
        display_layout.addWidget(QLabel("字体大小:"), 2, 0)
        self.font_scale_spin = QDoubleSpinBox()
        self.font_scale_spin.setRange(0.1, 2.0)
        self.font_scale_spin.setSingleStep(0.1)
        self.font_scale_spin.setDecimals(1)
        display_layout.addWidget(self.font_scale_spin, 2, 1)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # 颜色设置组
        color_group = QGroupBox("颜色设置")
        color_layout = QGridLayout()
        
        color_layout.addWidget(QLabel("边框颜色:"), 0, 0)
        self.bbox_color_btn = ColorButton()
        color_layout.addWidget(self.bbox_color_btn, 0, 1)
        
        color_layout.addWidget(QLabel("文字颜色:"), 1, 0)
        self.text_color_btn = ColorButton()
        color_layout.addWidget(self.text_color_btn, 1, 1)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_settings(self):
        """加载设置"""
        config = config_manager.display
        
        self.show_confidence_cb.setChecked(config.show_confidence)
        self.show_class_names_cb.setChecked(config.show_class_names)
        self.bbox_thickness_spin.setValue(config.bbox_thickness)
        self.font_scale_spin.setValue(config.font_scale)
        self.bbox_color_btn.set_color(config.bbox_color)
        self.text_color_btn.set_color(config.text_color)
    
    def save_settings(self):
        """保存设置"""
        config = config_manager.display
        
        config.show_confidence = self.show_confidence_cb.isChecked()
        config.show_class_names = self.show_class_names_cb.isChecked()
        config.bbox_thickness = self.bbox_thickness_spin.value()
        config.font_scale = self.font_scale_spin.value()
        config.bbox_color = self.bbox_color_btn.color
        config.text_color = self.text_color_btn.color


class KinectSettingsTab(QWidget):
    """Kinect 设置选项卡"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Kinect 设置组
        kinect_group = QGroupBox("Kinect 设置")
        kinect_layout = QGridLayout()
        
        kinect_layout.addWidget(QLabel("彩色分辨率:"), 0, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(['1920x1080', '1280x720', '640x480'])
        kinect_layout.addWidget(self.resolution_combo, 0, 1)
        
        kinect_layout.addWidget(QLabel("帧率 (FPS):"), 1, 0)
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(15, 60)
        kinect_layout.addWidget(self.fps_spin, 1, 1)
        
        self.auto_exposure_cb = QCheckBox("自动曝光")
        kinect_layout.addWidget(self.auto_exposure_cb, 2, 0, 1, 2)
        
        kinect_group.setLayout(kinect_layout)
        layout.addWidget(kinect_group)
        
        # 状态信息组
        status_group = QGroupBox("设备状态")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("正在检测 Kinect 设备...")
        status_layout.addWidget(self.status_label)
        
        refresh_btn = QPushButton("刷新设备状态")
        refresh_btn.clicked.connect(self.refresh_status)
        status_layout.addWidget(refresh_btn)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # 初始状态检测
        self.refresh_status()
    
    def refresh_status(self):
        """刷新设备状态"""
        try:
            from pykinect2 import PyKinectV2, PyKinectRuntime
            kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
            if kinect:
                self.status_label.setText("✓ Kinect 2.0 设备已连接并就绪")
                kinect.close()
            else:
                self.status_label.setText("✗ 未检测到 Kinect 2.0 设备")
        except Exception as e:
            self.status_label.setText(f"✗ Kinect 初始化失败: {str(e)}")
    
    def load_settings(self):
        """加载设置"""
        config = config_manager.kinect
        
        self.resolution_combo.setCurrentText(config.color_resolution)
        self.fps_spin.setValue(config.fps)
        self.auto_exposure_cb.setChecked(config.auto_exposure)
    
    def save_settings(self):
        """保存设置"""
        config = config_manager.kinect
        
        config.color_resolution = self.resolution_combo.currentText()
        config.fps = self.fps_spin.value()
        config.auto_exposure = self.auto_exposure_cb.isChecked()


class SettingsDialog(QDialog):
    """设置对话框"""
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("系统设置")
        self.setFixedSize(600, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 检测设置选项卡
        self.detection_tab = DetectionSettingsTab()
        self.tab_widget.addTab(self.detection_tab, "检测设置")
        
        # 显示设置选项卡
        self.display_tab = DisplaySettingsTab()
        self.tab_widget.addTab(self.display_tab, "显示设置")
        
        # Kinect 设置选项卡
        self.kinect_tab = KinectSettingsTab()
        self.tab_widget.addTab(self.kinect_tab, "Kinect 设置")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮组
        buttons_layout = QHBoxLayout()
        
        reset_btn = QPushButton("重置默认值")
        reset_btn.clicked.connect(self.reset_defaults)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setDefault(True)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def reset_defaults(self):
        """重置为默认值"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置所有设置为默认值吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            config_manager.reset_to_defaults()
            
            # 重新加载所有选项卡的设置
            self.detection_tab.load_settings()
            self.display_tab.load_settings()
            self.kinect_tab.load_settings()
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存所有选项卡的设置
            self.detection_tab.save_settings()
            self.display_tab.save_settings()
            self.kinect_tab.save_settings()
            
            # 保存配置文件
            config_manager.save_config()
            
            # 发出设置改变信号
            self.settings_changed.emit()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存设置时出错: {e}")
