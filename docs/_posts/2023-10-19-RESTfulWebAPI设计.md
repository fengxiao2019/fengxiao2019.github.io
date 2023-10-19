layout: post
title: "RESTful Web API 设计"
date: 2023-10-19 23:33:19 -0000
---

# RESTful Web API 设计
设计良好的WEB API 需要支持两种特性：平台的独立性和支持服务的演变。所谓的平台独立性是指不管你的API内部的实现方式如何，任何客户端都可以调用该API，这就需要使用标准协议，例如http协议。支持服务的演变，是指在不影响客户端使用的情况下改进和添加功能。这就涉及到API 版本管理。
REST 其实是一组架构上的约束，表示对资源的状态呈现（或着表述），设计Restful Web API 有一些原则可以遵循：
 - 围绕资源设计，这里需要界定资源：任何类型的对象、数据或者服务等
 - 每个资源都应该有一个标识符，也就是唯一标识该资源的URI。
 - 资源通过一定的表示形式在客户端和服务端之间进行传输。例如json
 - 使用统一的接口，有助于实现前后端分离，例如以http构建的api，使用标准的http动作对资源执行操作。
 - 无状态请求模型。无状态可以保证服务的可扩展性。
 - rest api 在表示形式中添加资源的驱动链接。（rel，href，action）
 有人对web api 的成熟度分成了4个级别，级别0: 定义一个URL，所有的操作都是对此URL发出的post请求，级别1:为各个资源单独创建url，级别2: 使用http方法来定义对资源执行的操作，级别3: 使用HATEOAS。

https://docs.microsoft.com/zh-cn/azure/architecture/best-practices/api-design