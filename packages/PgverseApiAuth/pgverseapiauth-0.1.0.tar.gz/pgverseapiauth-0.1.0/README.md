# 项目介绍
本项目是python版本对接api平台的sdk。
sdk包括两个功能
1. 对于接口进行鉴权，对于不属于平台的api不进行服务
2. 限流，对于三方接口有qpm的限制，api平台会帮你做个限流。在请求鉴权接口会限流。
3. 记录api log以及费用记录。


#### 下载安装

pip 安装
pypi主页 https://pypi.org/project/pgver-api-auth/0.1.0/

```
pip install pgver-api-auth==0.1.0
```


#### 实现参考

[对于讯飞自己封装sdk参考](https://github.com/HuiDBK/SparkAISDK)
[阿里巴巴acm参考](https://github.com/alibaba/acm-sdk-python)


#### 调用实例

```python

if __name__ == "__main__":
    from api.common.code import error_code_range
    sdk = AuthSDK.init(appid=os.getenv("APPID"), apikey=os.getenv("APIKEY"), apisecret=os.getenv("APISECRET"))
    result = sdk.auth.check_quota(interface_id="9", thrid_app_key="app_key_123")
    print("Quota Check Result:", result)
    if(result.code != 0):
        if(result.code in error_code_range):
            print(result.code)
            print(result.msg)


    log_data = mock_log_dto()
    asyncio.run(sdk.log.save_log(log_data))

```