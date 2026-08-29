# LwM2M/CoAP协议接入

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_0138.html
> **提取时间**: 2026-08-15T00:04:10.032538
> **云提供商**: HUAWEI

*本文导读*

* [概述](#section0)
* [使用限制](#section1)
* [调用说明](#section2)

*展开导读*

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0127.html)/ [开放协议接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0126.html)/ LwM2M/CoAP协议接入

链接复制成功！

LwM2M/CoAP协议接入
==============

#### 概述

LwM2M（Lightweight M2M，轻量级M2M），由开发移动联盟（OMA）提出，是一种轻量级的、标准通用的物联网设备管理协议，可用于快速部署客户端/服务器模式的物联网业务。LwM2M为物联网设备的管理和应用建立了一套标准，它提供了轻便小巧的安全通信接口及高效的数据模型，以实现M2M设备管理和服务支持。物联网平台支持加密与非加密两种接入设备接入方式，其中加密业务数据交互端口为5684端口，采用DTLS+CoAP协议通道接入，非加密端口为5683，接入协议为CoAP。物联网平台从安全角度考虑，强烈建议采用安全接入方式。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

LwM2M的语法和接口细节，请以此[标准规范](https://openmobilealliance.org/release/LightweightM2M/V1_1-20171208-C/)为准。

物联网平台支持协议规定的plain text, opaque, Core Link ,TLV , JSON编码格式。在多字段操作时（比如写多个资源），默认用TLV格式。

#### 使用限制

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表1** 使用限制

| 描述 | 限制 |
| --- | --- |
| 支持的LwM2M协议版本 | 1.1 |
| 支持的DTLS版本 | DTLS 1.2 |
| 支持的加密算法套件 | TLS\_PSK\_WITH\_AES\_128\_CCM\_8，TLS\_PSK\_WITH\_AES\_128\_CBC\_SHA256 |
| 支持的body体最大长度 | 1KB |
| 接口规格说明 | 请参考[产品规格说明](https://support.huaweicloud.com/productdesc-iothub/iot_04_0014.html)。 |

#### 调用说明

物联网平台的Endpoint请参见：[平台接入地址](https://support.huaweicloud.com/iothub_faq/iot_faq_01006.html)。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

使用“设备接入-> CoAP (5683)| CoAPS (5684)”对应的Endpoint，端口为5683（非加密接入方式）或者5684（加密接入方式）。

#### 相关文档

* [规则引擎](/usermanual-iothub/iot_01_0021.html)
* [设备策略使用示例](/usermanual-iothub/iot_01_1113.html)
* [广播通信](/usermanual-iothub/iot_01_00123.html)
* [MQTT场景--使用MQTT.fx接入设备发放示例](/usermanual-iothub/iot_03_00012.html)
* [创建产品](/usermanual-iothub/iot_01_0054.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)