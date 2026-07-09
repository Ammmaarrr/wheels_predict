"""
Secure Configuration Management
===============================

Centralized configuration management with environment variable support
for secure handling of sensitive data like database credentials.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Centralized configuration management"""
    
    # Database Configuration
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'pakwheelsdb')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    # Security Configuration
    SECRET_KEY: str = os.getenv('SECRET_KEY', '')
    
    # API Configuration
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD: Optional[str] = os.getenv('REDIS_PASSWORD')
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL for async connections"""
        if not cls.DB_PASSWORD:
            raise ValueError("DB_PASSWORD environment variable is required")
        
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_sync_db_params(cls) -> dict:
        """Get database parameters for synchronous connections"""
        if not cls.DB_PASSWORD:
            raise ValueError("DB_PASSWORD environment variable is required")
        
        return {
            'dbname': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'host': cls.DB_HOST,
            'port': cls.DB_PORT
        }
    
    @classmethod
    def validate_required_settings(cls) -> bool:
        """Validate that all required settings are present"""
        required_vars = ['DB_PASSWORD']
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please set them in your .env file or environment")
            return False
        
        return True

# Global config instance
config = Config()
