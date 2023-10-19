
python 可以利用queue数据结构实现生产者-消费者模型
> note: 以下代码Python 版本为3.8
```python
import threading
import uuid

# 定义退出标志 - 哨兵任务
class Sentinal(object):
    pass


class Consumer(threading.Thread):
    def __init__(self, queue):
        self._queue = queue
        self._name = '_consumer_' + uuid.uuid4().hex
        return super(Consumer, self).__init__()

    # override the run function
    def run(self) -> None:
        while True:
            task = self._queue.get()
            # 判断是否是哨兵任务
            if isinstance(task, Sentinal):
                return
            print(f'{self._name} receive {task}')
        print(f"{self._name} closed")
```

消费者模型
```python
class Producer(threading.Thread):
    def __init__(self, queue):
        self._queue = queue
        super(Producer, self).__init__()

    def run(self) -> None:
        i = 0
        while i < 1000:
            self._queue.put(f'task_{i}')
            print("producer", i)
            i += 1
        self._queue.put(Sentinal())
```

执行过程
```python
from queue import Queue
cur_queue = Queue()

producer = Producer(cur_queue)
producer.start()
producer.join()
consumer = Consumer(cur_queue)
consumer.start()
consumer.join()
```

## **分析下queue的实现原理**
```python
class Queue:
    def __init__(self, maxsize=0):
        self.maxsize = maxsize # 设置容量，如果 <= 0,不设限
        self._init(maxsize)
      	# 三个condition共享的锁，也就是要判断是否为空， 必须先拿到锁
		# 要判断是否not_full也要先拿到锁
		# 要判断是否所有任务都完成，也要拿到锁
        self.mutex = threading.Lock()
 
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self):
        return len(self.queue)

    # Put a new item in the queue
    def _put(self, item):
        self.queue.append(item)

    # Get an item from the queue
    def _get(self):
        return self.queue.popleft()
```
### **`not_empty`的作用**
#### `get`中的调用
因为`get` 方法block在`not_empty`上，所以，当添加一个元素到queue中后，通过`not_empty`就能唤醒 block 在 `get`方法上的线程。
```python
   	def get(self, block=True, timeout=None):
        with self.not_empty: # block在not empty上
            ...
```
#### `put`中的调用
```python
def put(self, item, block=True, timeout=None):
	with self.not_full:
		if self.max_size > 0:
			...
		
		self._put(item)
    	self.unfinished_tasks += 1
    	self.not_empty.notify() # 添加了元素，通知消费线程去取数据
```
### `not_full`的作用
当设置了容量之后，会通过`not_full`判断是否可以插入数据，否则就是一把普通的锁，谁拿到谁写入。
#### `put`方法中，当`self.max_size` 大于0时
```python

if not block: # 没阻塞
	# _qsize = len(self.queue)
	if self._qsize() >= self.maxsize: # 当前队列已经满了
        raise Full
elif timeout is None: # block 为True，timeout 是空
    while self._qsize() >= self.maxsize:
        self.not_full.wait() # 阻塞等待可以写入的信号
elif timeout < 0: # timeout 不能小于0
	raise ValueError("'timeout' must be a non-negative number")
else: # block 为True， timeout >= 0
	endtime = time() + timeout
	while self._qsize() >= self.maxsize: # 队列还是满的
    	remaining = endtime - time() # 查看剩余时间
        if remaining <= 0.0: # 如果等待的时间已经到了，当前队列还是满的，抛出异常
            raise Full
    self.not_full.wait(remaining) # 阻塞一定时长，等待可以写入的信号
```
从上面的代码可以看出，如果队列满了，一定会有一个线程block在`not_full`这个条件变量上，如果其它线程尝试写入队列，就会block在`put`的入口处`with self.not_full `。
#### **get方法中的调用**
当消费者消费完一个队列中一个元素时，队列此时变成`not_full`的状态，需要通知生产线程去生产数据。
```python
def get(self, block=True, timeout=None):
	with self.not_empty:
		... # 省略中间处理block timeout 和 空队列的代码
            
    	item = self._get() # 取出一个元素
        self.not_full.notify() # 现在队列有一个空位置了，赶紧写吧
        return item
```
### `all_tasks_done`的作用
> 源代码中的注释： Notify all\_tasks\_done whenever the number of unfinished tasks drops to zero; thread waiting to join() is notified to resume
> 对队列中所有的任务都完成时，wait在queue的join函数上的线程被唤醒
我们知道在`put`方法中，每添加一个任务，`self.unfinished_tasks`就会加1
减1的动作在`task_done`方法中
```python
def task_done(self):
	with self.all_tasks_done:
    	unfinished = self.unfinished_tasks - 1
        if unfinished <= 0:
        	if unfinished < 0:
            	raise ValueError('task_done() called too many times')
        	self.all_tasks_done.notify_all()
        self.unfinished_tasks = unfinished
```
和 `task_done`函数密切相关的一个函数是 `join`函数
```python
def join(self):
	with self.all_tasks_done: # 当前队列中的task都处理完了
    	while self.unfinished_tasks: # 还有任务没处理完
        	self.all_tasks_done.wait() # block，直到处理完
```
`all_tasks_done`的作用不太明显，简单的队列如果不关心生产和消费的速度差异，可以不用使用`task_done`和`join`方法。
但是如果你想调整生产-消费的速度，你就可以利用`task_done 和 join`方法。
```python
def produce():
    for item in ['A', 'B', 'C', 'D']:
        q.put(item)
        print('produce %s' % item)
    q.join() # 每4个一组，这样 生产-消费最多差4个元素
    print('------------ q is empty')

    for item in ['E', 'F', 'G', 'H']:
        q.put(item)            
        print('produce %s' % item)
    q.join()        
    print('------------ q is empty')

def consume():
    for i in range(8):
        item = q.get()
        print('  consume %s' % item)
        q.task_done() # 每消费完一个元素，检查下是否所有的任务都处理完了

```

### `self.mutex`
这个很简单，就不做解释了，除了用来初始化三个 condition 之外，在代码中其它的用处如下：
```python
    def qsize(self):
        with self.mutex:
            return self._qsize()

    def empty(self):
        with self.mutex:
            return not self._qsize()

    def full(self):
        with self.mutex:
            return 0 < self.maxsize <= self._qsize()

```

**引用**
[http://www.imooc.com/wiki/pythonlesson2/pythonqueue.html][1]

[1]:	http://www.imooc.com/wiki/pythonlesson2/pythonqueue.html