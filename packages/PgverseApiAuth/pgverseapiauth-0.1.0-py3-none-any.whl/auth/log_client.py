import requests
from datetime import datetime
from typing import Optional, Any
from api.config.AppConfig import config
from api.utils.sign_utils import generate_sign


class ApiLogDTO:
    """
    对应 Java 中的 ApiLogDO，用于封装日志数据

    字段说明：
    - business_id: 接口编号
    - interface_id: 接口唯一ID
    - trace_id: 全局唯一的日志记录ID
    - cost_price: 花费费用
    - charge_type: 收费方式
    - cost_count: 调用次数
    - cost_seconds: 消耗时长（秒）
    - cost_in_token: 输入 token 数量
    - cost_out_token: 输出 token 数量
    - code: 请求状态码
    """

    def __init__(
            self,
            business_id: str,
            interface_id: int,
            cost_price: float,
            charge_type: int,
            code: int,
            cost_count: Optional[int]= None,
            cost_seconds: Optional[int]= None,
            cost_in_token: Optional[int]= None,
            cost_out_token: Optional[int]= None,
            trace_id: Optional[str] = None,
            app_id: Optional[str] = None,
            timestamp: Optional[str] = None,
    ):
        self.business_id = business_id
        self.interface_id = interface_id
        self.trace_id = trace_id
        self.cost_price = cost_price
        self.charge_type = charge_type
        self.cost_count = cost_count
        self.cost_seconds = cost_seconds
        self.cost_in_token = cost_in_token
        self.cost_out_token = cost_out_token
        self.code = code
        self.app_id = app_id or config.appid  # 使用全局配置中的 appid
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """转换为 JSON 可序列化字典"""
        return {
            "businessId": self.business_id,
            "interfaceId": self.interface_id,
            "traceId": self.trace_id,
            "appId": self.app_id,
            "costPrice": self.cost_price,
            "chargeType": self.charge_type,
            "costCount": self.cost_count,
            "costSeconds": self.cost_seconds,
            "costInToken": self.cost_in_token,
            "costOutToken": self.cost_out_token,
            "code": self.code,
            "timestamp": self.timestamp,
        }


class ApiLogClient:
    def __init__(self, config):
        self.config = config

    async def save_log(self, log_dto: ApiLogDTO):
        """
        保存 API 调用日志
        :param log_dto: 日志数据对象
        :return: 响应结果
        """
        api_path = "/open-api/v1/log"
        url = f"http://{self.config.auth_ip}:{self.config.auth_port}{api_path}"
        sign = generate_sign(api_path, self.config.apisecret)
        headers = {
            # "Authorization": f"Bearer {self.config.apikey}",
            "X-App-Id": self.config.appid,
            "X-App-Key": self.config.apikey,
            "X-Signature": sign,
            "X-Api-type": "1",
            "sign-check": "0"
        }
        payload = log_dto.to_dict()
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
