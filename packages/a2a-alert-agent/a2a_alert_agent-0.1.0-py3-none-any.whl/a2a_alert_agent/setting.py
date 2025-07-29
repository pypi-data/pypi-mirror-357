"""Base settings for MCP and Gateway."""


from pydantic_settings import BaseSettings, SettingsConfigDict


class AIServiceKeySettings(BaseSettings):
    """Settings for AIServiceKey."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )
    openai_api_key: str
    anthropic_api_key: str
    tavily_api_key: str
    google_api_key: str
    google_genai_use_vertexai: bool = False


ai_service_key_settings = AIServiceKeySettings()


class LoggerSettings(BaseSettings):
    """Settings for Logger."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="LOG_", env_file=".env", extra="ignore"
    )
    config_file: str = "logging.conf"
    level: str = "INFO"


logger_settings = LoggerSettings()


class SystemMCPServerSettings(BaseSettings):
    """Settings for System MCP Server."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="SYS_MCP_SERVER_", env_file=".env", extra="ignore"
    )

    file_system_root_path: str = "/application/files"
    slack_bot_token: str | None = None
    slack_team_id: str | None = None


system_mcp_server_settings = SystemMCPServerSettings()


class S3Settings(BaseSettings):
    """Settings for AWS S3."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="AWS_", env_file=".env", extra="ignore"
    )
    access_key_id: str
    secret_access_key: str
    default_region: str
    s3_bucket_name: str
    s3_bucket_root: str


s3_settings = S3Settings()
