layout: post
title: "Python GIL   Global Interpreter Lock"
date: 2023-10-19 23:33:19 -0000
---

# Python GIL - Global Interpreter Lock
1. Cpython 解释器的内存管理并不是线程安全的
2. 保护多个线程情况下对Python 对象的访问
3. Cpython使用简单的锁机制避免多个线程同时执行字节码

**影响：**
 - 限制了程序的多核执行
 - 同一时间只能有一个多线程执行字节码
 - CPU密集程序难以利用多核优势
 - IO期间会释放GIL，对IO密集程序影响不大


**规避GIL的影响：**
- CPU 密集可以使用多进程 + 进程池
- IO密集使用多线程/协程
- cython扩展


**Python中什么操作才是原子操作？**
- 一个操作如果是一个字节码指令可以完成就是原子的
- 原子的是可以保证线程安全的
- 使用dis模块操作分析字节码
- 非原子操作不是线程安全的

**如何剖析程序性能？**
- 使用各种profile工具
- 二八定律  大部分时间耗时在少量代码上 
- 内置 /profile/cprofile工具
- 使用pyflame 火焰工具


