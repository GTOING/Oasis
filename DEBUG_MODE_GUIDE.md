# Oasis 调试模式功能指南

## 概述

调试模式是 Oasis 目标检测系统的一个重要功能，允许用户在没有 Kinect 2.0 设备的情况下，使用电脑摄像头进行目标检测。这个功能基于 `main.py` 的代码集成到图形界面中，为开发和测试提供了便利。

## 主要特性

### 🎯 核心功能
- **电脑摄像头支持**: 使用内置或外接 USB 摄像头
- **多摄像头选择**: 支持摄像头索引 0, 1, 2 的切换
- **实时目标检测**: 与 Kinect 模式相同的 YOLO 检测能力
- **模式无缝切换**: 可在 Kinect 和调试模式间快速切换

### 🔧 技术实现
- **CameraThread 类**: 专门的电脑摄像头视频处理线程
- **OpenCV 集成**: 使用 cv2.VideoCapture 进行摄像头控制
- **错误处理**: 完善的摄像头错误检测和用户反馈
- **性能优化**: 30FPS 采样率，640x480 默认分辨率

## 界面操作

### 1. 模式选择
在控制面板的"检测模式"组中：
- **Kinect 2.0 模式**: 使用 Kinect 深度相机
- **调试模式 (电脑摄像头)**: 使用电脑摄像头

### 2. 摄像头选择
当选择调试模式时，会显示摄像头选择下拉框：
- **摄像头 0**: 通常是内置摄像头
- **摄像头 1**: 第一个外接摄像头
- **摄像头 2**: 第二个外接摄像头

### 3. 检测控制
- **开始检测**: 启动选定模式的检测
- **停止检测**: 停止当前检测并释放资源
- **模式切换**: 自动停止当前检测并切换模式

## 技术架构

### CameraThread 类
```python
class CameraThread(QThread):
    """电脑摄像头视频处理线程（调试模式）"""
    frame_ready = pyqtSignal(np.ndarray)
    detection_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
```

#### 主要方法
- `set_model(model)`: 设置 YOLO 模型
- `set_camera_index(index)`: 设置摄像头索引
- `set_target_classes(classes)`: 设置检测类别
- `run()`: 主循环，处理视频帧和检测
- `stop()`: 停止线程并释放摄像头

#### 核心流程
1. **初始化摄像头**: `cv2.VideoCapture(camera_index)`
2. **设置参数**: 分辨率、帧率等
3. **视频循环**: 读取帧 → YOLO 检测 → 发送结果
4. **错误处理**: 摄像头异常时发送错误信号

### 集成到主窗口

#### 信号连接
```python
# 控制面板信号
self.control_panel.debug_mode_changed.connect(self.on_debug_mode_changed)
self.control_panel.camera_index_changed.connect(self.on_camera_index_changed)

# 摄像头线程信号
self.camera_thread.frame_ready.connect(self.update_video_display)
self.camera_thread.detection_ready.connect(self.update_detections)
self.camera_thread.error_occurred.connect(self.on_camera_error)
```

#### 检测启动逻辑
```python
def start_detection(self):
    if self.debug_mode:
        # 调试模式：使用电脑摄像头
        self.camera_thread = CameraThread()
        self.camera_thread.set_model(self.model)
        self.camera_thread.set_camera_index(self.control_panel.get_camera_index())
        self.camera_thread.start()
    else:
        # Kinect 模式
        self.video_thread = VideoThread()
        # ... Kinect 初始化
```

## 与 main.py 的关系

### 源代码集成
调试模式的功能直接集成了 `main.py` 的核心逻辑：

#### main.py 原始代码
```python
# 初始化摄像头
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    results = model(frame, verbose=False)
    
    # 处理检测结果
    for r in results:
        for box in r.boxes:
            # 绘制边界框和标签
```

#### 集成到 CameraThread
```python
def run(self):
    self.camera = cv2.VideoCapture(self.camera_index)
    
    while self.running:
        ret, frame = self.camera.read()
        
        # 发送原始帧
        self.frame_ready.emit(frame.copy())
        
        # 执行检测
        if self.model:
            results = self.model(frame, verbose=False)
            detections = self.process_detections(results)
            self.detection_ready.emit(detections)
```

### 功能增强
相比原始的 `main.py`，调试模式提供了以下增强：

1. **GUI 集成**: 不再是独立的窗口，集成到主界面
2. **多摄像头**: 支持多个摄像头设备选择
3. **错误处理**: 完善的错误反馈机制
4. **配置同步**: 使用统一的配置管理系统
5. **模式切换**: 可与 Kinect 模式无缝切换

## 使用场景

### 1. 开发测试
- **算法调试**: 无需 Kinect 设备即可测试检测算法
- **界面开发**: 验证 UI 组件的正确性
- **配置测试**: 测试不同的检测参数设置

### 2. 演示展示
- **便携性**: 在没有 Kinect 的环境中进行演示
- **兼容性**: 适用于各种电脑设备
- **快速启动**: 无需复杂的硬件设置

### 3. 教学培训
- **学习工具**: 理解目标检测的基本原理
- **实验平台**: 进行计算机视觉相关实验
- **成本降低**: 无需昂贵的 Kinect 设备

## 故障排除

### 常见问题

#### 1. 摄像头无法打开
**症状**: 显示 "无法打开摄像头 X"

**解决方案**:
- 检查摄像头是否被其他应用占用
- 尝试切换到不同的摄像头索引
- 确认摄像头驱动程序正常

#### 2. 摄像头权限问题
**症状**: 摄像头打开但无法读取帧

**解决方案**:
- 检查系统摄像头权限设置
- 在 macOS 上允许应用访问摄像头
- 在 Windows 上检查隐私设置

#### 3. 检测性能问题
**症状**: 检测速度慢或卡顿

**解决方案**:
- 降低摄像头分辨率
- 减少检测类别数量
- 调高置信度阈值

#### 4. 检测效果差
**症状**: 检测不准确或漏检

**解决方案**:
- 改善光照条件
- 调整摄像头角度和距离
- 降低置信度阈值
- 清洁摄像头镜头

## 开发指南

### 添加新功能

#### 1. 扩展摄像头控制
```python
# 在 CameraThread 中添加新的摄像头参数
self.camera.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
self.camera.set(cv2.CAP_PROP_CONTRAST, contrast)
```

#### 2. 增加检测后处理
```python
def process_detections(self, results):
    detections = []
    for r in results:
        for box in r.boxes:
            # 添加新的后处理逻辑
            detection = self.apply_custom_filter(box)
            if detection:
                detections.append(detection)
    return detections
```

#### 3. 自定义错误处理
```python
def handle_camera_error(self, error_type, error_message):
    if error_type == "permission_denied":
        self.error_occurred.emit("摄像头权限被拒绝")
    elif error_type == "device_busy":
        self.error_occurred.emit("摄像头被其他应用占用")
```

### 性能优化

#### 1. 帧率控制
```python
# 在 run() 方法中调整延迟
self.msleep(33)  # 30 FPS
self.msleep(66)  # 15 FPS (更省资源)
```

#### 2. 分辨率优化
```python
# 设置较低分辨率以提高性能
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
```

#### 3. 检测频率控制
```python
# 不是每帧都进行检测
self.frame_count += 1
if self.frame_count % 3 == 0:  # 每3帧检测一次
    results = self.model(frame, verbose=False)
```

## 总结

调试模式为 Oasis 目标检测系统提供了重要的开发和测试支持：

### ✅ 优势
- **设备独立**: 无需专门的 Kinect 设备
- **成本低廉**: 使用常见的电脑摄像头
- **易于使用**: 图形界面操作简单
- **功能完整**: 支持所有检测功能

### 📊 技术特点
- **多线程**: 独立的摄像头处理线程
- **错误处理**: 完善的异常处理机制
- **配置同步**: 与主系统配置保持一致
- **性能优化**: 适合实时检测的参数设置

### 🚀 应用价值
- **开发效率**: 加速算法开发和测试
- **部署灵活**: 适应不同的硬件环境
- **教学支持**: 降低学习和实验门槛
- **演示便利**: 随时随地进行系统演示

调试模式的成功集成使 Oasis 成为了一个更加完整和实用的目标检测系统，为用户提供了多样化的使用选择。
