from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DSN: str
    ELASTICSEARCH_DSN: str
    ELASTICSEARCH_INDEX: str

    class Config:
        env_file = ".env"


settings = Settings()
