from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ALGORITHM: str = os.getenv("ALGORITHM")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
settings = Settings()