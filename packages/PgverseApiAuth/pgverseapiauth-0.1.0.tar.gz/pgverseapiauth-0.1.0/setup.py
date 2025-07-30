from setuptools import setup, find_packages

setup(
    name="PgverseApiAuth",  # 包名
    version="0.1.0",  # 版本号
    description="A short description of your package",  # 简要描述
    long_description=
        """
        # 项目介绍
        本项目是python版本对接api平台的sdk。
        sdk包括两个功能
        1. 对于接口进行鉴权，对于不属于平台的api不进行服务
        2. 限流，对于三方接口有qpm的限制，api平台会帮你做个限流。在请求鉴权接口会限流。
        3. 记录api log以及费用记录。
        
        
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
        """,  # 详细描述
    long_description_content_type="text/markdown",  # 描述内容类型
    author="Your Name",  # 作者
    author_email="jingzhi.lu@pgverse.ai",  # 作者邮箱
    url="http://gitlab.os.hi.cn:60080/pgv_base/api-platform-auth-sdk#",  # 项目主页
    packages=find_packages("api"),  # 包含的包
    package_dir={"": "api"},  # 包的根目录
    include_package_data=True,  # 包含非代码文件
    install_requires=[  # 依赖的包
        "requests>=2.24.0"
    ],
    classifiers=[  # 分类信息
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)