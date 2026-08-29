# 非$oc开头自定义Topic通信使用说明

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_02_9999.html
> **提取时间**: 2026-08-15T00:04:38.041310
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [消息通信](https://support.huaweicloud.com/usermanual-iothub/iot_01_0045_1.html)/ [自定义Topic通信](https://support.huaweicloud.com/usermanual-iothub/iot_02_9992.html)/ 非$oc开头自定义Topic通信使用说明

链接复制成功！

非$oc开头自定义Topic通信使用说明
====================

#### 使用流程&操作步骤

**图1** 非$oc开头自定义topic通信

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001853049712.png "点击放大")

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

* 为了适配新老客户的使用，策略默认放通所有“非$oc开头的自定义Topic通信”。新增的资源空间会默认加入策略“system\_default\_policy”，system\_default\_policy策略会允许所有Topic的订阅与发布。当业务场景不适用时，可以删除该策略。
* 值得注意的是，策略只会限制“非$oc开头的自定义Topic通信”。“$oc开头的自定义Topic”权限由产品下的设定决定。
* Topic策略是用于管理Topic黑白名单，若业务中不需要该功能，可跳过策略（步骤2、3）、直接使用。

1. 在平台创建产品与设备。详情可见：[创建产品](https://support.huaweicloud.com/usermanual-iothub/iot_01_0054.html)、[注册单个设备](https://support.huaweicloud.com/usermanual-iothub/iot_01_0031.html)。
2. 访问[设备接入服务](https://www.huaweicloud.com/product/iothub.html)，单击“管理控制台”进入设备接入控制台。选择您的实例，单击实例卡片进入。
3. 创建策略。用于控制放通哪些Topic进行订阅/发布。（可选）
   1. 进入策略页面。在左侧导航栏选择“设备 > 策略”。

      **图2** 设备策略-进入界面   
      ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001981577933.png "点击放大")
   2. 创建策略。在策略界面单击“创建策略”，按照业务填写策略参数，填写完成后单击“生成策略”。下图以允许主题“/v1/test/hello”发布及订阅为例。

      ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

      **表1** 参数说明

      |  |  |
      | --- | --- |
      | 所属资源空间 | **参数说明：**下拉选择所属的资源空间。如无对应的资源空间，请先创建[资源空间](https://support.huaweicloud.com/usermanual-iothub/iot_01_0006.html)。 |
      | 策略名称 | **参数说明：**自定义，如PolicyTest。  **取值范围：**长度不超过128，只允许字母、数字、下划线（\_）、连接符（-）的组合。 |
      | 资源 | **约束限制：**在MQTT主题发布与订阅中，需要以“topic:”作为参数前缀。比如说：禁止订阅/test/v1，则该参数填写 topic:/test/v1。 |
      | 操作 | **参数说明：**值为发布或订阅。发布代表MQTT设备端Publish请求，订阅代表MQTT设备端Subscribe请求。 |
      | 权限 | **参数说明：**值为允许或拒绝。用于允许或拒绝某topic的发布或订阅。 |
4. 绑定策略目标。用于指定设备/产品/资源空间可以使用该策略。策略可以从“资源空间”、“产品”、“设备”这3个范围进行绑定，被绑定的设备将遵循策略的要求允许或拒绝某Topic的发布或订阅。（可选）

   **图3** 设备策略-绑定设备   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001981497785.png "点击放大")

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

   **表2** 参数说明

   |  |  |
   | --- | --- |
   | 设备目标类型 | **参数说明：**下拉选择设备目标类型。类型有“资源空间”、“产品”、“设备”三种。这三种类型并不是互斥的，可以同时存在，比如说：绑定产品A与设备C（C是产品B下的设备）。  * 资源空间：实现多业务应用的分域管理，绑定后所选资源空间下的所有设备都将匹配该策略。可选择多个资源空间绑定。 * 产品：一个产品下一般有多个设备，绑定后所选产品下的所有设备都将匹配该策略，比起资源空间，绑定范围更小。可绑定一个或多个不同资源空间下的产品。 * 设备：绑定策略目标的最小单位，可绑定一个或多个不同资源空间、不同产品的设备。 |
   | 策略目标 | **参数说明：**选择对应的“策略目标类型”后，在“策略目标”的参数中会显示可选的数据，勾选需要绑定的即可。 |
5. 设备订阅/发布。定义成功后可以发布、订阅该Topic。没有绑定策略成功的自定义Topic无法订阅/发布。

#### 设备侧JAVA SDK使用示例

设备端可以通过集成华为云IoT提供的[设备侧SDK](https://support.huaweicloud.com/sdkreference-iothub/iot_02_0178.html)快速连接华为云IoTDA，并进行消息上报。以下示例为通过JAVA SDK实现设备连接到华为云IoTDA对自定义Topic“/test/deviceToCloud”进行发布、订阅。

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
   device.getClient().publishRawMessage(new RawMessage("/test/deviceToCloud", "hello", 1), new ActionListener() {
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
   device.getClient().subscribeTopic(new RawMessage("/test/deviceToCloud", new ActionListener() {
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

* [设备接入](/usermanual-iothub/iot_01_0127.html)
* [安全态势感知](/usermanual-iothub/iot_01_00303.html)
* [消息通信](/usermanual-iothub/iot_01_0045_1.html)
* [设备远程配置](/usermanual-iothub/iot_01_00302.html)
* [广播通信使用说明](/usermanual-iothub/iot_01_00121.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)