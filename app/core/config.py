from typing import Optional, ClassVar
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings
from enum import Enum

class BaseConfig(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name":True 
    }

class LogLevel(str, Enum):
    DEBUG = "debug"  
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class CompressionType(str, Enum):
    GZIP = "gz"
    BZIP2 = "bz2"
    ZIP = "zip"

class AppSettings(BaseSettings):
    app_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        alias="APP_NAME" 
    )
    app_port: int = Field(
        ...,
        ge=1,
        le=65535,
        alias="APP_PORT" 
    )
    
    app_host: str = Field(default="0.0.0.0")
    app_reload: bool = Field(default=False)
    app_log_level: LogLevel = Field(default=LogLevel.INFO)
    log_format: str = Field(default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
    log_file: str = Field(default="logs/app.log")
    log_rotation: str = Field(default="1 day")
    log_compression: CompressionType = Field(default=CompressionType.GZIP)
    
    model_config = BaseConfig.model_config
class DatabaseSettings(BaseSettings):
    postgres_network_name: str = Field(..., alias="POSTGRES_NETWORK_NAME")
    postgres_user: str = Field(..., min_length=1, alias="POSTGRES_USER")
    postgres_password: str = Field(..., min_length=1, alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., min_length=1, alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(..., ge=1, le=65535, alias="POSTGRES_PORT")
    debug_sql: bool = Field(default=False)

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    model_config = BaseConfig.model_config
    
class DocsSettings(BaseSettings):
    docs_api_key: str = Field(..., alias="DOCS_API_KEY")
    
    model_config = BaseConfig.model_config
class JWTSettings(BaseSettings):
    secret_key: str = Field(..., min_length=32, alias="SECRET_KEY")
    refresh_token_secret_key: str = Field(..., min_length=32, alias="REFRESH_TOKEN_SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(..., alias="REFRESH_TOKEN_EXPIRE_MINUTES")
    
    model_config = BaseConfig.model_config

class VKSettings(BaseSettings):
    vk_oauth_url: HttpUrl = Field(
        default="https://id.vk.com/oauth2/auth", alias="VK_OAUTH_URL"
    )
    vk_api_url: HttpUrl = Field(
        default="https://api.vk.com/method/users.get", alias="VK_API_URL"
    )
    vk_auth_url: HttpUrl = Field(
        default="https://id.vk.com/auth", alias="VK_AUTH_URL"
    )
    vk_client_id: str = Field(..., min_length=1, alias="VK_CLIENT_ID")
    vk_client_secret: str = Field(..., min_length=1, alias="VK_CLIENT_SECRET")
    vk_redirect_uri: HttpUrl = Field(..., alias="VK_REDIRECT_URI")

    model_config = BaseConfig.model_config

class RedisSettings(BaseSettings):
    redis_network_name: str = Field(..., alias="REDIS_NETWORK_NAME")
    redis_port: int = Field(..., ge=1, le=65535, alias="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    redis_user: Optional[str] = Field(default=None, alias="REDIS_USER")
    redis_user_password: Optional[str] = Field(default=None, alias="REDIS_USER_PASSWORD")
    redis_ttl: int = Field(alias="REDIS_TTL")
    model_config = BaseConfig.model_config

class MinioSettings(BaseSettings):
    minio_root_user: str = Field(..., min_length=1, alias="MINIO_ROOT_USER")
    minio_root_password: str = Field(..., min_length=1, alias="MINIO_ROOT_PASSWORD")
    minio_default_buckets: str = Field(..., min_length=1, alias="MINIO_DEFAULT_BUCKETS")
    minio_network_name: str = Field(..., alias="MINIO_NETWORK_NAME")
    minio_port: int = Field(..., ge=1, le=65535, alias="MINIO_PORT")
    minio_endpoint_url: str = Field(..., alias="MINIO_ENDPOINT_URL")
    minio_bucket_name: str = Field(..., min_length=1, alias="MINIO_BUCKET_NAME")
    
    model_config = BaseConfig.model_config

class OllamaSettings(BaseSettings):
    ollama_url: HttpUrl = Field(..., alias="OLLAMA_URL")
    ollama_model_name: str = Field(..., min_length=1, alias="OLLAMA_MODEL_NAME")
    
    model_config = BaseConfig.model_config

class GigaChatSettings(BaseSettings):
    giga_auth_key: str = Field(..., min_length=1, alias="GIGA_AUTH_KEY")
    giga_client_id: str = Field(..., min_length=1, alias="GIGA_CLIENT_ID")
    giga_scope: str = Field(default="GIGACHAT_API_PERS", alias="GIGA_SCOPE")
    giga_oauth_url: HttpUrl = Field(..., alias="GIGA_OAUTH_URL")
    giga_api_url: HttpUrl = Field(..., alias="GIGA_API_URL")
    
    model_config = BaseConfig.model_config

class ChromaSettings(BaseSettings):
    chroma_network_name: str = Field(..., alias="CHROMA_NETWORK_NAME")
    chroma_port: int = Field(..., ge=1, le=65535, alias="CHROMA_PORT")
    chroma_collection_name: str = Field(..., alias="CHROMA_COLLECTION_NAME")
    
    model_config = BaseConfig.model_config
       