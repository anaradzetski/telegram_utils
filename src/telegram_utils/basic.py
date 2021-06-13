import re
from telegram.ext import Updater

def get_updater(path_to_token: str) -> Updater:
    """Get Updater by path to file with token"""
    with open(path_to_token) as f:
        return Updater(re.match(r'\S+', f.read()).group(0))
