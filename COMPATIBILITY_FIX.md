# PyQt6 兼容性问题修复指南

## 问题描述

在运行 Oasis 目标检测系统时，您可能会遇到以下 PyQt6 兼容性错误：

```
💥 意外错误: type object 'ApplicationAttribute' has no attribute 'AA_EnableHighDpiScaling'
```

这个错误是由于不同版本的 PyQt6 中高 DPI 支持属性的变化导致的。

## 根本原因

在 PyQt6 的某些版本中，以下高 DPI 相关属性可能：
- 被重命名
- 被移除（因为功能已默认启用）
- 移动到不同的命名空间

受影响的属性：
- `Qt.ApplicationAttribute.AA_EnableHighDpiScaling`
- `Qt.ApplicationAttribute.AA_UseHighDpiPixmaps`

## 解决方案

### 1. 使用安全启动器（推荐）

我们创建了一个自动处理兼容性问题的启动器：

```bash
python main_ui_safe.py
```

**特点：**
- 自动检测 PyQt6 版本
- 安全地设置高 DPI 属性
- 提供详细的错误诊断
- 自动降级到可用的 UI 模块

### 2. 代码修复详情

在启动器代码中，我们使用了 try-except 块来安全地处理属性设置：

```python
# 修复前（有问题的代码）
app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

# 修复后（兼容的代码）
try:
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
except AttributeError:
    # PyQt6 中这些属性可能不存在或已被弃用
    # 在 PyQt6 中，高 DPI 支持是默认启用的
    pass
```

### 3. 更强健的解决方案

在 `main_ui_safe.py` 中，我们实现了更详细的检查：

```python
def create_safe_application():
    """创建兼容的 QApplication"""
    app = QApplication(sys.argv)
    
    # 安全地设置高 DPI 支持
    high_dpi_attributes = [
        'AA_EnableHighDpiScaling',
        'AA_UseHighDpiPixmaps',
    ]
    
    for attr_name in high_dpi_attributes:
        try:
            if hasattr(Qt.ApplicationAttribute, attr_name):
                attr = getattr(Qt.ApplicationAttribute, attr_name)
                app.setAttribute(attr, True)
                print(f"✅ 高DPI支持: {attr_name} 已启用")
            else:
                print(f"ℹ️  高DPI支持: {attr_name} 不可用 (可能在此版本中已默认启用)")
        except Exception as e:
            print(f"⚠️  高DPI设置警告: {attr_name} - {e}")
    
    return app
```

## 测试和验证

### 1. 运行兼容性测试

```bash
python test_pyqt6_compatibility.py
```

这个测试会检查：
- PyQt6 基本功能
- 高 DPI 属性可用性
- UI 文件加载能力
- 依赖项完整性

### 2. 测试输出示例

正常情况：
```
✅ PyQt6 模块导入成功
✅ QApplication 创建成功
✅ AA_EnableHighDpiScaling 设置成功
✅ AA_UseHighDpiPixmaps 设置成功
✅ 窗口创建成功
```

兼容性问题情况：
```
✅ PyQt6 模块导入成功
✅ QApplication 创建成功
ℹ️  AA_EnableHighDpiScaling 属性不存在 (PyQt6 中可能已弃用，这是正常的)
ℹ️  AA_UseHighDpiPixmaps 属性不存在 (PyQt6 中可能已弃用，这是正常的)
✅ 窗口创建成功
```

## 启动器选择指南

### 可用的启动器

1. **main_ui_safe.py** (推荐)
   - 自动兼容性处理
   - 详细错误诊断
   - 最稳定的选择

2. **main_ui.py** (已修复)
   - 标准启动器
   - 包含基本兼容性修复
   - 适合大多数情况

3. **main_ui_loader.py** (UI文件版本)
   - 使用 .ui 文件的版本
   - 包含相同的兼容性修复
   - 适合界面开发

### 选择建议

- **首次使用**: 使用 `main_ui_safe.py`
- **开发调试**: 使用 `main_ui_loader.py`
- **日常使用**: 使用 `main_ui.py`

## 其他兼容性注意事项

### PyQt6 vs PyQt5

如果您之前使用过 PyQt5，请注意：

1. **模块名称变化**:
   ```python
   # PyQt5
   from PyQt5.QtWidgets import QApplication
   
   # PyQt6
   from PyQt6.QtWidgets import QApplication
   ```

2. **枚举值访问**:
   ```python
   # PyQt5
   Qt.AlignCenter
   
   # PyQt6
   Qt.AlignmentFlag.AlignCenter
   ```

3. **信号连接**:
   ```python
   # PyQt5 (仍然支持)
   button.clicked.connect(self.on_click)
   
   # PyQt6 (推荐)
   button.clicked.connect(self.on_click)
   ```

### 版本要求

- **Python**: 3.8 或更高版本
- **PyQt6**: 6.4.0 或更高版本
- **操作系统**: Windows 10/11, macOS 10.15+, Linux

## 故障排除步骤

如果仍然遇到问题，请按以下步骤操作：

1. **更新 PyQt6**:
   ```bash
   pip install --upgrade PyQt6
   ```

2. **清理 Python 缓存**:
   ```bash
   pip cache purge
   python -m pip install --force-reinstall PyQt6
   ```

3. **检查 Python 版本**:
   ```bash
   python --version
   ```

4. **运行完整测试**:
   ```bash
   python test_pyqt6_compatibility.py
   ```

5. **使用安全启动器**:
   ```bash
   python main_ui_safe.py
   ```

## 技术细节

### 高 DPI 支持的演变

在不同的 Qt/PyQt 版本中，高 DPI 支持经历了以下变化：

- **Qt 5.6+**: 引入 `AA_EnableHighDpiScaling`
- **Qt 5.14+**: 高 DPI 支持改进
- **Qt 6.0+**: 高 DPI 支持默认启用
- **PyQt6**: 某些属性可能被移除或重命名

### 我们的解决方案

通过使用 `hasattr()` 检查和异常处理，我们的代码能够：

1. 在属性存在时正确设置
2. 在属性不存在时优雅地跳过
3. 提供清晰的日志信息
4. 保证程序正常运行

这种方法确保了代码在不同版本的 PyQt6 中都能正常工作，同时保持了向前和向后兼容性。

## 总结

通过这些修复，Oasis 目标检测系统现在能够：

✅ 在不同版本的 PyQt6 中稳定运行  
✅ 自动处理高 DPI 支持兼容性问题  
✅ 提供清晰的错误诊断信息  
✅ 支持多种启动方式  
✅ 包含完整的测试和验证工具  

建议使用 `main_ui_safe.py` 作为主要启动器，它会自动处理所有已知的兼容性问题。
