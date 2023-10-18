# Python中的字典是否是线程安全的？
The Global Interpreter Lock (GIL) is used internally to ensure that only one thread runs in the Python VM at a time. In general, Python offers to switch among threads only between bytecode; how frequently it switches can be set via sys.setcheckinterval. Each bytecode instruction and therefore all the C implementation code reached from each instruction is therefore atomic from the point of view of a Python program.

In theory, this means an exact accounting requires an exact understanding of the PVM bytecode implementation. In practice, it means that operations on shared variables of builtin data types (int, list, dict, etc) that “look atomic” really are.

For example, the following operations are all atomic (L, L1, L2 are lists, D, D1, D2 are dicts, x, y are objects, i, j are ints):

```
L.append(x)
L1.extend(L2)
x = L[i]
x = L.pop()
L1[i:j] = L2
L.sort()
x = y
x.field = y
D[x] = y
D1.update(D2)
D.keys()

These aren’t:

i = i+1
L.append(L[-1])
L[i] = L[j]
D[x] = D[x] + 1
```
Operations that replace other objects may invoke those other objects’ __del__ method when their reference count reaches zero, and that can affect things. This is especially true for the mass updates to dictionaries and lists. When in doubt, use a mutex!

怎么理解最后一段话？
因为这涉及到垃圾回收，python使用的垃圾回收机制是引用计数+分代回收机制。
当引用计数为0时，会触发对象的 __del__ 方法。
如何获取当前对象的引用计数？
有两种方式：
```
import gc
import sys
ds = "dafaaaa"
len(gc.get_referrers(ds)) # 0
ma = {}
ma['ds'] = ds
len(gc.get_referrers(ds)) # 1   当降为0时，表示可以回收

sys.getrefcount(ds) # 3         通常为 对象自己+引用个数+ 1
```

获取引用者信息：
```
gc.get_referrers(ds)
[{'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <class '_frozen_importlib.BuiltinImporter'>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, 'gc': <module 'gc' (built-in)>, 'ds': 'dahhlda', 'ma': {'ds': 'dahhlda'}, 'sys': <module 'sys' (built-in)>}]
```