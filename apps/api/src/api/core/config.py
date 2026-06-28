from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OPENAI_API_KEY: str 
    GOOGLE_API_KEY: str
    GROQ_API_KEY: str

config = Config()