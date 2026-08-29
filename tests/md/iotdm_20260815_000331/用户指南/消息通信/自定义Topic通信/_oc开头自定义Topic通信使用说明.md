# $oc开头自定义Topic通信使用说明

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_02_9998.html
> **提取时间**: 2026-08-15T00:04:39.370551
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [消息通信](https://support.huaweicloud.com/usermanual-iothub/iot_01_0045_1.html)/ [自定义Topic通信](https://support.huaweicloud.com/usermanual-iothub/iot_02_9992.html)/ $oc开头自定义Topic通信使用说明

链接复制成功！

$oc开头自定义Topic通信使用说明
===================

#### 使用流程&操作步骤

**图1** $oc开头自定义topic通信

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001852337674.png "点击放大")

1. 访问[设备接入服务](https://www.huaweicloud.com/product/iothub.html)，单击“管理控制台”进入设备接入控制台。选择您的实例，单击实例卡片进入。
2. 创建产品：参考[创建产品](https://support.huaweicloud.com/usermanual-iothub/iot_01_0054.html)流程。
3. 设定$oc开头自定义Topic。在产品详情页中创建一个自定义Topic，Topic前缀固定为：$oc/devices/{device\_id}/user/。
   1. 选择MQTT协议类产品，在产品详情页中，选择“Topic管理 > 自定义Topic”，单击“新增自定义Topic”。

      **图2** Topic管理-自定义Topic   
      ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001981309841.png "点击放大")
   2. 在弹出的页面中，选择设备操作权限，填写Topic名称。

      **图3** Topic管理-新增自定义Topic   
      ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001950350270.png "点击放大")

      ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

      **表1** 页面参数说明

      | 参数名称 | 描述 |
      | --- | --- |
      | Topic名称 | Topic的前缀已经规定好，固定为：$oc/devices/{device\_id}/user/，其中{device\_id}为标识符变量，实际发布和订阅过程中需要替换为实际的设备ID。用户自定义Topic的格式必须以“/”进行分层。  长度限制为1-64位，只允许输入数字、大小写字母、下划线、斜杠符。其中，斜杠符不能连续。  说明：  自定义Topic不支持自定义变量，例如$oc/devices/{device\_id}/user/setting/{type}，其中的{type}为自定义变量，当前不支持这种使用方式。 |
      | 设备操作权限 | * 发布：设备侧消息上报时，可按配置中自定义的Topic进行消息上报；数据流转时，设备消息中会携带Topic参数标识该消息从哪个Topic上报。 * 订阅：应用侧消息下发时，可在消息内容中指定Topic；消息发往设备时，可以根据指定的Topic下发。 * 发布和订阅：同时具备发布和订阅的权限。 |
      | 描述 | 关于该Topic的描述。 |
   3. 单击“确定”，完成新增自定义Topic。自定义Topic添加成功后，您可以在自定义Topic列表执行修改和删除操作。
4. 创建设备：在该产品下创建设备。创建的设备将继承产品设定的自定义Topic。详情可见：[注册单个设备](https://support.huaweicloud.com/usermanual-iothub/iot_01_0031.html)流程。
5. 设备订阅/发布：查看[使用自定义Topic进行通信](https://support.huaweicloud.com/bestpractice-iothub/iot_bp_0019.html)的最佳实践，了解自定义Topic的发布与订阅的使用。

#### 设备侧JAVA SDK使用示例

设备端可以通过集成华为云IoT提供的[设备侧SDK](https://support.huaweicloud.com/sdkreference-iothub/iot_02_0178.html)快速连接华为云IoTDA，并进行消息上报。以下示例为通过JAVA SDK实现设备连接到华为云IoTDA进行发布、订阅自定义Topic。以订阅"$oc/devices/" + device.getDeviceId() + "/user/wpy"为例。

1. 配置设备侧SDK的Maven依赖。

   ```
   <dependency>
   	<groupId>com.huaweicloud</groupId>
   	<artifactId>iot-device-sdk-java</artifactId>
   	<version>1.1.4</version>
   </dependency>
   ```
2. 配置设备侧SDK，设备连接参数。

   ```
   //加载iot平台的ca证书，获取链接参考：证书资源。
   URL resource = MessageSample.class.getClassLoader().getResource("ca.jks");
   File file = new File(resource.getPath());

   //注意格式为：ssl://域名信息:端口号。
   //域名获取方式：登录华为云IoTDA控制台左侧导航栏“总览”页签，在选择的实例基本信息中，单击“接入信息”。选择8883端口对应的接入域名。
   String serverUrl = "ssl://<localhost>:8883";
   //在IoT平台创建的设备ID。
   String deviceId = "<deviceId>";
   //设备ID对应的密钥。
   String deviceSecret = "<secret>";
   //初始化设备连接
   IoTDevice device = new IoTDevice(serverUrl, deviceId, deviceSecret, file);
   if (device.init() != 0) {
       return;
   }
   ```
3. 上报设备消息：

   ```
   device.getClient().publishRawMessage(new RawMessage( "$oc/devices/" + device.getDeviceId() + "/user/wpy", "hello", 1), new ActionListener() {
       @Override
       public void onSuccess(Object context) {
           System.out.println("reportDeviceMessage success: ");
       }
       @Override
       public void onFailure(Object context, Throwable var2) {
           System.out.println("reportDeviceMessage fail: " + var2);
       }
   });
   ```
4. 订阅topic：

   ```
   device.getClient().subscribeTopic(new RawMessage("$oc/devices/" + device.getDeviceId() + "/user/wpy", new ActionListener() {
       @Override
       public void onSuccess(Object context) {
           System.out.println("subscribeTopic success: ");
       }
       @Override
       public void onFailure(Object context, Throwable var2) {
           System.out.println("subscribeTopic fail: " + var2);
       }
   }, 0);
   ```

#### 相关文档

* [MQTT 华为云证书注册组发放示例](/usermanual-iothub/iot_03_00010.html)
* [概述](/usermanual-iothub/iot_01_0206.html)
* [Node.js Demo使用说明](/usermanual-iothub/iot_01_00117.html)
* [转发方式概述](/usermanual-iothub/iot_01_00140.html)
* [部署插件](/usermanual-iothub/iot_01_0136.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)