import cv2
from ultralytics import YOLO

# 步骤 1: 加载 YOLOv8 模型
# 这里我们使用预训练的 'yolov8n.pt' 模型（'n' 代表 nano，它是最小、最快的模型）
# 你也可以尝试其他更大的模型，例如 'yolov8s.pt'，但速度会变慢。
model = YOLO('yolo11n.pt')

# 步骤 2: 初始化摄像头
# 0 表示默认的内置摄像头。
cap = cv2.VideoCapture(0)

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("错误：无法打开摄像头。")
    exit()

# 步骤 3: 循环读取摄像头帧并进行目标检测
while True:
    # 从摄像头读取一帧
    ret, frame = cap.read()

    # 如果无法读取帧，则退出循环
    if not ret:
        print("错误：无法从摄像头读取帧。")
        break

    # 步骤 4: 使用 YOLOv8 模型对帧进行推理（目标检测）
    # `stream=True` 可以提高性能
    results = model.predict(frame, stream=True)

    # 步骤 5: 遍历结果并绘制边界框
    for r in results:
        # 获取帧的原始图像（带有边界框和标签）
        im_with_boxes = r.plot()

        # 显示带有目标检测结果的帧
        cv2.imshow("YOLO 目标检测 - 按 'q' 退出", im_with_boxes)

    # 步骤 6: 等待按键，如果按下 'q' 键则退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 步骤 7: 释放摄像头并关闭所有窗口
cap.release()
cv2.destroyAllWindows()