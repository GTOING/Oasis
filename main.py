import cv2
from ultralytics import YOLO

# 步骤 1: 定义你想要检测的目标类别
# 注意：类别名称必须与 YOLO 训练时的名称完全匹配。
# 常用名称包括 'person', 'car', 'dog', 'cat', 'bottle', 'cell phone' 等。
target_classes = ['bottle', 'cup','cell phone','mouse','pen']

# Create a new YOLO model from scratch
model = YOLO("yolo11n.yaml")

# 步骤 2: 加载 YOLOv8 模型
model = YOLO('yolo11n.pt')

# 步骤 3: 初始化摄像头
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("错误：无法打开摄像头。")
    exit()

# 获取 YOLO 模型的所有类别名称，用于后面的查找
# 这是一个字典，例如 {0: 'person', 1: 'bicycle', ...}
class_names_dict = model.names

while True:
    ret, frame = cap.read()
    if not ret:
        print("错误：无法从摄像头读取帧。")
        break

    # 步骤 4: 使用 YOLO 模型对帧进行推理
    results = model(frame, verbose=False) # verbose=False 可以减少控制台输出

    # 创建一个用于绘制的副本
    display_frame = frame.copy()

    # 步骤 5: 遍历检测结果并只绘制目标类别
    for r in results:
        # 遍历每个检测到的边界框
        for box in r.boxes:
            # 获取检测到的类别 ID
            class_id = int(box.cls[0])
            
            # 使用 ID 查找对应的类别名称
            class_name = class_names_dict[class_id]

            # 检查类别是否是我们想要检测的目标
            if class_name in target_classes:
                # 如果是，则获取边界框坐标和置信度
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()

                # 将坐标转换为整数
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # 绘制边界框
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # 绘制标签和置信度
                label = f"{class_name} {conf:.2f}"
                cv2.putText(display_frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # 显示结果
    cv2.imshow("YOLO 目标检测 - 按 'q' 退出", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 步骤 6: 释放摄像头并关闭所有窗口
cap.release()
cv2.destroyAllWindows()