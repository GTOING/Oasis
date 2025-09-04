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
                             QMessageBox, QLineEdit, QScrollArea)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon, QAction
from ultralytics import YOLO
from .config import config_manager
from .settings_dialog import SettingsDialog


class VideoThread(QThread):
    """Kinect 视频处理线程"""
    frame_ready = pyqtSignal(np.ndarray)
    detection_ready = pyqtSignal(list)
    stream_info_ready = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.kinect = None
        self.running = False
        self.target_classes = config_manager.detection.target_classes
        self.stream_type = config_manager.kinect.video_stream_type
        self.depth_mode = config_manager.kinect.depth_mode
        
    def set_model(self, model):
        self.model = model
        
    def set_kinect(self, kinect):
        self.kinect = kinect
        
    def set_target_classes(self, classes):
        self.target_classes = classes
    
    def set_stream_type(self, stream_type):
        """设置视频流类型"""
        self.stream_type = stream_type
        
    def set_depth_mode(self, depth_mode):
        """设置深度模式"""
        self.depth_mode = depth_mode
        
    def run(self):
        """主运行循环"""
        self.running = True
        
        if not self.kinect:
            return
        
        # 发送流信息
        stream_name = config_manager.get_kinect_stream_types().get(self.stream_type, self.stream_type)
        self.stream_info_ready.emit(f"Kinect 模式: {stream_name}")
        
        while self.running:
            try:
                frame = None
                
                if self.stream_type == "color":
                    frame = self._get_color_frame()
                elif self.stream_type == "depth":
                    frame = self._get_depth_frame()
                elif self.stream_type == "infrared":
                    frame = self._get_infrared_frame()
                elif self.stream_type == "body_index":
                    frame = self._get_body_index_frame()
                
                if frame is not None:
                    # 发送原始帧
                    self.frame_ready.emit(frame.copy())
                    
                    # 只对彩色图像执行目标检测
                    if self.model and self.stream_type == "color":
                          results = self.model(frame, verbose=False)
                          detections = self.process_detections(results, frame)
                          self.detection_ready.emit(detections)
                    elif self.stream_type != "color":
                        # 非彩色流不进行目标检测
                        self.detection_ready.emit([])
                
                # 发送流信息用于状态显示
                if hasattr(self, 'stream_info_ready'):
                    stream_info = f"Kinect {self.stream_type.title()} 模式"
                    if self.stream_type == "color" and config_manager.detection.enable_3d_coordinates:
                        stream_info += " | 3D坐标已启用"
                    self.stream_info_ready.emit(stream_info)
                        
                self.msleep(33)  # 约30FPS
                
            except Exception as e:
                print(f"Kinect 视频线程错误: {e}")
    
    def _get_color_frame(self):
        """获取彩色帧"""
        try:
            if self.kinect.has_new_color_frame():
                frame_width = self.kinect.color_frame_desc.Width
                frame_height = self.kinect.color_frame_desc.Height
                frame = self.kinect.get_last_color_frame()
                
                if frame is not None and frame.size > 0:
                    # Kinect v2 实际提供的是BGRA格式（注意顺序）
                    frame = frame.reshape((frame_height, frame_width, 4))
                    
                    # 方法1：直接移除Alpha通道，保持BGRA->BGR
                    frame_bgr = frame[:, :, :3]  # 取前3个通道 (BGR)
                    
                    # 调试：检查帧是否正常
                    print(f"彩色帧: {frame_width}x{frame_height}, 数据范围: {frame_bgr.min()}-{frame_bgr.max()}")
                    
                    return frame_bgr
            return None
        except Exception as e:
            print(f"彩色帧处理错误: {e}")
            return None
    
    def _get_depth_frame(self):
        """获取深度帧"""
        try:
            if hasattr(self.kinect, 'has_new_depth_frame') and self.kinect.has_new_depth_frame():
                frame_width = self.kinect.depth_frame_desc.Width
                frame_height = self.kinect.depth_frame_desc.Height
                frame = self.kinect.get_last_depth_frame()
                
                if frame is not None and frame.size > 0:
                    frame = frame.reshape((frame_height, frame_width))
                    
                    # 改进深度数据转换，处理异常值
                    valid_depth = frame[frame > 0]  # 过滤无效深度值
                    if len(valid_depth) > 0:
                        # 使用实际深度范围进行归一化，避免异常值影响
                        depth_min = np.percentile(valid_depth, 5)  # 第5百分位数
                        depth_max = np.percentile(valid_depth, 95)  # 第95百分位数
                        depth_max = min(depth_max, 8000)  # 限制最大值
                        
                        # 创建归一化图像
                        frame_normalized = np.zeros_like(frame, dtype=np.uint8)
                        valid_mask = (frame > 0) & (frame <= 8000)
                        
                        if depth_max > depth_min:
                            frame_normalized[valid_mask] = np.clip(
                                (frame[valid_mask] - depth_min) / (depth_max - depth_min) * 255, 0, 255
                            ).astype(np.uint8)
                        
                        # 应用颜色映射增强可视化效果
                        frame_colored = cv2.applyColorMap(frame_normalized, cv2.COLORMAP_JET)
                        return frame_colored
                    else:
                        # 没有有效深度数据时返回黑色图像
                        frame_normalized = np.zeros((frame_height, frame_width), dtype=np.uint8)
                        return cv2.cvtColor(frame_normalized, cv2.COLOR_GRAY2BGR)
            return None
        except Exception as e:
            print(f"深度帧处理错误: {e}")
            return None
    
    def _get_infrared_frame(self):
        """获取红外帧"""
        try:
            if hasattr(self.kinect, 'has_new_infrared_frame') and self.kinect.has_new_infrared_frame():
                frame_width = self.kinect.infrared_frame_desc.Width
                frame_height = self.kinect.infrared_frame_desc.Height
                frame = self.kinect.get_last_infrared_frame()
                
                if frame is not None and frame.size > 0:
                    frame = frame.reshape((frame_height, frame_width))
                    
                    # 改进的红外数据转换，使用更保守的归一化
                    # 避免除零和数据溢出问题
                    frame_max = np.max(frame) if np.max(frame) > 0 else 65535
                    frame_min = np.min(frame[frame > 0]) if np.any(frame > 0) else 0
                    
                    # 使用动态范围进行归一化
                    if frame_max > frame_min:
                        frame_normalized = np.clip(
                            (frame - frame_min) / (frame_max - frame_min) * 255, 0, 255
                        ).astype(np.uint8)
                    else:
                        frame_normalized = np.zeros_like(frame, dtype=np.uint8)
                    
                    # 应用适度的对比度增强
                    frame_enhanced = cv2.equalizeHist(frame_normalized)
                    return cv2.cvtColor(frame_enhanced, cv2.COLOR_GRAY2BGR)
            return None
        except Exception as e:
            print(f"红外帧处理错误: {e}")
            return None
    
    def _get_body_index_frame(self):
        """获取人体索引帧"""
        try:
            if hasattr(self.kinect, 'has_new_body_index_frame') and self.kinect.has_new_body_index_frame():
                frame_width = self.kinect.body_index_frame_desc.Width
                frame_height = self.kinect.body_index_frame_desc.Height
                frame = self.kinect.get_last_body_index_frame()
                
                if frame is not None and frame.size > 0:
                    frame = frame.reshape((frame_height, frame_width))
                    
                    # 将人体索引转换为彩色图像
                    # 不同的人体索引用不同颜色表示
                    frame_colored = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
                    
                    # 更鲜明的颜色组合，包括背景处理
                    colors = [
                        (50, 50, 50),      # 背景 - 深灰色
                        (255, 100, 100),   # 人体1 - 红色
                        (100, 255, 100),   # 人体2 - 绿色  
                        (100, 100, 255),   # 人体3 - 蓝色
                        (255, 255, 100),   # 人体4 - 黄色
                        (255, 100, 255),   # 人体5 - 紫色
                        (100, 255, 255),   # 人体6 - 青色
                    ]
                    
                    # 检查是否有人体数据
                    unique_values = np.unique(frame)
                    print(f"人体索引帧包含值: {unique_values}")
                    
                    # 处理所有可能的索引值
                    for i in range(min(len(colors), 256)):  # 最多256个索引
                        mask = (frame == i)
                        if np.any(mask):
                            frame_colored[mask] = colors[i % len(colors)]
                            if i > 0:  # 人体索引 (非背景)
                                print(f"检测到人体索引 {i}: {np.sum(mask)} 像素")
                    
                    # 如果没有检测到任何人体，显示原始数据的可视化
                    if len(unique_values) <= 1 or np.all(frame == 0):
                        print("未检测到人体，显示原始索引数据")
                        # 将原始数据标准化为灰度图
                        frame_norm = np.clip(frame.astype(np.float32) * 40, 0, 255).astype(np.uint8)
                        frame_colored = cv2.cvtColor(frame_norm, cv2.COLOR_GRAY2BGR)
                    
                    return frame_colored
                else:
                    print("人体索引帧数据为空")
            return None
        except Exception as e:
            print(f"人体索引帧处理错误: {e}")
            return None
                
    def process_detections(self, results, color_frame=None):
        """处理检测结果"""
        detections = []
        
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                conf = box.conf[0].item()
                
                # 检查类别是否在目标类别中（包括自定义类别）
                all_target_classes = self.target_classes + config_manager.detection.custom_classes
                
                if class_name in all_target_classes and conf >= config_manager.detection.confidence_threshold:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    detection = {
                        'class_name': class_name,
                        'confidence': conf,
                        'bbox': (int(x1), int(y1), int(x2), int(y2))
                    }
                    
                    # 计算3D坐标（如果启用且有深度数据）
                    if config_manager.detection.enable_3d_coordinates and self.stream_type == "color":
                        coords_3d = self._calculate_3d_coordinates(detection['bbox'], color_frame)
                        if coords_3d:
                            detection['coordinates_3d'] = coords_3d
                    
                    detections.append(detection)
                    
                    # 限制最大检测数量
                    if len(detections) >= config_manager.detection.max_detections:
                        break
                    
        return detections
    
    def _calculate_3d_coordinates(self, bbox, color_frame):
        """计算目标的3D坐标 - 结合深度图进行坐标绘制"""
        try:
            if not self.kinect:
                print("Kinect 设备未初始化")
                return None
            
            # 获取深度数据 - 改进的同步策略
            depth_frame = None
            depth_data = None
            
            # 尝试多种方式获取深度帧
            for attempt in range(5):  # 增加重试次数
                try:
                    # 方法1：检查是否有新的深度帧
                    if hasattr(self.kinect, 'has_new_depth_frame'):
                        if self.kinect.has_new_depth_frame():
                            depth_frame = self.kinect.get_last_depth_frame()
                            print(f"方法1成功获取深度帧 (尝试{attempt+1})")
                            break
                    
                    # 方法2：直接获取最后的深度帧
                    if hasattr(self.kinect, 'get_last_depth_frame') and depth_frame is None:
                        depth_frame = self.kinect.get_last_depth_frame()
                        if depth_frame is not None:
                            print(f"方法2成功获取深度帧 (尝试{attempt+1})")
                            break
                    
                    # 短暂等待让Kinect更新数据
                    import time
                    time.sleep(0.005)  # 5ms等待
                    
                except Exception as e:
                    print(f"尝试{attempt+1}获取深度帧失败: {e}")
                    continue
            
            if depth_frame is None:
                print("⚠️  无法获取深度帧")
                print("📝 建议:")
                print("   1. 确保Kinect正在运行且连接正常")
                print("   2. 检查深度传感器是否被遮挡")
                print("   3. 尝试重启Kinect服务")
                print("   4. 在Kinect设置中同时启用彩色和深度传感器")
                return None
                
            try:
                depth_width = self.kinect.depth_frame_desc.Width
                depth_height = self.kinect.depth_frame_desc.Height
                depth_data = depth_frame.reshape((depth_height, depth_width))
                print(f"成功获取深度数据: {depth_width}x{depth_height}")
            except Exception as e:
                print(f"深度数据处理错误: {e}")
                return None
            
            # 计算边界框中心点在彩色图像中的位置
            x1, y1, x2, y2 = bbox
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            
            # 获取彩色图像尺寸
            try:
                color_width = self.kinect.color_frame_desc.Width
                color_height = self.kinect.color_frame_desc.Height
            except:
                # 从实际帧获取尺寸
                if color_frame is not None:
                    color_height, color_width = color_frame.shape[:2]
                else:
                    # 默认值（常见的Kinect v2分辨率）
                    color_width = 1920
                    color_height = 1080
            
            # 坐标映射：彩色图像坐标 -> 深度图像坐标
            # Kinect v2的深度和彩色相机略有偏移，这里使用简化映射
            depth_x = int(center_x * depth_width / color_width)
            depth_y = int(center_y * depth_height / color_height)
            
            # 确保坐标在深度图像范围内
            depth_x = max(0, min(depth_x, depth_width - 1))
            depth_y = max(0, min(depth_y, depth_height - 1))
            
            # 获取深度值（毫米）- 使用周围几个像素的平均值提高准确性
            radius = 2
            depth_values = []
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    try:
                        px = max(0, min(depth_x + dx, depth_width - 1))
                        py = max(0, min(depth_y + dy, depth_height - 1))
                        depth_val = depth_data[py, px]
                        if depth_val > 0:
                            depth_values.append(depth_val)
                    except:
                        continue
            
            if not depth_values:
                print(f"在位置({depth_x},{depth_y})周围未找到有效深度值")
                return None
            
            # 使用中位数减少噪声影响
            depth_mm = np.median(depth_values)
            
            # 调试信息
            print(f"3D坐标计算: bbox={bbox}, center=({center_x},{center_y}), depth_pos=({depth_x},{depth_y})")
            print(f"深度映射: color({color_width}x{color_height}) -> depth({depth_width}x{depth_height})")
            print(f"深度位置: ({depth_x},{depth_y}), 深度值: {depth_mm}mm (来自{len(depth_values)}个有效像素)")
            
            if depth_mm > 0 and depth_mm < 8000:  # 有效深度值范围
                # Kinect v2 深度相机内参（标准值）
                fx = 365.481  # 焦距x
                fy = 365.481  # 焦距y  
                cx = depth_width / 2.0  # 主点x
                cy = depth_height / 2.0  # 主点y
                
                # 将深度图像坐标转换为3D世界坐标（Kinect坐标系）
                z = depth_mm  # Z坐标（深度，毫米）
                x = (depth_x - cx) * z / fx  # X坐标（毫米）
                y = (depth_y - cy) * z / fy  # Y坐标（毫米）
                
                coords_3d = {
                    'x': round(x, 1),
                    'y': round(y, 1), 
                    'z': round(z, 1),
                    'unit': 'mm',
                    'depth_pos': f"({depth_x},{depth_y})",
                    'valid_pixels': len(depth_values)
                }
                
                print(f"计算出的3D坐标: X={coords_3d['x']}mm, Y={coords_3d['y']}mm, Z={coords_3d['z']}mm")
                return coords_3d
            else:
                print(f"无效深度值: {depth_mm}mm (有效范围: 0-8000mm)")
                return None
            
        except Exception as e:
            print(f"3D坐标计算异常: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # 基础检测信息
            item_text = f"{class_name} ({confidence:.2f})"
            
            # 如果有3D坐标信息，添加到显示中
            if 'coordinates_3d' in detection:
                coords_3d = detection['coordinates_3d']
                coords_text = f" | 3D: ({coords_3d['x']}, {coords_3d['y']}, {coords_3d['z']}) {coords_3d['unit']}"
                item_text += coords_text
            
            self.result_list.addItem(item_text)
            
        self.stats_label.setText(f"当前检测: {len(detections)} 个对象")


class ControlPanel(QWidget):
    """控制面板"""
    start_detection = pyqtSignal()
    stop_detection = pyqtSignal()
    target_classes_changed = pyqtSignal(list)
    debug_mode_changed = pyqtSignal(bool)
    camera_index_changed = pyqtSignal(int)
    kinect_stream_changed = pyqtSignal(str)
    enable_3d_coordinates_changed = pyqtSignal(bool)
    custom_class_added = pyqtSignal(str)
    custom_class_removed = pyqtSignal(str)
    
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
        
        # Kinect 视频流类型选择（仅 Kinect 模式）
        kinect_layout = QHBoxLayout()
        self.kinect_stream_label = QLabel("视频流:")
        self.kinect_stream_combo = QComboBox()
        
        # 添加视频流类型选项
        stream_types = config_manager.get_kinect_stream_types()
        for key, display_name in stream_types.items():
            self.kinect_stream_combo.addItem(display_name, key)
        
        # 设置当前选择
        current_stream = config_manager.kinect.video_stream_type
        for i in range(self.kinect_stream_combo.count()):
            if self.kinect_stream_combo.itemData(i) == current_stream:
                self.kinect_stream_combo.setCurrentIndex(i)
                break
        
        self.kinect_stream_combo.currentIndexChanged.connect(self.on_kinect_stream_changed)
        
        kinect_layout.addWidget(self.kinect_stream_label)
        kinect_layout.addWidget(self.kinect_stream_combo)
        kinect_layout.addStretch()
        
        mode_layout.addLayout(kinect_layout)
        
        # 初始状态设置
        self.camera_label.setEnabled(False)
        self.camera_combo.setEnabled(False)
        self.kinect_stream_label.setEnabled(True)
        self.kinect_stream_combo.setEnabled(True)
        
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
        
        # 3D坐标功能开关
        coords_group = QGroupBox("3D坐标功能")
        coords_layout = QVBoxLayout()
        
        self.enable_3d_checkbox = QCheckBox("启用3D坐标计算")
        self.enable_3d_checkbox.setChecked(config_manager.detection.enable_3d_coordinates)
        self.enable_3d_checkbox.stateChanged.connect(self.on_3d_coordinates_changed)
        coords_layout.addWidget(self.enable_3d_checkbox)
        
        coords_note = QLabel("注意：仅在Kinect彩色模式下有效")
        coords_note.setStyleSheet("color: gray; font-size: 10px;")
        coords_layout.addWidget(coords_note)
        
        coords_group.setLayout(coords_layout)
        layout.addWidget(coords_group)
        
        # 自定义类别管理
        custom_group = QGroupBox("自定义检测类别")
        custom_layout = QVBoxLayout()
        
        # 添加自定义类别的输入框和按钮
        add_layout = QHBoxLayout()
        self.custom_class_input = QLineEdit()
        self.custom_class_input.setPlaceholderText("输入自定义类别名称")
        self.add_custom_btn = QPushButton("添加")
        self.add_custom_btn.clicked.connect(self.on_add_custom_class)
        
        add_layout.addWidget(self.custom_class_input)
        add_layout.addWidget(self.add_custom_btn)
        custom_layout.addLayout(add_layout)
        
        # 自定义类别列表
        self.custom_classes_list = QListWidget()
        self.custom_classes_list.setMaximumHeight(100)
        self.load_custom_classes()
        custom_layout.addWidget(self.custom_classes_list)
        
        # 删除按钮
        self.remove_custom_btn = QPushButton("删除选中项")
        self.remove_custom_btn.clicked.connect(self.on_remove_custom_class)
        custom_layout.addWidget(self.remove_custom_btn)
        
        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)
        
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
            # 启用 Kinect 控件，禁用摄像头控件
            self.kinect_stream_label.setEnabled(True)
            self.kinect_stream_combo.setEnabled(True)
            self.camera_label.setEnabled(False)
            self.camera_combo.setEnabled(False)
            self.debug_mode_changed.emit(False)
        elif sender == self.debug_mode_rb and self.debug_mode_rb.isChecked():
            self.kinect_mode_rb.setChecked(False)
            # 启用摄像头控件，禁用 Kinect 控件
            self.camera_label.setEnabled(True)
            self.camera_combo.setEnabled(True)
            self.kinect_stream_label.setEnabled(False)
            self.kinect_stream_combo.setEnabled(False)
            self.debug_mode_changed.emit(True)
        
        # 如果都没选中，默认选择 Kinect 模式
        if not self.kinect_mode_rb.isChecked() and not self.debug_mode_rb.isChecked():
            self.kinect_mode_rb.setChecked(True)
            self.kinect_stream_label.setEnabled(True)
            self.kinect_stream_combo.setEnabled(True)
            self.camera_label.setEnabled(False)
            self.camera_combo.setEnabled(False)
            self.debug_mode_changed.emit(False)
    
    def on_camera_changed(self, index):
        """摄像头选择改变"""
        self.camera_index_changed.emit(index)
    
    def on_kinect_stream_changed(self, index):
        """Kinect 视频流类型改变"""
        stream_type = self.kinect_stream_combo.itemData(index)
        self.kinect_stream_changed.emit(stream_type)
    
    def is_debug_mode(self):
        """检查是否为调试模式"""
        return self.debug_mode_rb.isChecked()
    
    def get_camera_index(self):
        """获取选择的摄像头索引"""
        return self.camera_combo.currentIndex()
    
    def get_kinect_stream_type(self):
        """获取选择的 Kinect 视频流类型"""
        return self.kinect_stream_combo.currentData()
    
    def on_3d_coordinates_changed(self, state):
        """3D坐标功能开关改变"""
        enabled = state == 2  # Qt.Checked = 2
        config_manager.set_3d_coordinates_enabled(enabled)
        self.enable_3d_coordinates_changed.emit(enabled)
    
    def on_add_custom_class(self):
        """添加自定义类别"""
        class_name = self.custom_class_input.text().strip()
        if class_name:
            config_manager.add_custom_class(class_name)
            self.custom_class_input.clear()
            self.load_custom_classes()
            self.custom_class_added.emit(class_name)
            # 更新目标类别
            self.on_class_changed()
    
    def on_remove_custom_class(self):
        """删除选中的自定义类别"""
        current_item = self.custom_classes_list.currentItem()
        if current_item:
            class_name = current_item.text()
            config_manager.remove_custom_class(class_name)
            self.load_custom_classes()
            self.custom_class_removed.emit(class_name)
            # 更新目标类别
            self.on_class_changed()
    
    def load_custom_classes(self):
        """加载自定义类别列表"""
        self.custom_classes_list.clear()
        for class_name in config_manager.detection.custom_classes:
            self.custom_classes_list.addItem(class_name)
        
    def on_class_changed(self):
        selected_classes = []
        for class_name, checkbox in self.class_checkboxes.items():
            if checkbox.isChecked():
                selected_classes.append(class_name)
        
        # 包含自定义类别
        selected_classes.extend(config_manager.detection.custom_classes)
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
        
    def update_frame(self, frame, detections=None, stream_type="color"):
        """更新显示帧"""
        # 为不同的流类型添加标识
        if stream_type != "color":
            stream_names = {
                "depth": "深度图像",
                "infrared": "红外图像", 
                "body_index": "人体索引"
            }
            stream_label = stream_names.get(stream_type, stream_type)
            
            # 在图像顶部添加流类型标识
            cv2.putText(frame, stream_label, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 只在彩色流上绘制检测结果
        if detections and stream_type == "color":
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
        
        if stream_type == "color":
            # 对于彩色流，Kinect提供BGR格式，需要转换为RGB用于Qt显示
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        else:
            # 对于其他流类型（深度、红外等），已经是BGR格式，直接使用rgbSwapped
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
        # 设置视频显示的最小尺寸和大小策略
        self.video_display.setMinimumSize(480, 360)
        self.video_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        splitter.addWidget(self.video_display)
        
        # 右侧：控制面板和检测结果（带滚动条）
        right_panel = QWidget()
        right_panel.setMinimumWidth(350)
        right_panel.setMaximumWidth(450)
        right_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_panel.setLayout(right_layout)
        
        # 创建控制面板的滚动区域
        control_scroll = QScrollArea()
        control_scroll.setWidgetResizable(True)
        control_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        control_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        control_scroll.setMaximumHeight(450)  # 限制控制面板最大高度
        
        # 控制面板
        self.control_panel = ControlPanel()
        self.control_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.control_panel.start_detection.connect(self.start_detection)
        self.control_panel.stop_detection.connect(self.stop_detection)
        self.control_panel.target_classes_changed.connect(self.update_target_classes)
        self.control_panel.debug_mode_changed.connect(self.on_debug_mode_changed)
        self.control_panel.camera_index_changed.connect(self.on_camera_index_changed)
        self.control_panel.kinect_stream_changed.connect(self.on_kinect_stream_changed)
        self.control_panel.enable_3d_coordinates_changed.connect(self.on_3d_coordinates_changed)
        self.control_panel.custom_class_added.connect(self.on_custom_class_added)
        self.control_panel.custom_class_removed.connect(self.on_custom_class_removed)
        
        # 将控制面板放入滚动区域
        control_scroll.setWidget(self.control_panel)
        right_layout.addWidget(control_scroll)
        
        # 检测结果
        self.detection_widget = DetectionWidget()
        self.detection_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        right_layout.addWidget(self.detection_widget)
        
        splitter.addWidget(right_panel)
        
        # 设置分割器比例：视频区域占大部分，控制面板占较小部分
        try:
            splitter.setSizes(config_manager.ui.splitter_sizes)
        except:
            splitter.setSizes([800, 400])  # 默认比例
        
        splitter.setStretchFactor(0, 1)  # 视频区域可伸缩
        splitter.setStretchFactor(1, 0)  # 控制面板保持固定比例
        
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
            
            # 根据配置的流类型初始化不同的帧源
            stream_type = config_manager.kinect.video_stream_type
            frame_types = self._get_kinect_frame_types(stream_type)
            
            self.kinect = PyKinectRuntime.PyKinectRuntime(frame_types)
            self.status_bar.showMessage("Kinect 传感器初始化成功")
        except Exception as e:
            self.status_bar.showMessage(f"Kinect 初始化失败: {e}")
    
    def _get_kinect_frame_types(self, stream_type):
        """根据流类型获取对应的帧类型 - 支持3D坐标的多传感器模式"""
        try:
            from pykinect2 import PyKinectV2
            
            frame_type_map = {
                'color': PyKinectV2.FrameSourceTypes_Color,
                'depth': PyKinectV2.FrameSourceTypes_Depth,
                'infrared': PyKinectV2.FrameSourceTypes_Infrared,
                'body_index': PyKinectV2.FrameSourceTypes_BodyIndex
            }
            
            # 🔧 修复关键问题：为了支持3D坐标计算，始终启用彩色和深度传感器
            if config_manager.detection.enable_3d_coordinates:
                print("🎯 3D坐标模式：同时启用彩色和深度传感器")
                frame_types = (PyKinectV2.FrameSourceTypes_Color | 
                              PyKinectV2.FrameSourceTypes_Depth)
                
                # 添加当前选择的流类型（如果不是彩色或深度）
                if stream_type in frame_type_map:
                    if stream_type not in ['color', 'depth']:
                        frame_types |= frame_type_map[stream_type]
                        print(f"📷 添加额外传感器: {stream_type}")
            else:
                # 普通模式：只启用选择的传感器类型
                print(f"📷 单传感器模式: {stream_type}")
                if stream_type in frame_type_map:
                    frame_types = frame_type_map[stream_type]
                else:
                    frame_types = PyKinectV2.FrameSourceTypes_Color  # 默认彩色
            
            print(f"🔧 Kinect初始化类型: {frame_types}")
            return frame_types
            
        except ImportError:
            # 如果 PyKinect2 不可用，返回默认值
            return 1  # 假设的默认值
            
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
            self.video_thread.set_stream_type(self.control_panel.get_kinect_stream_type())
            
            self.video_thread.frame_ready.connect(self.update_video_display)
            self.video_thread.detection_ready.connect(self.update_detections)
            self.video_thread.stream_info_ready.connect(self.update_stream_info)
            
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
    
    def on_kinect_stream_changed(self, stream_type):
        """Kinect 视频流类型改变处理"""
        # 更新配置
        config_manager.kinect.video_stream_type = stream_type
        
        # 如果正在运行检测且是 Kinect 模式，重启以使用新的流类型
        if self.video_thread and self.video_thread.isRunning() and not self.debug_mode:
            self.stop_detection()
            # 重新初始化 Kinect 以支持新的流类型
            self.init_kinect()
            self.start_detection()
    
    def update_stream_info(self, info):
        """更新流信息显示"""
        # 可以在界面上显示当前流类型信息
        # 暂时在状态栏显示
        if "Kinect" in info:
            self.status_bar.showMessage(info)
    
    def on_3d_coordinates_changed(self, enabled):
        """3D坐标功能开关改变处理"""
        if enabled:
            self.status_bar.showMessage("3D坐标功能已启用 - 正在重新初始化Kinect...")
            print("🎯 启用3D坐标功能，需要同时访问彩色和深度传感器")
        else:
            self.status_bar.showMessage("3D坐标功能已禁用 - 正在重新初始化Kinect...")
            print("📷 禁用3D坐标功能，切换到单传感器模式")
        
        # 重新初始化Kinect以支持新的传感器配置
        if hasattr(self, 'video_thread') and self.video_thread and self.video_thread.running:
            print("🔄 重新启动Kinect检测以应用新配置...")
            self.stop_detection()
            # 重新初始化 Kinect 以支持新的传感器配置
            self.init_kinect()
            self.start_detection()
    
    def on_custom_class_added(self, class_name):
        """自定义类别添加处理"""
        self.status_bar.showMessage(f"已添加自定义类别: {class_name}")
    
    def on_custom_class_removed(self, class_name):
        """自定义类别删除处理"""
        self.status_bar.showMessage(f"已删除自定义类别: {class_name}")
        
    def update_target_classes(self, classes):
        """更新目标类别"""
        if self.video_thread:
            self.video_thread.set_target_classes(classes)
        if self.camera_thread:
            self.camera_thread.set_target_classes(classes)
            
    @pyqtSlot(np.ndarray)
    def update_video_display(self, frame):
        """更新视频显示"""
        # 获取当前流类型
        stream_type = "color"  # 默认
        if not self.debug_mode and self.video_thread:
            stream_type = self.video_thread.stream_type
        
        self.video_display.update_frame(frame, self.current_detections, stream_type)
        
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
