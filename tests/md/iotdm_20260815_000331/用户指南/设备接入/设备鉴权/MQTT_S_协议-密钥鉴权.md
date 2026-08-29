# MQTT(S)协议-密钥鉴权

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_0210.html
> **提取时间**: 2026-08-15T00:04:01.858375
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0127.html)/ [设备鉴权](https://support.huaweicloud.com/usermanual-iothub/iot_01_0019.html)/ MQTT(S)协议-密钥鉴权

链接复制成功！

MQTT(S)协议-密钥鉴权
==============

#### 概述

MQTT(S)协议-密钥鉴权是指设备在接入物联网平台时，携带设备ID和密钥以完成设备的接入鉴权。对于使用MQTTS协议接入的设备，需要在设备侧预置CA证书；对于使用MQTT非安全协议接入的设备，无需在设备侧预置CA证书。

#### 使用MQTT(S)协议-密钥接入的鉴权流程

**图1** MQTT(S)协议-密钥接入鉴权流程图   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001939765472.png "点击放大")

1. 通过调用注册接口向物联网平台发送注册请求或者在控制台上注册设备。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   注册时需要填写设备标识码，通常使用MAC地址，Serial No或IMEI作为nodeId。
2. 物联网平台向设备分配全局唯一的设备ID （deviceId）和密钥（secret）。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   密钥可以在注册设备时自定义，如果没有定义，平台将自动分配密钥。
3. 设备侧需集成预置CA证书[获取CA证书](https://support.huaweicloud.com/devg-iothub/iot_02_1004.html#section3)（仅针对MQTTS协议接入的鉴权流程）。
4. 设备登录时，携带设备ID（deviceId）和密钥（secret）发起接入鉴权请求。
5. 平台验证通过后，返回成功响应，设备连接物联网平台成功。

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