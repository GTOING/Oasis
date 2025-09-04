import cv2
import numpy as np
from ultralytics import YOLO
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

# 步骤 1: 定义你想要检测的目标类别
target_classes = ['bottle', 'cup', 'cell phone', 'mouse', 'pen']

# 步骤 2: 加载 YOLOv8 模型
model = YOLO('yolo11n.pt')

# 步骤 3: 初始化 Kinect 2.0 传感器
try:
    kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
except Exception as e:
    print(f"初始化Kinect时出错: {e}")
    print("请确保已安装Kinect for Windows SDK 2.0且传感器已连接到USB 3.0端口。")
    exit()

# 获取彩色帧的尺寸
frame_width, frame_height = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height

# 获取 YOLO 模型的所有类别名称
class_names_dict = model.names

while True:
    # 检查是否有新的彩色帧
    if kinect.has_new_color_frame():
        # 获取最新的彩色帧并转换为 NumPy 数组
        frame = kinect.get_last_color_frame()
        frame = frame.reshape((frame_height, frame_width, 4)) # RGBA 格式

        # 将 RGBA 格式的帧转换为 OpenCV 兼容的 BGR 格式
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        
        # 步骤 4: 使用 YOLO 模型对帧进行推理
        results = model(frame_bgr, verbose=False)

        # 创建一个用于绘制的副本
        display_frame = frame_bgr.copy()

        # 步骤 5: 遍历检测结果并只绘制目标类别
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                class_name = class_names_dict[class_id]

                if class_name in target_classes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = box.conf[0].item()

                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{class_name} {conf:.2f}"
                    cv2.putText(display_frame, label, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 显示结果
        cv2.imshow("YOLO 目标检测 - Kinect 2.0 (Windows)", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 步骤 6: 关闭传感器并释放资源
kinect.close()
cv2.destroyAllWindows()