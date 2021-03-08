import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # CONFIG LOCALHOST
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
    MYSQL_PORT = os.getenv("MYSQL_PORT")
    MYSQL_PORT2 = os.getenv("MYSQL_PORT2")
    # CONFIG AWS
    # MYSQL_HOST = os.getenv("MYSQL_HOST_AWS")
    # MYSQL_USER = os.getenv("MYSQL_USER_AWS")
    # MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD_AWS")
    # MYSQL_DB = os.getenv("MYSQL_DB_AWS")
