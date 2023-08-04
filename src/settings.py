from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    """This fields rewritten variables by env file"""
    server_host: str = '127.0.0.1'
    server_port: int = 8000


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8'
)
