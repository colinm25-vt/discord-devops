from datetime import datetime


def get_timestamp() -> str:
    '''Return a timestamp in the form of YYYY-MM-DD hh:mm:ss'''
    return datetime.now().strftime("%Y-%m-%d %T")


def log(message: str):
    '''Log a message with a prepended timestamp'''
    timestamped_message = f"[{get_timestamp()}] {message}"
    print(timestamped_message)
