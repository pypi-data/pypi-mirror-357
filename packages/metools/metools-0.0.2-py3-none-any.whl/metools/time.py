def timer_decorator(interval=1.0, repeat=None, run_first=True, daemon=True):
    """
    一个简单好用的定时器装饰器
    参数:
        interval (float): 定时器间隔，单位为秒
        repeat (int, 可选): 重复执行次数，None表示无限重复
        run_first (bool): 是否立即运行一次，默认为True
        daemon (bool): 是否设置为守护线程，默认为True
    """
    import threading
    import logging
    import sys
    from functools import wraps

    # 参数验证
    if interval <= 0:
        raise ValueError("interval 必须大于 0")
    if repeat is not None and repeat <= 0:
        raise ValueError("repeat 必须大于 0 或为 None")

    def decorator(func):
        # 添加线程锁，防止竞态条件
        _lock = threading.Lock()

        @wraps(func)
        def wrapper(*args, **kwargs):
            with _lock:
                # 如果已经有定时器在运行，先停止它
                if (
                    hasattr(wrapper, "_timer_thread")
                    and wrapper._timer_thread.is_alive()
                ):
                    wrapper._stop_event.set()
                    wrapper._timer_thread.join(timeout=2.0)
                    if wrapper._timer_thread.is_alive():
                        logging.warning(
                            f"定时器线程在{func.__name__}中未能在预期时间内停止"
                        )

                # 创建新的停止事件
                stop_event = threading.Event()
                wrapper._stop_event = stop_event

            def timer_task():
                executed_count = 0

                try:
                    # 如果设置了立即运行，则先执行一次
                    if run_first:
                        func(*args, **kwargs)
                        executed_count += 1
                        # 检查是否达到重复次数
                        if repeat is not None and executed_count >= repeat:
                            return

                    while not stop_event.is_set():
                        # 等待指定的间隔时间
                        if stop_event.wait(interval):
                            break

                        # 执行被装饰的函数
                        try:
                            func(*args, **kwargs)
                            executed_count += 1
                        except Exception as e:
                            # 记录异常但不中断定时器
                            print(f"定时器执行函数时发生异常: {e}", file=sys.stderr)
                            if logging.getLogger().hasHandlers():
                                logging.error(
                                    f"定时器执行函数时发生异常: {e}", exc_info=True
                                )

                        # 检查是否达到重复次数
                        if repeat is not None and executed_count >= repeat:
                            break

                except Exception as e:
                    print(f"定时器线程发生异常: {e}", file=sys.stderr)
                    if logging.getLogger().hasHandlers():
                        logging.error(f"定时器线程发生异常: {e}", exc_info=True)

            # 创建并启动新线程
            timer_thread = threading.Thread(target=timer_task)
            timer_thread.daemon = daemon
            timer_thread.start()

            # 保存线程引用
            wrapper._timer_thread = timer_thread

            # 返回控制对象，包含原函数的功能
            class TimerController:
                def __init__(self, stop_event, thread):
                    self.stop_event = stop_event
                    self.thread = thread
                    self.func = func  # 保存原函数引用

                def stop(self):
                    """停止定时器"""
                    self.stop_event.set()

                def is_running(self):
                    """检查定时器是否在运行"""
                    return self.thread.is_alive()

                def join(self, timeout=None):
                    """等待定时器线程结束"""
                    self.thread.join(timeout)

                def __enter__(self):
                    """上下文管理器入口"""
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    """上下文管理器退出时停止定时器"""
                    self.stop()
                    self.join(timeout=2.0)

            return TimerController(stop_event, timer_thread)

        # 添加停止方法
        def stop_timer():
            """停止当前运行的定时器"""
            if hasattr(wrapper, "_stop_event"):
                wrapper._stop_event.set()

        wrapper.stop_timer = stop_timer
        return wrapper

    return decorator
