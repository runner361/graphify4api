# Node.js Demo使用说明

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00117.html
> **提取时间**: 2026-08-15T00:05:39.049209
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [规则引擎](https://support.huaweicloud.com/usermanual-iothub/iot_01_0021.html)/ [数据转发至第三方应用](https://support.huaweicloud.com/usermanual-iothub/iot_01_1000.html)/ [使用MQTT转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_00110.html)/ Node.js Demo使用说明

链接复制成功！

Node.js Demo使用说明
================

本文以Node.js语言为例，介绍应用通过MQTTS协议接入平台，接收服务端订阅消息的示例。

#### 前提条件

熟悉Node.js语言开发环境配置，熟悉Node.js语言基本语法。

#### 开发环境

本示例所使用的开发环境为Node.js v13.14.0版本。请前往Node.js官网[下载](https://nodejs.org/en/download/)。安装成功之后可以通过以下命令查看node版本。

```
node --version
```

#### 添加依赖

本示例使用的Node.js语言的Mqtt依赖为mqtt（本示例使用版本为4.0.0），可以通过以下命令下载依赖。

```
npm install mqtt@4.0.0
```

#### 代码示例

```
const mqtt = require('mqtt');
// 订阅topic名称
var topic = "your mqtt topic";
// 接入凭证键值，可通过环境变量预置
var accessKey = process.env.MQTT_ACCESS_KEY;
// 接入凭证密钥，可通过环境变量预置
var accessCode = process.env.MQTT_ACCESS_CODE;
// mqtt接入地址
var mqttHost = "your mqtt host";
// mqtt接入端口
var mqttPort = 8883;
// 实例Id
var instanceId = "your instanceId";
// mqtt client id
var clientId = "your clientId";
// mqtt 客户端
var client = null;
connectWithRetry();
async function connectWithRetry() {
    // 退避重试，从1s依次x2，直到20s。
    var duration = 1000;
    var maxDuration = 20000;
    var success = connect(topic);
    var times = 0;
    while (!success) {
       await sleep(duration)
       if (duration < maxDuration) {
          duration *= 2
       }
       times++
       console.log('connect mqtt broker retry. times: ' + times)
        if (client == null) {
            connect(topic)
            continue
        }
       client.end(true, function() {
            connect(topic)
        });
    }
}
function sleep(ms) {
    return new Promise(resolve => setTimeout(() => resolve(), ms))
}
function connect(topic) {
    try {
        client = mqtt.connect(getClientOptions())
        if (client == null) {
            return false
        }
        client.on('connect', connectCallBack)
        client.subscribe(topic, subscribeCallBack)
        client.on('message', messageCallBack)
        client.on('error', clientErrorCallBack)
        client.on('close', closeCallBack)
        return true
    } catch (error) {
        console.log('connect to mqtt broker failed. err ' + error)
    }
    return false
}
function getClientOptions() {
    var timestamp = Math.round(new Date);
    const username = 'accessKey=' + accessKey + '|timestamp=' + timestamp + '|instanceId=' + instanceId;
    var options = {
        host: mqttHost,
        port: mqttPort,
        connectTimeout: 4000,
        clientId: clientId,
        protocol: 'mqtts',
        keepalive: 120,
        username: username,
        password: accessCode,
        rejectUnauthorized: false,
        secureProtocol: 'TLSv1_2_method'
    };
    return options;
};
function connectCallBack() {
    console.log('connect mqtt server success');
};
function subscribeCallBack(err, granted) {
    if (err != null || granted[0].qos === 128) {
        console.log('subscribe topic failed. granted: ' + granted[0].qos)
        return
    }
    console.log('subscribe topic success. granted: ' + granted[0].qos);
};
function clientErrorCallBack(err) {
    console.log('mqtt client error ' + err);
};
function messageCallBack(topic, message) {
    console.log('receive message ' + message);
};
function closeCallBack() {
    console.log('Disconnected from mqtt broker')
    client.end(true, function() {
        console.log('close connection');
        connectWithRetry();
     });
}
```

#### 成功示例

接入成功后，客户端打印信息如下：

**图1** node.js mqtt客户端接入成功示例   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001864256454.png "点击放大")

#### 相关文档

* [自定义模板示例](/usermanual-iothub/iot_01_0235.html)
* [AMQP转发](/usermanual-iothub/iot_01_0003.html)
* [概述](/usermanual-iothub/iot_01_0045_2.html)
* [网关与子设备](/usermanual-iothub/iot_01_0052.html)
* [权限管理](/usermanual-iothub/iot_01_0230.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)