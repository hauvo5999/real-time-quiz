from tortoise.contrib.fastapi import register_tortoise
from app.core.config import TORTOISE_ORM

def init_db(app):
    """
    Initialize database connection and create tables
    """
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    ) 