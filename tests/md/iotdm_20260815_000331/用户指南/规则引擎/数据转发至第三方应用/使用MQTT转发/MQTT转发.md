# MQTT转发

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00111.html
> **提取时间**: 2026-08-15T00:05:34.838115
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [规则引擎](https://support.huaweicloud.com/usermanual-iothub/iot_01_0021.html)/ [数据转发至第三方应用](https://support.huaweicloud.com/usermanual-iothub/iot_01_1000.html)/ [使用MQTT转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_00110.html)/ MQTT转发

链接复制成功！

MQTT转发
======

订阅推送的示意图如下图所示：

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001504731488.png "点击放大")

**推送机制**：物联网平台向用户推送Qos0的消息，如果用户未建链或者建链后未订阅Topic，服务端仅保存24小时以内，且占用磁盘容量小于1GB的数据，若用户超过24小时没有拉取数据，则平台会清理所有积压数据。

#### 如何进行数据订阅

1. 在物联网平台创建规则、添加转发目标为MQTT消息队列后实现数据订阅，详情请参考[配置MQTT服务端](https://support.huaweicloud.com/usermanual-iothub/iot_01_00112.html)。
2. 通过调用API接口进行数据订阅。通过API接口进行数据订阅请参考[如何调用API](https://support.huaweicloud.com/api-iothub/iot_06_v5_0004.html)、[创建规则触发条件](https://support.huaweicloud.com/api-iothub/iot_06_v5_01307.html)、[创建规则动作](https://support.huaweicloud.com/api-iothub/iot_06_v5_01302.html)和[修改规则触发条件](https://support.huaweicloud.com/api-iothub/iot_06_v5_01309.html)。

#### 推送数据格式

数据订阅成功后，物联网平台推送到应用侧的数据格式样例请参考[数据流转](https://support.huaweicloud.com/api-iothub/iot_06_v5_01200.html)。

#### 使用限制

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 描述 | 限制 |
| --- | --- |
| 支持的MQTT协议版本 | 3.1.1 |
| 与标准MQTT协议的区别 | * 支持Qos 0 * 支持Topic自定义 * 支持共享订阅 * 不支持QoS1，QoS2 * 不支持will、retain msg * 不支持客户端Publish |
| MQTTS支持的安全等级 | 采用TCP通道基础 + TLS协议（TLSV1.2、TLSV1.3），国密企业版实例支持GMTLS协议。  支持的加密套件列表：   * TLS\_AES\_256\_GCM\_SHA384 * TLS\_AES\_128\_GCM\_SHA256 * TLS\_ECDHE\_RSA\_WITH\_AES\_128\_GCM\_SHA256 * TLS\_ECDHE\_RSA\_WITH\_AES\_256\_GCM\_SHA384 * TLS\_ECDHE\_ECDSA\_WITH\_AES\_256\_GCM\_SHA384 * TLS\_ECDHE\_ECDSA\_WITH\_AES\_128\_GCM\_SHA256   国密企业版支持的加密套件列表：   * ECC\_SM4\_GCM\_SM3 * ECDHE\_SM4\_GCM\_SM3 * TLS\_ECDHE\_ECDSA\_WITH\_AES\_256\_GCM\_SHA384 * TLS\_ECDHE\_RSA\_WITH\_AES\_256\_GCM\_SHA384 * TLS\_ECDHE\_ECDSA\_WITH\_AES\_128\_GCM\_SHA256 * TLS\_ECDHE\_RSA\_WITH\_AES\_128\_GCM\_SHA256 |
| 单账号每秒最大MQTT连接请求数 | 10个 |
| 单个账号支持的最大MQTT连接数 | 10个/接入凭证 |
| 单个MQTT连接每秒最大推送速率 | 1000TPS |
| 消息最大缓存时长及大小 | 最大时长1天，最大消息量1GB，以最先到达的限制为准。例如，缓存时长超过1天即使没达到1GB也不会缓存。 |
| MQTT连接心跳时间建议值 | 心跳时间限定为30秒至1200秒，推荐设置为120秒。 |
| 消息发布与订阅 | * 支持共享订阅，订阅同一Topic的客户端轮询消费推送数据，客户端只能订阅流转规则中创建的Topic。 * 不支持消息发布。 |
| 每个订阅请求的最大订阅数 | 同账号的最大Topic数一致。 |
| 每个账号可订阅的Topic数（在创建规则动作时创建） | 100 |

#### 相关文档

* [HJ212协议说明](/usermanual-iothub/iot_01_0140.html)
* [证书策略](/usermanual-iothub/iot_01_0100.html)
* [使用前必读](/usermanual-iothub/iot_03_0001.html)
* [Python SDK接入示例](/usermanual-iothub/iot_01_00100_7.html)
* [设备策略使用示例](/usermanual-iothub/iot_01_1113.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)