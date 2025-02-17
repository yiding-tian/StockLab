import re
import pandas as pd

def sanitize_filename(name):
    return re.sub(r'[*]', '', name)

def safe_round(value, decimals=2):
    if isinstance(value, (int, float)) and not pd.isna(value):
        return round(value, decimals)
    return "N/A"