# MQTT客户端接入说明

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00113.html
> **提取时间**: 2026-08-15T00:05:33.424380
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [规则引擎](https://support.huaweicloud.com/usermanual-iothub/iot_01_0021.html)/ [数据转发至第三方应用](https://support.huaweicloud.com/usermanual-iothub/iot_01_1000.html)/ [使用MQTT转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_00110.html)/ MQTT客户端接入说明

链接复制成功！

MQTT客户端接入说明
===========

在调用[创建规则触发条件](https://support.huaweicloud.com/api-iothub/iot_06_v5_01307.html)、[创建规则动作](https://support.huaweicloud.com/api-iothub/iot_06_v5_01302.html)和[修改规则触发条件](https://support.huaweicloud.com/api-iothub/iot_06_v5_01309.html)配置并激活规则后，您需要参考本文将MQTT客户端接入物联网平台，成功接入后，在您的服务端运行MQTT客户端，即可接收订阅的消息。

#### 连接配置说明

MQTT客户端接入物联网平台的连接地址和连接认证参数说明如下：

* MQTT接入域名

  每个账号会自动生成，请前往[管理控制台](https://console.huaweicloud.com/iotdm/#/dm-portal/home)-接入信息页面获取。

  **图1** 接入信息-应用侧MQTT接入地址   
  ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002252955404.png "点击放大")
* 端口：8883
* 客户端身份认证参数

  clientId：全局唯一即可，建议使用“username”。

  username =“accessKey=${accessKey}|timestamp=${timestamp}|instanceId=${instanceId}”

  password =“${accessCode}”

  ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

  | 参数 | 是否必须 | 说明 |
  | --- | --- | --- |
  | ${accessKey} | 是 | **参数说明：**接入凭证键值，单个键值最多允许10个客户端同时进行建链。 首次建链时候，请参考[获取AMQP接入凭证](https://support.huaweicloud.com/usermanual-iothub/iot_01_00100_2.html#ZH-CN_TOPIC_0267714241__section7857181216612)进行预置。 |
  | ${timestamp} | 否 | **参数说明：**客户端传递当前时间的13位毫秒级时间戳。  如果传递该参数，服务端会校验该时间戳与服务器时间的差值，若超过5分钟则视为无效请求。 |
  | instanceId | 否 | **参数说明：**实例Id，同一Region购买多个标准版实例时需要填设置该参数，实例Id参考这里[查看实例](https://support.huaweicloud.com/usermanual-iothub/iot_01_0079.html#ZH-CN_TOPIC_0262066193__section15214114810410)获取。 |
  | ${accessCode} | 是 | **参数说明：**接入凭证密钥，长度不超过256个。 |

#### 获取MQTT接入凭证

若应用使用MQTT协议接入物联网平台进行数据流转需要使用接入凭证，首次使用或者忘记接入凭证请先预置接入凭证。您可以通过调用[生成接入凭证](https://support.huaweicloud.com/api-iothub/iot_06_v5_0111.html)接口预置，也可以前往控制台页面进行预置，详细方法请参考如下操作：

1. 访问[设备接入服务](https://www.huaweicloud.com/product/iothub.html)，单击“管理控制台”进入设备接入控制台。选择您的实例，单击实例卡片进入。
2. 选择“规则>数据转发”进入“规则列表”页面。

   **图2** 规则详情-数据转发规则   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001950384052.png "点击放大")
3. 单击“详情”(如果没有规则请先创建规则)进入规则详情页面后切换到“设置转发目标”。

   **图3** 转发目标-进入设置转发目标   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001983499269.png "点击放大")
4. 单击“添加”进入添加转发目标页面，设置转发目标为“MQTT推送消息队列”，单击“预置服务接入凭证”预置接入凭证密钥（access\_code）和接入凭证键值（access\_key）。

   **图4** 新建转发目标-转发至MQTT推送消息队列预置凭证   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002356493485.png "点击放大")

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   如果您之前预置过接入凭证，重新预置之后，之前的接入凭证密钥将不能再使用。

#### 接收平台推送的消息

客户端和平台之间建链成功后，订阅数据流转规则中MQTT通道中的Topic，设备上报数据后触发流转规则，平台就会把流转数据推送至MQTT客户端。

#### 相关文档

* [属性下发](/usermanual-iothub/iot_01_0335.html)
* [JT808协议接入](/usermanual-iothub/iot_01_0131.html)
* [数据转发至OBS长期存储](/usermanual-iothub/iot_bp_0001.html)
* [LwM2M/CoAP协议接入](/usermanual-iothub/iot_01_0138.html)
* [MQTT(S)协议接入](/usermanual-iothub/iot_01_0128.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)