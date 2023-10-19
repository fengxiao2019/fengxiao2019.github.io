---
layout: post
title: "Rebalance 源码解析"
date: 2023-10-19 23:33:19 -0000
---

# Rebalance 源码解析
## 基本的设计原则
1. 一个消息消费队列在同一时间只能被同一消费组的一个消费者消费，而一个消息消费者可以同时消费多个消息队列。
## 为什么需要做rebalance？
在RocketMQ中，Consumer端的有两种消费模式（Push/Pull），但是都是基于pull模式来获取消息的，Push模式只是对pull模式的一种封装，本质上是消息拉取线程从server 拉取消息。在提交给消息消耗线程池后，它又继续尝试将消息拉到服务器上。*如果消息没有被拉出，就会block，直到超时，再继续拉取*。在这两种基于拉动模式的消费模式（推/拉）中，消费者需要知道哪个消息队列。因为同一个消费者组中有多个消费者，同时，同一个topic下有多个消息队列，为了实现消息的负载均衡，就需要在消费者端做负载均衡消费。
    但是，由于网络和人为操作，导致broke下线、上线、topic扩容导致队列增加、topic缩容导致队列减少、或者消费者组中的消费者数量增加或者减少，都需要实现队列和消费者的重新分配才能达到消费侧负载均衡的目的。

## 触发的时机以及调用周期
消费者启动的时候，会启动一个线程。


源码文件：src/consumer/Rebalance.h  src/consumer/Rebalance.cpp
RebalancePull 和 RebalancePush继承自Rebalance 类
最核心的操作就是doRebalance函数。

循环遍历m_subscriptionData,针对每一个topic做重平衡。
以下逻辑适用于单个topic的重平衡：
step1: 获取该topic下所有的messageQueue，getTopicSubscribeInfo(topic, mqAll), 存储到mqAll。
step2: 消费模型分为两种，一种是广播模型，一种是集群消费模型。
step3: 集群模式的重平衡
step3.1: 根据topic + group_name 获取所有的消费者ID，存储到cidAll中 。
step3.1.1:如果cidAll为空，抛出异常，doRebalance the cidAll is empty
step3.2: 对mqAll和 cidAll进行排序。
step3.3: 调用重平衡策略，进行重平衡。将结果存储在allocateResult中。但是，实际上cpp 提供的分配策略只有一种，平均分配。
 ```
 m_pAllocateMQStrategy->allocate(m_pConsumer->getMQClientId(), mqAll, cidAll, allocateResult);
```
实际的分配算法：
```    int mqAllSize = mqAll.size();
    int mod = mqAllSize % cidAllSize;
    int averageSize =
        mqAllSize <= cidAllSize ? 1 : (mod > 0 && index < mod ? mqAllSize / cidAllSize + 1 : mqAllSize / cidAllSize);
    int startIndex = (mod > 0 && index < mod) ? index * averageSize : index * averageSize + mod;
    int range = (std::min)(averageSize, mqAllSize - startIndex);
    if (range >= 0)  // example: range is:-1, index is:1, mqAllSize is:1,
                     // averageSize is:1, startIndex is:2
    {
      for (int i = 0; i < range; i++) {
        if ((startIndex + i) >= 0) {
          outReuslt.push_back(mqAll.at((startIndex + i) % mqAllSize));
        }
      }
    }
  }
```
step3.4: 更新RequestTable，方法：updateRequestTableInRebalance，实际变更的变量是：m_requestQueueTable。
step3.5: 如果上一步中有变化，例如MessageQueue不可用或者新增了MessageQueue，需要调用messageQueueChanged函数，但是实际上，这个函数是个空函数。

step4: 集群模型的重平衡
Rebalance的成员变量：
``` 
map<string, SubscriptionData*> m_subscriptionData; 
// key 是主题的名称，val为SubscriptionData 指针

boost::mutex m_topicSubscribeInfoTableMutex;
map<string, vector<MQMessageQueue>> m_topicSubscribeInfoTable;
typedef map<MQMessageQueue, boost::shared_ptr<PullRequest>> MQ2PULLREQ;
MQ2PULLREQ m_requestQueueTable;
boost::mutex m_requestTableMutex;

AllocateMQStrategy* m_pAllocateMQStrategy;
MQConsumer* m_pConsumer;
MQClientFactory* m_pClientFactory;
```
