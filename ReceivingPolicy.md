```
成功success返回规范：
{
  "version": "1.0",
  "type": "flight_search_response",
  "status": "success", //状态暂定成功success，错误error
  "results": { //客户搜票信息
	"airline": "CX", //航司
    "origin": "YVR", //起飞机场
    "destination": "HKG", //到达机场
    "depart_date": "20260127", //搜索起飞日期
    "cabin_class": "any", //舱等
	"stop_policy": "any", //中转策略 {不限:any, 直飞:direct}
    "total_flights": 7, //集合搜到的所有航票线路数量
    "redeemable_flights": 7, //搜到线路中可兑换线路数量
	"uuid": "exriveiv@gmail.com_20251212011653", // uuid(邮箱+请求时间时间戳)
	"ts_result": "20251212011901", // 生成结果的时间戳(年月日小时分钟秒钟)
  },
  "flights": [ //航票结果
    {
      "flight_no": "CX865",//航班号
      "depart_time": "00:05", //起飞时间
      "arrival_time": "06:25 +1", //到达时间
      "origin": "YVR", //起飞机场
      "destination": "HKG", //到达机场
      "stop": "0", //中转次数
      "stop_airports": "", //中转机场
      "miles": "27,000", //里程数
      "can_redeem": true //是否有票可兑换
    },
    {
      "flight_no": "BA84-BA31",
      "depart_time": "21:25",
      "arrival_time": "14:50 +2",
      "origin": "YVR",
      "destination": "HKG",
      "stop": "1",
      "stop_airports": "LHR",
      "miles": "47,000",
      "can_redeem": true
    }
  ]
}

错误error返回规范：
{
  "version": "1.0",
  "type": "flight_search_response",
  "status": "error",
  "results": {
	"airline": "CX", //航司
    "origin": "YVR", //起飞机场
    "destination": "HKG", //到达机场
    "depart_date": "20260127", //搜索起飞日期
    "cabin_class": "any", //舱等
	"stop_policy": "any", //中转策略 {不限:any, 直飞:direct}
    "total_flights": 0,
    "redeemable_flights": 0,
    "uuid": "exriveiv@gmail.com_20251212011653",
    "ts_result": "20251212011901"
  },
  "error": { //无航票结果，只返回错误结果
    "code": "PAGE_BLOCKED", //错误代码{TIMEOUT, PAGE_BLOCKED, CAPTCHA_REQUIRED, PARSING_FAILED, NETWORK_ERROR, UNKNOWN}
    "message": "Access denied / bot protection triggered", //风控：账号软封禁
  }
}
```
