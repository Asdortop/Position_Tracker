from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # Database configuration
    DATABASE_URL: str

    # Security settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    KAFKA_TRADES_TOPIC: str = "transactions.enriched"
    KAFKA_CONSUMER_GROUP: str = "position-tracker-group"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()