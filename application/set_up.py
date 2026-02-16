class Setup:
    """
    Basic set up for the db's
    """
    SECRET_KEY = "passwordfortest"
    USERNAME = "postgres"
    DB_OLTP_NAME = "vayora_test"
    DB_OLAP_NAME = "vayora_dw"
    SQLALCHEMY_DATABASE_URI = f"postgresql://{USERNAME}:{SECRET_KEY}@localhost:5432/{DB_OLTP_NAME}"

    SQLALCHEMY_BINDS = {
        'dw' : f"postgresql://{USERNAME}:{SECRET_KEY}@localhost:5432/{DB_OLAP_NAME}"
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False