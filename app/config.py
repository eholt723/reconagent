from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    tavily_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    database_path: str = "research_history.db"

    class Config:
        env_file = ".env"


settings = Settings()
