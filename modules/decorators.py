from functools import wraps
import pymssql
import pandas as pd

def sql_cloud_connection(func):
    """
    Décorateur pour gérer la connexion et la déconnexion à la base de données SQL Azure.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        cred_dict = kwargs.get('cred_dict')
        conn = pymssql.connect(server=cred_dict['AZURE_SERVER'], 
                               user=cred_dict['AZURE_UID'], 
                               password=cred_dict['AZURE_PWD'], 
                               database=cred_dict['AZURE_DATABASE'])
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper