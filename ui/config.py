"""
Oasis 目标检测系统 - 配置管理
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class DetectionConfig:
    """检测配置"""
    target_classes: List[str]
    confidence_threshold: float
    model_path: str
    max_detections: int
    
    @classmethod
    def default(cls):
        return cls(
            target_classes=['bottle', 'cup', 'cell phone', 'mouse', 'pen'],
            confidence_threshold=0.5,
            model_path='yolo11n.pt',
            max_detections=50
        )


@dataclass
class DisplayConfig:
    """显示配置"""
    show_confidence: bool
    show_class_names: bool
    bbox_thickness: int
    font_scale: float
    bbox_color: tuple
    text_color: tuple
    
    @classmethod
    def default(cls):
        return cls(
            show_confidence=True,
            show_class_names=True,
            bbox_thickness=2,
            font_scale=0.5,
            bbox_color=(0, 255, 0),  # 绿色
            text_color=(0, 255, 0)   # 绿色
        )


@dataclass
class KinectConfig:
    """Kinect 配置"""
    color_resolution: str
    fps: int
    auto_exposure: bool
    
    @classmethod
    def default(cls):
        return cls(
            color_resolution="1920x1080",
            fps=30,
            auto_exposure=True
        )


@dataclass
class UIConfig:
    """界面配置"""
    theme: str
    window_size: tuple
    splitter_sizes: List[int]
    auto_start: bool
    
    @classmethod
    def default(cls):
        return cls(
            theme="light",
            window_size=(1200, 800),
            splitter_sizes=[800, 400],
            auto_start=False
        )


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.detection = DetectionConfig.default()
        self.display = DisplayConfig.default()
        self.kinect = KinectConfig.default()
        self.ui = UIConfig.default()
        
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 加载各个配置段
                if 'detection' in config_data:
                    self.detection = DetectionConfig(**config_data['detection'])
                
                if 'display' in config_data:
                    self.display = DisplayConfig(**config_data['display'])
                
                if 'kinect' in config_data:
                    self.kinect = KinectConfig(**config_data['kinect'])
                
                if 'ui' in config_data:
                    self.ui = UIConfig(**config_data['ui'])
                    
            except Exception as e:
                print(f"配置文件加载失败: {e}, 使用默认配置")
    
    def save_config(self):
        """保存配置"""
        try:
            config_data = {
                'detection': asdict(self.detection),
                'display': asdict(self.display),
                'kinect': asdict(self.kinect),
                'ui': asdict(self.ui)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"配置文件保存失败: {e}")
    
    def get_all_classes(self) -> List[str]:
        """获取所有可用的检测类别"""
        return [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush', 'pen'
        ]
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.detection = DetectionConfig.default()
        self.display = DisplayConfig.default()
        self.kinect = KinectConfig.default()
        self.ui = UIConfig.default()
        self.save_config()


# 全局配置实例
config_manager = ConfigManager()
