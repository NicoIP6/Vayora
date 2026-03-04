import os
import duckdb


class Setup:
    """
    Basic set up for the database_file's
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "secret")
    PASSWORD = os.getenv("POSTGRES_PASSWORD")
    USERNAME = os.getenv("POSTGRES_USER")
    DB_OLTP_NAME = os.getenv("POSTGRES_DB")
    DB_OLAP_NAME = os.getenv("POSTGRES_DW")
    DB_WEATHER_NAME = os.getenv("POSTGRES_STG")

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{USERNAME}:{PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_OLTP_NAME}"
    )

    SQLALCHEMY_BINDS = {
        "vayora_dw": f"postgresql://{USERNAME}:{PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_OLAP_NAME}",
        "weather": f"postgresql://{USERNAME}:{PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_WEATHER_NAME}"
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def get_duckdb_conn(cls) -> duckdb.DuckDBPyConnection | None:
        """
        Creates a DuckDB connection attached to all configured Postgresql databases.
        :return: a duckdb connection or None on failure
        """

        databases = {
            "vayora": cls.SQLALCHEMY_DATABASE_URI,
            "vayora_dw": cls.SQLALCHEMY_BINDS["vayora_dw"],
            "weather": cls.SQLALCHEMY_BINDS["weather"]
        }
        try:
            conn = duckdb.connect()
            conn.execute("INSTALL postgres")
            conn.execute("LOAD postgres")

            for alias, uri in databases.items():
                conn.execute(f"ATTACH '{uri}' AS {alias} (TYPE postgres)")

            return conn

        except Exception as e:
            print(f"Something went wrong while connecting to DuckDB. {e}")
            return None