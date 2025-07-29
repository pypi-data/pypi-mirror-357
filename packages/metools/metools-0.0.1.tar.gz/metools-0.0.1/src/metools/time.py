def timer_decorator(interval=1.0, repeat=None, run_first=True, daemon=True):
    """
    一个简单好用的定时器装饰器

    参数:
        interval (float): 定时器间隔，单位为秒
        repeat (int, 可选): 重复执行次数，None表示无限重复
        run_first (bool): 是否立即运行一次，默认为True
        daemon (bool): 是否设置为守护线程，默认为True

    用法:
        @timer_decorator(interval=2.0)
        def my_task():
            print("每2秒执行一次")

        @timer_decorator(interval=5.0, repeat=3)
        def limited_task():
            print("每5秒执行一次，共执行3次")
    """
    import threading
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 创建一个事件对象，用于控制定时器停止
            stop_event = threading.Event()

            # 内部函数，在单独的线程中运行
            def timer_task():
                count = 0

                # 如果设置了立即运行，则先执行一次
                if run_first:
                    func(*args, **kwargs)
                    count += 1
                    # 检查是否达到重复次数
                    if repeat is not None and count >= repeat:
                        return

                while not stop_event.is_set():
                    # 等待指定的间隔时间
                    if stop_event.wait(interval):
                        break

                    # 执行被装饰的函数
                    func(*args, **kwargs)
                    count += 1

                    # 检查是否达到重复次数
                    if repeat is not None and count >= repeat:
                        break

            # 创建并启动一个新线程
            timer_thread = threading.Thread(target=timer_task)
            timer_thread.daemon = daemon
            timer_thread.start()

            # 返回停止事件，用于外部控制
            return stop_event

        return wrapper

    return decorator