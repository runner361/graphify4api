# SQL语句

> **来源**: https://support.huaweicloud.com/usermanual-iothub/iot_01_0025.html
> **提取时间**: 2026-08-15T00:05:14.632810
> **云提供商**: HUAWEI

更新时间：2026-06-10 GMT+08:00

[查看PDF](https://support.huaweicloud.com/usermanual-iothub/usermanual-iothub-pdf.pdf)

[分享](javascript:void(0);)

* [微博](javascript:void(0);)
* [微信](javascript:void(0);)
* [复制链接](javascript:void(0);)

  复制链接到剪贴板

链接复制成功！

SQL语句
=====

创建数据转发规则时，需要编写SQL来解析和处理设备上报的JSON数据，JSON数据具体格式参考[数据流转](https://support.huaweicloud.com/api-iothub/iot_06_v5_01200.html)。本文主要介绍如何编写数据转发规则的SQL表达式。

#### SQL语句

SQL语句由SELECT子句和WHERE子句组成，每个子句不能大于500个字符，暂不支持中文等其他字符集。SELECT子句和WHERE子句里的内容大小写敏感，SELECT和WHERE，AS等关键字大小写不敏感。

以设备消息上报为SQL源数据示例:

```
{
  "resource" : "device.message",
  "event" : "report",
  "event_time" : "20151212T121212Z",
  "notify_data" : {
    "header" : {
      "device_id" : "********",
      "product_id" : "ABC123456789",
      "app_id" : "********",
      "gateway_id" : "********",
      "node_id" : "ABC123456789",
      "tags" : [ {
        "tag_value" : "testTagValue",
        "tag_key" : "testTagName"
      } ]
    },
    "body" : {
      "topic" : "topic",
      "content" : {
          "temperature" : 40,
          "humidity" : 24
      }
    }
  }
}
```

在源数据中，body中的content是设备消息上报的数据，设置当设备上报数据中temperature大于38时触发条件，并筛选出device\_id、content，不需要任何其他字段时，SQL语句示例如下：

```
SELECT notify_data.header.device_id AS device_id, notify_data.body.content WHERE notify_data.body.content.temperature > 38
```

当设备上报消息中temperature大于38度时，会触发转发，转发后的数据格式如下：

```
{
    "device_id": "********",
    "notify_data.body.content" : {
          "temperature" : 40,
          "humidity" : 24
     }
}
```

#### SELECT子句

SELECT子句由SELECT后跟多个SELECT子表达式组成，子表达式可以为\*，JSON变量，字符串常量或整数常量。JSON变量后跟一个AS关键字和AS变量，长度不超过32个字符。如果使用常量或函数，则必须使用AS指定名称。

* JSON变量

  JSON变量支持大小写字母，数字，下划线和中划线，为了和减号的意思区分，当使用中划线的时候，请将JSON变量使用双引号进行引用，如："msg-type"。

  **Json变量抽取嵌套结构体的数据**

  ```
  {
    "a":"b"，
    "c": {
      "d" : "e"
    }
  }
  ```

  c.d 即可抽取出字符串e，可以多层嵌套。
* AS变量

  AS变量由大小写字母组成，大小写敏感。目前支持[a-zA-Z\_-]\*的模式，如果使用中划线，需要使用双引号进行引用。
* 常数整数

  正如标准的SQL一样，SELECT支持常数整数，常数后必须跟AS子句，如

  ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

  常数整数的大小范围：-2147483648~2147483647

  ```
  SELECT 5 AS number
  ```
* 常数字符串

  正如标准的SQL一样，SELECT支持常数字符串，目前支持[a-zA-Z\_-]\*的模式，需要使用单引号进行引用，常数后必须跟AS子句，如

  ![](https://support.huaweicloud.com/usermanual-iothub/public_sys-resources/note_3.0-zh-cn.png) 

  字符串长度范围不能超过50

  ```
  SELECT 'constant_info' AS str
  ```

#### WHERE

在WHERE子句中，您可以用JSON变量进行布尔运算，进行一些非空判断，然后使用AND， OR关键字把结果组合起来。

* **比较运算符 >、<、>=、<=、=****、<>**

  比较运算符可以用于WHERE子句中，当且仅当JSON变量的值为常量整数时，可以进行两个JSON变量的比较或者JSON变量和常量的比较。如果两个JSON变量IS NULL成立，那么=比较结果为false。比较运算符也可以用于常量和常量的比较。也可以通过AND或者OR来连接起来运算。

  比如

  ```
  WHERE data.number > 5  -- 提取出json表达式大于5的信息
  WHERE data.tag < 4  -- 提取出json表达式中小于4的信息
  WHERE data.number >= 5 AND data.tag <= 4  -- 提取出json表达式data.number大于等于5的信息并且json表达式data.tag中小于等于4的信息
  WHERE data.number = 5 OR data.tag = 4  -- 提取出json表达式data.number等于5的信息或者json表达式data.tag中等于4的信息
  WHERE data.number <> 5  -- 提取出json表达式不等于5的信息
  ```
* **算术运算符** **+、-、\*、/**

  算术运算符可以用于对数值进行计算。

  比如

  ```
  WHERE data.number + 2 > 5  -- 提取`number`加2后大于5的信息
  WHERE data.tag - 1 < 3  -- 提取`tag`减1后小于3的信息
  WHERE data.price * 2 > 100  -- 提取`price`乘以2后大于100的信息
  WHERE data.total / data.count > 10  -- 提取`total`除以`count`后大于10的信息
  ```
* **模式匹配运算符** **LIKE**

  用于判断一个字符串是否符合指定的模式。

  **通配符：**

  + %：匹配任意长度的字符串（包括空字符串）。
  + \_：匹配任意单个字符。

  比如

  ```
  WHERE data.name LIKE 'A%'  -- 提取`name`以'A'开头的数据
  WHERE data.description LIKE '%test%'  -- 提取`description`包含'test'的数据
  WHERE data.email NOT LIKE '%.com'  -- 提取`email`不以'.com'结尾的数据
  WHERE data.name LIKE 'a_b' -- 匹配所有长度为 3 且第二个字符为任意单个字符的字符串，例如 abb、acb
  ```
* **字符串连接运算符** **||**

  字符串连接运算符用于将两个或多个字符串拼接成一个字符串。

  比如

  ```
  WHERE data.first_name || ' ' || data.last_name = 'John Doe'  -- 提取`first_name`和`last_name`拼接后等于'John Doe'的数据
  ```

* **为空判断 IS NULL， IS NOT NULL**

  为空判断可以用在WHERE子句中，如果JSON变量抽取不到数据，或者抽取到的数组为空，那么IS NULL成立，反之IS NOT NULL成立。

  ```
  WHERE data IS NULL
  ```
* **集合运算符 IN， NOT IN**

  集合运算符可以用于WHERE子句中，如果目标值在指定值集合中，则IN成立，NOT IN反之。IN运算符支持字符串和数字，IN集合只支持常量且各集合元素值类型必须一致，集合元素值类型与目标值类型必须一致。

  ```
  WHERE notify_data.header.product_id IN ('productId1','productId2')
  ```

#### 使用限制

**表1** SQL语句使用限制

| 对象 | 限制 |
| --- | --- |
| SELECT子句 | 500个字符 |
| WHERE子句 | 500个字符 |
| AS子句 | 10个AS子句 |
| JSON数据最大深度 | 400层 |

#### 调试SQL语句

物联网平台提供SQL在线调试功能。调试方法如下。

1. 编写SQL后，单击“调试语句”。
2. 在SQL调试对话框的调试参数页签下，输入用于调试数据，然后单击“启动调试”。

#### 函数列表

规则引擎提供多种函数，您可以在编写SQL时使用这些函数，实现多样化数据处理。

**表2** 函数列表

| 函数名称 | 携带参数 | 用途 | 返回值类型 | 限制 |
| --- | --- | --- | --- | --- |
| GET\_TAG | String tagKey | 获取指定tag\_key对应的tag\_value。   ``` GET_TAG('testTagName') ``` | 字符串 | - |
| CONTAINS\_TAG | String tagKey | 判断是否包含指定tag\_key。   ``` CONTAINS_TAG('testTagName') ``` | 布尔值 | - |
| GET\_SERVICE | String serviceId，boolean fuzzy | 获取service，若fuzzy为false或者不填，则获取指定service\_id的service，若fuzzy为true，则通过模糊匹配查询service，如果您在一个消息体里有多个service\_id相同的service，结果目前不保证。   ``` GET_SERVICE('Battery',true) ``` | Json结构体格式 | 只能在属性上报时使用 |
| GET\_SERVICES | String serviceId，boolean fuzzy | 获取services，若fuzzy为false或者不填，获取指定service\_id的services，若fuzzy为true，则通过模糊匹配查询services。查询结果将汇合为一个数组。   ``` GET_SERVICES('Battery',true) ``` | JSON数组格式 | 只能在属性上报时使用 |
| CONTAINS\_SERVICES | String serviceId，boolean fuzzy | 若fuzzy为false或者不填，则判断是否存在指定service\_id。若fuzzy为true，则使用模糊匹配的方式判断属性中的service\_id是否包含指定参数。   ``` CONTAINS_SERVICES('Battery',true) ``` | 布尔值 | 只能在属性上报时使用 |
| GET\_SERVICE\_PROPERTIES | String serviceId | 获取指定service\_id的service中的properties字段。   ``` GET_SERVICE_PROPERTIES('Battery') ``` | Json结构体格式 | 只能在属性上报时使用 |
| GET\_SERVICE\_PROPERTY | String serviceId, String propertyKey | 获取指定service\_id的service中的properties中指定属性的值。  示例：   ``` GET_SERVICE_PROPERTY('Battery','batteryLevel') ``` | 字符串 | 限制只能在属性上报时使用 |
| STARTS\_WITH | String input, String prefix | 判断input的值是否以prefix开头。   ``` STARTS_WITH('abcd','abc') STARTS_WITH(notify_data.header.device_id,'abc') STARTS_WITH(notify_data.header.device_id,notify_data.header.product_id) ``` | 布尔值 | - |
| ENDS\_WITH | String input, String suffix | 判断input的值是否以suffix结尾。   ``` ENDS_WITH('abcd','bcd') ENDS_WITH(notify_data.header.device_id,'abc') ENDS_WITH(notify_data.header.device_id,notify_data.header.node_id) ``` | 布尔值 | - |
| CONCAT | String input1, String input2 | 用于连接字符串，返回连接后的字符串。   ``` CONCAT('ab','cd') CONCAT(notify_data.header.device_id,'abc') CONCAT(notify_data.header.product_id,notify_data.header.node_id) ``` | 字符串 | - |
| REPLACE | String input, String target, String replacement | 对字符串某部分值进行替换。即用replacement替换input中的target。   ``` REPLACE(notify_data.header.node_id,'nodeId','IMEI') ``` | - | - |
| SUBSTRING | String input, int beginIndex, int endIndex(required=false) | 获取字符串的子串，即返回input从beginIndex（包含）到endIndex（不包含）的子字符串。  说明：endIndex非必填。   ``` SUBSTRING(notify_data.header.device_id,3) SUBSTRING(notify_data.header.device_id,3,12) ``` | - | - |
| LOWER | String input | 将input中的值全部转换成小写   ``` LOWER(notify_data.header.app_id) ``` | - | - |
| UPPER | String input | 将input中的值全部转换成大写   ``` UPPER(notify_data.header.app_id) ``` | - | - |