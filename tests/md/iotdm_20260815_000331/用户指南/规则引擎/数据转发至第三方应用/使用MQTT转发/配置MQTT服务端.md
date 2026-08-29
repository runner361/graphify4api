# 配置MQTT服务端

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_00112.html
> **提取时间**: 2026-08-15T00:05:32.432897
> **云提供商**: HUAWEI

*本文导读*

*展开导读*

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [规则引擎](https://support.huaweicloud.com/usermanual-iothub/iot_01_0021.html)/ [数据转发至第三方应用](https://support.huaweicloud.com/usermanual-iothub/iot_01_1000.html)/ [使用MQTT转发](https://support.huaweicloud.com/usermanual-iothub/iot_01_00110.html)/ 配置MQTT服务端

链接复制成功！

配置MQTT服务端
=========

本文介绍如何在物联网平台设置和管理MQTT服务端订阅。

1. 访问[设备接入服务](https://www.huaweicloud.com/product/iothub.html)，单击“管理控制台”进入设备接入控制台。选择您的实例，单击实例卡片进入。
2. 选择左侧导航栏的“规则 > 数据转发”，单击页面左侧的“创建规则”。

   **图1** 数据转发-新建规则   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001951372392.png "点击放大")
3. 参考下表填写参数后，单击“创建规则”。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

   **表1** 创建规则参数列表

   | 参数名 | 参数说明 |
   | --- | --- |
   | 规则名称 | 创建的规则名称。 |
   | 规则描述 | 对该规则的描述。 |
   | 数据来源 | * 设备：将操作设备的信息，如设备添加、设备删除、设备更新设置为数据来源。当数据来源选择“设备”时，不支持快速配置。 * 设备属性：将归属在某个资源空间下的设备上报给平台的属性值设置为数据来源。单击右侧的“快速配置”勾选需要转发的产品、属性、服务等数据。 * 设备消息：将归属在某个资源空间下的设备上报给平台的消息设置为转发目标。单击右侧的“快速配置”，仅转发指定Topic的数据。选择所属产品，填写Topic名称。您可以使用在产品详情页面[自定义的Topic](https://support.huaweicloud.com/usermanual-iothub/iot_02_9997.html)，也可以使用平台预置的Topic，可参考[Topic定义](https://support.huaweicloud.com/api-iothub/iot_06_v5_3004.html)。 * 设备消息状态：将设备和平台之间流转的设备消息状态变更设置为转发目标。设备消息状态详见[这里](https://support.huaweicloud.com/usermanual-iothub/iot_01_0331.html#ZH-CN_TOPIC_0000001504028806__section865254324320)。当数据来源选择“设备消息状态”，不支持快速配置。 * 设备状态：将归属在某个资源空间下的直连或非直连设备状态变更转发至其他服务。单击“快速配置”，您可以转发设备状态为“在线”、“离线”和“异常”的设备信息到其他服务。物联网平台直连设备状态详见[这里](https://support.huaweicloud.com/usermanual-iothub/iot_01_0065.html)。 * 批量任务：将批量任务状态的数据设置为数据来源。当数据来源选择“批量任务”时，不支持快速配置。 * 产品：将操作产品的信息，如产品添加、产品删除、产品更新设置为数据来源。当数据来源选择“产品”时，不支持快速配置。 * 设备异步命令状态：针对LwM2M/CoAP协议的设备，物联网平台支持下发异步命令给设备。将异步命令的状态变更设置为数据来源。物联网平台设备异步命令状态详见[这里](https://support.huaweicloud.com/usermanual-iothub/iot_01_0339.html#ZH-CN_TOPIC_0000001595655209__section36814865812)。当数据来源选择“设备异步命令状态”时，不支持快速配置。 * 运行日志：将MQTT设备的业务运行日志设置为数据来源。当数据来源选择“运行日志”时，不支持快速配置。 |
   | 触发事件 | 选择数据来源后，对应修改触发事件。 |
   | 资源空间 | 您可以选择单个资源空间或所有资源空间。当选择“所有资源空间”时，不支持快速配置。 |
   | SQL语句 | 您需要编辑处理消息数据的SQL，设置数据转发目的地。  单击“编辑SQL”，编写处理消息字段的SQL。  SQL编写方法，可参考[SQL语句](https://support.huaweicloud.com/usermanual-iothub/iot_01_0025.html)。  说明：  * 仅标准版实例和企业版实例支持SQL语句编辑，基础版实例不支持。 * 若使用快速配置，将自动生成查询语句。生成的查询语句将覆盖您之前编辑的SQL语句。 * 运行日志不支持SQL。 |
4. 在设置转发目标页面，单击“添加”，在弹出的页面中参考下表配置完参数后，单击“确认”。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

   | 参数名 | 参数说明 |
   | --- | --- |
   | 转发目标 | **参数说明：**选择“MQTT推送消息队列”。 |
   | 推送Topic | **参数说明：**输入要转发的MQTT Topic。  * Topic队列名称自定义且单个租户名下唯一，最大长度 128位，支持大小写英文字符串、数字、下划线（\_）、中划线（-）和斜杠（/），不支持除此之外的其他字符。 * 第一次使用的Topic会归属于该规则创建选择的资源空间，后续该Topic只能在该资源空间下使用，如果创建规则时选择的资源空间为"所有资源空间"，则该Topic在所有资源空间下都可以使用。 |

   **图2** 新建转发目标-转发至MQTT推送消息队列   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000002322454028.png "点击放大")
5. 完成完整的规则定义后，单击“启动规则”，实现数据转发至MQTT消息队列。

#### 相关文档

* [使用场景](/usermanual-iothub/iot_02_0004.html)
* [告警管理](/usermanual-iothub/iot_01_0030_3.html)
* [LwM2M/CoAP协议鉴权](/usermanual-iothub/iot_01_0208.html)
* [MQTT(S)协议-自定义鉴权](/usermanual-iothub/iot_01_0205.html)
* [设备证书](/usermanual-iothub/iot_01_0116.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)