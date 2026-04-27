from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #服务名称
    app_name:str="ecom-agent-api"
    #版本号
    app_version :str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8001
    #开启调试模式，一般用在 Web 项目（比如 FastAPI、Flask、Django）里
    """
    开启后会有这些效果：
         代码报错时，浏览器 / 控制台会显示详细错误信息，方便你找 bug
         修改代码后，服务会自动重启，不用手动停了再开
         开发阶段用，上线时必须改成 False
    """
    debug:bool=True
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    # class config:
    #     env_file=".env"
settings=Settings()

