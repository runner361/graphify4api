# MQTT 注册组自定义策略发放示例

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_03_0008.html
> **提取时间**: 2026-08-15T00:06:13.348068
> **云提供商**: HUAWEI

更新时间：2026-06-09 GMT+08:00

[查看PDF](https://support.huaweicloud.com/usermanual-iothub/usermanual-iothub-pdf.pdf)

[分享](javascript:void(0);)

* [微博](javascript:void(0);)
* [微信](javascript:void(0);)
* [复制链接](javascript:void(0);)

  复制链接到剪贴板

链接复制成功！

MQTT 注册组自定义策略发放示例
=================

#### 获取设备发放终端节点

**表1** 设备发放节点列表

| 区域名称 | 区域 | 终端节点（Endpoint） | 端口 | 协议 |
| --- | --- | --- | --- | --- |
| 华北-北京四 | cn-north-4 | iot-bs.cn-north-4.myhuaweicloud.com | 8883 | MQTTS |

#### 整体流程

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001189794612.png "点击放大")

#### 制作CA证书

1. 在浏览器中访问[这里](https://slproweb.com/products/Win32OpenSSL.html)，下载并进行安装OpenSSL工具，安装完成后配置环境变量。
2. 在 D:\certificates 文件夹下，以管理员身份运行cmd命令行窗口。
3. 生成密钥对（rootCA.key）：

   ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

   生成“密钥对”时输入的密码在生成“证书签名请求文件”、“CA证书”，“验证证书”以及“设备证书”时需要用到，请妥善保存。

   ```
   openssl genrsa -des3 -out rootCA.key 2048
   ```
4. 使用密钥对生成证书签名请求文件：

   ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

   生成证书签名请求文件时，要求填写证书唯一标识名称（Distinguished Name，DN）信息，参数说明如下[表1](#ZH-CN_TOPIC_0000001938891453__zh-cn_topic_0000001147693376_zh-cn_topic_0000001194787007_table17909204620310) 所示。

   **表2** 证书签名请求文件参数说明

   | **提示** | **参数名称** | **取值样例** |
   | --- | --- | --- |
   | Country Name (2 letter code) []: | 国家/地区 | CN |
   | State or Province Name (full name) []: | 省/市 | GuangDong |
   | Locality Name (eg, city) []: | 城市 | ShenZhen |
   | Organization Name (eg, company) []: | 组织机构（或公司名） | Huawei Technologies Co., Ltd. |
   | Organizational Unit Name (eg, section) []: | 机构部门 | Cloud Dept. |
   | Common Name (eg, fully qualified host name) []: | CA名称（CN） | Huawei IoTDP CA |
   | Email Address []: | 邮箱地址 | / |
   | A challenge password []: | 证书密码，如您不设置密码，可以直接回车 | / |
   | An optional company name []: | 可选公司名称，如您不设置，可以直接回车 | / |

   ```
   openssl req -new -key rootCA.key -out rootCA.csr
   ```
5. 生成CA证书（rootCA.crt）：

   ```
   openssl x509 -req -days 50000 -in rootCA.csr -signkey rootCA.key -out rootCA.crt
   ```

   ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

   “-days”后的参数值指定了该证书的有效天数，此处示例为50000天，您可根据实际业务场景和需要进行调整。

#### 上传并验证CA证书

1. 登录[设备发放控制台](https://console.huaweicloud.com/iotdm/#/dm-portal/iotps/home)，进入“证书”界面，单击右上角“上传CA证书”，填写“证书名称”并上传上述“制作CA证书”步骤后生成的“CA证书（rootCA.crt文件）”，单击“确定”。

   **图1** 上传CA证书   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001835989777.png "点击放大")
2. 验证[步骤1](#ZH-CN_TOPIC_0000001938891453__zh-cn_topic_0000001147693376_zh-cn_topic_0000001193533185_zh-cn_topic_0000001124148879_li394524510241)中上传的CA证书，只有成功验证证书后该证书方可使用。
   1. 为验证证书生成密钥对。

      ```
      openssl genrsa -out verificationCert.key 2048
      ```
   2. 获取随机验证码。

      **图2** 上传CA证书完成页   
      ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001789190628.png "点击放大")

      **图3** 复制验证码   
      ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002322657170.png "点击放大")
   3. 利用此验证码生成证书签名请求文件CSR。

      ```
      openssl req -new -key verificationCert.key -out verificationCert.csr
      ```

      ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

      CSR文件的Common Name (e.g. server FQDN or YOUR name) 需要填写前一过程中获取到的随机验证码。
   4. 使用CA证书、CA证书私钥和CSR文件创建验证证书（verificationCert.crt）。

      ```
      openssl x509 -req -in verificationCert.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out verificationCert.crt -days 500 -sha256
      ```

      ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

      生成验证证书用到的“rootCA.crt”和“rootCA.key”这两个文件，为“制作CA证书”中所生成的两个文件。

      “-days”后的参数值指定了该证书的有效天数，此处示例为500天，您可根据实际业务场景和需要进行调整。
   5. 上传验证证书进行验证。

      **图4** 上传验证证书   
      ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002356657209.png "点击放大")

#### 生成设备证书

1. 使用OpenSSL工具为设备证书生成密钥对（设备私钥）：

   ```
   openssl genrsa -out deviceCert.key 2048
   ```
2. 使用设备密钥对，生成证书签名请求文件：

   ```
   openssl req -new -key deviceCert.key -out deviceCert.csr
   ```

   ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

   生成证书签名请求文件时，要求填写证书唯一标识名称（Distinguished Name，DN）信息，参数说明如下[表2](#ZH-CN_TOPIC_0000001938891453__zh-cn_topic_0000001147693376_zh-cn_topic_0000001193533185_table17909204620310)所示。

   **表3** 证书签名请求文件参数说明

   | **提示** | **参数名称** | **取值样例** |
   | --- | --- | --- |
   | Country Name (2 letter code) []: | 国家/地区 | CN |
   | State or Province Name (full name) []: | 省/市 | GuangDong |
   | Locality Name (eg, city) []: | 城市 | ShenZhen |
   | Organization Name (eg, company) []: | 组织机构（或公司名） | Huawei Technologies Co., Ltd. |
   | Organizational Unit Name (eg, section) []: | 机构部门 | Cloud Dept. |
   | Common Name (eg, fully qualified host name) []: | CA名称（CN） | Huawei IoTDP CA |
   | Email Address []: | 邮箱地址 | / |
   | A challenge password []: | 证书密码，如您不设置密码，可以直接回车 | / |
   | An optional company name []: | 可选公司名称，如您不设置，可以直接回车 | / |
3. 使用CA证书、CA证书私钥和CSR文件创建设备证书（deviceCert.crt）。

   ```
   openssl x509 -req -in deviceCert.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out deviceCert.crt -days 36500 -sha256
   ```

   ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

   生成设备证书用到的“rootCA.crt”和“rootCA.key”这两个文件，为“制作CA证书”中所生成的两个文件，且需要完成“上传并验证CA证书”。

   “-days”后的参数值指定了该证书的有效天数，此处示例为36500天，您可根据实际业务场景和需要进行调整。

#### 添加自定义策略

添加自定义策略。

**图5** 添加自定义策略   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001836144161.png "点击放大")

#### 创建注册组

**图6** 新增注册组   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001789544630.png "点击放大")

**图7** 创建证书自定义注册组   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002063410921.png "点击放大")

#### 连接鉴权

MQTT.fx 是目前主流的MQTT桌面客户端，它支持 Windows, Mac, Linux，可以快速验证是否可以与设备发放服务进行连接并发布或订阅消息。

本文主要介绍 MQTT.fx 如何与华为设备发放交互，其中设备发放服务MQTT的南向接入地址请参考[获取终端节点](#ZH-CN_TOPIC_0000001938891453__zh-cn_topic_0000001147693376_section31227352232)。

1. 下载 [MQTT.fx](https://iotda-document.obs.cn-north-4.myhuaweicloud.com/mqttfx-1.7.1-windows-x64.exe)（默认是64位操作系统，如果是32位操作系统，单击此处下载 [MQTT.fx](https://iotda-document.obs.cn-north-4.myhuaweicloud.com/mqttfx-1.7.1-windows.exe) ），安装MQTT.fx工具。
2. 打开 MQTT.fx 客户端程序，单击“设置”。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001194259189.gif "点击放大")
3. 填写 Connection Profile 相关信息和 General 信息。其中General 信息可以用工具默认的参数配置。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001148339380.gif "点击放大")
4. 填写 User Credentials 信息。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001194179311.png "点击放大")

   ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

   其中Username 参考[MQTT CONNECT连接鉴权](https://support.huaweicloud.com/usermanual-iothub/iot_03_0003.html#ZH-CN_TOPIC_0000001899812022)参数说明（无需填写Password）。

   注：注册组的场景不存在选择产品，所以命名需要注意：如果命名字符串有“\_”，那么第一项必须为对应设备接入已经存在的产品ID，如果不包括“\_”，那么可以随意命名。
5. 选择开启 SSL/TLS，勾选Self signed certificates，配置相关证书内容。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001148179602.gif "点击放大")

   ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

   * CA File为设备发放对应的CA证书。
   * Client Certificate File为设备的设备证书。
   * Client Key File为设备的私钥。
6. 完成以上步骤后，单击“Apply”和“OK”保存，并在配置文件框中选择刚才创建的文件名，单击“Connect”，当右上角圆形图标为绿色时，说明连接设备发放服务成功，可进行订阅（Subscribe）和消息推送（Publish）操作。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001194259191.gif "点击放大")

#### 引导消息订阅

按照[设备接收引导信息](https://support.huaweicloud.com/usermanual-iothub/iot_03_0005.html#ZH-CN_TOPIC_0000001938891469)topic填写对应的topic，单击“Subscribe”进行订阅。订阅成功如下所示：

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001148339382.gif "点击放大")

#### 引导请求发布

按照[设备请求引导信息](https://support.huaweicloud.com/usermanual-iothub/iot_03_0004.html#ZH-CN_TOPIC_0000001899971914)topic填写对应的topic，单击“Publish”进行消息推送。

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001194179313.gif "点击放大")

#### 接收到引导消息

消息推送成功如下所示，在Subscribe的topic下会返回对应设备的设备接入服务的地址。

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001148179604.gif "点击放大")

#### 后续操作

至此，您已完成了设备发放的流程。设备发放已成功将您的设备【**接入IoTDA****所需的必要信息**】预置到了IoTDA实例中。

如您想要体验物联网平台的更多强大功能，您可通过如下步骤完成对IoTDA的后续操作：

1. 取用引导消息中的设备接入地址；
2. 单击Disconnect，断开与设备发放的连接；
3. 将引导信息中的设备接入地址填入MQTT.fx的MQTT Broker Profile Settings中的Broker Address和Broker Port，建立与设备接入的连接；
4. 完成与设备接入的上报数据等业务交互。

您可参考指导：[设备接入 IoTDA> 开发指南> 设备侧开发> 使用MQTT Demo接入> 使用MQTT.fx调测](https://support.huaweicloud.com/devg-iothub/iot_01_2127.html#section3)中的【**上报数据**】和【**进阶体验**】部分。

![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

得益于设备发放的预置功能，在参考IoTDA指导过程中，您无需再创建产品和设备。