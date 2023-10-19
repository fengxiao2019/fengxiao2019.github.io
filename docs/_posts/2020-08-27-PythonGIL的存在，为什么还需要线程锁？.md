
# Python GIL的存在，为什么还需要线程锁？

 虽然说GIL的存在导致同一个时刻只能有一个Python线程在运行，但是，这条线程操作的数据结构
还是可能遭到破坏，因为这条线程在执行完一条字节码之后，可能会被别的线程切换走，等它再切回来
继续执行下一条字节码指令时，当前数据获取已经不是最新的值了。
Effective Python 中有一节专门讲解这个问题

## 总结
"""
虽然Python 有GIL，但是开发者还是得设法避免线程之间数据竞争
把未经过互斥锁保护的的数据开放给多个线程同时修改，可能导致这份数据的结构遭到破坏
可以利用threading 内置模块的lock类确保程序中的固定关系不会在多个线程环境下受到干扰
"""

```
import threading
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self, offset):
        self.count += offset
```

###  改进后，有锁锁住要保护的执行步骤
```
class Counter:
    def __init__(self):
        self.count = 0

        self.lock = threading.Lock()

    def increment(self, offset):
        with self.lock:
            self.count += offset



def worker(sensor_index, how_many, counter):
    for _ in range(how_many):
        counter.increment(1)


from threading import Thread
how_many = 10 ** 5
counter = Counter()
threads = []
for i in range(5):
    threads.append(Thread(target=worker, args=(i, how_many, counter)))
    threads[-1].start()

# join threads
for thread in threads:
    thread.join()

expected = how_many * 5
found = counter.count

print(f"Counter should be {expected}, now should got {found}")
```