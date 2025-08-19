# 提交短信

**功能说明:** 用于提交发送短信的常规方法

## 请求地址

`https://api.51welink.com/EncryptionSubmit/SendSms.ashx`

## 请求参数

| 参数名 | 参数类型 | 是否必传 | 参数描述 |
|---|---|---|---|
| Accountid | string | Y | 提交账户 |
| AccessKey | string | Y | 加密后的key,加密说明见下方 |
| Timestamp | long | Y | Unix时间戳,精确到秒,长度10,不能含有小数及L |
| ExtendNo | string | N | 企业代码,不超过12位数字,超出会被截断,数字串 |
| Random | long | Y | 随机数,大于等于1,小于等于9223372036854775807 |
| Productid | int | Y | 产品编码,供应商提供 |
| PhoneNos | string | Y | 接收号码间用英文半角逗号","隔开,触发产品一次只能提交一个,其他产品一次不能超过10万个号码 |
| Content | string | Y | 短信内容:不超过1000字符 |
| SendTime | datetime | N | 短信定时时间,格式: yyyy-MM-dd HH:mm:ss |
| Outid | string | N | 用户自定义参数,长度≤32,字符串格式 |

## AccessKey加密说明

AccessKey根据公式`sha256("AccountId=(账户名称)&PhoneNos=(第一个手机号码)&Password=(md5(密码原文+SMmsEncryptKey))&Random=(随机数)&Timestamp=(unix时间戳精确到秒)`)生成。
AccessKey串中的参数名称注意大小写和参数顺序,随机数是long类型,数值范围在1至9223372036854775807之间

**譬如:**

账户(Accountid): `51welink`
第一个手机号码(PhoneNos): `138****0005`
密码(Password): `password***`
固定的加密key: `SMmsEncryptKey`
随机数(Random): `6203922`
时间戳(Timestamp): `1532928860`

则MD5加密后的密码(password)为:

`MD5("password***SMmsEncryptKey")="4F1108FE9B50B8037D56446446F3513A"`, 必须为大写。

则凭证(AccessKey)为:

`sha256("AccountId=51welink&PhoneNos=138****0005&Password=4F1108FE9B50B8037D56446446F3513A&Random=6203922&Timestamp=1532928860")="bce988660a23f03bf330ede8cc2c22a23653778994ef0c55c772ee86d4bd24d7"`, 加密后的AccessKey为小写。

## 传参示例

```json
{
  "AccountId":"51welink",
  "AccessKey":"bce988660a23f03bf330ede8cc2c22a23653778994ef0c55c772ee86d4bd24d7",
  "Timestamp":1532928860,
  "Random":6203922,
  "ExtendNo":"",
  "Productid":1012***,
  "PhoneNos":"138****0005",
  "Content":"短信内容【微网通联】",
  "SendTime":"",
  "Outid":""
}
```

## 返回值字段说明

| 字段名 | 字段类型 | 描述 |
|---|---|---|
| Result | string | 返回状态值,返回succ标识提交成功 |
| Reason | string | 返回状态描述,参见文档错误码-返回值枚举部分 |
| Msgid | long | 信息批次号 |
| SplitCount | byte | 单条短信内容拆分条数 |

## 返回值示例

```json
{
  "Result":"succ",
  "Reason":"提交成功",
  "MsgId":190605100257008****,
  "SplitCount":1
}
```