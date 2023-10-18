# 条件变量Condition源码解析
## 源码解析

```
class Condition:
    """Class that implements a condition variable.	
	一个条件变量允许一个或多个线程等待，直到它们被另一个线程通知。
 	如果给出了锁的参数而不是None，它必须                                                                                                                                                                                                                                                                                                           self.acquire = lock.acquire
        self.release = lock.release
        # If the lock defines _release_save() and/or _acquire_restore(),
        # these override the default implementations (which just call
        # release() and acquire() on the lock).  Ditto for _is_owned().
        try:
            self._release_save = lock._release_save
        except AttributeError:
            pass
        try:
            self._acquire_restore = lock._acquire_restore
        except AttributeError:
            pass
        try:
            self._is_owned = lock._is_owned
        except AttributeError:
            pass
		# 多个线程等待的关键在这里，使用一个队列来记录等待的线程
		# 实际是每次调用一个wait都会生成一把新的锁，放入到队列中
		# 通过notify释放具体的锁，间接的实现唤醒的动作
		# 如果需要唤醒多个线程，就是释放多把锁，也就间接唤醒了多个线程
        self._waiters = _deque()
	
	# 支持上下文操作
    def __enter__(self):
        return self._lock.__enter__()
	
	# 支持上下文操作
    def __exit__(self, *args):
        return self._lock.__exit__(*args)
	
	# 锁 + 当前有多少个线程在等待
    def __repr__(self):
        return "<Condition(%s, %d)>" % (self._lock, len(self._waiters))

	# 释放操作
    def _release_save(self):
        self._lock.release()           # No state to save

	# 获取锁操作
    def _acquire_restore(self, x):
        self._lock.acquire()           # Ignore saved state
	
	# RLock 有自己的_is_owned
	"""
	    def _is_owned(self):
	        return self._owner == get_ident()
	"""
	# 针对Lock的情况下， 
	# 可以使用下面的方式
    def _is_owned(self):
        # Return True if lock is owned by current_thread.
        # This method is called only if _lock doesn't have _is_owned().
		# 因为锁要么被持有，要没没有被持有
		# 如果没有被持有，if 语句会立即进入，因此返回False
		# 否则的话，返回True
        if self._lock.acquire(0):
            self._lock.release()
            return False
        else:
            return True

    def wait(self, timeout=None):
        """
	等待，直到收到通知或发生超时为止。
如果调用此方法时，调用的线程还没有获得锁，就会产生一个RuntimeError。
该方法释放底层锁，然后阻塞，直到它被另一个线程的相同条件变量的notify()或notify_all()调用唤醒，或者直到可选的超时发生。一旦被唤醒或超时，它将重新获得锁并返回。
当超时参数存在而不是无时，它应该是一个浮点数，指定操作的超时，单位是秒（或其分数）。
        当底层锁是一个RLock时，它不会使用其release()方法来释放，因为当它被多次递归获取时，这可能不会真正解锁。相反，RLock类的一个内部接口被使用，即使它被递归地获取了几次，也能真正解锁。然后，当锁被重新获取时，另一个内部接口被用来恢复递归级别。
        """
        if not self._is_owned():
            raise RuntimeError("cannot wait on un-acquired lock")
		# 创建一把锁
        waiter = _allocate_lock()
		# 获取这把锁
        waiter.acquire()
		# 将这把锁加入到等待队列中
        self._waiters.append(waiter)
        saved_state = self._release_save()
        gotit = False
        try:    # restore state no matter what (e.g., KeyboardInterrupt)
            if timeout is None:
				# block住，等待释放
                waiter.acquire()
                gotit = True
            else:
                if timeout > 0:
                    gotit = waiter.acquire(True, timeout)
                else:
                    gotit = waiter.acquire(False)
            return gotit
        finally:
            self._acquire_restore(saved_state)
            if not gotit:
                try:
                    self._waiters.remove(waiter)
                except ValueError:
                    pass

    def wait_for(self, predicate, timeout=None):
        """
		等待，直到一个条件被评估为True。谓词应该是一个可调用的，
		其结果将被解释为一个布尔值。 
		可以提供一个超时，给出最大的等待时间。
        """
        endtime = None
        waittime = timeout
        result = predicate()
        while not result:
            if waittime is not None:
                if endtime is None:
                    endtime = _time() + waittime
                else:
                    waittime = endtime - _time()
                    if waittime <= 0:
                        break
            self.wait(waittime)
            result = predicate()
        return result

    def notify(self, n=1):
        """
		唤醒一个或多个在此条件下等待的线程，如果有的话。
		如果调用此方法时，调用的线程还没有获得锁，就会产生一个RuntimeError。
		这个方法最多唤醒n个等待条件变量的线程；如果没有线程在等待，那么它就是一个无用功。

        """
        if not self._is_owned():
            raise RuntimeError("cannot notify on un-acquired lock")
        all_waiters = self._waiters
        waiters_to_notify = _deque(_islice(all_waiters, n))
        if not waiters_to_notify:
            return
        for waiter in waiters_to_notify:
            waiter.release()
            try:
                all_waiters.remove(waiter)
            except ValueError:
                pass

    def notify_all(self):
        """
		唤醒所有在此条件下等待的线程。
		如果调用此方法时，调用的线程还没有获得锁，就会引发一个RuntimeError。
        """
        self.notify(len(self._waiters))

    notifyAll = notify_all

```