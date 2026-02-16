import duckdb


def setup_duckdb(*args):
    """

    :param args: Every args must be a tuple with db name or alias and the connexion path.
    Check duckdb documentation to know the correct format.
    For exemple with postgres : postgresql://username:password@host:port/dbname

    :return: a duckdb connexion
    """

    try:
        conn = duckdb.connect()

        conn.execute("INSTALL postgres")
        conn.execute("LOAD postgres")

        for db in args:
            if not isinstance(db, tuple):
                print("One or more arguments given to the function weren't a tuple")
                return -1
            else:
                conn.execute(f"ATTACH '{db[1]}' as {db[0]} (TYPE postgres)")

        return conn

    except Exception as e:
        print(f"Something went wrong while connecting to duckdb : Exception {e}")