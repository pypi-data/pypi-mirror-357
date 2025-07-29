# 定时器装饰器 (timer_decorator)

## 功能介绍

`timer_decorator` 是一个功能强大的定时器装饰器，可以将任何函数转换为定时执行的任务。适用于需要周期性执行的操作，如数据同步、状态检查、定时提醒等场景。

## 参数说明

```python
@timer_decorator(interval=1.0, repeat=None, run_first=True, daemon=True)
```

- **interval**: `float` - 定时间隔，单位为秒，必须大于0
- **repeat**: `int` 或 `None` - 重复执行次数，`None`表示无限重复，指定数字时必须大于0
- **run_first**: `bool` - 是否在启动定时器后立即执行一次函数，默认为`True`
- **daemon**: `bool` - 是否将定时器线程设置为守护线程，默认为`True`

## 基本用法

```python
from metools import timer_decorator
import time

# 每2秒执行一次，无限重复
@timer_decorator(interval=2.0)
def my_function():
    print("执行定时任务")

# 启动定时器并获取控制器对象
timer_controller = my_function()

# 主程序继续执行其他操作
time.sleep(10)

# 手动停止定时器
timer_controller.stop()
```

## 控制器对象方法

定时器启动后返回一个`TimerController`对象，提供以下方法：

```python
# 停止定时器
timer_controller.stop()

# 检查定时器是否在运行
if timer_controller.is_running():
    print("定时器正在运行")

# 等待定时器完成（可选超时参数）
timer_controller.join(timeout=5.0)
```

## 上下文管理器用法

```python
# 使用上下文管理器自动管理定时器生命周期
with my_function() as controller:
    print("定时器已启动")
    time.sleep(10)
    # 退出上下文块时自动停止定时器
```

## 有限次数执行

```python
# 只执行5次后自动停止
@timer_decorator(interval=1.0, repeat=5)
def limited_task():
    print("有限次数任务")

limited_task()
```

## 停止已有定时器

```python
# 如果函数被多次调用，每次都会停止之前的定时器
@timer_decorator(interval=1.0)
def restart_task():
    print("任务重新开始")

# 第一次启动
controller1 = restart_task()
time.sleep(3)

# 第二次启动会自动停止第一次的定时器
controller2 = restart_task()

# 也可以使用函数上的方法直接停止
restart_task.stop_timer()
```

## 异常处理

装饰器内部会捕获并记录函数执行过程中的异常，不会导致定时器中断：

```python
@timer_decorator(interval=1.0)
def error_prone_task():
    # 即使抛出异常，定时器也会继续运行
    raise ValueError("测试异常")

error_prone_task()
```

## 注意事项

1. **资源管理**：定时器使用线程实现，请注意线程安全问题
2. **主程序结束**：如果`daemon=True`（默认），主程序结束时定时器会自动终止
3. **函数返回值**：被装饰的函数的返回值会被忽略
4. **参数传递**：调用时传入的参数会传递给被装饰的函数
5. **线程安全**：如果被装饰函数访问共享资源，请确保使用适当的锁机制
