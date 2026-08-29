# 设备Topic策略使用前必读

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_1114.html
> **提取时间**: 2026-08-15T00:04:44.356849
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [消息通信](https://support.huaweicloud.com/usermanual-iothub/iot_01_0045_1.html)/ [设备Topic策略](https://support.huaweicloud.com/usermanual-iothub/iot_01_1110.html)/ 设备Topic策略使用前必读

链接复制成功！

设备Topic策略使用前必读
==============

设备策略主要用于对发布/订阅的非$oc开头自定义topic中的数据进行传输限制。能够管理客户端发布/订阅主题的授权。借助策略功能，可以保证非$oc开头的自定义Topic的通信安全。设备Topic策略用于发布、订阅机制的协议，比如说设备侧的MQTT、MQTTS协议。

#### 策略通配符

策略中具有不同的通配符，使用前需注意。在策略中，“\*”表示字符的任意组合，问号“? ”表示任何单个字符，而通配符“+”和“#”被视为没有特殊含义的字符。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表1** 策略通配符

| 通配符 | 是MQTT通配符 | 策略配置是否适用 | MQTT中主题示例 | 适用于MQTT主题示例的策略示例 |
| --- | --- | --- | --- | --- |
| # | 是 | 否 | test/# | 不适用，“#”被视为没有特殊含义的字符。 |
| + | 是 | 否 | test/+/some | 不适用，“+”被视为没有特殊含义的字符。 |
| \* | 否 | 是 | 不适用，“\*”被视为没有特殊含义的字符。 | test/\*  test/\*/some |
| ？ | 否 | 是 | 不适用，“？”被视为没有特殊含义的字符。 | test/????/some  test/set?????/some |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表2** 定义策略通配符示例

| 发布/订阅的Topic | 策略Topic定义 | 解释 |
| --- | --- | --- |
| 假设设备需要订阅/发布以下Topic:  “test/topic1/some”  “test/topic2/some”  “test/topic3/some” | “topic:test/topic?/some” | 在发布、订阅的Topic中可以发现有共同点：“test/topic”+ 某一字符 + “/some”，而在策略定义中“?”代表某一字符。所以策略Topic可以定义为“topic:test/topic?/some” |
| 假设设备需要订阅/发布以下Topic:  “test/topic1/pub/some”  “test/topic2/sub/some”  “test/topic3/some” | “topic:test/topic\*/some” | 在发布、订阅的Topic中可以发现有共同点：“test/topic”+ 一个或多个字符 + “/some”，而在策略定义中“\*”代表多个或一个字符。所以策略Topic可以定义为“topic:test/topic\*/some” |

#### 策略变量

在策略中定义resource时，如果不知道对设备资源或条件键的精确值，可以使用策略变量作为占位符，进行发布/订阅主题筛选。策略变量在校验MQTT的主题时，会把变量变为接入设备对应的ID值，再进行匹配。

变量使用前缀“$”标记，后面跟一对大括号“{ }”，其中包含请求中值的变量名称。如下表，假设MQTT设备是在客户端ID为test\_clientId，产品ID为test\_productId，设备ID为test\_deviceId。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表3** 策略变量

| 策略变量 | 描述 | MQTT中主题示例 | 适用于MQTT主题示例的策略示例 |
| --- | --- | --- | --- |
| ${devices.deviceId} | 设备ID | test/test\_deviceId/topic | test/${devices.deviceId}/topic |
| ${devices.clientId} | 客户端ID | test/test\_clientId/topic | test/${devices.clientId}/topic |
| ${devices.productId} | 产品ID | test/test\_productId/topic | test/${devices.productId}/topic |

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表4** 定义策略变量示例

| 场景 | 策略Topic定义示例 | 描述 |
| --- | --- | --- |
| 想通过topic区分不同设备的自定义上报时。 | “test/${devices.deviceId}/topic” | 允许Topic为“test/${本设备ID}/topic”的主题订阅或发布。有利于设备间数据隔离。 |
| 想通过topic区分不同设备的自定义上报、区分同一设备不同时间段上报的数据时。 | “test/${devices.clientId}/topic” | 允许Topic为“test/${本设备的clientId}/topic”的主题订阅或发布。与deviceId不同的是，clientId携带时间戳。可用主题来区分时间段。 |

#### 策略优先级

当某个设备绑定的策略中有多个匹配且Effect不同时，具有优先级：拒绝 > 允许。

例如：某设备同时具有策略一、策略二两个策略，策略一拒绝订阅TopicA，策略二允许订阅TopicA，当该设备订阅TopicA时，平台会拒绝设备的订阅请求。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表5** 策略优先级

| 订阅/发布主题 | 策略一 | 策略二 | 策略匹配结果 |
| --- | --- | --- | --- |
| test/topic | "effect": "ALLOW",  "resources": ["topic:test/topic" ] | "effect": "DENY",  "resources": ["topic:test/topic" ] | 拒绝 |

#### 策略主题基础检查

1. 长度不超过128字节。
2. 发布（publish）不允许使用topic通配符“#”、“+”。
3. 主题中“/”分隔符不超过7个。

#### 相关文档

* [批量注册设备](/usermanual-iothub/iot_01_0032.html)
* [查看运行日志（旧版）](/usermanual-iothub/iot_01_0030_4.html)
* [资源空间](/usermanual-iothub/iot_01_0006.html)
* [设备Topic策略](/usermanual-iothub/iot_01_1110.html)
* [HTTPS协议鉴权](/usermanual-iothub/iot_01_0218.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)