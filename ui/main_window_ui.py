"""
Oasis 目标检测系统 - 主窗口界面 (UI文件版本)
基于 PyQt6 和 .ui 文件的现代化界面设计
"""

import sys
import cv2
import numpy as np
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QGroupBox, QListWidget, QSlider, QSpinBox,
                             QCheckBox, QComboBox, QStatusBar, QSplitter,
                             QFrame, QGridLayout, QSpacerItem, QSizePolicy,
                             QMenuBar, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon, QAction
from ultralytics import YOLO
from .config import config_manager
from .settings_dialog_ui import SettingsDialogUI
from .ui_loader import UILoader, UI_FILES


class VideoThread(QThread):
    """视频处理线程"""
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
                print(f"视频线程错误: {e}")
                
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


class VideoDisplayWidget(QLabel):
    """视频显示组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_display()
        
    def setup_display(self):
        """设置显示属性"""
        self.setMinimumSize(640, 480)
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


class MainWindowUI(QMainWindow):
    """主窗口 - 使用 UI 文件版本"""
    
    def __init__(self):
        super().__init__()
        self.video_thread = None
        self.model = None
        self.kinect = None
        self.current_detections = []
        self.class_checkboxes = {}
        
        # 加载 UI
        self.setup_ui()
        self.init_model()
        self.init_kinect()
        
    def setup_ui(self):
        """设置用户界面"""
        # 加载 UI 文件
        self.ui = UILoader.load_ui(UI_FILES['MAIN_WINDOW'], self)
        
        # 应用样式表
        UILoader.apply_stylesheet(self)
        
        # 替换视频显示组件
        self.setup_video_display()
        
        # 设置控制面板
        self.setup_control_panel()
        
        # 连接信号
        self.connect_signals()
        
        # 设置窗口属性
        self.setGeometry(100, 100, *config_manager.ui.window_size)
        
        # 设置分割器比例
        self.ui.splitter.setSizes(config_manager.ui.splitter_sizes)
        
        # 设置状态栏
        self.ui.statusbar.showMessage("就绪")
        
    def setup_video_display(self):
        """设置视频显示组件"""
        # 创建自定义视频显示组件
        self.video_display = VideoDisplayWidget()
        
        # 替换 UI 文件中的标签
        old_video_label = self.ui.video_display
        parent_layout = old_video_label.parent().layout()
        
        # 获取位置索引
        index = parent_layout.indexOf(old_video_label)
        
        # 移除旧组件并添加新组件
        parent_layout.removeWidget(old_video_label)
        old_video_label.deleteLater()
        parent_layout.insertWidget(index, self.video_display)
        
        # 更新引用
        self.ui.video_display = self.video_display
        
    def setup_control_panel(self):
        """设置控制面板"""
        # 创建类别复选框
        self.create_class_checkboxes()
        
    def create_class_checkboxes(self):
        """创建类别复选框"""
        # 获取类别列表容器
        container = self.ui.classes_content
        layout = container.layout()
        
        # 清除现有内容
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 添加类别复选框
        all_classes = config_manager.get_all_classes()[:10]  # 显示前10个类别
        default_classes = config_manager.detection.target_classes
        
        self.class_checkboxes = {}
        
        for class_name in all_classes:
            checkbox = QCheckBox(class_name)
            checkbox.setChecked(class_name in default_classes)
            checkbox.stateChanged.connect(self.on_class_changed)
            self.class_checkboxes[class_name] = checkbox
            layout.addWidget(checkbox)
            
    def connect_signals(self):
        """连接信号槽"""
        # 按钮信号
        self.ui.start_btn.clicked.connect(self.on_start_clicked)
        self.ui.stop_btn.clicked.connect(self.on_stop_clicked)
        
        # 菜单信号
        self.ui.settings_action.triggered.connect(self.show_settings)
        self.ui.exit_action.triggered.connect(self.close)
        self.ui.reset_layout_action.triggered.connect(self.reset_layout)
        self.ui.about_action.triggered.connect(self.show_about)
        
    def on_start_clicked(self):
        """开始检测"""
        self.ui.start_btn.setEnabled(False)
        self.ui.stop_btn.setEnabled(True)
        self.start_detection()
        
    def on_stop_clicked(self):
        """停止检测"""
        self.ui.start_btn.setEnabled(True)
        self.ui.stop_btn.setEnabled(False)
        self.stop_detection()
        
    def on_class_changed(self):
        """类别改变处理"""
        selected_classes = []
        for class_name, checkbox in self.class_checkboxes.items():
            if checkbox.isChecked():
                selected_classes.append(class_name)
        self.update_target_classes(selected_classes)
        
    def update_class_selection(self, target_classes):
        """更新类别选择状态"""
        for class_name, checkbox in self.class_checkboxes.items():
            checkbox.setChecked(class_name in target_classes)

    def show_settings(self):
        """显示设置对话框"""
        settings_dialog = SettingsDialogUI(self)
        settings_dialog.settings_changed.connect(self.on_settings_changed)
        settings_dialog.exec()
    
    def reset_layout(self):
        """重置布局"""
        # 重置分割器大小
        self.ui.splitter.setSizes(config_manager.ui.splitter_sizes)
    
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
        self.update_class_selection(config_manager.detection.target_classes)
        
        self.ui.statusbar.showMessage("设置已更新")

    def init_model(self):
        """初始化 YOLO 模型"""
        try:
            model_path = config_manager.detection.model_path
            self.model = YOLO(model_path)
            self.ui.statusbar.showMessage("YOLO 模型加载成功")
        except Exception as e:
            self.ui.statusbar.showMessage(f"模型加载失败: {e}")
            
    def init_kinect(self):
        """初始化 Kinect 传感器"""
        try:
            from pykinect2 import PyKinectV2, PyKinectRuntime
            self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
            self.ui.statusbar.showMessage("Kinect 传感器初始化成功")
        except Exception as e:
            self.ui.statusbar.showMessage(f"Kinect 初始化失败: {e}")
            
    def start_detection(self):
        """开始检测"""
        if not self.kinect or not self.model:
            self.ui.statusbar.showMessage("设备未就绪")
            return
            
        self.video_thread = VideoThread()
        self.video_thread.set_model(self.model)
        self.video_thread.set_kinect(self.kinect)
        
        self.video_thread.frame_ready.connect(self.update_video_display)
        self.video_thread.detection_ready.connect(self.update_detections)
        
        self.video_thread.start()
        self.ui.statusbar.showMessage("检测运行中...")
        
    def stop_detection(self):
        """停止检测"""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()
            self.video_thread = None
            
        self.ui.statusbar.showMessage("检测已停止")
        
    def update_target_classes(self, classes):
        """更新目标类别"""
        if self.video_thread:
            self.video_thread.set_target_classes(classes)
            
    @pyqtSlot(np.ndarray)
    def update_video_display(self, frame):
        """更新视频显示"""
        self.video_display.update_frame(frame, self.current_detections)
        
    @pyqtSlot(list)
    def update_detections(self, detections):
        """更新检测结果"""
        self.current_detections = detections
        self.update_detection_list(detections)
        
    def update_detection_list(self, detections):
        """更新检测结果列表"""
        self.ui.result_list.clear()
        
        for detection in detections:
            item_text = f"{detection['class_name']} ({detection['confidence']:.2f})"
            self.ui.result_list.addItem(item_text)
            
        self.ui.stats_label.setText(f"当前检测: {len(detections)} 个对象")
        
    def closeEvent(self, event):
        """关闭事件"""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()
            
        if self.kinect:
            self.kinect.close()
            
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("Oasis 目标检测系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Oasis Team")
    
    window = MainWindowUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
