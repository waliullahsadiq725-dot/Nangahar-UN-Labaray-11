from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Nangarhar University Digital Library API"
    environment: str = "production"
    secret_key: str = "CHANGE_THIS_SECRET_KEY"
    access_token_expire_minutes: int = 720
    database_url: str = "sqlite:///./nudl.db"
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 30
    cors_origins: str = "*"
    auto_create_tables: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self):
        return ["*"] if self.cors_origins.strip() == "*" else [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
