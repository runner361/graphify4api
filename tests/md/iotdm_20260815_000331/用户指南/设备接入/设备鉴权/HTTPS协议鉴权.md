# HTTPS协议鉴权

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_0218.html
> **提取时间**: 2026-08-15T00:04:02.399865
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0127.html)/ [设备鉴权](https://support.huaweicloud.com/usermanual-iothub/iot_01_0019.html)/ HTTPS协议鉴权

链接复制成功！

HTTPS协议鉴权
=========

#### 概述

HTTPS协议鉴权是指设备通过调用HTTPS协议设备鉴权接口并携带设备ID和使用算法加密后的密钥，以完成设备的接入鉴权。鉴权成功后可以建立设备与平台间的连接，并且平台会返回用于业务处理的access\_token。

#### 约束与限制

* 在调用属性上报、消息上报等其他HTTPS协议接口时，都需要携带access\_token信息。
* 如果access\_token超期，需要重新认证设备获取access\_token。
* 如果access\_token未超期重复获取access\_token，原access\_token在未超期前保留30s，30s之后失效。

#### 使用HTTPS协议接入的鉴权流程

**图1** HTTPS协议接入鉴权流程图   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001938615748.png "点击放大")

1. 通过调用注册接口向物联网平台发送注册请求或者在控制台上注册设备。
2. 物联网平台向设备分配全局唯一的设备ID （deviceId）和密钥（secret）。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   密钥可以在注册设备时自定义，如果没有定义，平台将自动分配密钥
3. 设备登录时，调用HTTPS协议设备鉴权接口并携带设备ID和使用“HMACSHA256”算法签名后的密钥（以时间戳为key，对平台分配的密码进行签名后的值，参考[密钥生成工具](https://iot-tool.obs-website.cn-north-4.myhuaweicloud.com/)），向平台发起接入鉴权请求。
4. 平台验证通过后，返回成功响应，设备连接物联网平台成功。

#### 相关文档

* [HTTPS协议接入](/usermanual-iothub/iot_01_00129.html)
* [$oc开头自定义Topic通信使用说明](/usermanual-iothub/iot_02_9998.html)
* [设备高级搜索](/usermanual-iothub/iot_01_0111.html)
* [自定义模板示例](/usermanual-iothub/iot_01_0235.html)
* [AMQP转发](/usermanual-iothub/iot_01_0003.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)