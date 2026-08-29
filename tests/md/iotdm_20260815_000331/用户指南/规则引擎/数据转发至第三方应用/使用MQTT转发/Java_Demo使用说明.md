# Java Demo使用说明

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00114.html
> **提取时间**: 2026-08-15T00:05:33.898017
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [规则引擎](https://support.huaweicloud.com/usermanual-iothub/iot_01_0021.html)/ [数据转发至第三方应用](https://support.huaweicloud.com/usermanual-iothub/iot_01_1000.html)/ [使用MQTT转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_00110.html)/ Java Demo使用说明

链接复制成功！

Java Demo使用说明
=============

本文以Java语言为例，介绍应用通过MQTTS协议接入平台，接收服务端订阅消息的示例。

#### 前提条件

已安装**IntelliJ IDEA**开发工具。若未安装请参考[安装IntelliJ IDEA](#ZH-CN_TOPIC_0288189809__section6870282816)。

#### 安装IntelliJ IDEA

1. 访问[IntelliJ IDEA官网](https://www.jetbrains.com/idea/)，选择合适系统的版本下载。（本文以windows 64-bit系统IntelliJ IDEA 2019.2.3 Ultimate为例）。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0288587633.png "点击放大")
2. 下载完成后，运行安装文件，根据界面提示安装。

#### 导入代码样例

1. 下载[JAVA样例](https://obs-pipeline.obs.cn-north-4.myhuaweicloud.com/north/mqttdemo-new.zip)。
2. 打开IDEA开发者工具，单击“ Import Project”。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0288587636.png "点击放大")
3. 选择[1](#ZH-CN_TOPIC_0288189809__li111122321211)中下载的样例，然后根据界面提示，单击“next”。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0288587640.png "点击放大")
4. 完成代码导入。

   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002063849181.png)

#### 建立连接

1. 在com.iot.mqtt.example.demo.MqttConstants中设置接入地址及鉴权参数的值：

   ```
   // IoT平台mqtt接入地址，替换成"连接配置说明中"的"MQTT接入域名。
   String HOST = "${HOST}";
   // 接入凭证，替换成"获取MQTT接入凭证"中获取的接入凭证。
   String ACCESS_KEY = "${accessKey}";
   String ACCESS_CODE = "${accessCode}";
   // 实例ID，当同一region购买多个标准版实例该参数必填。
   String INSTANCE_ID = "${instanceId}";
   // 接收数据的Topic，替换成"创建规则动作"中的Topic。
   String SUBSCRIBE_TOPIC = "${subscribeTopic}";
   ```

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   Demo中涉及的参数说明，请参考[连接配置说明](https://support.huaweicloud.com/usermanual-iothub/iot_01_00113.html#ZH-CN_TOPIC_0288189808__section8427203915214)。
2. 运行com.iot.mqtt.example.demo.MqttDemo样例代码，根据以下日志信息判断是否订阅成功。该示例忽略服务端证书校验，如需校验服务端证书可参考com.iot.mqtt.example.demo.MqttTlsDemo。
   * 订阅成功。

     **图1** 订阅成功   
     ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002063899805.png "点击放大")
   * 订阅失败。
     1. 用户名或密码错误。

        **图2** 用户或密码错误   
        ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002027727262.png "点击放大")
     2. 订阅的Topic不存在。

        **图3** 订阅topic不存在   
        ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002027886590.png "点击放大")

#### 接收数据

Topic订阅后设备上报数据并触发规则后，MQTT客户端就可以收到流转数据。样例代码收取到流转数据的日志如下图所示：

**图4** 接收到流转数据   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002027887154.png "点击放大")

#### 相关文档

* [AMQP转发](/usermanual-iothub/iot_01_0003.html)
* [广播通信概述](/usermanual-iothub/iot_01_00120.html)
* [MQTT 华为云证书注册组发放示例](/usermanual-iothub/iot_03_00010.html)
* [概述](/usermanual-iothub/iot_01_0206.html)
* [Node.js Demo使用说明](/usermanual-iothub/iot_01_00117.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)