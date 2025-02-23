from functools import wraps
import time
import pymssql


def time_logger(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"Function '{func.__name__}' took {end_time - start_time:.4f} seconds.")
        return result

    return wrapper


def retry(retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay)
            raise Exception(f"Function '{func.__name__}' failed after {retries} retries.")

        return wrapper

    return decorator


def type_check(*expected_types):
    """
    Python’s type hints are informative but not enforced at runtime.
    This decorator ensures that functions are called with the correct argument types.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for arg, expected in zip(args, expected_types):
                if not isinstance(arg, expected):
                    raise TypeError(f"Expected {expected}, got {type(arg)}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def debug(func):
    """
    Logs input arguments and return values, making the debugging process easier.
    """

    def wrapper(*args, **kwargs):
        print(f"Calling '{func.__name__}' with args: {args} kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"'{func.__name__}' returned: {result}")
        return result

    return wrapper


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
