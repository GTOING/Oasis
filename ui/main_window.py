"""
Oasis 目标检测系统 - 主窗口界面
基于 PyQt6 的现代化 UI 设计
"""

import sys
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QGroupBox, QListWidget, QSlider, QSpinBox,
                             QCheckBox, QComboBox, QStatusBar, QSplitter,
                             QFrame, QGridLayout, QSpacerItem, QSizePolicy,
                             QMessageBox)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon, QAction
from ultralytics import YOLO
from .config import config_manager
from .settings_dialog import SettingsDialog


class VideoThread(QThread):
    """Kinect 视频处理线程"""
    frame_ready = pyqtSignal(np.ndarray)
    detection_ready = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.kinect = None
        self.running = False
        self.target_classes = config_manager.detection.target_classes
        
    def set_model(self, model):
        self.model = model
        
    def set_kinect(self, kinect):
        self.kinect = kinect
        
    def set_target_classes(self, classes):
        self.target_classes = classes
        
    def run(self):
        """主运行循环"""
        self.running = True
        
        if not self.kinect:
            return
            
        frame_width = self.kinect.color_frame_desc.Width
        frame_height = self.kinect.color_frame_desc.Height
        
        while self.running:
            try:
                if self.kinect.has_new_color_frame():
                    # 获取彩色帧
                    frame = self.kinect.get_last_color_frame()
                    frame = frame.reshape((frame_height, frame_width, 4))
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                    
                    # 发送原始帧
                    self.frame_ready.emit(frame_bgr.copy())
                    
                    # 执行检测
                    if self.model:
                        results = self.model(frame_bgr, verbose=False)
                        detections = self.process_detections(results)
                        self.detection_ready.emit(detections)
                        
                self.msleep(30)  # 约30FPS
                
            except Exception as e:
                print(f"Kinect 视频线程错误: {e}")
                
    def process_detections(self, results):
        """处理检测结果"""
        detections = []
        
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                conf = box.conf[0].item()
                
                if class_name in self.target_classes and conf >= config_manager.detection.confidence_threshold:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    detection = {
                        'class_name': class_name,
                        'confidence': conf,
                        'bbox': (int(x1), int(y1), int(x2), int(y2))
                    }
                    detections.append(detection)
                    
                    # 限制最大检测数量
                    if len(detections) >= config_manager.detection.max_detections:
                        break
                    
        return detections
    
    def stop(self):
        self.running = False


class CameraThread(QThread):
    """电脑摄像头视频处理线程（调试模式）"""
    frame_ready = pyqtSignal(np.ndarray)
    detection_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.camera = None
        self.running = False
        self.target_classes = config_manager.detection.target_classes
        self.camera_index = 0
        
    def set_model(self, model):
        self.model = model
        
    def set_camera_index(self, index):
        self.camera_index = index
        
    def set_target_classes(self, classes):
        self.target_classes = classes
        
    def run(self):
        """主运行循环"""
        self.running = True
        
        # 初始化摄像头
        self.camera = cv2.VideoCapture(self.camera_index)
        
        if not self.camera.isOpened():
            self.error_occurred.emit(f"无法打开摄像头 {self.camera_index}")
            return
        
        # 设置摄像头参数
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        while self.running:
            try:
                ret, frame = self.camera.read()
                
                if not ret:
                    self.error_occurred.emit("无法从摄像头读取帧")
                    break
                
                # 发送原始帧
                self.frame_ready.emit(frame.copy())
                
                # 执行检测
                if self.model:
                    results = self.model(frame, verbose=False)
                    detections = self.process_detections(results)
                    self.detection_ready.emit(detections)
                
                self.msleep(33)  # 约30FPS
                
            except Exception as e:
                self.error_occurred.emit(f"摄像头线程错误: {e}")
                break
                
    def process_detections(self, results):
        """处理检测结果"""
        detections = []
        
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                conf = box.conf[0].item()
                
                if class_name in self.target_classes and conf >= config_manager.detection.confidence_threshold:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    detection = {
                        'class_name': class_name,
                        'confidence': conf,
                        'bbox': (int(x1), int(y1), int(x2), int(y2))
                    }
                    detections.append(detection)
                    
                    # 限制最大检测数量
                    if len(detections) >= config_manager.detection.max_detections:
                        break
                    
        return detections
    
    def stop(self):
        self.running = False
        if self.camera:
            self.camera.release()


class ModernButton(QPushButton):
    """现代化样式按钮"""
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.setFixedHeight(35)
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0056D3;
                }
                QPushButton:pressed {
                    background-color: #004A9F;
                }
                QPushButton:disabled {
                    background-color: #C7C7CC;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F2F2F7;
                    color: #007AFF;
                    border: 1px solid #C7C7CC;
                    border-radius: 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #E5E5EA;
                }
                QPushButton:pressed {
                    background-color: #D1D1D6;
                }
            """)


class DetectionWidget(QWidget):
    """检测结果显示组件"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("检测结果")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 结果列表
        self.result_list = QListWidget()
        self.result_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #C7C7CC;
                border-radius: 8px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                margin: 2px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
        """)
        layout.addWidget(self.result_list)
        
        # 统计信息
        self.stats_label = QLabel("当前检测: 0 个对象")
        self.stats_label.setStyleSheet("color: #8E8E93; font-size: 12px;")
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
        
    def update_detections(self, detections):
        """更新检测结果"""
        self.result_list.clear()
        
        for detection in detections:
            item_text = f"{detection['class_name']} ({detection['confidence']:.2f})"
            self.result_list.addItem(item_text)
            
        self.stats_label.setText(f"当前检测: {len(detections)} 个对象")


class ControlPanel(QWidget):
    """控制面板"""
    start_detection = pyqtSignal()
    stop_detection = pyqtSignal()
    target_classes_changed = pyqtSignal(list)
    debug_mode_changed = pyqtSignal(bool)
    camera_index_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("控制面板")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 模式选择组
        mode_group = QGroupBox("检测模式")
        mode_layout = QVBoxLayout()
        
        # 模式选择
        self.kinect_mode_rb = QCheckBox("Kinect 2.0 模式")
        self.debug_mode_rb = QCheckBox("调试模式 (电脑摄像头)")
        
        # 默认选择 Kinect 模式
        self.kinect_mode_rb.setChecked(True)
        
        # 连接信号
        self.kinect_mode_rb.toggled.connect(self.on_mode_changed)
        self.debug_mode_rb.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.kinect_mode_rb)
        mode_layout.addWidget(self.debug_mode_rb)
        
        # 摄像头选择（仅调试模式）
        camera_layout = QHBoxLayout()
        self.camera_label = QLabel("摄像头:")
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["摄像头 0", "摄像头 1", "摄像头 2"])
        self.camera_combo.setCurrentIndex(0)
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        
        camera_layout.addWidget(self.camera_label)
        camera_layout.addWidget(self.camera_combo)
        camera_layout.addStretch()
        
        mode_layout.addLayout(camera_layout)
        
        # 初始状态：摄像头选择不可用
        self.camera_label.setEnabled(False)
        self.camera_combo.setEnabled(False)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # 控制按钮组
        button_group = QGroupBox("检测控制")
        button_layout = QVBoxLayout()
        
        self.start_btn = ModernButton("开始检测", primary=True)
        self.stop_btn = ModernButton("停止检测")
        self.stop_btn.setEnabled(False)
        
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)
        
        # 目标类别选择
        classes_group = QGroupBox("检测类别")
        classes_layout = QVBoxLayout()
        
        all_classes = config_manager.get_all_classes()[:10]  # 显示前10个类别
        
        self.class_checkboxes = {}
        default_classes = config_manager.detection.target_classes
        
        for class_name in all_classes:
            checkbox = QCheckBox(class_name)
            checkbox.setChecked(class_name in default_classes)
            checkbox.stateChanged.connect(self.on_class_changed)
            self.class_checkboxes[class_name] = checkbox
            classes_layout.addWidget(checkbox)
            
        classes_group.setLayout(classes_layout)
        layout.addWidget(classes_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.setLayout(layout)
        
    def on_start_clicked(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.start_detection.emit()
        
    def on_stop_clicked(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.stop_detection.emit()
        
    def on_mode_changed(self):
        """模式切换处理"""
        # 确保只有一个模式被选中
        sender = self.sender()
        if sender == self.kinect_mode_rb and self.kinect_mode_rb.isChecked():
            self.debug_mode_rb.setChecked(False)
            self.camera_label.setEnabled(False)
            self.camera_combo.setEnabled(False)
            self.debug_mode_changed.emit(False)
        elif sender == self.debug_mode_rb and self.debug_mode_rb.isChecked():
            self.kinect_mode_rb.setChecked(False)
            self.camera_label.setEnabled(True)
            self.camera_combo.setEnabled(True)
            self.debug_mode_changed.emit(True)
        
        # 如果都没选中，默认选择 Kinect 模式
        if not self.kinect_mode_rb.isChecked() and not self.debug_mode_rb.isChecked():
            self.kinect_mode_rb.setChecked(True)
            self.camera_label.setEnabled(False)
            self.camera_combo.setEnabled(False)
            self.debug_mode_changed.emit(False)
    
    def on_camera_changed(self, index):
        """摄像头选择改变"""
        self.camera_index_changed.emit(index)
    
    def is_debug_mode(self):
        """检查是否为调试模式"""
        return self.debug_mode_rb.isChecked()
    
    def get_camera_index(self):
        """获取选择的摄像头索引"""
        return self.camera_combo.currentIndex()
        
    def on_class_changed(self):
        selected_classes = []
        for class_name, checkbox in self.class_checkboxes.items():
            if checkbox.isChecked():
                selected_classes.append(class_name)
        self.target_classes_changed.emit(selected_classes)
    
    def update_class_selection(self, target_classes):
        """更新类别选择状态"""
        for class_name, checkbox in self.class_checkboxes.items():
            checkbox.setChecked(class_name in target_classes)


class VideoDisplayWidget(QLabel):
    """视频显示组件"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #C7C7CC;
                border-radius: 8px;
                background-color: #000000;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("等待视频输入...")
        self.setScaledContents(True)
        
    def update_frame(self, frame, detections=None):
        """更新显示帧"""
        if detections:
            # 在帧上绘制检测结果
            display_config = config_manager.display
            
            for detection in detections:
                bbox = detection['bbox']
                class_name = detection['class_name']
                confidence = detection['confidence']
                
                x1, y1, x2, y2 = bbox
                
                # 绘制边界框
                cv2.rectangle(frame, (x1, y1), (x2, y2), 
                             display_config.bbox_color, display_config.bbox_thickness)
                
                # 构建标签文本
                label_parts = []
                if display_config.show_class_names:
                    label_parts.append(class_name)
                if display_config.show_confidence:
                    label_parts.append(f"{confidence:.2f}")
                
                if label_parts:
                    label = " ".join(label_parts)
                    cv2.putText(frame, label, (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, display_config.font_scale, 
                               display_config.text_color, display_config.bbox_thickness)
        
        # 转换为 QImage 并显示
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        self.setPixmap(pixmap)


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.video_thread = None
        self.camera_thread = None
        self.model = None
        self.kinect = None
        self.current_detections = []
        self.debug_mode = False
        
        self.init_ui()
        self.init_model()
        self.init_kinect()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Oasis 目标检测系统")
        self.setGeometry(100, 100, *config_manager.ui.window_size)
        
        # 加载样式表
        self.load_stylesheet()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：视频显示
        self.video_display = VideoDisplayWidget()
        splitter.addWidget(self.video_display)
        
        # 右侧：控制面板和检测结果
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # 控制面板
        self.control_panel = ControlPanel()
        self.control_panel.start_detection.connect(self.start_detection)
        self.control_panel.stop_detection.connect(self.stop_detection)
        self.control_panel.target_classes_changed.connect(self.update_target_classes)
        self.control_panel.debug_mode_changed.connect(self.on_debug_mode_changed)
        self.control_panel.camera_index_changed.connect(self.on_camera_index_changed)
        right_layout.addWidget(self.control_panel)
        
        # 检测结果
        self.detection_widget = DetectionWidget()
        right_layout.addWidget(self.detection_widget)
        
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes(config_manager.ui.splitter_sizes)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
    def load_stylesheet(self):
        """加载样式表"""
        try:
            style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
            if os.path.exists(style_path):
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
        except Exception as e:
            print(f"样式表加载失败: {e}")
            # 使用默认样式
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #F2F2F7;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #C7C7CC;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: white;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: #007AFF;
                }
            """)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 设置动作
        settings_action = QAction("设置", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        # 重置布局动作
        reset_layout_action = QAction("重置布局", self)
        reset_layout_action.triggered.connect(self.reset_layout)
        view_menu.addAction(reset_layout_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def show_settings(self):
        """显示设置对话框"""
        settings_dialog = SettingsDialog(self)
        settings_dialog.settings_changed.connect(self.on_settings_changed)
        settings_dialog.exec()
    
    def reset_layout(self):
        """重置布局"""
        # 重置分割器大小
        splitter = self.centralWidget().findChild(QSplitter)
        if splitter:
            splitter.setSizes(config_manager.ui.splitter_sizes)
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于 Oasis", 
                         "Oasis 目标检测系统 v1.0\n\n"
                         "基于 YOLO 和 Kinect 2.0 的实时目标检测应用\n"
                         "支持多种物体识别和自定义配置\n\n"
                         "© 2024 Oasis Team")
    
    def on_settings_changed(self):
        """设置改变时的处理"""
        # 重新加载配置
        if self.video_thread:
            self.video_thread.set_target_classes(config_manager.detection.target_classes)
        
        # 更新控制面板的类别选择
        self.control_panel.update_class_selection(config_manager.detection.target_classes)
        
        self.status_bar.showMessage("设置已更新")

    def init_model(self):
        """初始化 YOLO 模型"""
        try:
            model_path = config_manager.detection.model_path
            self.model = YOLO(model_path)
            self.status_bar.showMessage("YOLO 模型加载成功")
        except Exception as e:
            self.status_bar.showMessage(f"模型加载失败: {e}")
            
    def init_kinect(self):
        """初始化 Kinect 传感器"""
        try:
            from pykinect2 import PyKinectV2, PyKinectRuntime
            self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
            self.status_bar.showMessage("Kinect 传感器初始化成功")
        except Exception as e:
            self.status_bar.showMessage(f"Kinect 初始化失败: {e}")
            
    def start_detection(self):
        """开始检测"""
        if not self.model:
            self.status_bar.showMessage("模型未加载")
            return
        
        # 根据模式选择不同的检测方式
        if self.debug_mode:
            # 调试模式：使用电脑摄像头
            self.camera_thread = CameraThread()
            self.camera_thread.set_model(self.model)
            self.camera_thread.set_camera_index(self.control_panel.get_camera_index())
            self.camera_thread.set_target_classes(config_manager.detection.target_classes)
            
            self.camera_thread.frame_ready.connect(self.update_video_display)
            self.camera_thread.detection_ready.connect(self.update_detections)
            self.camera_thread.error_occurred.connect(self.on_camera_error)
            
            self.camera_thread.start()
            self.status_bar.showMessage("调试模式检测运行中...")
        else:
            # Kinect 模式
            if not self.kinect:
                self.status_bar.showMessage("Kinect 设备未就绪")
                return
                
            self.video_thread = VideoThread()
            self.video_thread.set_model(self.model)
            self.video_thread.set_kinect(self.kinect)
            self.video_thread.set_target_classes(config_manager.detection.target_classes)
            
            self.video_thread.frame_ready.connect(self.update_video_display)
            self.video_thread.detection_ready.connect(self.update_detections)
            
            self.video_thread.start()
            self.status_bar.showMessage("Kinect 检测运行中...")
        
    def stop_detection(self):
        """停止检测"""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()
            self.video_thread = None
            
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
            
        self.status_bar.showMessage("检测已停止")
    
    def on_debug_mode_changed(self, debug_mode):
        """调试模式切换处理"""
        self.debug_mode = debug_mode
        
        # 如果正在运行检测，先停止
        if self.video_thread or self.camera_thread:
            self.stop_detection()
            self.control_panel.on_stop_clicked()  # 更新按钮状态
        
        # 更新状态栏显示
        if debug_mode:
            self.status_bar.showMessage("已切换到调试模式 (电脑摄像头)")
        else:
            self.status_bar.showMessage("已切换到 Kinect 模式")
    
    def on_camera_index_changed(self, index):
        """摄像头索引改变处理"""
        if self.camera_thread and self.camera_thread.isRunning():
            # 如果摄像头线程正在运行，重启以使用新的摄像头
            self.stop_detection()
            self.start_detection()
    
    def on_camera_error(self, error_message):
        """摄像头错误处理"""
        self.status_bar.showMessage(f"摄像头错误: {error_message}")
        QMessageBox.warning(self, "摄像头错误", error_message)
        
    def update_target_classes(self, classes):
        """更新目标类别"""
        if self.video_thread:
            self.video_thread.set_target_classes(classes)
        if self.camera_thread:
            self.camera_thread.set_target_classes(classes)
            
    @pyqtSlot(np.ndarray)
    def update_video_display(self, frame):
        """更新视频显示"""
        self.video_display.update_frame(frame, self.current_detections)
        
    @pyqtSlot(list)
    def update_detections(self, detections):
        """更新检测结果"""
        self.current_detections = detections
        self.detection_widget.update_detections(detections)
        
    def closeEvent(self, event):
        """关闭事件"""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()
            
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
            
        if self.kinect:
            self.kinect.close()
            
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("Oasis 目标检测系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Oasis Team")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
