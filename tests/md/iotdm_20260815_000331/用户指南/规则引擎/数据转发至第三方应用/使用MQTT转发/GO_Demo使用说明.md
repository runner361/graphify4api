# GO Demo使用说明

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00116.html
> **提取时间**: 2026-08-15T00:05:38.117607
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [规则引擎](https://support.huaweicloud.com/usermanual-iothub/iot_01_0021.html)/ [数据转发至第三方应用](https://support.huaweicloud.com/usermanual-iothub/iot_01_1000.html)/ [使用MQTT转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_00110.html)/ GO Demo使用说明

链接复制成功！

GO Demo使用说明
===========

本文以Go语言为例，介绍应用通过MQTTS协议接入平台，接收服务端订阅消息的示例。

#### 前提条件

熟悉Go语言开发环境配置，熟悉Go语言基本语法。

#### 开发环境

本示例使用了Go 1.18版本。

#### 添加依赖

本示例使用的Go语言的Mqtt依赖为paho.mqtt.golang（本示例使用版本为v1.4.3），在go.mod中添加依赖的代码如下：

```
require (
    github.com/eclipse/paho.mqtt.golang v1.4.3
)
```

#### 代码示例

```
package main

import (
   "crypto/tls"
   "fmt"
   mqtt "github.com/eclipse/paho.mqtt.golang"
   "os"
   "os/signal"
   "time"
)
type MessageHandler func(message string)
type MqttClient struct {
   Host            string
   Port            int
   ClientId        string
   AccessKey       string
   AccessCode      string
   Topic           string
   InstanceId      string
   Qos             int
   Client          mqtt.Client
   messageHandlers []MessageHandler
}
func (mqttClient *MqttClient) Connect() bool {
   return mqttClient.connectWithRetry()
}
func (mqttClient *MqttClient) connectWithRetry() bool {
   // 退避重试，从10ms依次x2，直到20s。
   duration := 10 * time.Millisecond
   maxDuration := 20000 * time.Millisecond
   // 建链失败进行重试
   internal := mqttClient.connectInternal()
   times := 0
   for !internal {
      time.Sleep(duration)
      if duration < maxDuration {
         duration *= 2
      }
      times++
      fmt.Println("connect mqttgo broker retry. times: ", times)
      internal = mqttClient.connectInternal()
   }
   return internal
}
func (mqttClient *MqttClient) connectInternal() bool {
   // 建链前先关闭已有连接
   mqttClient.Close()
   options := mqtt.NewClientOptions()
   options.AddBroker(fmt.Sprintf("mqtts://%s:%d", mqttClient.Host, mqttClient.Port))
   options.SetClientID(mqttClient.ClientId)
   userName := fmt.Sprintf("accessKey=%s|timestamp=%d", mqttClient.AccessKey, time.Now().UnixNano()/1000000)
   if len(mqttClient.InstanceId) != 0 {
      userName = userName + fmt.Sprintf("|instanceId=%s", mqttClient.InstanceId)
   }
   options.SetUsername(userName)
   options.SetPassword(mqttClient.AccessCode)
   options.SetConnectTimeout(10 * time.Second)
   options.SetKeepAlive(120 * time.Second)
   // 关闭sdk内部重连，使用自定义重连刷新时间戳
   options.SetAutoReconnect(false)
   options.SetConnectRetry(false)
   tlsConfig := &tls.Config{
      InsecureSkipVerify: true,
      MaxVersion:         tls.VersionTLS12,
      MinVersion:         tls.VersionTLS12,
   }
   options.SetTLSConfig(tlsConfig)
   options.OnConnectionLost = mqttClient.createConnectionLostHandler()
   client := mqtt.NewClient(options)
   if token := client.Connect(); token.Wait() && token.Error() != nil {
      fmt.Println("device create bootstrap client failed,error = ", token.Error().Error())
      return false
   }
   mqttClient.Client = client
   fmt.Println("connect mqttgo broker success.")
   mqttClient.subscribeTopic()
   return true
}
func (mqttClient *MqttClient) subscribeTopic() {
   subRes := mqttClient.Client.Subscribe(mqttClient.Topic, 0, mqttClient.createMessageHandler())
   if subRes.Wait() && subRes.Error() != nil {
      fmt.Printf("sub topic failed,error is %s\n", subRes.Error())
      panic("subscribe topic failed.")
   } else {
      fmt.Printf("sub topic success\n")
   }
}
func (mqttClient *MqttClient) createMessageHandler() func(client mqtt.Client, message mqtt.Message) {
   messageHandler := func(client mqtt.Client, message mqtt.Message) {
      fmt.Println("receive message from server.")
      go func() {
         for _, handler := range mqttClient.messageHandlers {
            handler(string(message.Payload()))
         }
      }()
   }
   return messageHandler
}
func (mqttClient *MqttClient) createConnectionLostHandler() func(client mqtt.Client, reason error) {
   // 断链后进行自定义重连
   connectionLostHandler := func(client mqtt.Client, reason error) {
      fmt.Printf("connection lost from server. begin to reconnect broker. reason: %s\n", reason.Error())
      connected := mqttClient.connectWithRetry()
      if connected {
         fmt.Println("reconnect mqttgo broker success.")
      }
   }
   return connectionLostHandler
}
func (mqttClient *MqttClient) Close() {
   if mqttClient.Client != nil {
      mqttClient.Client.Disconnect(1000)
   }
}
func main() {
   // 以下参数配置请参考连接配置说明
   // mqtt接入域名
   mqttHost := "your mqtt host"
   // mqtt接入端口
   mqttPort := 8883
   //接入凭证键值
   mqttAccessKey := os.Getenv("MQTT_ACCESS_KEY")
   //接入凭证密钥
   mqttAccessCode := os.Getenv("MQTT_ACCESS_CODE")
   //订阅topic名称
   mqttTopic := "your mqtt topic"
   //实例Id
   instanceId := "your instance Id"
   //mqttgo client id
   clientId := "your mqtt client id"

   mqttClient := MqttClient{
      Host:       mqttHost,
      Port:       mqttPort,
      Topic:      mqttTopic,
      ClientId:   clientId,
      AccessKey:  mqttAccessKey,
      AccessCode: mqttAccessCode,
      InstanceId: instanceId,
   }
   //自定义消息处理handler
   mqttClient.messageHandlers = []MessageHandler{func(message string) {
      fmt.Println(message)
   }}
   connect := mqttClient.Connect()
   if !connect {
      fmt.Println("init mqttgo client failed.")
      return
   }
   //阻塞方法，保持mqtt客户端一直拉消息
   interrupt := make(chan os.Signal, 1)
   signal.Notify(interrupt, os.Interrupt)
   for {
      <-interrupt
      break
   }
}
```

#### 成功示例

接入成功后，客户端打印信息如下：

**图1** go mqtt客户端接入成功示例   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001864213190.png "点击放大")

#### 相关文档

* [和其他服务的关系](/usermanual-iothub/iot_02_0003.html)
* [委托授权](/usermanual-iothub/iot_01_0203.html)
* [设备策略使用示例](/usermanual-iothub/iot_01_1113.html)
* [IoTDA资源](/usermanual-iothub/iot_01_0233.html)
* [MQTT场景--使用MQTT.fx接入设备发放示例](/usermanual-iothub/iot_03_00012.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)