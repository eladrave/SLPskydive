import os

# In a real app, this would be handled by a more robust settings management library
# like pydantic-settings, but we are using os.getenv as a workaround for environment issues.

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/skydiving")
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
