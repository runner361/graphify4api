# 批量设备OTA升级

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_01553.html
> **提取时间**: 2026-08-15T00:05:06.410559
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备管理](https://support.huaweicloud.com/usermanual-iothub/iot_01_0123.html)/ [OTA升级](https://support.huaweicloud.com/usermanual-iothub/iot_01_002.html)/ 批量设备OTA升级

链接复制成功！

批量设备OTA升级
=========

#### 上传软固件包

创建批量设备软件、固件升级任务前需要上传软件升级包，平台支持两种方式上传软件、固件包：

1. 应用服务器通过调用“创建OTA升级包”API接口，创建OTA升级包，详情请参考[创建OTA升级包](https://support.huaweicloud.com/api-iothub/CreateOtaPackage.html)。
2. 通过控制台，在软固件升级页面上传软件、固件升级包，详情请参考[软固件包上传](https://support.huaweicloud.com/usermanual-iothub/iot_01_0155.html)。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   * 通过API接口创建的OTA升级包，只支持MQTT协议设备升级。
   * 升级包为OBS对象时，无论OBS桶是否配置了CDN域名加速功能，下发的升级包链接都为OBS链接地址。

#### 批量设备软件升级

用户对批量设备进行软件升级有两种方式：

1. 应用服务器通过调用的“创建软件升级任务”API接口，创建批量设备的升级任务，详情请参考[创建批量任务](https://support.huaweicloud.com/api-iothub/iot_06_v5_0045.html)。
2. 通过控制台，创建批量设备的软件升级任务。

下面将重点介绍通过控制台创建批量设备的软件升级任务。

1. 访问[设备接入服务](https://www.huaweicloud.com/product/iothub.html)，单击“管理控制台”进入设备接入控制台。选择您的实例，单击实例卡片进入。
2. 在左侧导航栏选择"设备 > 软固件升级"，单击“升级任务”。
3. 选择“软件升级”页签，单击“新建任务”按钮，进入新建软件升级任务页面。

   **图1** 软固件升级-新建软件升级任务   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001982816137.png "点击放大")
4. 设置“任务信息”，填写任务名称、执行时间、启用重试。

   启用重试后，可以设置重启次数和重启间隔。重启次数建议设置为2次，重启间隔设置为5分钟，即设备升级失败后，隔5分钟后会进行升级重试。

   **图2** 新建软件升级任务-基本信息   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001982698345.png "点击放大")
5. 选择需要升级的软件包。

   **图3** 新建软件升级任务-选择升级包   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001951020020.png "点击放大")
6. 选择需要升级的设备或者设备群组，然后单击“立即创建任务”。

   设备群组可以参考[群组和标签](https://support.huaweicloud.com/usermanual-iothub/iot_01_0020.html)创建需要升级的设备群组，并绑定对应的设备。

   **图4** 新建软件升级任务-选择设备群组   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001951021952.png "点击放大")
7. 创建完批量升级任务后，可以在软件升级任务列表中查看批量任务的执行结果。单击对应任务“详情”按钮，可以在“执行详情”界面查看每个设备的升级结果。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   如果升级任务正在执行中，是不允许删除任务的，如需删除，请先在任务列表中，手动停止任务后，再删除升级任务。

#### 批量设备固件升级

用户对批量设备进行固件升级有两种方式：

1. 应用服务器通过调用的“创建固件升级任务”API接口，创建批量设备的升级任务，详情请参考[创建批量任务](https://support.huaweicloud.com/api-iothub/iot_06_v5_0045.html)。
2. 通过控制台，创建批量设备的固件升级任务。

下面将重点介绍通过控制台创建批量设备的固件升级任务。

1. 访问[设备接入服务](https://www.huaweicloud.com/product/iothub.html)，单击“管理控制台”进入设备接入控制台。选择您的实例，单击实例卡片进入。
2. 在左侧导航栏选择"设备 > 软固件升级"，单击“升级任务”。
3. 在“固件升级”页签，单击“新建任务”按钮，进入新建固件任务页面。

   **图5** 软固件升级-新建固件升级任务   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001982729977.png "点击放大")
4. 设置“任务信息”，填写任务名称、执行时间、启用重试。

   启用重试后，可以设置重启次数和重启间隔。重启次数建议设置为2次，重启间隔设置为5分钟（最大重启次数为5次，最大重启间隔为1440分钟），即设备升级失败后，隔5分钟后会进行升级重试。

   **图6** 新建固件升级任务-基本信息   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001951057434.png "点击放大")
5. 选择需要升级的固件包。

   **图7** 新建固件升级任务-选择升级包   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001954982226.png "点击放大")
6. 选择需要升级的设备群组，然后单击“提交”。

   设备群组可以参考[群组和标签](https://support.huaweicloud.com/usermanual-iothub/iot_01_0020.html)创建需要升级的设备群组，并绑定对应的设备。

   **图8** 新建固件升级任务-选择设备群组   
   ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001990781397.png "点击放大")
7. 创建完批量升级任务后，可以在固件升级任务列表中查看批量任务的执行结果。单击对应任务“详情”按钮，可以在“执行详情”界面查看每个设备的升级结果。

   ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

   如果升级任务正在执行中，是不允许删除任务的，如需删除，请先在任务列表中，手动停止任务后，再删除升级任务。

#### 软固件升级失败原因

**物联网平台上报的失败原因：**

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 失败原因 | 原因解释 | 处理建议 |
| --- | --- | --- |
| Device Abnormal is not online | 设备异常未在线 | 请检查设备侧。 |
| Task Conflict | 任务冲突 | 请检查当前设备是否有软件升级、固件升级、日志收集或设备重启的任务正在进行。 |
| Waiting for the device online timeout | 等待设备上线超时 | 请检查设备侧。 |
| Wait for the device to report upgrade result timeout | 等待设备上报升级结果超时 | 请检查设备侧。 |
| Waiting for report device firmware version timeout | 等待上报设备固件版本超时 | 请检查设备侧。 |
| Waiting for report cellId timeout | 等待上报cellId超时 | 请检查设备侧。 |
| Updating timeout and query device version for check timeout | 等待升级结果超时，且等待设备版本信息超时 | 请检查设备侧。 |
| Waiting for device downloaded package timeout | 等待设备完成下载固件包超时 | 请检查设备侧。 |
| Waiting for device start to update timeout | 等待设备启动更新超时 | 请检查设备侧。 |
| Waiting for device start download package timeout | 等到设备开始下载固件包超时 | 请检查设备侧。 |

**设备上报的失败原因：**

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/expand-table.svg)

| 失败原因 | 原因解释 | 处理建议 |
| --- | --- | --- |
| Not enough storage for the new firmware package | 下载的固件包存储空间不足 | 请检查设备存储。 |
| Out of memory during downloading process | 下载过程中内存不足 | 请检查设备内存。 |
| Connection lost during downloading process | 下载过程中连接断开 | 请检查设备连接状态。 |
| Integrity check failure for new downloaded package | 下载的固件包完整性校验失败 | 请检查设备下载的固件包是否完整。 |
| Unsupported package type | 固件包类型不支持 | 请检查设备状态和厂商提供的固件包是否正确。 |
| Invalid URI | URI不可用 | 检查设备侧的固件包下载地址是否正确。 |
| Firmware update failed | 固件更新失败 | 请检查设备侧。 |

#### 常见问题

软/固件升级业务热点咨询问题如下，更多咨询问题请访问[OTA升级相关问题](https://support.huaweicloud.com/iothub_faq/iot_faq_01001.html)。

* [目标版本可以比当前版本低吗？](https://support.huaweicloud.com/iothub_faq/iot_faq_01001.html#section2)
* [软/固件包及其版本号如何获取？](https://support.huaweicloud.com/iothub_faq/iot_faq_01001.html#section3)
* [在软/固件升级任务中，业务处理是否会中断？](https://support.huaweicloud.com/iothub_faq/iot_faq_01001.html#section6)
* [常见的软/固件升级错误有哪些？](https://support.huaweicloud.com/iothub_faq/iot_faq_01001.html#section4)

#### 相关API接口

* [创建批量任务](https://support.huaweicloud.com/api-iothub/iot_06_v5_0045.html)
* [查询批量任务列表](https://support.huaweicloud.com/api-iothub/iot_06_v5_0028.html)
* [查询批量任务](https://support.huaweicloud.com/api-iothub/iot_06_v5_0017.html)

#### 相关文档

* [创建产品](/usermanual-iothub/iot_01_0054.html)
* [数据转发至GeminiDB Influx](/usermanual-iothub/iot_01_1005.html)
* [自定义模板示例](/usermanual-iothub/iot_01_0235.html)
* [AMQP转发](/usermanual-iothub/iot_01_0003.html)
* [应用侧对接](/usermanual-iothub/iot_02_15.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)