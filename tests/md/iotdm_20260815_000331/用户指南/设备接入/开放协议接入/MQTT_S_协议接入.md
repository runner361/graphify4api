# MQTT(S)协议接入

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_0128.html
> **提取时间**: 2026-08-15T00:04:13.015611
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0127.html)/ [开放协议接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0126.html)/ MQTT(S)协议接入

链接复制成功！

MQTT(S)协议接入
===========

#### 概述

MQTT消息由固定报头（Fixed header）、可变报头（Variable header）和有效载荷（Payload）三部分组成。

其中固定报头（Fixed header）和可变报头（Variable header）格式的填写请参考[MQTT标准规范](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/)，有效载荷（Payload）的格式（须使用UTF-8编码格式）由应用定义，即由设备和物联网平台之间定义。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

MQTT的语法和接口细节，请以[MQTT标准规范](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/)为准。

常见MQTT消息类型主要有CONNECT、SUBSCRIBE、PUBLISH。

* CONNECT：指客户端发起与服务端的连接请求。有效载荷（Payload）的主要参数，参考[MQTT设备连接鉴权](https://support.huaweicloud.com/api-iothub/iot_06_v5_3009.html)填写。
* SUBSCRIBE：指客户端发起订阅的请求。有效载荷（Payload）中的主要参数“Topic name”，参考[Topic定义](https://support.huaweicloud.com/api-iothub/iot_06_v5_3004.html)中订阅者为设备的Topic。
* PUBLISH：平台发布消息。
  + 可变报头（Variable header）中的主要参数“Topic name”，指当设备上报到物联网平台，发布者为设备时所对应的Topic。详细请参考[Topic定义](https://support.huaweicloud.com/api-iothub/iot_06_v5_3004.html)。
  + 有效载荷（Payload）中的主要参数为完整的数据上报和命令下发的消息内容，目前是一个JSON对象。

#### Topic说明

设备使用MQTT协议接入时,可通过Topic实现消息的发送和接收。

* 以$oc开头的topic是IoTDA预置的系统topic。您可以在允许的情况下订阅和发布到这些系统预置的Topic；具体Topic列表和功能说明可参考[Topic定义](https://support.huaweicloud.com/api-iothub/iot_06_v5_3004.html)。
* 您可以创建非$oc 开头的topic进行自定义消息的发送和接收。

#### 使用限制

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 描述 | 限制 |
| --- | --- |
| 单个MQTT直连设备在同一时间的连接数 | 1 |
| 单账户设备侧每秒最大建链请求数量 | * 基础版100 * 标准版请参考[标准版规格](https://support.huaweicloud.com/productdesc-iothub/iot_04_0014.html#section2) * 企业版请参考[企业版规格](https://support.huaweicloud.com/productdesc-iothub/iot_04_0014.html#section3) |
| 单账号设备侧每秒最大上行的请求数量（单消息payload平均为512字节） | * 基础版500 * 标准版请参考[标准版规格](https://support.huaweicloud.com/productdesc-iothub/iot_04_0014.html#section2) * 企业版请参考[企业版规格](https://support.huaweicloud.com/productdesc-iothub/iot_04_0014.html#section3) |
| 单个MQTT连接每秒最大上行消息数量 | 50/s |
| 单个MQTT连接最大带宽（上行消息） | 1MB（默认） |
| MQTT单条发布消息最大长度。超过此大小的发布请求将被直接拒绝。 | 1MB |
| MQTT协议规范 | MQTT v5.0、MQTT v3.1.1、MQTT v3.1 |
| 与标准MQTT协议的区别 | * 不支持QoS2 * 不支持will、retain msg |
| MQTT协议支持的安全等级 | 采用TCP通道基础 + TLS协议（TLSv1、 TLSv1.1、TLSv1.2和TLSv1.3版本） |
| MQTT连接心跳时间建议值 | 心跳时间限定为30至1200秒，推荐设置为120秒 |
| MQTT协议消息发布与订阅 | 设备只能对自己的Topic进行消息发布与订阅 |
| 单个MQTT连接的最大订阅数量。 | 100个 |
| MQTT自定义Topic支持的最大长度 | 128字节 |
| MQTT自定义Topic支持每个产品添加的最大个数 | 10个/产品 |
| 单账号支持上传设备侧CA证书个数 | 100个 |

#### 与标准MQTT协议的兼容说明

华为云IoTDA服务支持设备基于[MQTT 5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/)、[MQTT 3.1.1](https://mqtt.org/)和 [MQTT 3.1](https://public.dhe.ibm.com/software/dw/webservices/ws-mqtt/mqtt-v3r1.html)规范的接入，但同这些MQTT协议规范有一些差异， IoTDA服务不是简单的MQTT Broker，而是在支持设备使用MQTT协议接入的基础上集成消息通信、设备管理、规则引擎、数据流转等能力。与MQTT标准规范的的区别如下：

* 支持设备与IoTDA服务之间使用MQTT规范中的CONNECT、CONNACK、PUBLISH、PUBACK、SUBSCRIBE、SUBACK、UNSUBSCRIBE、UNSUBACK、PINGREQ、PINGRESP、DISCONNECT等报文进行通信。
* 支持MQTT的服务质量等级为QoS 0、QoS 1，不支持QoS 2。
* 支持MQTT协议规范中的clean session。
* 不支持MQTT协议规范中的will。 IoTDA提供设备状态推送的能力，设备离线后支持根据流转规则将设备状态推送到客户应用或者云服务。
* 不支持MQTT协议规范中retain msg。IoTDA提供消息缓存的能力消息上报和消息下发时支持对消息进行缓存。

#### 支持的MQTT 5.0特性说明

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

MQTT5.0相关特性仅在企业版支持。

IoTDA服务支持的MQTT 5.0的部分新增特性如下：

* 支持Topic Alias。将消息通信Topic缩小为整型数值，来减小MQTT报文，节约网络带宽资源。
* 支持ResponseTopic 和CorrelationData。消息上报和下发时支持携带这两个参数，实现类似云HTTP的请求和响应。
* 支持设置UserProperty属性列表。每个属性由Key和Value组成，用于在非payload区传输属性数据。
* 支持Content-Type属性。消息上报的报文可以携带Content-Type属性，标识报文类型。

* 支持在CONNACK和PUBACK报文中返回码，便于设备快速定位请求状态及问题。

#### MQTT的TLS支持

平台推荐使用TLS来保护设备和平台的传输安全。 平台目前支持TLS1.3、1.2 、1.1版本以及GMTLS。其中TLS 1.1 计划后续不再支持，建议使用 TLS 1.3作为首选 TLS 版本。GMTLS版本仅在国密算法的企业版才支持。

基础版，标准版以及支持通用加密算法的企业版使用TLS连接时，平台支持如下加密套件：

* TLS\_AES\_256\_GCM\_SHA384
* TLS\_AES\_128\_GCM\_SHA256
* TLS\_ECDHE\_RSA\_WITH\_AES\_128\_GCM\_SHA256
* TLS\_ECDHE\_RSA\_WITH\_AES\_256\_GCM\_SHA384
* TLS\_ECDHE\_RSA\_WITH\_AES\_128\_CBC\_SHA
* TLS\_ECDHE\_RSA\_WITH\_AES\_256\_CBC\_SHA

支持国密算法的企业版使用TLS连接时平台支持如下加密套件：

* ECC\_SM4\_GCM\_SM3
* ECDHE\_SM4\_GCM\_SM3
* TLS\_ECDHE\_ECDSA\_WITH\_AES\_256\_GCM\_SHA384
* TLS\_ECDHE\_RSA\_WITH\_AES\_256\_GCM\_SHA384
* TLS\_ECDHE\_ECDSA\_WITH\_AES\_128\_GCM\_SHA256
* TLS\_ECDHE\_RSA\_WITH\_AES\_128\_GCM\_SHA256

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

带CBC的加密套件存在安全风险，请谨慎使用。

#### 业务流程

采用MQTT协议接入物联网平台的设备，设备与物联网平台之间的通信过程，数据没有加密，建议使用MQTTS协议。

若选择MQTTS协议接入平台，建议参考[IoT Device SDK介绍](https://support.huaweicloud.com/sdkreference-iothub/iot_02_0178.html)使用IoT Device SDK接入。

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0263925108.png "点击放大")

1. 设备接入前，需创建产品（可通过控制台创建或者使用应用侧API[创建产品](https://support.huaweicloud.com/api-iothub/iot_06_v5_0050.html)）。
2. 产品创建完毕后，需注册设备（可通过控制台[注册单个设备](https://support.huaweicloud.com/usermanual-iothub/iot_01_0031.html)或者使用应用侧AP[创建设备](https://support.huaweicloud.com/api-iothub/iot_06_v5_0046.html)创建）。
3. 设备注册完毕后，可以按照图中流程实现消息/属性上报、接收命令/属性/消息、OTA升级、自定义Topic等功能。关于平台预置Topic可参考[Topic定义](https://support.huaweicloud.com/api-iothub/iot_06_v5_3004.html)

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

您可以通过mqtt.fx进行原生协议接入调测，可以参考[快速体验mqtt接入](https://support.huaweicloud.com/bestpractice-iothub/iot_bp_00016.html)。

#### 相关文档

* [编解码插件](/usermanual-iothub/iot_02_9990.html)
* [云端数据下发](/usermanual-iothub/iot_01_0051.html)
* [委托授权](/usermanual-iothub/iot_01_0203.html)
* [MQTT 华为云X.509证书认证设备使用证书策略发放示例](/usermanual-iothub/iot_03_0009.html)
* [批量注册设备](/usermanual-iothub/iot_01_0032.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)