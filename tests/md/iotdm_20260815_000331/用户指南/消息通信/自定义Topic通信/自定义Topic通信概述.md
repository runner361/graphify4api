# 自定义Topic通信概述

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_02_9997.html
> **提取时间**: 2026-08-15T00:04:37.494687
> **云提供商**: HUAWEI

*本文导读*

* [概述](#section0)
* [使用场景](#section1)
* [使用限制](#section2)

*展开导读*

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [消息通信](https://support.huaweicloud.com/usermanual-iothub/iot_01_0045_1.html)/ [自定义Topic通信](https://support.huaweicloud.com/usermanual-iothub/iot_02_9992.html)/ 自定义Topic通信概述

链接复制成功！

自定义Topic通信概述
============

#### 概述

使用MQTT协议接入的设备，平台和设备之间基于Topic进行通信。Topic分为系统Topic和自定义Topic。系统Topic为平台预置的基本通信Topic，自定义Topic是可以根据实际业务需要用户自行定义的Topic，客户可根据使用场景进行选择使用。值得注意的是，自定义Topic与系统Topic的消息上报一样，在平台都进行透传（平台不主动解析数据具体内容）。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

2025年08月31日后新用户不再提供自定义Topic进行topic校验的功能，推荐使用设备topic策略进行设备topic管理，详细请参考[设备Topic策略概述](https://support.huaweicloud.com/usermanual-iothub/iot_01_1111.html)。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表1** topic分类

| Topic类别 | 描述 | 使用场景 |
| --- | --- | --- |
| 系统Topic | 平台预先定义了各种设备和平台通信的Topic，具体Topic列表和功能说明可参考[Topic定义](https://support.huaweicloud.com/api-iothub/iot_06_v5_3004.html)。 | 消息上报、属性上报、命令下发、事件类主题。 |
| 自定义Topic | 用户可以自定义Topic，设备和平台间可以基于用户自定义的Topic进行通信。  **自定义topic分类：**   * [$oc开头的自定义Topic](https://support.huaweicloud.com/usermanual-iothub/iot_02_9998.html)：在产品中定义需要使用的Topic，这类Topic有$oc/devices/{device\_id}/user/前缀，消息上报或者消息下发时平台会校验Topic是否在产品中定义，未在产品中定义的Topic会被平台拒绝。  * [非$oc开头的自定义Topic](https://support.huaweicloud.com/usermanual-iothub/iot_02_9999.html)：如/aircondition/data/up进行消息通信，平台会通过[Topic策略](https://support.huaweicloud.com/usermanual-iothub/iot_01_1110.html)校验主题权限，可以用于进行Topic的消息上下行通信。 | 在业务需要特定Topic的场景。比如说[端到端通信](https://support.huaweicloud.com/usermanual-iothub/iot_02_9993.html)、[广播通信](https://support.huaweicloud.com/usermanual-iothub/iot_01_00123.html)、设备迁移等。 |

#### 使用场景

* 设备端向自定义Topic发布消息；应用端通过[数据转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_0024.html)功能实现数据平滑流转至消息中间件、存储、数据分析、业务应用。
* 应用端调用[下发设备消息](https://support.huaweicloud.com/api-iothub/iot_06_v5_0059.html)接口，向指定的自定义Topic发布消息。设备通过订阅该Topic，接收来自服务端的消息。
* [端到端通信](https://support.huaweicloud.com/usermanual-iothub/iot_02_9993.html)、[广播通信](https://support.huaweicloud.com/usermanual-iothub/iot_01_00123.html)、设备迁移。

#### 使用限制

* 每个产品模型最多支持50个自定义Topic。
* 自定义Topic只支持消息通信，不支持属性通信。
* MQTT自定义Topic支持的最大长度为128字节。

#### 相关文档

* [MQTT场景--使用MQTT.fx接入设备发放示例](/usermanual-iothub/iot_03_00012.html)
* [创建产品](/usermanual-iothub/iot_01_0054.html)
* [批量设备OTA升级](/usermanual-iothub/iot_01_01553.html)
* [JT808协议说明](/usermanual-iothub/iot_01_0142.html)
* [和其他服务的关系](/usermanual-iothub/iot_02_0003.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)