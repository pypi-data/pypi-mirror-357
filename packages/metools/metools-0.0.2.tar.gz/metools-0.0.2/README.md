<div align="center">
  <h1>MeTools - 实用 Python 小工具集</h1>
  <p>简单、高效、可定制的 Python 工具库，让您的日常开发更轻松</p>

  <a href="https://github.com/111hgx/metools/issues">
    <img src="https://img.shields.io/github/issues/111hgx/metools" alt="issues">
  </a>
  <a href="https://github.com/111hgx/metools/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/111hgx/metools" alt="license">
  </a>
  <a href="https://github.com/111hgx/metools">
    <img src="https://img.shields.io/github/stars/111hgx/metools?style=social" alt="stars">
  </a>
</div>

## 📚 项目简介

MeTools 是一个轻量级的 Python 工具库，提供了一系列实用的工具函数和装饰器，帮助开发者简化日常编程任务。该项目专注于提供简单易用的API，让您能够快速集成到现有项目中。

## 🚀 功能特性

- **简单易用** - 直观的 API 设计，低学习成本
- **零依赖** - 仅使用 Python 标准库，无需额外安装依赖包
- **高度可定制** - 灵活的参数配置，满足各种使用场景
- **类型提示** - 完整的类型注解，支持现代编辑器的代码补全和类型检查

## 📦 安装方法

```bash
pip install metools
```

## 🔧 使用示例

### 时间工具

#### 定时器装饰器

一个功能强大的定时器装饰器，可以将任何函数转换为定时执行的任务：

```python
from metools import timer_decorator
import time


# 每2秒执行一次，只执行3次
@timer_decorator(interval=2.0, repeat=3)
def limited_task():
    print("定时任务执行中!")


# 每1.5秒执行一次，无限重复
@timer_decorator(interval=1.5)
def infinite_task():
    print("无限任务执行中...")


# 启动定时器并获取控制器对象
timer_controller = infinite_task()

# 在需要时停止定时任务
timer_controller.stop()

# 或者使用上下文管理器自动管理生命周期
with infinite_task() as controller:
    print("定时器正在运行")
    time.sleep(10)  # 执行10秒后自动停止
```

定时器装饰器参数说明：
- `interval`: 定时间隔（秒），必须大于0
- `repeat`: 重复次数（None表示无限重复）
- `run_first`: 是否立即执行一次（默认为True）
- `daemon`: 是否设为守护线程（默认为True）

控制器对象方法：
- `stop()`: 停止定时器
- `is_running()`: 检查定时器是否在运行
- `join(timeout=None)`: 等待定时器完成

## 🔜 即将推出的功能

- 文件操作工具
- 日志工具
- 字符串处理工具
- 网络请求工具
- 更多实用装饰器

## 🤝 参与贡献

欢迎参与项目贡献！您可以通过以下方式参与：

1. 提交Issue：报告bug或提出新功能建议
2. 提交Pull Request：改进代码或文档
3. 分享使用经验：在Issues中分享您的使用案例

## 📄 许可证

```text
MIT License

Copyright (c) 2025 111hgx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

<div align="center">
  <strong>如果这个项目对您有帮助，请考虑给一个 ⭐️ Star！</strong>
</div>