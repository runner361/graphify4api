# 设备Topic策略概述

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_1111.html
> **提取时间**: 2026-08-15T00:04:43.651596
> **云提供商**: HUAWEI

*本文导读*

* [概述](#section0)
* [使用场景](#section1)
* [限制](#section2)

*展开导读*

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [消息通信](https://support.huaweicloud.com/usermanual-iothub/iot_01_0045_1.html)/ [设备Topic策略](https://support.huaweicloud.com/usermanual-iothub/iot_01_1110.html)/ 设备Topic策略概述

链接复制成功！

设备Topic策略概述
===========

#### 概述

设备策略主要用于对发布/订阅的非$oc开头自定义topic中的数据进行传输限制。通过灵活访问的控制模型，提供了基于用户角色的访问控制，能够管理客户端发布/订阅主题的授权。借助策略功能，可以用于管理一个或多个设备/产品/群组发布、订阅的权限，以保证非$oc开头的自定义Topic的通信安全。设备Topic策略用于发布、订阅机制的协议，比如说设备侧的MQTT、MQTTS协议。

**图1** 策略概念图   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001635823108.png "点击放大")

#### 使用场景

* 群组通信场景，如设备A、设备B、设备C属于一个群组，只允许设备A、设备B、设备C订阅该群组的Topic，其他设备不允许订阅该Topic。
* 用于划分发布/订阅区域。每个区域可以相互通信，其他区域不可访问的情况。

#### 限制

* 一个租户配置的策略数量不超过50个。
* 用于非$oc开头的自定义Topic，对系统主题及$oc开头的自定义Topic无效。
* 一个策略配置的策略文档大小不大于10KB，策略文档数目不大于10条。
* 单个设备或产品最多绑定5个策略。
* 单个设备（客户端）订阅Topic的数量不大于50。
* 设备订阅的Topic的字节长度不超过128字节。
* Topic发布订阅只支持Qos0，Qos1。

#### 相关文档

* [应用侧对接](/usermanual-iothub/iot_02_15.html)
* [自定义Topic通信](/usermanual-iothub/iot_02_9992.html)
* [广播通信使用示例](/usermanual-iothub/iot_01_00122.html)
* [C# Demo使用说明](/usermanual-iothub/iot_01_00118.html)
* [使用AMQP转发](/usermanual-iothub/iot_01_00100.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)