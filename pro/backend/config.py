"""Configuration settings for HoneyBadger Pro"""
import os
from datetime import timedelta

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://honeybadger:honeybadger@localhost:5432/honeybadger")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "honeybadger-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Roles
ROLE_ADMIN = "admin"
ROLE_BASIC = "basic"
