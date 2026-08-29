# C# Demo使用说明

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00118.html
> **提取时间**: 2026-08-15T00:05:39.636814
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [规则引擎](https://support.huaweicloud.com/usermanual-iothub/iot_01_0021.html)/ [数据转发至第三方应用](https://support.huaweicloud.com/usermanual-iothub/iot_01_1000.html)/ [使用MQTT转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_00110.html)/ C# Demo使用说明

链接复制成功！

C# Demo使用说明
===========

本文以C#语言为例，介绍应用通过MQTTS协议接入平台，接收服务端订阅消息的示例。

#### 前提条件

熟悉.NETFramework开发环境配置，熟悉C#语言基本语法。

#### 开发环境

本示例所使用的开发环境为.NETFramework 4.6.2版本，.Net SDK 6.0.421版本。请前往.NET官网[下载](https://dotnet.microsoft.com/zh-cn/download)。安装成功之后可以通过以下命令查看.Net SDK版本。

```
dotnet -v
```

#### 添加依赖

本示例使用C#语言的Mqtt依赖为MQTTnet和MQTTnet.Extension.ManagedClient（使用版本为3.0.11)，可以在NuGet管理器中搜索到"MQTTnet"后安装所需版本。

**图1** nuget安装依赖   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001914051909.png "点击放大")

#### 代码示例

ClientConf.cs代码如下：

```
using MQTTnet.Protocol;

namespace mqttcs
{
    public class ClientConf
    {
        // mqtt订阅地址
        public string ServerUri { get; set; }

        // mqtt订阅端口号
        public int Port { get; set; }
        
        // mqtt接入凭据access_key
        public string AccessKey { get; set; }
        
        // mqtt接入凭据access_code
        public string AccessCode { get; set; }
        
        // mqtt 客户端ID
        public string ClientId { get; set; }
        
        // 实例Id，同一Region购买多个标准版实例时需要填写该参数
        public string InstanceId { get; set; }
        
        // mqtt订阅topic
        public string Topic { get; set; }
        
        // mqtt qos
        public MqttQualityOfServiceLevel Qos { get; set; }
        
    }
}
```

MqttListener代码如下：

```
using System;
using MQTTnet.Client.Connecting;
using MQTTnet.Client.Disconnecting;
using MQTTnet.Extensions.ManagedClient;

namespace mqttcs
{
    public interface MqttListener
    {
        // mqtt客户端与服务端断链回调函数
        void ConnectionLost(MqttClientDisconnectedEventArgs e);

        // mqtt客户端与服务端建链成功回调函数
        void ConnectComplete(MqttClientConnectResultCode resultCode, String reason);
        
        // mqtt客户端消费消息回调函数
        void OnMessageReceived(String message);
        
        // mqtt客户端与服务端建链失败回调函数
        void ConnectFail(ManagedProcessFailedEventArgs e);
    }
}
```

MqttConnection.cs代码示例如下：

```
using System;
using System.Text;
using System.Threading;
using MQTTnet;
using MQTTnet.Client.Connecting;
using MQTTnet.Client.Disconnecting;
using MQTTnet.Client.Options;
using MQTTnet.Client.Receiving;
using MQTTnet.Extensions.ManagedClient;
using MQTTnet.Formatter;

namespace mqttcs
{
    public class MqttConnection
    {
        private static IManagedMqttClient client = null;
        
        private static ManualResetEvent mre = new ManualResetEvent(false);
        
        private static readonly ushort DefaultKeepLive = 120;
        
        private static int _retryTimes = 0;
        
        private readonly int _retryTimeWait = 1000;
        
        private readonly ClientConf _clientConf;

        private MqttListener _listener;
        
        public MqttConnection(ClientConf clientConf, MqttListener listener)
        {
            _clientConf = clientConf;
            _listener = listener;
        }
        
        public int Connect()
        {
            client?.StopAsync();
            // 退避重试，从1s直到20s
            var duration = 1000;
            var maxDuration = 20 * 1000;
            var rc = InternalConnect();
            while (rc != 0)
            {
                Thread.Sleep((int)duration);
                if (duration < maxDuration)
                {
                    duration *= 2;
                }
                client?.StopAsync();
                _retryTimes++;
                Console.WriteLine("connect mqtt broker retry. times: " + _retryTimes);
                rc = InternalConnect();
            }

            return rc;
        }

        private int InternalConnect()
        {
            try
            {
                client = new MqttFactory().CreateManagedMqttClient();
                client.ApplicationMessageReceivedHandler =
                    new MqttApplicationMessageReceivedHandlerDelegate(ApplicationMessageReceiveHandlerMethod);
                client.ConnectedHandler = new MqttClientConnectedHandlerDelegate(OnMqttClientConnected);
                client.DisconnectedHandler = new MqttClientDisconnectedHandlerDelegate(OnMqttClientDisconnected);
                client.ConnectingFailedHandler = new ConnectingFailedHandlerDelegate(OnMqttClientConnectingFailed);
                IManagedMqttClientOptions options = GetOptions();
                // Connects to the platform.
                client.StartAsync(options);
                mre.Reset();

                mre.WaitOne();
                if (!client.IsConnected)
                {
                    return -1;
                }

                var mqttTopicFilter = new MqttTopicFilterBuilder().WithTopic(_clientConf.Topic).WithQualityOfServiceLevel(_clientConf.Qos).Build();
                
                client.SubscribeAsync(mqttTopicFilter).Wait();
                Console.WriteLine("subscribe topic success.");
                return 0;
            }
            catch (Exception e)
            {
                Console.WriteLine("Connect to mqtt server failed. err: " + e);
                return -1;
            }
        }

        private void ApplicationMessageReceiveHandlerMethod(MqttApplicationMessageReceivedEventArgs e)
        {
            string payload = null;
            if (e.ApplicationMessage.Payload != null)
            {
                payload = Encoding.UTF8.GetString(e.ApplicationMessage.Payload);
            }
            try
            {
                _listener?.OnMessageReceived(payload);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Message received error, the message is " + payload);
            }
            
        }
        
        private void OnMqttClientConnected(MqttClientConnectedEventArgs e)
        {
            try
            {
                _retryTimes = 0;
                _listener?.ConnectComplete(e.AuthenticateResult.ResultCode, e.AuthenticateResult.ReasonString);
                mre.Set();
            }
            catch (Exception exception)
            {
                Console.WriteLine("handle connect callback failed. e: " + exception.Message);
            }
        }
        
        private void OnMqttClientDisconnected(MqttClientDisconnectedEventArgs e)
        {
            try
            {
                _listener?.ConnectionLost(e);
            }
            catch (Exception exception)
            {
                Console.WriteLine("handle disConnect callback failed. e: " + exception.Message);
            }
            
        }

        private void OnMqttClientConnectingFailed(ManagedProcessFailedEventArgs e)
        {
            try
            {
                if (_listener != null)
                {
                    _listener.ConnectFail(e);
                }
                Thread.Sleep(_retryTimeWait);
                Connect();
            }
            catch (Exception exception)
            {
                Console.WriteLine("handle connect failed callback failed. e: " + exception.Message);
            }
        }

        private IManagedMqttClientOptions GetOptions()
        {
            IManagedMqttClientOptions options = null;
            long timestamp = new DateTimeOffset(DateTime.UtcNow).ToUnixTimeMilliseconds();
            string userName = "accessKey=" + _clientConf.AccessKey + "|timestamp=" + timestamp + "|instanceId=" + _clientConf.InstanceId;

            options = new ManagedMqttClientOptionsBuilder()
                .WithClientOptions(new MqttClientOptionsBuilder()
                    .WithTcpServer(_clientConf.ServerUri, _clientConf.Port)
                    .WithCredentials(userName, _clientConf.AccessCode)
                    .WithClientId(_clientConf.ClientId)
                    .WithKeepAlivePeriod(TimeSpan.FromSeconds(DefaultKeepLive))
                    .WithTls(new MqttClientOptionsBuilderTlsParameters()
                    {
                        AllowUntrustedCertificates = true,
                        UseTls = true,
                        CertificateValidationHandler = delegate { return true; },
                        IgnoreCertificateChainErrors = false,
                        IgnoreCertificateRevocationErrors = false,
                        SslProtocol = System.Security.Authentication.SslProtocols.Tls12,
                    })
                    .WithProtocolVersion(MqttProtocolVersion.V500)
                    .Build())
                .Build();
            return options;
        }
    }
}
```

MqttClient.cs代码示例如下：

```
using System;
using System.Threading;
using System.Threading.Tasks;
using MQTTnet.Client.Connecting;
using MQTTnet.Client.Disconnecting;
using MQTTnet.Extensions.ManagedClient;
using MQTTnet.Protocol;

namespace mqttcs
{
    class MqttClient: MqttListener
    {
        private static ManualResetEvent mre = new ManualResetEvent(false);

        public static async Task Main(string[] args)
        {
            ClientConf clientConf = new ClientConf();
            clientConf.ClientId = "your mqtt clientId";
            clientConf.ServerUri = "your mqtt host";
            clientConf.Port = 8883;
            clientConf.AccessKey = Environment.GetEnvironmentVariable("MQTT_ACCESS_KEY");
            clientConf.AccessCode = Environment.GetEnvironmentVariable("MQTT_ACCESS_CODE");
            clientConf.InstanceId = "your instanceId";
            clientConf.Topic = "your mqtt topic";
            clientConf.Qos = MqttQualityOfServiceLevel.AtMostOnce;

            MqttConnection connection = new MqttConnection(clientConf, new MqttClient());
            var connect = connection.Connect();
            if (connect == 0)
            {
                Console.WriteLine("success to init mqtt connection.");
                mre.WaitOne();
            }
        }

        public void ConnectionLost(MqttClientDisconnectedEventArgs e)
        {
            if (e?.Exception != null)
            {
                Console.WriteLine("connect was lost. exception: " + e.Exception.Message);
                return;
            }
            Console.WriteLine("connect was lost");
            
        }

        public void ConnectComplete(MqttClientConnectResultCode resultCode, String reason)
        {
            Console.WriteLine("connect success. resultCode: " + resultCode + " reason: " + reason);
        }

        public void OnMessageReceived(string message)
        {
            Console.WriteLine("receive msg: " + message);
        }

        public void ConnectFail(ManagedProcessFailedEventArgs e)
        {
            Console.WriteLine("connect mqtt broker failed. e: " + e.Exception.Message);
        }
    }
}
```

#### 成功示例

接入成功后，客户端打印如下：

**图2** c#客户端接入成功示例   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001868148224.png "点击放大")

#### 相关文档

* [实例管理](/usermanual-iothub/iot_01_0079.html)
* [数据转发流控策略配置](/usermanual-iothub/iot_01_0037.html)
* [和其他服务的关系](/usermanual-iothub/iot_02_0003.html)
* [查看报表](/usermanual-iothub/iot_01_0030_1.html)
* [接口说明](/usermanual-iothub/iot_03_0002.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)