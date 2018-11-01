"""Default configuration

Use env var to override
"""
import datetime
import os

DEBUG = os.getenv('DEBUG', True)
SECRET_KEY = os.getenv('SECRET_KEY', 'not_secret')

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:////tmp/insta_pic.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'insta-pic')
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
