import os

database_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///euromed_lost_found.db"
)

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql+psycopg://",
        1
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "uemfind-development-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    ALLOWED_IMAGE_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp"
    }