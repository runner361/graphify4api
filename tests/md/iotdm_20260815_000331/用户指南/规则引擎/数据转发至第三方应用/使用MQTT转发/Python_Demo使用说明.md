# Python Demo使用说明

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00115.html
> **提取时间**: 2026-08-15T00:05:35.443504
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [规则引擎](https://support.huaweicloud.com/usermanual-iothub/iot_01_0021.html)/ [数据转发至第三方应用](https://support.huaweicloud.com/usermanual-iothub/iot_01_1000.html)/ [使用MQTT转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_00110.html)/ Python Demo使用说明

链接复制成功！

Python Demo使用说明
===============

本文以Python语言为例，介绍应用通过MQTTS协议接入平台，接收服务端订阅消息的示例。

#### 前提条件

熟悉Python语言开发环境配置，熟悉Python语言基本语法。

#### 开发环境

本示例使用了Python 3.8.8版本。

#### 添加依赖

本示例使用的Python语言的Mqtt依赖为[paho-mqtt](https://github.com/eclipse/paho.mqtt.python)(本示例使用版本为2.0.0)，可以通过以下命令下载依赖。

```
pip install paho-mqtt==2.0.0
```

#### 代码示例

ClientConf代码如下：

```
from typing import Optional
class ClientConf:
    def __init__(self):
        # mqtt订阅地址
        self.__host: Optional[str] = None
        # mqtt订阅端口号
        self.__port: Optional[int] = None
        # mqtt接入凭据access_key
        self.__access_key: Optional[str] = None
        # mqtt接入凭据access_code
        self.__access_code: Optional[str] = None
        # mqtt订阅topic
        self.__topic: Optional[str] = None
        # 实例Id，同一Region购买多个标准版实例时需要填写该参数
        self.__instance_id: Optional[str] = None
        # mqtt qos
        self.__qos = 1

    @property
    def host(self):
        return self.__host
    @host.setter
    def host(self, host):
        self.__host = host
    @property
    def port(self):
        return self.__port
    @port.setter
    def port(self, port):
        self.__port = port
    @property
    def access_key(self):
        return self.__access_key
    @access_key.setter
    def access_key(self, access_key):
        self.__access_key = access_key
    @property
    def access_code(self):
        return self.__access_code
    @access_code.setter
    def access_code(self, access_code):
        self.__access_code = access_code
    @property
    def topic(self):
        return self.__topic
    @topic.setter
    def topic(self, topic):
        self.__topic = topic
    @property
    def instance_id(self):
        return self.__instance_id
    @instance_id.setter
    def instance_id(self, instance_id):
        self.__instance_id = instance_id
    @property
    def qos(self):
        return self.__qos
    @qos.setter
    def qos(self, qos):
        self.__qos = qos
```

MqttClient代码如下：

```
import os
import ssl
import threading
import time
import traceback
import secrets
from client_conf import ClientConf
import paho.mqtt.client as mqtt
class MqttClient:
    def __init__(self, client_conf: ClientConf):
        self.__host = client_conf.host
        self.__port = client_conf.port
        self.__access_key = client_conf.access_key
        self.__access_code = client_conf.access_code
        self.__topic = client_conf.topic
        self.__instance_id = client_conf.instance_id
        self.__qos = client_conf.qos
        self.__paho_client: Optional[mqtt.Client] = None
        self.__connect_result_code = -1
        self.__default_backoff = 1000
        self.__retry_times = 0
        self.__min_backoff = 1 * 1000  # 1s
        self.__max_backoff = 30 * 1000  # 30s

    def connect(self):
        self.__valid_params()
        rc = self.__connect()
        while rc != 0:
            # 退避重连
            low_bound = int(self.__default_backoff * 0.8)
            high_bound = int(self.__default_backoff * 1.0)
            random_backoff = secrets.randbelow(high_bound - low_bound)
            backoff_with_jitter = int(pow(2, self.__retry_times)) * (random_backoff + low_bound)
            wait_time_ms = self.__max_backoff if (self.__min_backoff + backoff_with_jitter) > self.__max_backoff else (
                    self.__min_backoff + backoff_with_jitter)
            wait_time_s = round(wait_time_ms / 1000, 2)
            print("client will try to reconnect after " + str(wait_time_s) + " s")
            time.sleep(wait_time_s)
            self.__retry_times += 1
            self.close()  # 释放之前的connection
            rc = self.__connect()
            # rc为0表示建链成功，其它表示连接不成功
            if rc != 0:
                print("connect with result code: " + str(rc))
                if rc == 134:
                    print("connect failed with bad username or password, "
                          "reconnection will not be performed")
                    pass
        return rc
    def __connect(self):
        try:
            timestamp = self.current_time_millis()
            user_name = "accessKey=" + self.__access_key + "|timestamp=" + timestamp
            if self.__instance_id:
                user_name = user_name + "|instanceId=" + self.__instance_id
            pass_word = self.__access_code
            self.__paho_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "mqttClient")
            # 关闭自动重试， 采用手动重试的方式刷新时间戳
            self.__paho_client._reconnect_on_failure = False
            # 设置回调函数
            self._set_callback()
            # topic放在userdata中，回调函数直接拿topic订阅
            self.__paho_client.user_data_set(self.__topic)
            self.__paho_client.username_pw_set(user_name, pass_word)
            # 当前mqtt broker仅支持TLS1.2
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            # 不校验服务端证书
            context.verify_mode = ssl.CERT_NONE
            context.check_hostname = False
            self.__paho_client.tls_set_context(context)
            rc = self.__paho_client.connect(self.__host, self.__port)
            self.__connect_result_code = rc
            if rc == 0:
                threading.Thread(target=self.__paho_client.loop_forever, args=(1, False), name="MqttThread").start()
            # 等待建链
            time.sleep(1)
        except Exception as e:
            self.__connect_result_code = -1
            print("Mqtt connection error. traceback: " + traceback.format_exc())
        if self.__paho_client.is_connected():
            return 0
        else:
            return self.__connect_result_code
    def __valid_params(self):
        assert self.__access_key is not None
        assert self.__access_code is not None
        assert self.__topic is not None

    @staticmethod
    def current_time_millis():
        return str(int(round(time.time() * 1000)))
    def _set_callback(self):
        # 当平台响应连接请求时，执行self._on_connect()
        self.__paho_client.on_connect = self._on_connect
        # 当与平台断开连接时，执行self._on_disconnect()
        self.__paho_client.on_disconnect = self._on_disconnect
        # 当订阅topic时，执行self._on_subscribe
        self.__paho_client.on_subscribe = self._on_subscribe
        # 当接收到一个原始消息时，执行self._on_message()
        self.__paho_client.on_message = self._on_message
    def _on_connect(self, client, userdata, flags, rc: mqtt.ReasonCode, properties):
        if rc == 0:
            print("Connected to Mqtt Broker! topic " + self.__topic)
            client.subscribe(userdata, 1)
        else:
            # 只有当用户名或密码错误，才不进行自动重连。
            # 如果这里不使用disconnect()方法，那么loop_forever会一直进行重连。
            if rc == 134:
                self.__paho_client.disconnect()
            print("Failed to connect. return code :" + str(rc.value) + ", reason" + rc.getName())
    def _on_subscribe(self, client, userdata, mid, granted_qos, properties):
        print("Subscribed: " + str(mid) + " " + str(granted_qos) + " topic: " + self.__topic)
    def _on_message(self, client, userdata, message: mqtt.MQTTMessage):
        print("topic " + self.__topic + " Received message: " + message.payload.decode())
    def _on_disconnect(self, client, userdata, flags, rc, properties):
        print("Disconnect to Mqtt Broker. topic: " + self.__topic)
        # 断链后将客户端主动关闭，手动重连刷新时间戳
        try:
            self.__paho_client.disconnect()
        except Exception as e:
            print("Mqtt connection error. traceback: " + traceback.format_exc())
        self.connect()
    def close(self):
        if self.__paho_client is not None and self.__paho_client.is_connected():
            try:
                self.__paho_client.disconnect()
                print("Mqtt connection close")
            except Exception as e:
                print("paho client disconnect failed. exception: " + str(e))
        else:
            pass
```

MqttDemo代码如下：

```
from client_conf import ClientConf
from mqtt_client import MqttClient
import os
from typing import Optional
def main():
    client_conf = ClientConf()
    client_conf.host = "your ip host"
    client_conf.port = 8883
    client_conf.topic = "your mqtt topic"
    # mqtt接入凭据access_key可使用环境变量的方式注入
    client_conf.access_key = os.environ.get("MQTT_ACCESS_KEY")
    # mqtt接入凭据access_code可使用环境变量的方式注入
    client_conf.access_code = os.environ.get("MQTT_ACCESS_CODE")
    client_conf.instance_id = "your instance id"
    mqtt_client = MqttClient(client_conf)
    if mqtt_client.connect() != 0:
        print("init failed")
        return
if __name__ == "__main__":
    main()
```

#### 成功示例

接入成功后，客戶端打印信息如下：

**图1** python mqtt订阅接入成功示例   
![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001852193414.png "点击放大")

#### 相关文档

* [消息通信](/usermanual-iothub/iot_01_0045_1.html)
* [数据转发至Kafka存储](/usermanual-iothub/iot_bp_00012.html)
* [设备属性上报](/usermanual-iothub/iot_01_0326.html)
* [规则引擎](/usermanual-iothub/iot_01_0021.html)
* [AMQP队列告警配置](/usermanual-iothub/iot_01_0039.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)