import os


class Config:
    SECRET_KEY = os.environ.get('12345') or 'dev-secret-key-2024'
    DEBUG = True