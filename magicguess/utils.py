# dedupe, shuffle, load/save wordlists

import os
import platform
from datetime import datetime

def clear_screen():
    if platform.system().lower() == "windows":
        os.system("cls")
    else:
        os.system("clear")

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False
