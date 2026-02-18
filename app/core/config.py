from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    dynamodb_endpoint: str = "http://localhost:8000"
    dynamodb_region: str = "us-east-1"
    dynamodb_table_name: str = "users"

    log_level: str = "INFO"
    log_json_format: bool = False


settings = Settings()
