# HTTPS协议接入

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00129.html
> **提取时间**: 2026-08-15T00:04:14.226099
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0127.html)/ [开放协议接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0126.html)/ HTTPS协议接入

链接复制成功！

HTTPS协议接入
=========

#### 概述

HTTPS是基于HTTP协议，通过SSL加密的一种安全通信协议。物联网平台支持HTTPS协议通信。

#### 使用限制

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 描述 | 限制 |
| --- | --- |
| 支持的HTTP协议版本 | 支持 Hypertext Transfer Protocol — HTTP/1.0 协议  支持 Hypertext Transfer Protocol — HTTP/1.1 协议 |
| 支持HTTPS协议 | 物联网平台仅支持HTTPS协议，证书下载请参考[证书资源](https://support.huaweicloud.com/devg-iothub/iot_02_1004.html#section3)。 |
| 支持的TLS版本 | TLS 1.2 |
| 支持的body体最大长度 | 1MB |
| 接口规格说明 | 请参考[产品规格说明](https://support.huaweicloud.com/productdesc-iothub/iot_04_0014.html)。 |
| 网关上报子设备属性时一次最大可上报子设备数 | 50 |

#### 调用说明

物联网平台的Endpoint请参见：[平台接入地址](https://support.huaweicloud.com/iothub_faq/iot_faq_01006.html)。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

使用“设备接入-> HTTPS(443)”对应的Endpoint，端口为443。

#### HTTPS设备与物联网平台通信

设备使用HTTPS协议接入平台时，平台和设备通过HTTPS接口调用通信。通过这些接口，平台和设备可以实现设备鉴权、消息上报及属性上报。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 消息类型 | 说明 |
| --- | --- |
| 设备鉴权 | 用于设备获取鉴权信息access\_token。 |
| 设备属性上报 | 用于设备按产品模型中定义的格式将属性数据上报给平台。 |
| 设备消息上报 | 用于设备将自定义数据上报给平台，平台将设备上报的消息转发给应用服务器或华为云其他云服务上进行存储和处理。 |
| 网关批量属性上报 | 用于网关设备将多个子设备的属性数据一次性上报给平台。 |

#### 业务流程

1. 设备接入前，需创建产品（可通过控制台创建或者使用应用侧API[创建产品](https://support.huaweicloud.com/api-iothub/iot_06_v5_0050.html)）。
2. 产品创建完毕后，需注册设备（可通过控制台[注册单个设备](https://support.huaweicloud.com/usermanual-iothub/iot_01_0031.html)或者使用应用侧API[创建设备](https://support.huaweicloud.com/api-iothub/iot_06_v5_0046.html)）。
3. 设备注册完毕后，通过设备鉴权接口获取设备的access\_token。

   **图1** 获取设备access\_token   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001890893606.png "点击放大")
4. 获取到access\_token之后，可以使用消息/属性上报等功能。其中access\_token放于消息头中，下面示例为上报属性：

   **图2** 上报属性   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001891053554.png "点击放大")

   **图3** 上报属性   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001934453293.png "点击放大")

#### HTTP接口介绍

物联网平台的接口如下表所示：

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 接口分类 | API | 接口 | 说明 |
| --- | --- | --- | --- |
| 设备鉴权相关接口 | [设备鉴权接口说明](#ZH-CN_TOPIC_0000001223916920__section5165739217) | /v5/device-auth | 设备鉴权接口，鉴权通过后才能建立设备与平台间的业务处理连接。鉴权成功后平台返回access\_token。调用属性上报、消息上报等其他接口时，都需要携带access\_token信息。如果access\_token超期，需要重新认证设备获取access\_token。如果access\_token未超期重复获取access\_token，原access\_token在未超期前保留30s，30s之后失效。 |
| 设备消息相关接口 | [设备消息上报接口说明](#ZH-CN_TOPIC_0000001223916920__section095265482315) | /v5/devices/{device\_id}/sys/messages/up | 用于设备将自定义数据上报给平台，平台将设备上报的消息转发给应用服务器或华为云其他云服务上进行存储和处理。 |
| 设备属性相关接口 | [设备属性上报接口说明](#ZH-CN_TOPIC_0000001223916920__section1786101112514) | /v5/devices/{device\_id}/sys/properties/report | 用于设备按产品模型中定义的格式将属性数据上报给平台。 |
| [网关上报子设备属性接口说明](#ZH-CN_TOPIC_0000001223916920__section11954238112614) | /v5/devices/{device\_id}/sys/gateway/sub-devices/properties/report | 用于批量设备上报属性数据给平台。网关设备可以用此接口同时上报最多50个子设备的属性数据。 |

#### 设备鉴权接口说明

设备鉴权接口鉴权通过后才能建立设备与平台间的业务处理连接。鉴权成功后平台返回access\_token，调用属性上报、消息上报等其他接口时，都需要携带access\_token信息。如果access\_token超期，需要重新认证设备获取access\_token。如果access\_token未超期重复获取access\_token，原access\_token在未超期前保留30s，30s之后失效。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

|  |  |
| --- | --- |
| 请求方法 | POST |
| URI | /v5/device-auth |
| 传输协议 | HTTPS |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 名称 | 必选 | 类型 | 位置 | 说明 |
| --- | --- | --- | --- | --- |
| device\_id | 是 | String | Body | **参数说明:** 设备ID，用于唯一标识一个设备。在注册设备时直接指定，或者由物联网平台分配获得。由物联网平台分配时，生成规则为"product\_id" + "\_" + "node\_id"拼接而成。  **取值范围****：**长度不超过128，只允许字母、数字、下划线（\_）、连接符（-）的组合。 |
| sign\_type | 是 | Integer | Body | **参数说明:** 密码校验方式: 0 代表HMACSHA256校验时间戳时不会校验消息时间戳与平台时间是否一致，仅判断密码是否正确; 1 代表HMACSHA256校验时间戳时会先校验消息时间戳与平台时间是否一致，再判断密码是否正确。  **取值范围:** 大小0~1 |
| timestamp | 是 | String | Body | **参数说明:** 时间戳：为设备连接平台时的UTC时间，格式为YYYYMMDDHH，如UTC 时间2018/7/24 17:56:20 则应表示为2018072417。  **取值范围:** 固定长度10 |
| password | 是 | String | Body | **参数说明:** password的值为使用“HMACSHA256”算法对secret进行签名后的密钥（以时间戳为key，对平台返回的secret进行签名后的值，参考[密钥生成工具](https://iot-tool.obs-website.cn-north-4.myhuaweicloud.com/)）。secret为注册设备时平台返回的secret。  **取值范围:** 固定长度64 |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 名称 | 类型 | 说明 |
| --- | --- | --- |
| access\_token | String | **参数说明:** 设备token，用于设备鉴权。  **取值范围:** 长度32-256 |
| expires\_in | Integer | **参数说明:** 鉴权信息的剩余有效时间, 单位：秒。 |

请求示例如下：

```
POST https://{endpoint}/v5/device-auth
Content-Type: application/json

{
  "device_id" : "********",
  "sign_type" : 0,
  "timestamp" : "2019120219",
  "password" : "********"
}
```

响应示例如下：

Status Code: 200 OK

```
Content-Type: application/json

{
  "access_token" : "********",
  "expires_in" : 86399
}
```

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| HTTP状态码 | HTTP状态码描述 | 错误码 | 错误码描述 | 错误码中文描述 |
| --- | --- | --- | --- | --- |
| 200 | OK | - | - | - |
| 400 | Bad Request | IOTDA.000006 | Invalid input data. | 请求参数不合法 |
| 401 | Unauthorized | IOTDA.000002 | Authentication failed. | 鉴权失败 |
| 403 | Forbidden | IOTDA.021101 | Request reached the maximum rate limit. | 请求已经达到限制速率 |
| IOTDA.021102 | The request rate has reached the upper limit of the tenant, limit %s. | 请求已经达到租户的限制速率 |

#### 设备消息上报接口说明

用于设备将自定义数据上报给平台，平台将设备上报的消息转发给应用服务器或华为云其他云服务上进行存储和处理。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

|  |  |
| --- | --- |
| 请求方法 | POST |
| URI | /v5/devices/{device\_id}/sys/messages/up |
| 传输协议 | HTTPS |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 名称 | 必选 | 类型 | 位置 | 说明 |
| --- | --- | --- | --- | --- |
| access\_token | 是 | String | Header | **参数说明:** 调用设备鉴权信息返回的access\_token。  **取值范围:** 长度1-256 |
| device\_id | 是 | String | Path | **参数说明:** 设备ID，用于唯一标识一个设备。在注册设备时直接指定，或者由物联网平台分配获得。由物联网平台分配时，生成规则为"product\_id" + "\_" + "node\_id"拼接而成。  **取值范围**：长度不超过128，只允许字母、数字、下划线（\_）、连接符（-）的组合。 |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

该接口支持设备将自定义数据通过请求中的body体上报给平台，平台收到该请求后会将body内容转发给应用服务器或华为云其他云服务上进行存储和处理。平台对body中的内容无具体格式限制，小于1MB的数据可以通过该接口携带。

请求示例如下：

```
POST https://{endpoint}/v5/devices/{device_id}/sys/messages/up
Content-Type: application/json
access_token: ********
{
  "name" : "name",
  "id" : "id",
  "content" : "messageUp"
}
```

响应示例如下：

Status Code: 200 ok

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| HTTP状态码 | HTTP状态码描述 | 错误码 | 错误码描述 | 错误码中文描述 |
| --- | --- | --- | --- | --- |
| 200 | OK | - | - | - |
| 400 | Bad Request | IOTDA.000006 | Invalid input data. | 请求参数不合法 |
| 401 | Unauthorized | IOTDA.000002 | Authentication failed. | 鉴权失败 |
| 403 | Forbidden | IOTDA.000004 | Invalid access token. | 非法token |
| IOTDA.021101 | Request reached the maximum rate limit. | 请求已经达到限制速率 |
| IOTDA.021102 | The request rate has reached the upper limit of the tenant, limit %s. | 请求已经达到租户的限制速率 |

#### 设备属性上报接口说明

用于设备按产品模型中定义的格式将属性数据上报给平台。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

|  |  |
| --- | --- |
| 请求方法 | POST |
| URI | /v5/devices/{device\_id}/sys/properties/report |
| 传输协议 | HTTPS |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 名称 | 必选 | 类型 | 位置 | 说明 |
| --- | --- | --- | --- | --- |
| access\_token | 是 | String | Header | **参数说明:** 调用设备鉴权信息返回的access\_token。  **取值范围:** 长度1-256 |
| device\_id | 是 | String | Path | **参数说明:** 设备ID，用于唯一标识一个设备。在注册设备时直接指定，或者由物联网平台分配获得。由物联网平台分配时，生成规则为"product\_id" + "\_" + "node\_id"拼接而成。  **取值范围**：长度不超过128，只允许字母、数字、下划线（\_）、连接符（-）的组合。 |
| services | 是 | List<[表1](#ZH-CN_TOPIC_0000001223916920__zh-cn_topic_0000001225393069_req-ServiceProperty)> | Body | **参数说明:** 设备服务数据列表。 |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表1** ServiceProperty

| 名称 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| service\_id | 是 | String | **参数说明:** 设备服务id。 |
| properties | 是 | Object | **参数说明:** 设备服务的属性列表，具体字段在设备关联的产品模型中定义。 |
| event\_time | 否 | String | **参数说明:** 设备采集数据UTC时间（格式：yyyy-MM-dd'T'HH:mm:ss.SSS'Z'），设备上报数据不带该参数或参数格式错误时，则数据上报时间以平台时间为准。 |

请求示例如下：

```
POST https://{endpoint}/v5/devices/{device_id}/sys/properties/report
Content-Type: application/json
access_token: ********

{
  "services" : [ {
    "service_id" : "serviceId",
    "properties" : {
      "Height" : 124,
      "Speed" : 23.24
    },
    "event_time" : "2021-08-13T10:10:10.555Z"
  } ]
}
```

响应示例如下：

Status Code: 200 上报正常

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| HTTP状态码 | HTTP状态码描述 | 错误码 | 错误码描述 | 错误码中文描述 |
| --- | --- | --- | --- | --- |
| 200 | OK | - | - | - |
| 400 | Bad Request | IOTDA.000006 | Invalid input data. | 请求参数不合法 |
| IOTDA.021104 | Subdevices in the request does not exist or does not belong to the gateway. | 请求中有部分子设备不存在或不属于该网关. |
| 403 | Forbidden | IOTDA.000004 | Invalid access token. | 非法token |
| IOTDA.021101 | Request reached the maximum rate limit. | 请求已经达到限制速率 |
| IOTDA.021102 | The request rate has reached the upper limit of the tenant, limit %s. | 请求已经达到租户的限制速率 |
| IOTDA.021105 | The content reported in a single request cannot exceed 1 MB. | 单次请求上报的内容不能超过1MB |

#### 网关上报子设备属性接口说明

用于批量设备上报属性数据给平台。网关设备可以用此接口同时上报最多50个子设备的属性数据。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

|  |  |
| --- | --- |
| 请求方法 | POST |
| URI | /v5/devices/{device\_id}/sys/gateway/sub-devices/properties/report |
| 传输协议 | HTTPS |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 名称 | 必选 | 类型 | 位置 | 说明 |
| --- | --- | --- | --- | --- |
| access\_token | 是 | String | Header | **参数说明:** 调用设备鉴权信息返回的access\_token。  **取值范围:** 长度1-256 |
| device\_id | 是 | String | Path | **参数说明:** 设备ID，用于唯一标识一个设备。在注册设备时直接指定，或者由物联网平台分配获得。由物联网平台分配时，生成规则为"product\_id" + "\_" + "node\_id"拼接而成。  **取值范围**：长度不超过128，只允许字母、数字、下划线（\_）、连接符（-）的组合。 |
| devices | 是 | List<[表2](#ZH-CN_TOPIC_0000001223916920__zh-cn_topic_0000001225194513_req-DeviceProperty)> | Body | **参数说明:** 设备数据列表。  **取值范围:** 长度不超过50 |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表2** DeviceProperty

| 名称 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| device\_id | 是 | String | **参数说明:**子设备的设备ID，用于唯一标识一个设备，在注册设备时由物联网平台分配获得。  **取值范围**：长度不超过128，只允许字母、数字、下划线（\_）、连接符（-）的组合。 |
| services | 是 | List<[表3](#ZH-CN_TOPIC_0000001223916920__zh-cn_topic_0000001225194513_req-ServiceProperty)> | **参数说明:** 设备服务数据列表 |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表3** ServiceProperty

| 名称 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| service\_id | 是 | String | **参数说明:** 设备服务id。 |
| properties | 是 | Object | **参数说明:** 设备服务的属性列表，具体字段在设备关联的产品模型中定义。 |
| event\_time | 否 | String | **参数说明:** 设备采集数据UTC时间（格式：yyyy-MM-dd'T'HH:mm:ss.SSS'Z'），设备上报数据不带该参数或参数格式错误时，则数据上报时间以平台时间为准。 |

请求示例如下：

```
POST https://{endpoint}/v5/devices/{device_id}/sys/gateway/sub-devices/properties/report
Content-Type: application/json
access_token: ********

{
  "devices" : [ {
    "device_id" : "deviceId_0001",
    "services" : [ {
      "service_id" : "serviceId",
      "properties" : {
        "Height" : 124,
        "Speed" : 23.24
      },
      "event_time" : "2021-08-13T10:10:10.555Z"
    } ]
  }, {
    "device_id" : "deviceId_0002",
    "services" : [ {
      "service_id" : "serviceId",
      "properties" : {
        "Height" : 124,
        "Speed" : 23.24
      },
      "event_time" : "2021-08-13T10:10:10.555Z"
    } ]
  } ]
}
```

响应示例如下：

Status Code: 200 上报正常

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| HTTP状态码 | HTTP状态码描述 | 错误码 | 错误码描述 | 错误码中文描述 |
| --- | --- | --- | --- | --- |
| 200 | OK | - | - | - |
| 400 | Bad Request | IOTDA.000006 | Invalid input data. | 请求参数不合法 |
| IOTDA.021104 | Subdevices in the request does not exist or does not belong to the gateway. | 请求中有部分子设备不存在或不属于该网关. |
| 401 | Unauthorized | IOTDA.000002 | Authentication failed. | 鉴权失败 |
| 403 | Forbidden | IOTDA.000004 | Invalid access token. | 非法token |
| IOTDA.021101 | Request reached the maximum rate limit. | 请求已经达到限制速率 |
| IOTDA.021102 | The request rate has reached the upper limit of the tenant, limit %s. | 请求已经达到租户的限制速率 |
| IOTDA.021103 | The number of child devices in the request has reached the upper limit (%s). | 请求中子设备数量达到上限 |
| IOTDA.021105 | The content reported in a single request cannot exceed 1 MB. | 单次请求上报的内容不能超过1MB |

#### 相关文档

* [部署插件](/usermanual-iothub/iot_01_0136.html)
* [设备鉴权](/usermanual-iothub/iot_01_0019.html)
* [Python SDK接入示例](/usermanual-iothub/iot_01_00100_7.html)
* [数据转发积压策略配置](/usermanual-iothub/iot_01_0038.html)
* [部署插件](/usermanual-iothub/iot_01_0134.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)