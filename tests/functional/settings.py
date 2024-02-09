import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    app_url: str
    elastic_host: str
    elastic_port: str
    elastic_dsn: str
    elastic_indexes: str

settings = Settings()