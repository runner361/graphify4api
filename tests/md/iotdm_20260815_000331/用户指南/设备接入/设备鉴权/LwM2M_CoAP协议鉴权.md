# LwM2M/CoAP协议鉴权

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_0208.html
> **提取时间**: 2026-08-15T00:04:00.886497
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0127.html)/ [设备鉴权](https://support.huaweicloud.com/usermanual-iothub/iot_01_0019.html)/ LwM2M/CoAP协议鉴权

链接复制成功！

LwM2M/CoAP协议鉴权
==============

#### 概述

LwM2M/CoAP协议鉴权支持加密与非加密两种接入方式，若设备采用非加密方式接入时，非加密端口为5683，在设备接入物联网平台时携带设备唯一标识nodeId，完成设备的接入鉴权；当设备采用加密方式接入时，加密业务数据交互端口为5684，使用DTLS/DTLS+传输层安全协议通道接入，并携带nodeId和密钥以完成设备的接入鉴权。

#### 使用LwM2M/CoAP协议接入的鉴权流程

**图1** LwM2M/CoAP协议接入鉴权流程图   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001966892377.png "点击放大")

1. 通过调用注册接口向物联网平台发送注册请求或者在控制台上注册设备。
2. 物联网平台向设备分配密钥，返回timeout。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   * 密钥可以在注册设备时自定义，如果没有定义，平台将自动分配预置密钥。
   * timeout是指超时时间，若设备在有效时间未接入物联网平台，则平台会删除该设备的注册信息。
3. 设备登录时，安全设备携带设备唯一标识码nodeId（如IMEI）和密钥发起接入鉴权请求；非安全设备携带设备唯一标识码nodeId发起接入鉴权请求。
4. 平台验证通过后，返回成功响应，设备连接物联网平台成功。

[上一篇：概述](https://support.huaweicloud.com/usermanual-iothub/iot_01_0206.html)

[下一篇：HTTPS协议鉴权](https://support.huaweicloud.com/usermanual-iothub/iot_01_0218.html)

#### 相关文档

* [概述](/usermanual-iothub/iot_01_0045_2.html)
* [数据转发积压策略配置](/usermanual-iothub/iot_01_0038.html)
* [部署插件](/usermanual-iothub/iot_01_0134.html)
* [群组和标签](/usermanual-iothub/iot_01_0020.html)
* [通过IAM进行授权](/usermanual-iothub/iot_01_0200.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)