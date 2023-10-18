# 源码解析
实现原理是借助了Condition
在Python多线程的实现中也是利用Semphore的特性
```python
class Semaphore:
    """
	该类实现了信号器对象
Semaphores管理一个计数器，代表release()调用的次数减去acquire()调用的次数，再加上一个初始值。如果有必要，acquisition()方法会阻塞，直到它可以返回而不使计数器变成负值。如果没有给出，值默认为1。
    """

    # After Tim Peters' semaphore class, but not quite the same (no maximum)

    def __init__(self, value=1):
        # 初始的value 的值必须大于等于0
        if value < 0:
            raise ValueError("semaphore initial value must be >= 0")
        self._cond = Condition(Lock())
        self._value = value

    def acquire(self, blocking=True, timeout=None):
        """
		acquire -> self._value -= 1
			无参数的情况下
				self._value 如果大于0 ，直接返回
				self._value 如果等于0，阻塞，直到其他线程release
			如果有多个线程调用了acqure，只有一个会被唤醒
			具体是哪个线程被唤醒，是随机的
        	
			blocking 设置为True的情况
				处理逻辑和无参数保持一致
			blocking 为False，如果被阻塞了会立即返回，return False
			否则，return True
		
			如果指定了timeout，block 最多timeout时长，如果还是没有acquire成功，返回False，否则，返回True。
        """
        if not blocking and timeout is not None:
            raise ValueError("can't specify timeout for non-blocking acquire")
        rc = False
        endtime = None
        with self._cond:
            while self._value == 0:
                if not blocking:
                    break
                if timeout is not None:
                    if endtime is None:
                        endtime = _time() + timeout
                    else:
                        timeout = endtime - _time()
                        if timeout <= 0:
                            break
                self._cond.wait(timeout)
            else:
                self._value -= 1
                rc = True
        return rc

    __enter__ = acquire

    def release(self):
        """Release a semaphore, incrementing the internal counter by one.

        When the counter is zero on entry and another thread is waiting for it
        to become larger than zero again, wake up that thread.

        """
        with self._cond:
            self._value += 1     # 释放的场景下 + 1
            self._cond.notify()  # 通知一个线程

    def __exit__(self, t, v, tb):
        self.release()   # 退出时释放

```

## 用Semphore实现一个生产者&消费者模型

