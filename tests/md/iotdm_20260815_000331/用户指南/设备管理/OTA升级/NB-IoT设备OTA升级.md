# NB-IoT设备OTA升级

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_0027.html
> **提取时间**: 2026-08-15T00:05:03.020767
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备管理](https://support.huaweicloud.com/usermanual-iothub/iot_01_0123.html)/ [OTA升级](https://support.huaweicloud.com/usermanual-iothub/iot_01_002.html)/ NB-IoT设备OTA升级

链接复制成功！

NB-IoT设备OTA升级
=============

#### LwM2M协议设备软件升级流程

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001921395113.png)

LwM2M协议SOTA升级流程的详细说明：

1～2. 用户在设备管理服务的控制台上传软件包，并在控制台或者应用服务器上创建软件升级任务。

3. LwM2M设备上报数据，平台感知设备上线，触发升级协商流程。(超时时间为24小时)

4～5. 物联网平台向设备下发查询设备软件版本的命令，查询成功后，物联网平台根据升级的目标版本判断设备是否需要升级。（第4步等待设备上报软件版本，超时时间为3分钟）

* 如果返回的软件版本信息与升级的目标版本信息相同，则升级流程结束，不做升级处理。
* 如果返回的软件版本信息与升级的目标版本信息不同，则继续进行下一步的升级处理。

6. 物联网平台向设备订阅软件升级的状态。

7～8. 物联网平台查询终端设备所在的无线信号覆盖情况，获取小区ID、RSRP（Reference Signal Received Power，参考信号接收功率）和SINR（Signal to Interference Plus Noise Ratio，信号干扰噪声比）信息。（等待上报无线覆盖等级和小区ID，超时时间为3分钟左右）

* 查询成功：则根据如下方式计算可同时升级的并发数计算，并按照第10步进行处理。
  + 如下图所示，如果设备的RSRP强度和SINR强度均落在等级“0”中，则同时可以对该小区的50个相同信号覆盖区间的设备进行同时升级。
  + 如果设备的RSRP强度和SINR强度分别落在等级“0”和“1”中，则以信号较弱的等级“1”为准，则只能同时对该小区的10个设备进行升级。
  + 如果设备的RSRP强度和SINR强度分别落在等级“1”和“2”中，则以信号较弱的等级“2”为准，则只能同时对该小区的1个设备进行升级。
  + 如果设备的RSRP强度和SINR强度不在该3个等级范围内，且均可以查询到，则按照信号最弱覆盖等级“2”处理，则只能同时对1个设备进行升级。

    ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001875475782.png "点击放大")

    ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

    如果用户在软件升级中发现同时进行升级的设备数较少，则可以联系当地运营商检查和优化设备所在小区的无线覆盖情况。
* 查询失败：则按照流程第9步进行处理。

9. 物联网平台继续下发查询小区ID信息的命令，获取终端设备所在的小区ID信息。

* 如果查询成功：物联网平台支持同时对该小区的10个相同情况的设备进行软件升级。
* 如果查询失败：则升级失败。

10～12. 物联网平台通知设备有新的软件包版本，设备启动软件包的下载。软件包的下载按照分片的方式进行下载，支持断点续传功能，通过软件包分片中携带的“versionCheckCode”确定是否属于同一个软件包。下载完成后，设备知会物联网平台软件包已下载完毕。（第11步超时时间为60分钟）

13～14. 物联网平台向设备下发升级的命令，终端设备进行升级操作，升级完成后终端设备向物联网平台反馈升级的结果。（等待设备上报升级结果和升级状态，超时时间为30分钟）

15. 物联网平台向控制台/应用服务器通知升级的结果。

#### LwM2M协议设备固件升级流程

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001921554777.png)

LwM2M协议FOTA升级流程的详细说明：

1～2. 用户在设备接入服务的控制台上传固件包，并在控制台或者应用服务器上创建固件升级任务。

3. LwM2M设备上报数据，平台感知设备上线，触发升级协商流程。(超时时间为24小时)

4～5. 物联网平台向设备下发查询设备固件版本的命令，查询成功后，物联网平台根据升级的目标版本判断设备是否需要升级。（第4步等待设备上报固件版本，超时时间为3分钟）

* 如果返回的固件版本信息与升级的目标版本信息相同，则升级流程结束，不做升级处理。
* 如果返回的固件版本信息与升级的目标版本信息不同，则继续进行下一步的升级处理。

6～7. 物联网平台查询终端设备所在的无线信号覆盖情况，获取小区ID、RSRP（Reference Signal Received Power，参考信号接收功率）和SINR（Signal to Interference Plus Noise Ratio，信号干扰噪声比）信息。（等待上报无线覆盖等级和小区ID，超时时间为3分钟左右）

* 查询成功：则根据如下方式计算可同时升级的并发数计算，并按照第9步进行处理。
  + 如下图所示，如果设备的RSRP强度和SINR强度均落在等级“0”中，则同时可以对该小区的50个相同信号覆盖区间的设备进行同时升级。
  + 如果设备的RSRP强度和SINR强度分别落在等级“0”和“1”中，则以信号较弱的等级“1”为准，则只能同时对该小区的10个设备进行升级。
  + 如果设备的RSRP强度和SINR强度分别落在等级“1”和“2”中，则以信号较弱的等级“2”为准，则只能同时对该小区的1个设备进行升级。
  + 如果设备的RSRP强度和SINR强度不在该3个等级范围内，且均可以查询到，则按照信号最弱覆盖等级“2”处理，则只能同时对1个设备进行升级。

    ![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001875635658.png "点击放大")

    ![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

    如果用户在固件升级中发现同时进行升级的设备数较少，则可以联系当地运营商检查和优化设备所在小区的无线覆盖情况。
* 查询失败：则按照流程第8步进行处理。

8. 物联网平台继续下发查询小区ID信息的命令，获取终端设备所在的小区ID信息。

* 如果查询成功：物联网平台支持同时对该小区的10个相同情况的设备进行固件升级。
* 如果查询失败：则升级失败。

9. 物联网平台向设备订阅固件升级的状态。

10～11. 物联网平台向设备下发下载固件包的URL地址，通知设备下载固件包。终端设备根据该URL地址下载固件包，固件包的下载支持分片下载，下载完成后，设备知会物联网平台固件包已下载完毕。（第11步超时时间为60分钟）

12～13. 物联网平台向设备下发升级的命令，终端设备进行升级操作，升级完成后终端设备向物联网平台反馈升级结束。（等待设备上报升级结果和升级状态，超时时间为30分钟）

14～16. 物联网平台下发命令查询固件升级的结果，获取升级结果后，向终端设备取消订阅升级状态通知，并向控制台应用服务器通知升级的结果。

![](https://res-static.hc-cdn.cn/aem/content/dam/cloudbu-site/archive/china/zh-cn/support/resource/framework/v3/images/support-doc-revision-note.svg)说明：

在下载包中断的情况下，平台支持断点续传功能。

#### 固件升级失败原因

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

* [MQTT 华为云X.509证书认证设备使用证书策略发放示例](/usermanual-iothub/iot_03_0009.html)
* [设备请求引导消息](/usermanual-iothub/iot_03_0004.html)
* [IoTDA自定义策略](/usermanual-iothub/iot_01_0232.html)
* [Python SDK接入示例](/usermanual-iothub/iot_01_00100_7.html)
* [设备接收引导信息](/usermanual-iothub/iot_03_0005.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)