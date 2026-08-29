# GO SDK接入示例

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00100_8.html
> **提取时间**: 2026-08-15T00:05:31.132921
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [规则引擎](https://support.huaweicloud.com/usermanual-iothub/iot_01_0021.html)/ [数据转发至第三方应用](https://support.huaweicloud.com/usermanual-iothub/iot_01_1000.html)/ [使用AMQP转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_00100.html)/ GO SDK接入示例

链接复制成功！

GO SDK接入示例
==========

本文介绍使用GO SDK通过AMQP接入华为云物联网平台，接收服务端订阅消息的示例。

#### 开发环境要求

本示例使用的开发环境为Go 1.16及以上版本。

#### 添加依赖

在go.mod中添加以下依赖。

```
require (
    pack.ag/amqp v0.12.5 // 本示例使用v0.12.5,根据实际需要选择版本
)
```

#### 代码示例

```
package main

import (
	"context"
	"crypto/tls"
	"fmt"
	"pack.ag/amqp"
	"time"
)

type AmqpClient struct {
	Title      string
	Host       string
	AccessKey  string
	AccessCode string
        InstanceId string
	QueueName  string

	address  string
	userName string
	password string

	client   *amqp.Client
	session  *amqp.Session
	receiver *amqp.Receiver
}

type MessageHandler interface {
	Handle(message *amqp.Message)
}

func (ac *AmqpClient) InitConnect() {
	if ac.QueueName == "" {
		ac.QueueName = "DefaultQueue"
	}
	ac.address = "amqps://" + ac.Host + ":5671"
	ac.userName = fmt.Sprintf("accessKey=%s|timestamp=%d|instanceId=%s", ac.AccessKey, time.Now().UnixNano()/1000000, ac.InstanceId)
	ac.password = ac.AccessCode
}

func (ac *AmqpClient) StartReceiveMessage(ctx context.Context, handler MessageHandler) {
	childCtx, _ := context.WithCancel(ctx)
	err := ac.generateReceiverWithRetry(childCtx)
	if nil != err {
		return
	}
	defer func() {
		_ = ac.receiver.Close(childCtx)
		_ = ac.session.Close(childCtx)
		_ = ac.client.Close()
	}()

	for {
		// 阻塞接受消息，如果ctx是background则不会被打断。
		message, err := ac.receiver.Receive(ctx)
		if nil == err {
			go handler.Handle(message)
			_ = message.Accept()
		} else {
			fmt.Println("amqp receive data error: ", err)

			//如果是主动取消，则退出程序。
			select {
			case <-childCtx.Done():
				return
			default:
			}

			//非主动取消，则重新建立连接。
			err := ac.generateReceiverWithRetry(childCtx)
			if nil != err {
				return
			}
		}
	}
}

func (ac *AmqpClient) generateReceiverWithRetry(ctx context.Context) error {
	// 退避重试，从10ms依次x2，直到20s。
	duration := 10 * time.Millisecond
	maxDuration := 20000 * time.Millisecond
	times := 1

	// 异常情况，退避重连。
	for {
		select {
		case <-ctx.Done():
			return amqp.ErrConnClosed
		default:
		}

		err := ac.generateReceiver()
		if nil != err {
			fmt.Println("amqp ac.generateReceiver error ", err)
			time.Sleep(duration)
			if duration < maxDuration {
				duration *= 2
			}
			fmt.Println("amqp connect retry,times:", times, ",duration:", duration)
			times++
			return nil
		} else {
			fmt.Println("amqp connect init success")
			return nil
		}
	}
}

// 由于包不可见，无法判断conn和session状态，重启连接获取。
func (ac *AmqpClient) generateReceiver() error {

	if ac.session != nil {
		receiver, err := ac.session.NewReceiver(
			amqp.LinkSourceAddress(ac.QueueName),
			amqp.LinkCredit(20),
		)
		// 如果断网等行为发生，conn会关闭导致session建立失败，未关闭连接则建立成功。
		if err == nil {
			ac.receiver = receiver
			return nil
		}
	}

	// 清理上一个连接。
	if ac.client != nil {
		_ = ac.client.Close()
	}
        ac.userName = fmt.Sprintf("accessKey=%s|timestamp=%d|instanceId=%s", ac.AccessKey, time.Now().UnixNano()/1000000, ac.InstanceId)
	fmt.Println("[" + ac.Title + "] Dial... addr=[" + ac.address + "], username=[" + ac.userName + "], password=[" + ac.password + "]")
	client, err := amqp.Dial(ac.address,
		amqp.ConnSASLPlain(ac.userName, ac.password),
		amqp.ConnProperty("vhost", "default"),
		amqp.ConnServerHostname("default"),
		amqp.ConnTLSConfig(&tls.Config{InsecureSkipVerify: true,
			MaxVersion: tls.VersionTLS12,
		}),
		amqp.ConnConnectTimeout(8*time.Second))
	if err != nil {
		fmt.Println("Dial", err)
		return err
	}
	ac.client = client
	session, err := client.NewSession()
	if err != nil {
		XDebug("Error： NewSession", err)
		return err
	}
	ac.session = session

	receiver, err := ac.session.NewReceiver(
		amqp.LinkTargetDurability(amqp.DurabilityUnsettledState),
		amqp.LinkSourceAddress(ac.QueueName),
		amqp.LinkCredit(100),
	)
	if err != nil {
		XDebug("Error： NewReceiver", err)
		return err
	}
	ac.receiver = receiver

	return nil
}

func XDebug(s string, err error) {
	fmt.Println(s, err)
}

type CustomerMessageHandler struct {
}

func (c *CustomerMessageHandler) Handle(message *amqp.Message) {
	fmt.Println("AMQP收到消息：", message.Value)
}

func main() {
	// 以下参数配置请参考连接配置说明
        // AMQP接入域名
	amqpHost := "127.0.0.1"

	//接入凭证键值
	amqpAccessKey := "your accessKey"

	// 接入凭证密钥
	amqpAccessCode := "your accessCode"

        // 实例Id
	instanceId:= "your instanceId"

	// 订阅队列名称
	amqpQueueName := "DefaultQueue"

	amqpClient := &AmqpClient{
		Title:      "test",
		Host:       amqpHost,
		AccessKey:  amqpAccessKey,
		AccessCode: amqpAccessCode,
                InstanceId: instanceId,
		QueueName:  amqpQueueName,
	}

	handle := CustomerMessageHandler{}
	amqpClient.InitConnect()
	ctx := context.Background()
	amqpClient.StartReceiveMessage(ctx, &handle)
}
```

#### 相关文档

* [接口说明](/usermanual-iothub/iot_03_0002.html)
* [自定义鉴权概述](/usermanual-iothub/iot_01_0212.html)
* [MQTT 华为云X.509证书认证设备使用证书策略发放示例](/usermanual-iothub/iot_03_0009.html)
* [设备接收引导信息](/usermanual-iothub/iot_03_0005.html)
* [数据转发至FunctionGraph函数工作流](/usermanual-iothub/iot_bp_00013.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)