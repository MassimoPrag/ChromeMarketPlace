import os
import time
import pandas as pd
from functools import wraps

def run_weekly(file_path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if os.path.exists(file_path):
                file_mod_time = os.path.getmtime(file_path)
                current_time = time.time()
                one_week = 7 * 24 * 60 * 60  # One week in seconds
                if current_time - file_mod_time < one_week:
                    return pd.read_csv(file_path)
            df = func(*args, **kwargs)
            df.to_csv(file_path, index=False)
            return df
        return wrapper
    return decorator