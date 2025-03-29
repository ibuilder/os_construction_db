import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""
    # App settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    DEBUG = False
    TESTING = False
    
    # Supabase settings
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 hours
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Cache settings
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # More permissive rate limits for development
    RATELIMIT_DEFAULT = "1000 per day;200 per hour"


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    # This would be more relevant if using SQLAlchemy
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    # Ensure these are set in production
    def __init__(self):
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY must be set in production")
        if not os.environ.get('JWT_SECRET_KEY'):
            raise ValueError("JWT_SECRET_KEY must be set in production")
    
    # Stricter rate limits for production
    RATELIMIT_DEFAULT = "100 per day;20 per hour"
    
    # Production caching (would use Redis or Memcached in a real app)
    CACHE_TYPE = "SimpleCache"  # Change to "RedisCache" in real production
    
    # Logging
    LOG_LEVEL = 'WARNING'


# Map environment names to config classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Return the appropriate configuration object based on the environment."""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])