from os import environ
import databases


DATABASE_URL = environ.get("DATABASE_URL", "postgres:postgres@db:5432/pharmacies")
TESTING = False


if TESTING:
    DB_NAME = "startup_backend"
    TEST_SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{DATABASE_URL}"
    )
    database = databases.Database(TEST_SQLALCHEMY_DATABASE_URL)
else:
    DB_NAME = "startup_backend"
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{DATABASE_URL}"
    )
    print(SQLALCHEMY_DATABASE_URL)
    database = databases.Database(SQLALCHEMY_DATABASE_URL)
