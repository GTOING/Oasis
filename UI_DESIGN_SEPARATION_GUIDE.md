# Oasis UI 设计分离指南

## 概述

本指南详细介绍了如何将 Oasis 目标检测系统的界面设计与业务逻辑分离，使用 `.ui` 文件进行动态加载的方法。

## 架构变更

### 原始架构
```
main_window.py (界面 + 逻辑混合)
├── UI 组件创建
├── 布局设置  
├── 样式定义
└── 业务逻辑
```

### 新架构
```
UI 文件层
├── main_window.ui          # 界面设计文件
├── settings_dialog.ui      # 设置对话框设计
└── styles.qss             # 样式表文件

业务逻辑层
├── main_window_ui.py       # 主窗口逻辑
├── settings_dialog_ui.py   # 设置对话框逻辑
└── ui_loader.py           # UI 加载工具

配置层
└── config.py              # 配置管理
```

## 文件结构

### 新增文件

1. **UI 设计文件**
   - `ui/main_window.ui` - 主窗口界面设计
   - `ui/settings_dialog.ui` - 设置对话框界面设计

2. **UI 加载器**
   - `ui/ui_loader.py` - UI 文件动态加载工具类

3. **业务逻辑文件**
   - `ui/main_window_ui.py` - 主窗口业务逻辑
   - `ui/settings_dialog_ui.py` - 设置对话框业务逻辑

4. **启动器**
   - `main_ui_loader.py` - 使用 UI 文件版本的启动器

5. **测试文件**
   - `test_ui_loader.py` - UI 加载功能测试脚本

## 核心特性

### 1. UI 文件动态加载

```python
from ui.ui_loader import UILoader, UI_FILES

# 加载主窗口 UI
ui = UILoader.load_ui(UI_FILES['MAIN_WINDOW'], self)

# 应用样式表
UILoader.apply_stylesheet(self)
```

### 2. 组件化设计

**UILoader 类功能：**
- 动态加载 .ui 文件
- 自动应用样式表
- 路径管理和验证
- 错误处理

**UIComponent 基类：**
- 标准化的 UI 组件接口
- 简化 UI 加载流程
- 便于扩展和维护

### 3. 界面与逻辑分离

**UI 文件负责：**
- 组件布局和排列
- 基础样式定义
- 控件属性设置
- 菜单和动作定义

**Python 代码负责：**
- 事件处理和信号槽
- 业务逻辑实现
- 数据绑定和更新
- 动态行为控制

## 使用方法

### 1. 运行 UI 文件版本

```bash
# 启动 UI 文件版本
python main_ui_loader.py

# 或者启动原始版本
python main_ui.py
```

### 2. 修改界面设计

**方法一：使用 Qt Designer**
```bash
# 安装 Qt Designer (包含在 PyQt6-tools 中)
pip install PyQt6-tools

# 打开 UI 文件进行编辑
designer ui/main_window.ui
```

**方法二：直接编辑 .ui 文件**
- UI 文件是标准的 XML 格式
- 可以直接修改属性和布局
- 支持版本控制和差异比较

### 3. 自定义组件替换

```python
# 在 Python 代码中替换 UI 组件
def setup_video_display(self):
    # 创建自定义组件
    self.video_display = VideoDisplayWidget()
    
    # 替换 UI 文件中的组件
    old_component = self.ui.video_display
    parent_layout = old_component.parent().layout()
    
    # 移除旧组件，添加新组件
    parent_layout.removeWidget(old_component)
    parent_layout.insertWidget(index, self.video_display)
```

## 优势分析

### 1. 开发效率提升

- **可视化设计**：使用 Qt Designer 进行拖拽式界面设计
- **快速原型**：无需编写代码即可设计界面布局
- **实时预览**：在设计器中即时查看界面效果

### 2. 维护性增强

- **职责分离**：界面设计师专注 UI，程序员专注逻辑
- **版本控制**：UI 文件变更清晰可见
- **团队协作**：设计和开发可以并行进行

### 3. 灵活性提高

- **样式热更新**：修改样式文件立即生效
- **布局调整**：在设计器中轻松调整布局
- **多主题支持**：通过不同的样式文件支持多主题

### 4. 代码质量改善

- **代码简化**：Python 代码不再包含 UI 创建代码
- **逻辑清晰**：业务逻辑更加集中和清晰
- **易于测试**：界面和逻辑分离便于单元测试

## 最佳实践

### 1. UI 文件组织

```
ui/
├── main_window.ui          # 主窗口
├── settings_dialog.ui      # 设置对话框
├── about_dialog.ui         # 关于对话框
├── components/             # 自定义组件
│   ├── video_widget.ui
│   └── control_panel.ui
└── styles/                 # 样式文件
    ├── light.qss
    └── dark.qss
```

### 2. 命名规范

**UI 文件命名：**
- 使用下划线分隔：`main_window.ui`
- 与对应的 Python 文件一致
- 描述性命名，避免缩写

**组件命名：**
- 使用描述性前缀：`start_btn`, `video_display`
- 保持一致的命名风格
- 在 UI 文件中设置 objectName

### 3. 样式管理

```css
/* 使用 CSS 选择器进行精确控制 */
QPushButton[objectName="start_btn"] {
    background-color: #007AFF;
    color: white;
}

QGroupBox[title="控制面板"] {
    font-weight: bold;
    border: 1px solid #C7C7CC;
}
```

### 4. 错误处理

```python
try:
    ui = UILoader.load_ui('main_window.ui', self)
except FileNotFoundError:
    # 降级到代码创建的界面
    self.create_fallback_ui()
except Exception as e:
    # 显示错误信息
    QMessageBox.critical(self, "UI加载失败", str(e))
```

## 测试验证

### 运行测试

```bash
# 运行 UI 系统测试
python test_ui_loader.py
```

### 测试内容

1. **UI 文件存在性检查**
   - 验证所有必需的 .ui 文件
   - 检查文件路径和命名

2. **UI 加载器功能测试**
   - 测试 UI 文件加载
   - 验证样式表应用

3. **配置管理器测试**
   - 检查配置文件加载
   - 验证默认设置

## 迁移指南

### 从原始版本迁移到 UI 文件版本

1. **备份原始文件**
```bash
cp ui/main_window.py ui/main_window_backup.py
```

2. **使用新的启动器**
```bash
# 原始版本
python main_ui.py

# UI 文件版本
python main_ui_loader.py
```

3. **逐步迁移组件**
   - 先迁移主窗口布局
   - 再迁移设置对话框
   - 最后迁移自定义组件

### 兼容性保证

- 保留原始的 `main_ui.py` 启动器
- 两个版本可以并存
- 配置文件共享，设置互通

## 扩展指南

### 添加新的 UI 组件

1. **创建 .ui 文件**
```bash
# 使用 Qt Designer 创建
designer ui/new_component.ui
```

2. **注册到 UI_FILES**
```python
# 在 ui_loader.py 中添加
UI_FILES = {
    'MAIN_WINDOW': 'main_window.ui',
    'SETTINGS_DIALOG': 'settings_dialog.ui',
    'NEW_COMPONENT': 'new_component.ui',  # 新增
}
```

3. **创建对应的业务逻辑类**
```python
# ui/new_component_ui.py
class NewComponentUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.ui = UILoader.load_ui(UI_FILES['NEW_COMPONENT'], self)
        # 添加业务逻辑
```

### 自定义样式主题

1. **创建新的样式文件**
```css
/* ui/themes/dark.qss */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}
```

2. **在应用中切换主题**
```python
# 动态切换样式
UILoader.apply_stylesheet(self, "themes/dark.qss")
```

## 总结

通过将界面设计与业务逻辑分离，Oasis 目标检测系统获得了：

✅ **更好的代码组织**：清晰的职责分离  
✅ **提高开发效率**：可视化界面设计  
✅ **增强维护性**：独立的 UI 和逻辑文件  
✅ **更好的团队协作**：设计师和开发者可以并行工作  
✅ **灵活的样式系统**：支持主题切换和样式热更新  

这种架构为未来的功能扩展和界面优化提供了强大的基础。
