from functools import wraps

import pymssql


def sql_cloud_connection(func):
    """
    Decorator to handle connection and disconnection to the Azure SQL database.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        cred_dict = kwargs.get("cred_dict")
        conn = pymssql.connect(
            server=cred_dict["AZURE_SERVER"],
            user=cred_dict["AZURE_UID"],
            password=cred_dict["AZURE_PWD"],
            database=cred_dict["AZURE_DATABASE"],
        )
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()

    return wrapper
