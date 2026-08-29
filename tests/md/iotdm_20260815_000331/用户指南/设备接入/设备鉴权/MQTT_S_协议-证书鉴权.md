# MQTT(S)协议-证书鉴权

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_0211.html
> **提取时间**: 2026-08-15T00:04:03.189869
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备接入](https://support.huaweicloud.com/usermanual-iothub/iot_01_0127.html)/ [设备鉴权](https://support.huaweicloud.com/usermanual-iothub/iot_01_0019.html)/ MQTT(S)协议-证书鉴权

链接复制成功！

MQTT(S)协议-证书鉴权
==============

#### 概述

MQTT(S)协议-证书鉴权是指在设备接入物联网平台前，用户通过控制台上传设备的CA证书，然后应用服务调用[创建设备](https://support.huaweicloud.com/api-iothub/iot_06_v5_0046.html)接口或通过控制台在物联网平台注册设备，获取设备ID。在设备接入物联网平台时携带设备侧X.509证书（一种用于通信实体鉴别的数字证书），完成设备的接入鉴权。

#### 约束与限制

* 当前物联网平台只支持基于MQTT协议接入的设备使用X.509证书进行设备身份认证。
* 每个用户最多上传100个CA证书。

#### 使用MQTT(S)协议-证书接入的鉴权流程

**图1** MQTT(S)协议-证书接入鉴权流程图   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001967039145.png "点击放大")

1. 在控制台上传设备CA证书。
2. 通过调用注册接口向物联网平台发送注册请求或者在控制台上注册设备。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   注册时需要填写设备标识码，通常使用MAC地址，Serial No或IMEI作为nodeId。
3. 物联网平台向设备分配全局唯一的设备ID（deviceId）。
4. 设备登录时，携带设备侧[X.509证书](https://support.huaweicloud.com/usermanual-iothub/iot_01_0055.html#section4)发起接入鉴权请求。
5. 平台验证通过后，返回成功响应，设备连接物联网平台成功。

#### 相关API接口

* [创建设备](https://support.huaweicloud.com/api-iothub/iot_06_v5_0046.html)
* [重置设备密钥](https://support.huaweicloud.com/api-iothub/iot_06_v5_0093.html)
* [获取CA证书列表](https://support.huaweicloud.com/api-iothub/iot_06_v5_0099.html)
* [上传CA证书](https://support.huaweicloud.com/api-iothub/iot_06_v5_0014.html)
* [删除CA证书](https://support.huaweicloud.com/api-iothub/iot_06_v5_0022.html)
* [验证CA证书](https://support.huaweicloud.com/api-iothub/iot_06_v5_0016.html)

#### 相关文档

* [管理设备](/usermanual-iothub/iot_01_0065.html)
* [设备数据上报](/usermanual-iothub/iot_01_0045.html)
* [MQTT 密钥设备使用静态策略发放](/usermanual-iothub/iot_03_00015.html)
* [使用前必读](/usermanual-iothub/iot_03_0001.html)
* [Python SDK接入示例](/usermanual-iothub/iot_01_00100_7.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)