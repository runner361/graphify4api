# MQTT设备OTA升级

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_0047.html
> **提取时间**: 2026-08-15T00:05:05.389237
> **云提供商**: HUAWEI

[文档首页](/index.html)/ [设备接入 IoTDA](https://support.huaweicloud.com/iothub/index.html)/ [用户指南](https://support.huaweicloud.com/usermanual-iothub/iot_01_0015.html)/ [设备管理](https://support.huaweicloud.com/usermanual-iothub/iot_01_0123.html)/ [OTA升级](https://support.huaweicloud.com/usermanual-iothub/iot_01_002.html)/ MQTT设备OTA升级

链接复制成功！

MQTT设备OTA升级
===========

#### MQTT协议设备软件升级流程

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001921421361.png)

MQTT协议SOTA升级流程的详细说明：

1～2. 用户在设备管理服务的控制台上传软件包，并在控制台或者应用服务器上创建软件升级任务。

3. 平台感知设备是否在线，当设备在线时立即触发升级协商流程。当设备不在线时，等待设备上线[订阅升级Topic](https://support.huaweicloud.com/api-iothub/iot_06_v5_3028.html)，平台感知设备上线，触发升级协商流程。

4~5. 平台向设备下发查询设备软件版本号的命令，查询成功后，物联网平台根据升级的目标版本判断设备是否需要升级 。（第5步超时时间3分钟）

* 如果返回的软件版本信息与升级的目标版本信息相同，则升级流程结束，不做升级处理，升级任务置为成功。
* 如果返回的软件版本信息与升级的目标版本信息不同，且该版本号支持升级，则继续进行下一步的升级处理。

6~7. 物联网平台下发下载包URL参考[平台下发升级通知](https://support.huaweicloud.com/api-iothub/iot_06_v5_3030.html)，token及包的相关信息，用户根据下载包URL和token通过HTTPS协议来下载软件包，24小时后token无效。（下载包和升级状态上报超时时间为24小时）

8. 终端设备进行下载包升级操作，升级完成后终端设备向物联网平台反馈升级的结果。(设备升级完成后返回的版本号和设置的版本一致为成功)

9. 物联网平台向控制台/应用服务器通知升级的结果。

#### MQTT协议固件升级流程

![](https://support.huaweicloud.com/usermanual-iothub/figure/zh-cn_image_0000001921581025.png)

MQTT协议FOTA升级流程的详细说明：

1～2. 用户在设备接入服务的控制台上传固件包，并在控制台或者应用服务器上创建固件升级任务。

3. 平台感知设备是否在线，当设备在线时立即触发升级协商流程。当设备不在线时，等待设备上线[订阅升级Topic](https://support.huaweicloud.com/api-iothub/iot_06_v5_3028.html)，平台感知设备上线，触发升级协商流程。（等待设备上线时间25小时以内）

4~5. 平台向设备下发查询设备固件版本号的命令，查询成功后，物联网平台根据升级的目标版本判断设备是否需要升级 。（第5步超时时间3分钟）

* 如果返回的固件版本信息与升级的目标版本信息相同，则升级流程结束，不做升级处理，升级任务置为成功。
* 如果返回的固件版本信息与升级的目标版本信息不同，且该版本号支持升级，则继续进行下一步的升级处理。

6~7. 物联网平台下发下载包URL参考[平台下发升级通知](https://support.huaweicloud.com/api-iothub/iot_06_v5_3030.html)，token及包的相关信息，用户根据下载包URL和token通过HTTPS协议来下载升级包，24小时后token无效。（下载包和升级状态上报超时时间为24小时）

8. 终端设备进行下载包升级操作，升级完成后终端设备向物联网平台反馈升级的结果。(设备升级完成后返回的版本号和设置的版本一致为成功)

9. 物联网平台向控制台/应用服务器通知升级的结果。

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

* [文件上传](/usermanual-iothub/iot_01_0033.html)
* [数据转发至BCS可信上链](/usermanual-iothub/iot_bp_00015.html)
* [Android SDK接入示例](/usermanual-iothub/iot_01_00100_6.html)
* [权限管理](/usermanual-iothub/iot_01_0230.html)
* [HJ212协议接入](/usermanual-iothub/iot_01_0133.html)

### 

### 文档内容是否对您有帮助？

[有帮助](javascript:void(0))   [没帮助](javascript:void(0))

提供反馈 

0/500

[直接提交](javascript:void(0)) [取消](javascript:void(0)) 

[云宝助手提问](https://www.huaweicloud.com/ai-assistant/index.html)[云社区提问](https://bbs.huaweicloud.com/forum/)