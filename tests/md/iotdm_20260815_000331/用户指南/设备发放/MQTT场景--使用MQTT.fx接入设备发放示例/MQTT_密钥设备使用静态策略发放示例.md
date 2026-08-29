# MQTT 密钥设备使用静态策略发放示例

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_03_0006.html
> **提取时间**: 2026-08-15T00:06:12.523982
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备发放](https://support.huaweicloud.com/usermanual-iothub/iot_01_0091.html)/ [MQTT场景--使用MQTT.fx接入设备发放示例](https://support.huaweicloud.com/usermanual-iothub/iot_03_00012.html)/ MQTT 密钥设备使用静态策略发放示例

链接复制成功！

MQTT 密钥设备使用静态策略发放示例
===================

#### 获取设备发放终端节点

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

**表1** 设备发放节点列表

| 区域名称 | 区域 | 终端节点（Endpoint） | 端口 | 协议 |
| --- | --- | --- | --- | --- |
| 华北-北京四 | cn-north-4 | iot-bs.cn-north-4.myhuaweicloud.com | 8883 | MQTTS |

#### 整体流程

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001190554446.png "点击放大")

#### 添加静态策略

添加静态策略，根据关键字发放到指定的IoTDA。

**图1** 创建静态策略   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001836024129.png "点击放大")

**图2** 创建静态策略详情   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001789390626.png "点击放大")

#### 注册设备

在设备发放控制台，注册MQTT设备，其中安全模式选择密钥模式（如果需要下发初始化配置，那么对应在初始设备配置选项中填写对应的JSON字符串，设备发放不理解该字段，只是透传该JSON字符串，由设备理解解析。如果不需要下发该字段则不填）。

**图3** 注册设备   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001789384946.png "点击放大")

**图4** 创建密钥模式静态策略设备   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001835987553.png "点击放大")

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

此处注册设备的设备名称需与[添加静态策略](#ZH-CN_TOPIC_0000001899812002__zh-cn_topic_0000001193613315_section18919205314919)步骤的策略实例关键字相匹配，方能触发该静态策略。

#### 连接鉴权

MQTT.fx 是目前主流的MQTT桌面客户端，它支持 Windows, Mac, Linux，可以快速验证是否可以与设备发放服务进行连接并发布或订阅消息。

本文主要介绍 MQTT.fx 如何与华为设备发放交互，其中设备发放服务MQTT的南向接入地址请参考[获取终端节点](#ZH-CN_TOPIC_0000001899812002__zh-cn_topic_0000001193613315_section995782616494)。

1. 下载 [MQTT.fx](https://iotda-document.obs.cn-north-4.myhuaweicloud.com/mqttfx-1.7.1-windows-x64.exe)（默认是64位操作系统，如果是32位操作系统，单击此处下载 [MQTT.fx](https://iotda-document.obs.cn-north-4.myhuaweicloud.com/mqttfx-1.7.1-windows.exe) ），安装MQTT.fx工具。
2. 打开 MQTT.fx 客户端程序，单击“设置”。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001194169437.png "点击放大")
3. 填写 Connection Profile 相关信息和 General 信息。其中General 信息可以用工具默认的参数配置。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001194249319.png "点击放大")
4. 填写 User Credentials 信息。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001148329512.png "点击放大")

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   其中Username 和Password 参数参考[MQTT CONNECT连接鉴权](https://support.huaweicloud.com/usermanual-iothub/iot_03_0003.html#ZH-CN_TOPIC_0000001899812022)参数说明。
5. 选择开启 SSL/TLS，勾选CA certificate file，CA Certificate File指定为物联网平台根证书（请先下载[物联网平台的根证书](https://iodps-file.obs.cn-north-4.myhuaweicloud.com/rootca/composed/huaweicloud-iot-root-ca-list.zip)，解压后，选择其中c或java目录下PEM后缀的文件）的本地路径。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001148169730.png "点击放大")
6. 完成以上步骤后，单击“Apply”和“OK”保存，并在配置文件框中选择刚才创建的文件名，单击“Connect”，当右上角圆形图标为绿色时，说明连接设备发放服务成功，可进行订阅（Subscribe）和消息推送（Publish）操作。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001194169439.png "点击放大")

#### 引导消息订阅

按照[设备接收引导信息](https://support.huaweicloud.com/usermanual-iothub/iot_03_0005.html#ZH-CN_TOPIC_0000001938891469)topic填写对应的topic，单击“Subscribe”进行订阅。订阅成功如下所示：

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001194249321.png "点击放大")

#### 引导请求发布

按照[设备请求引导信息](https://support.huaweicloud.com/usermanual-iothub/iot_03_0004.html#ZH-CN_TOPIC_0000001899971914)topic填写对应的topic，单击“Publish”进行消息推送。

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001148329514.png "点击放大")

#### 接收到引导消息

消息推送成功如下所示，在Subscribe的topic下会返回对应设备的设备接入服务的地址。

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001148169732.png "点击放大")

#### 后续操作

至此，您已完成了设备发放的流程。设备发放已成功将您的设备【**接入IoTDA****所需的必要信息**】预置到了IoTDA实例中。

如您想要体验物联网平台的更多强大功能，您可通过如下步骤完成对IoTDA的后续操作：

1. 取用引导消息中的设备接入地址；
2. 单击Disconnect，断开与设备发放的连接；
3. 将引导信息中的设备接入地址填入MQTT.fx的MQTT Broker Profile Settings中的Broker Address和Broker Port，建立与设备接入的连接；
4. 完成与设备接入的上报数据等业务交互。

您可参考指导：[设备接入 IoTDA> 开发指南> 设备侧开发> 使用MQTT Demo接入> 使用MQTT.fx调测](https://support.huaweicloud.com/devg-iothub/iot_01_2127.html#section3)中的【**上报数据**】和【**进阶体验**】部分。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

得益于设备发放的预置功能，在参考IoTDA指导过程中，您无需再创建产品和设备。

#### 相关文档

* [和其他服务的关系](/usermanual-iothub/iot_02_0003.html)
* [自定义设备侧域名](/usermanual-iothub/iot_01_0089.html)
* [产品介绍](/usermanual-iothub/iot_01_0150.html)
* [使用前必读](/usermanual-iothub/iot_03_0001.html)
* [MQTT场景--使用MQTT.fx接入设备发放示例](/usermanual-iothub/iot_03_00012.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)